#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主题生成 —— 用户一句话 → 4 套贴合需求的主题候选。

管线：归约（固定格式）→ 提示词（固定模板，喂大模型）→ 校验（固定闸）→ 卡片（HTML呈现）
大模型调用由 agent/控制台完成，本程序不碰 LLM API；输出 JSON 形状固定。

用法:
  python 主题生成.py 归约 --输入 "双11电商大促战报" --输出 /tmp/brief.json
  python 主题生成.py 提示词 --归约 /tmp/brief.json            # 打印固定提示词
  python 主题生成.py 校验 --主题 /tmp/themes.json             # 大模型输出过闸
  python 主题生成.py 卡片 --主题 /tmp/themes.json --归约 /tmp/brief.json --输出 /tmp/cards.html
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import LIB_DIR, read_json, die
from 配色 import contrast, lum

# ---------- 归约词典 ----------
行业词 = [
    (["电商", "双11", "618", "带货", "直播", "GMV", "店铺", "促销", "秒杀",
      "团购", "拼团", "私域", "微商"], "电商"),
    (["化学", "氧化", "分子", "元素", "物理", "力学", "电路", "生物", "细胞", "数学", "方程"], "教育"),
    (["财报", "财务", "营收", "利润", "风控", "审计"], "金融"),
    (["融资", "BP", "路演", "投资", "创业"], "融资"),
    (["医疗", "医院", "健康", "诊断"], "医疗"),
    (["年会", "庆典", "晚会", "发布会"], "庆典"),
    (["培训", "内训", "SOP"], "培训"),
    (["政府", "政务", "党建"], "政务"),
]
受众词 = [
    (["学生", "初中", "高中", "课堂", "课件", "教学"], "学生"),
    (["客户", "甲方", "提案", "方案"], "客户"),
    (["领导", "汇报", "述职", "总结", "复盘", "战报"], "管理层"),
    (["投资人", "路演"], "投资人"),
]
场景词 = [
    (["战报", "复盘", "总结", "述职", "汇报"], "复盘汇报"),
    (["路演", "融资", "BP"], "路演融资"),
    (["课件", "课堂", "教学"], "课堂"),
    (["提案", "方案"], "提案"),
    (["年会", "庆典", "晚会"], "年会"),
    (["培训", "内训"], "培训"),
]
行业情绪 = {
    "电商": ["热烈", "紧迫", "胜利感"],
    "教育": ["清新", "启发", "亲和"],
    "金融": ["稳重", "专业", "信任"],
    "融资": ["锐气", "未来感", "可信"],
    "医疗": ["洁净", "安心", "专业"],
    "庆典": ["喜庆", "隆重", "热烈"],
    "培训": ["清晰", "条理", "亲和"],
    "政务": ["庄重", "规范", "可信"],
    "通用": ["专业", "清晰", "得体"],
}
行业禁忌 = {
    "电商": ["性冷淡风", "低饱和莫兰迪", "文艺小清新"],
    "教育": ["暗黑压抑", "过度商务"],
    "金融": ["花哨", "卡通", "荧光色"],
    "融资": ["陈旧", "沉闷"],
    "医疗": ["暗黑压抑", "血腥暗示"],
    "庆典": ["冷淡", "性冷淡风"],
    "培训": ["花哨", "低对比"],
    "政务": ["轻浮", "卡通"],
    "通用": ["低对比度"],
}


def 命中(text, 词表, 缺省):
    for kws, v in 词表:
        for k in kws:
            if k in text:
                return v
    return 缺省


def 归约(text):
    行业 = 命中(text, 行业词, "通用")
    关键词 = []
    for kws, _ in 行业词 + 受众词:
        for k in kws:
            if k in text and k not in 关键词:
                关键词.append(k)
    return {
        "题材": text.strip(),
        "行业": 行业,
        "受众": 命中(text, 受众词, "公众"),
        "场景": 命中(text, 场景词, "通用"),
        "情绪": 行业情绪.get(行业, 行业情绪["通用"]),
        "关键词": 关键词[:6],
        "禁忌": 行业禁忌.get(行业, 行业禁忌["通用"]),
    }


PROMPT_TPL = (
    "你是资深PPT视觉设计师。用户需求（JSON）：\n{brief}\n\n"
    "第一步：用一句话分析该行业×场景×情绪的视觉诉求"
    "（例如电商大促→紧迫感、热烈、胜利感→高饱和暖色、深色底、大字报排版）。\n"
    "第二步：生成4套主题方案，每套输出以下字段的JSON对象："
    "slug(英文小写短横线)、name(中文名≤6字)、风格一句话、设计推理(为什么贴合该需求，一句话)、"
    "适用场景、bg、bg_dark、ink、gold、gold_soft、green、ox(均为#RRGGBB)、"
    "字体风格(衬线/无衬线/混搭)、封面版式(一句话描述)、卡片版式(一句话描述)。\n\n"
    "硬约束：4套必须拉开差距——至少1套深色底、至少1套浅色底；"
    "主色(gold)色相两两不同；不许出现以下禁忌风格：{taboo}；不许只微调色相的套娃方案。\n"
    "只输出JSON数组，不要markdown、不要解释。"
)

必填 = ["slug", "name", "风格一句话", "设计推理", "适用场景", "bg", "bg_dark",
        "ink", "gold", "gold_soft", "green", "ox", "字体风格", "封面版式", "卡片版式"]
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def rgb_dist(a, b):
    a = a.lstrip("#")
    b = b.lstrip("#")
    ra, ga, ba = int(a[0:2], 16), int(a[2:4], 16), int(a[4:6], 16)
    rb, gb, bb = int(b[0:2], 16), int(b[2:4], 16), int(b[4:6], 16)
    return ((ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2) ** 0.5


def 现有主题色():
    out = []
    for f in os.listdir(LIB_DIR):
        if f.startswith("theme-") and f.endswith(".css"):
            txt = open(os.path.join(LIB_DIR, f), encoding="utf-8").read()
            bg = re.search(r"--bg:\s*(#[0-9a-fA-F]{6})", txt)
            gold = re.search(r"--gold:\s*(#[0-9a-fA-F]{6})", txt)
            if bg and gold:
                out.append((f, bg.group(1), gold.group(1)))
    return out


def 校验(themes):
    errs = []
    if not isinstance(themes, list) or len(themes) != 4:
        return ["须是4套主题的JSON数组"]
    slugs = set()
    for i, t in enumerate(themes):
        tag = "第%d套(%s)" % (i + 1, t.get("slug", "?"))
        for f in 必填:
            if f not in t or not t[f]:
                errs.append("%s 缺字段 %s" % (tag, f))
        for c in ["bg", "bg_dark", "ink", "gold", "gold_soft", "green", "ox"]:
            if c in t and not HEX.match(str(t[c])):
                errs.append("%s 色值 %s 非法" % (tag, c))
        if t.get("slug") in slugs:
            errs.append("%s slug 重复" % tag)
        slugs.add(t.get("slug"))
        if HEX.match(str(t.get("bg", ""))) and HEX.match(str(t.get("ink", ""))):
            if contrast(t["ink"], t["bg"]) < 4.5:
                errs.append("%s ink/bg 对比度 %.2f < 4.5" % (tag, contrast(t["ink"], t["bg"])))
            for c in ["gold", "green", "ox"]:
                if HEX.match(str(t.get(c, ""))) and contrast(t[c], t["bg"]) < 3.0:
                    errs.append("%s %s/bg 对比度 %.2f < 3.0" % (tag, c, contrast(t[c], t["bg"])))
    for i, t in enumerate(themes):
        for f, ebg, egold in 现有主题色():
            if rgb_dist(t["bg"], ebg) <= 70 and rgb_dist(t["gold"], egold) <= 50:
                errs.append("第%d套(%s) 与现有的 %s 过近，判套娃" % (i + 1, t["slug"], f))
    for i in range(4):
        for j in range(i + 1, 4):
            if rgb_dist(themes[i]["bg"], themes[j]["bg"]) <= 70 and \
               rgb_dist(themes[i]["gold"], themes[j]["gold"]) <= 80:
                errs.append("第%d套与第%d套底色与主色都过近" % (i + 1, j + 1))
    lums = [lum(t["bg"]) for t in themes]
    if not any(v < 0.35 for v in lums):
        errs.append("4套中没有深色底(lum<0.35)")
    if not any(v > 0.6 for v in lums):
        errs.append("4套中没有浅色底(lum>0.6)")
    return errs


CARD_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"PingFang SC","Microsoft YaHei",sans-serif;background:#f2f2f2;padding:16px}
h1{font-size:20px;margin-bottom:4px}
.sub{color:#666;font-size:13px;margin-bottom:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.card{border-radius:12px;overflow:hidden;background:#fff;box-shadow:0 2px 12px rgba(0,0,0,.08);cursor:pointer;border:2px solid transparent}
.card.sel{border-color:#1677ff}
.hero{height:150px;padding:20px;display:flex;flex-direction:column;justify-content:flex-end}
.hero .t1{font-size:26px;font-weight:800}
.hero .t2{font-size:12px;letter-spacing:3px;margin-bottom:6px;opacity:.8}
.swatches{display:flex;height:34px}
.swatches div{flex:1}
.body{padding:14px 16px}
.body h2{font-size:17px;margin-bottom:2px}
.body .style{color:#888;font-size:13px;margin-bottom:8px}
.body .why{font-size:13px;line-height:1.6;color:#333;background:#f7f7f7;border-radius:8px;padding:8px 10px;margin-bottom:8px}
.body .meta{font-size:12px;color:#999;line-height:1.7}
.body .meta b{color:#555}
.pick{margin-top:10px;text-align:center;font-size:13px;color:#1677ff}
"""


def 卡片_html(themes, brief):
    cards = []
    for t in themes:
        cards.append(
            '<div class="card" data-slug="{slug}">'
            '<div class="hero" style="background:{bg};color:{ink}">'
            '<div class="t2" style="color:{gold}">THEME PREVIEW</div>'
            '<div class="t1">{name}</div>'
            '<div style="color:{gold_soft};font-size:13px;margin-top:4px">双11 · 电商大促战报</div>'
            "</div>"
            '<div class="swatches">'
            '<div style="background:{bg}"></div><div style="background:{bg_dark}"></div>'
            '<div style="background:{ink}"></div><div style="background:{gold}"></div>'
            '<div style="background:{gold_soft}"></div><div style="background:{green}"></div>'
            "</div>"
            '<div class="body"><h2>{name}</h2><div class="style">{style}</div>'
            '<div class="why">💡 {why}</div>'
            '<div class="meta"><b>适用</b>：{scene}<br><b>封面</b>：{cover}'
            "<br><b>卡片</b>：{card}<br><b>字体</b>：{font}</div>"
            '<div class="pick">👉 点我选中这套</div></div></div>'.format(
                slug=t["slug"], bg=t["bg"], bg_dark=t["bg_dark"], ink=t["ink"],
                gold=t["gold"], gold_soft=t["gold_soft"], green=t["green"],
                name=t["name"], style=t["风格一句话"], why=t["设计推理"],
                scene=t["适用场景"], cover=t["封面版式"], card=t["卡片版式"],
                font=t["字体风格"]))
    head = (
        '<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>主题候选 · " + brief["题材"] + "</title><style>" + CARD_CSS + "</style></head>"
        "<body><h1>🎨 为「" + brief["题材"] + "」生成 4 套主题</h1>"
        '<div class="sub">行业：' + brief["行业"] + " · 场景：" + brief["场景"] +
        " · 情绪：" + "、".join(brief["情绪"]) + " — 点一张卡即选中</div>"
        '<div class="grid">' + "".join(cards) + "</div>"
        "<script>"
        "document.querySelectorAll('.card').forEach(function(c){c.onclick=function(){"
        "document.querySelectorAll('.card').forEach(function(x){x.classList.remove('sel')});"
        "c.classList.add('sel');alert('已选：'+c.dataset.slug);}});"
        "</script></body></html>"
    )
    return head


def 落库(spec, brief):
    """LLM 主题 spec → 库/theme-<slug>.css（13 令牌）+ 主题卡。

    7 个令牌取 LLM spec；另 6 个按 配色.full_scheme 同源逻辑推导。
    """
    import colorsys
    from 配色 import 最近过闸值, rgb, hex_of
    bg, bg_dark = spec["bg"], spec["bg_dark"]
    dark = lum(bg) < 0.5
    mut_cand = "9AA3B2" if dark else "5A6472"
    muted = mut_cand if contrast(mut_cand, bg) >= 4.5 else 最近过闸值(mut_cand, bg, 4.5)
    r, g, b = rgb(bg)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    card = hex_of(*colorsys.hls_to_rgb(h, min(1, max(0, l + (0.06 if dark else -0.05))), s))
    line = hex_of(*colorsys.hls_to_rgb(h, min(1, max(0, l + (0.12 if dark else -0.10))), s))
    rh2, rl2, rs2 = colorsys.rgb_to_hls(*rgb(bg_dark))
    line_dark = hex_of(*colorsys.hls_to_rgb(rh2, min(0.95, rl2 + 0.14), rs2))
    ink_dark = "F5F7FA"
    if contrast(ink_dark, bg_dark) < 4.5:
        ink_dark = 最近过闸值(ink_dark, bg_dark, 4.5) or ink_dark

    def H(x):
        x = x if x.startswith("#") else "#" + x
        return x.upper()

    tokens = {"bg": bg, "bg-dark": bg_dark, "gold": spec["gold"],
              "gold-soft": spec["gold_soft"], "ink": spec["ink"],
              "green": spec["green"], "silver": muted, "muted": muted,
              "line": line, "line-dark": line_dark, "card": card,
              "ox": spec["ox"], "ink-dark": ink_dark}
    src = open(os.path.join(LIB_DIR, "theme-chemlab.css"), encoding="utf-8").read()
    for k, v in tokens.items():
        src = re.sub(r"(--" + k + r"\s*:\s*)#[0-9a-fA-F]{6}",
                     r"\g<1>" + H(v), src)
    out = os.path.join(LIB_DIR, "theme-%s.css" % spec["slug"])
    open(out, "w", encoding="utf-8").write(src)
    # 主题卡（供 校验.py --主题 与 主题推荐.py 消费）
    深浅 = "深底" if dark else "浅底"
    md = ("# 主题卡-{slug}\n\n- id: 主题卡-{slug}\n- 卡型: 主题卡\n"
          "- 标题: {name}\n- 来源轨: 主题生成算法（提问哲学分则1，大模型生成+规则校验）\n"
          "- 生产者: Muse\n- 状态: 草案（待样张目视）\n- css路径: 库/theme-{slug}.css\n\n"
          "## 匹配标签（主题推荐.py 消费）\n\n- 深浅: {deep}\n- 行业: {ind}\n"
          "- 气质: {emo}\n- 场景: {scene}\n- 关键词: {kw}\n\n## 一句话\n\n{style}\n\n"
          "## 设计推理\n\n{why}\n").format(
        slug=spec["slug"], name=spec["name"], deep=深浅, ind=brief["行业"],
        emo="、".join(brief["情绪"]), scene=brief["场景"],
        kw="、".join(brief["关键词"]), style=spec["风格一句话"],
        why=spec["设计推理"])
    open(os.path.join(LIB_DIR, "主题", "卡片", "主题卡-%s.md" % spec["slug"]),
         "w", encoding="utf-8").write(md)
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("归约")
    p.add_argument("--输入", required=True)
    p.add_argument("--输出", required=True)
    p = sub.add_parser("提示词")
    p.add_argument("--归约", required=True)
    p = sub.add_parser("校验")
    p.add_argument("--主题", required=True)
    p = sub.add_parser("卡片")
    p.add_argument("--主题", required=True)
    p.add_argument("--归约", required=True)
    p.add_argument("--输出", required=True)
    p = sub.add_parser("落库")
    p.add_argument("--主题", required=True, help="校验通过的主题 JSON")
    p.add_argument("--选择", required=True, help="slug")
    p.add_argument("--归约", required=True)
    a = ap.parse_args()
    if a.cmd == "归约":
        b = 归约(a.输入)
        json.dump(b, open(a.输出, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("归约 → %s（行业=%s，情绪=%s）" % (a.输出, b["行业"], "、".join(b["情绪"])))
    elif a.cmd == "提示词":
        b = read_json(a.归约)
        print(PROMPT_TPL.format(brief=json.dumps(b, ensure_ascii=False, indent=2),
                                taboo="、".join(b["禁忌"])))
    elif a.cmd == "校验":
        themes = read_json(a.主题)
        errs = 校验(themes)
        if errs:
            print("FAIL 校验不通过（%d项）：" % len(errs))
            for e in errs:
                print(" - " + e)
            sys.exit(1)
        print("校验 PASS：4套主题全过（格式/对比度/去重/互异）")
    elif a.cmd == "卡片":
        themes = read_json(a.主题)
        brief = read_json(a.归约)
        open(a.输出, "w", encoding="utf-8").write(卡片_html(themes, brief))
        print("卡片 → %s" % a.输出)
    elif a.cmd == "落库":
        themes = read_json(a.主题)
        brief = read_json(a.归约)
        spec = next(t for t in themes if t["slug"] == a.选择)
        out = 落库(spec, brief)
        print("落库 → %s（+主题卡）" % out)
    else:
        die("用法见文件头注释")


if __name__ == "__main__":
    main()
