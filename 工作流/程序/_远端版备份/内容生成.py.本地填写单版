#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""内容生成.py —— 一句话→成品 的"内容生成层"（P0-1，见 进度与目标.md 三/1）。

把 一句话.py 只到大纲的断点续上：

    一句话 → 大纲 → 填写单 →(agent 填文案/数据)→ 组装 → pages.json → 校验闸

机械部分（选型/字段单/图表渲染/配图规划/占位图/组装/过闸）全代码化；
写真实文案、编数据、拍板标题留给 agent，通过"填写单"（fill.json）
这一机器可读接口交接。不手算、不口头约定。

用法（在 工作流/程序/ 下运行）：
    python 内容生成.py 大纲 --输入 "双11大促战报" --输出 /tmp/outline.json
    python 内容生成.py 填写单 --大纲 /tmp/outline.json --输出 /tmp/fill.json [--主题 dianshang]
    # agent 按 fill.json 的填写说明逐页填"填/图表/配图"，存 filled.json
    python 内容生成.py 组装 --填写 /tmp/filled.json --项目 示例-双11/双11战报 [--主题 dianshang] [--主题校验]
    python 内容生成.py 配图 --填写 /tmp/fill.json     # 打印配图 prompt 清单

规约：规约/内容生成规约.json
"""
import argparse
import io
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, USAGE, ERR, read_json, die, WORKFLOW, RULES_DIR

HERE = os.path.dirname(os.path.abspath(__file__))

# 生图 prompt 规约（延迟导入，缺文件时降级）
try:
    sys.path.insert(0, os.path.join(HERE, "生图"))
    from prompt规约 import complete as _补全, add_realism as _写实, check as _检查
    有提示规约 = True
except Exception:
    有提示规约 = False

import 一句话 as _一句话


def 载入规约():
    选型 = read_json(os.path.join(RULES_DIR, "选型规约.json"))
    卡型 = read_json(os.path.join(RULES_DIR, "卡型规约.json"))
    内容 = read_json(os.path.join(RULES_DIR, "内容生成规约.json"))
    return 选型, 卡型, 内容


def 写文件(path, obj):
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# ---------- 选型 ----------

def 选型(意图, tpl建议, 选型规约):
    """意图 → (选中tpl, 候选, 理由)。规则见 内容生成规约.选型规则。"""
    映射表 = 选型规约["映射"]
    if 意图 not in 映射表:
        die("意图 %r 不在选型规约意图闭集内" % 意图)
    映射 = 映射表[意图]
    if 映射 and isinstance(映射[0], dict):
        映射tpls = [e["tpl"] for e in 映射]
    else:
        映射tpls = list(映射)
    交集 = [t for t in (tpl建议 or []) if t in 映射tpls]
    备注 = ""
    if not 交集:
        备注 = "（模板建议与映射无交集，回退映射首位）"
    选中 = 交集[0] if 交集 else 映射tpls[0]
    # 候选取映射全量（校验⑦期望候选=映射[意图]；模板建议只决定选中，记在理由里）
    候选 = 映射tpls
    理由 = "意图=%s；模板建议=%s；映射候选=%s；选中交集首位=%s%s" % (
        意图, list(tpl建议 or []), 映射tpls, 选中, 备注)
    return 选中, 候选, 理由


# ---------- 配图 prompt ----------

场景词 = {"电商": "仓库", "大促": "直播间", "带货": "直播间", "课堂": "教室",
        "化学": "教室", "物理": "教室", "办公": "办公室", "会议": "办公室",
        "城市": "城市", "夜景": "城市", "家庭": "家庭", "街道": "街道"}


def 配图prompt(输入, 意图, 文案提示):
    """按 prompt规约 生成规约合规的生图 prompt 草稿。返回 (prompt, 场景, 有人物)。"""
    场景 = None
    for k, v in 场景词.items():
        if k in (输入 or "") or k in (文案提示 or ""):
            场景 = v
            break
    头 = {"封面": "封面主视觉，大气构图"}.get(意图, "页面配图")
    draft = "%s，%s，commercial photography" % (文案提示 or 意图, 头)
    有人物 = False
    if 有提示规约:
        p = _补全(draft, has_people=有人物, scene=场景)
        p = _写实(p)
    else:
        p = draft
    return p, 场景, 有人物


# ---------- 占位图 ----------

def 占位图(path, 页id, title):
    """无桌面生图环境时生成占位图过闸（交付前须替换）。"""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), (24, 24, 28))
    dr = ImageDraw.Draw(img)
    for y in range(H):  # 纵向微渐变
        t = y / H
        dr.line([(0, y), (W, y)],
                fill=(int(24 + 20 * t), int(24 + 18 * t), int(28 + 22 * t)))
    try:
        fc = os.path.expanduser("~/.local/share/fonts/NotoSansCJKsc-Regular.otf")
        f1 = ImageFont.truetype(fc, 64)
        f2 = ImageFont.truetype(fc, 36)
    except Exception:
        try:
            f1 = ImageFont.load_default(size=64)
            f2 = ImageFont.load_default(size=36)
        except TypeError:
            f1 = ImageFont.load_default()
            f2 = f1
    dr.text((W // 2, H // 2 - 60), 页id, font=f1, fill=(200, 170, 90),
            anchor="mm")
    dr.text((W // 2, H // 2 + 20), (title or "")[:14], font=f2,
            fill=(160, 160, 160), anchor="mm")
    dr.text((W // 2, H // 2 + 90), "占位图 · 待 Gemini 生图替换", font=f2,
            fill=(120, 120, 120), anchor="mm")
    img.save(path)


# ---------- 图表渲染 ----------

def 渲染图表(kind, 主题, g, out):
    """g: fill.json 里 图表。数据约定见 内容生成规约.图表纪律.数据格式。"""
    import 图表 as G
    数据 = g["数据"]
    kw = dict(主题=主题, 输出=out, 标题=g.get("图表标题", ""),
            单位=g.get("单位", ""))
    if kind == "bar":
        G.bar(数据=数据, 强调=g.get("强调"), **kw)
    elif kind == "pie":
        G.pie(数据=数据, **kw)
    elif kind == "funnel":
        G.funnel(数据=数据, **kw)
    elif kind == "waterfall":
        G.waterfall(数据=数据, **kw)
    elif kind == "line":
        x = g.get("x") or ["P%d" % (i + 1) for i in range(len(next(iter(数据.values()))))]
        G.line(x=x, 系列=数据, **kw)
    else:
        die("图表 kind=%r 非法，闭集 %s" % (kind, ["bar", "line", "pie", "funnel", "waterfall"]))


# ---------- 子命令 ----------

def cmd_大纲(a):
    out = _一句话.生成大纲(a.输入)
    txt = json.dumps(out, ensure_ascii=False, indent=2)
    if a.输出:
        io.open(a.输出, "w", encoding="utf-8").write(txt)
    else:
        print(txt)
    print("大纲：%d页，模板=%s" % (out["页数"], out["大纲模板"]), file=sys.stderr)
    return OK


def cmd_填写单(a):
    选型规约, 卡型规约, 内容规约 = 载入规约()
    大纲 = read_json(a.大纲)
    条目规约 = 卡型规约["页面条目"]
    字段说明表 = 内容规约["字段说明"]
    # 主题：参数优先，否则取主题推荐首位
    主题 = a.主题
    if not 主题 and 大纲.get("主题推荐"):
        主题 = 大纲["主题推荐"][0]["主题"]
    页s = []
    for p in 大纲["页"]:
        页id, 意图 = p["页"], p["意图"]
        选中, 候选, 理由 = 选型(意图, p.get("tpl建议"), 选型规约)
        if 选中 not in 条目规约:
            die("%s 选中 tpl=%r 不在卡型规约内" % (页id, 选中))
        必填 = 条目规约[选中]["必填"]
        说明 = dict(字段说明表.get("通用", {}))
        说明.update(字段说明表.get(选中, {}))
        条目 = {
            "页": 页id,
            "意图": 意图,
            "tpl": 选中,
            "_选型": {"意图": 意图, "候选": 候选, "选中": 选中, "理由": 理由},
            "文案提示": p.get("文案提示", ""),
            "必填": 必填,
            "字段说明": {k: 说明[k] for k in 必填 if k in 说明},
            "填": {},
        }
        if 选中 == "chart":
            条目["图表"] = {
                "kind": None,
                "数据": None,
                "kind候选": 内容规约["图表纪律"]["kind闭集"],
                "说明": "agent 填 kind+数据（格式见内容生成规约.图表纪律.数据格式）；"
                        "组装时调 洞察.py 算标题、调 图表.py 渲染 PNG 进 素材/",
            }
        # 配图规划：img 必填（chart 除外，图表即视觉）/ bg 必填 / img 选填（photo_*）
        字段 = None
        if "img" in 必填 and 选中 != "chart":
            字段 = "img"
        elif "bg" in 必填:
            字段 = "bg"
        elif "img" in (条目规约.get(选中, {}).get("选填") or []):
            字段 = "img"
        if 字段:
            prompt, 场景, 有人物 = 配图prompt(大纲.get("输入"), 意图, p.get("文案提示"))
            必填图 = (字段 == "img" and "img" in 必填) or (字段 == "bg")
            条目["配图"] = {
                "字段": 字段,
                "文件": "%s-%s.png" % (页id, 选中) if 字段 == "img" else "%s-bg.png" % 页id,
                "prompt": prompt,
                "场景": 场景,
                "有人物": 有人物,
                "状态": "待生图" if 必填图 else "待生图（选填）",
                "说明": "prompt 已过 prompt规约；生图默认走 Playwright 连谷歌 Gemini（千问 API 仅备选），"
                        "组装时缺图自动生成占位图过闸，交付前用 生图 子命令替换",
            }
        页s.append(条目)
    out = {
        "输入": 大纲["输入"],
        "意图": 大纲["意图"],
        "主题推荐": 大纲.get("主题推荐"),
        "主题选用": 主题,
        "大纲模板": 大纲.get("大纲模板"),
        "页数": len(页s),
        "填写说明": 内容规约["填写单"]["填写说明"],
        "页": 页s,
    }
    写文件(a.输出, out)
    print("填写单 → %s（%d页，主题=%s）" % (a.输出, len(页s), 主题), file=sys.stderr)
    print("下一步：agent 按 填写说明 逐页填 填/图表/配图，存 filled.json 后跑 组装",
          file=sys.stderr)
    return OK


def cmd_组装(a):
    选型规约, 卡型规约, 内容规约 = 载入规约()
    fill = read_json(a.填写)
    主题 = a.主题 or fill.get("主题选用") or "sodium"
    proj = os.path.normpath(os.path.join(WORKFLOW, a.项目))
    页dir = os.path.join(proj, "页")
    素材dir = os.path.join(proj, "素材")
    os.makedirs(页dir, exist_ok=True)
    os.makedirs(素材dir, exist_ok=True)
    from 洞察 import 分析器 as 洞察器

    pages, 跳过数 = [], 0
    for p in fill["页"]:
        if p.get("跳过"):
            跳过数 += 1
            print("跳过 %s：%s" % (p["页"], p.get("跳过理由", "")), file=sys.stderr)
            continue
        entry = {"id": p["页"], "tpl": p["tpl"]}
        entry.update(p.get("填") or {})
        # 图表页：数据 → 洞察 → 标题 → 渲染
        g = p.get("图表")
        if p["tpl"] == "chart":
            if not (g and g.get("kind") and g.get("数据")):
                die("%s 是 chart 页但 图表.kind/数据 未填" % p["页"])
            kind = g["kind"]
            if kind not in 洞察器:
                die("%s 图表 kind=%r 非法" % (p["页"], kind))
            res = 洞察器[kind](g["数据"])
            # LLM 洞察优先：填写单 图表.洞察（洞察生成.py 产出，已过数字出处闸）→ 直接用；
            # 无则回落规则版 洞察.py（离线兜底，同一形状）
            llm = g.get("洞察")
            if isinstance(llm, dict) and llm.get("标题候选") and llm.get("支撑"):
                bullets = llm["支撑"][:3]
                print("洞察 %s：LLM 路径（%d 条支撑）" % (p["页"], len(bullets)),
                      file=sys.stderr)
            else:
                bullets = res["支撑"][:3]
            title = entry.get("title") or (res["标题候选"][0] if res["标题候选"] else "")
            if not title:
                die("%s 洞察无标题候选且 title 未填" % p["页"])
            entry["title"] = title
            entry["insight"] = {"take": title, "bullets": bullets}
            out_png = os.path.join(素材dir, "%s-chart.png" % p["页"])
            渲染图表(kind, 主题, g, out_png)
            entry["img"] = "%s-chart.png" % p["页"]
            print("图表 %s：%s → %s" % (p["页"], kind, os.path.basename(out_png)),
                  file=sys.stderr)
        # 配图 / 背景图：缺图则占位图过闸（交付前用 生图 子命令替换）
        pg = p.get("配图")
        if pg:
            fp = os.path.join(素材dir, pg["文件"])
            if not os.path.isfile(fp):
                占位图(fp, p["页"], entry.get("title", ""))
                pg["状态"] = "占位图（待生图替换）"
                print("占位图 %s：%s" % (p["页"], pg["文件"]), file=sys.stderr)
            # img 必填而 agent 没填时自动填入；选填 img 由 agent 定夺（不硬塞）
            必填 = 卡型规约["页面条目"][p["tpl"]]["必填"]
            if pg.get("字段") == "img" and "img" in 必填 and "img" not in entry:
                entry["img"] = pg["文件"]
        for imgkey in ("bg", "img"):
            fn = entry.get(imgkey)
            if fn and not os.path.isfile(os.path.join(素材dir, fn)):
                占位图(os.path.join(素材dir, fn), p["页"], entry.get("title", ""))
                print("占位图 %s：%s（%s）" % (p["页"], fn, imgkey), file=sys.stderr)
        entry["_选型"] = p["_选型"]
        # 全局选填透传：transition/enter 等动效字段（卡型规约·全局选填）
        for _k in ("transition", "enter"):
            if p.get(_k):
                entry[_k] = p[_k]
        pages.append(entry)

    # id 连续性整理：no 字段由 agent 填，这里只保证 id 唯一（校验会查重复）
    写文件(os.path.join(页dir, "pages.json"), pages)

    # 过闸
    env = dict(os.environ, PPT_PROJECT=a.项目)
    cmd = [sys.executable, os.path.join(HERE, "校验.py")]
    if a.主题校验:
        cmd += ["--主题", 主题]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=HERE)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode == 0:
        print("组装 PASS：%s，共 %d 页（跳过 %d 页）" % (a.项目, len(pages), 跳过数))
        return OK
    print("组装 FAIL：按 校验 输出修 filled.json 后重跑 组装（不许绕过）",
          file=sys.stderr)
    return FAIL


def cmd_配图(a):
    fill = read_json(a.填写)
    for p in fill["页"]:
        pg = p.get("配图")
        if not pg:
            continue
        print("== %s（%s）→ 素材/%s ==" % (p["页"], p["tpl"], pg["文件"]))
        print("场景=%s 有人物=%s 状态=%s" % (pg.get("场景"), pg.get("有人物"), pg.get("状态")))
        print(pg["prompt"])
        print()
    return OK


# ---------- 生图 ----------

生图后端 = {"千问": "千问生图.py", "gemini": "gemini生图.py"}
后端模型 = {"千问": "qwen-image-3.0", "gemini": "gemini-web"}


def 登记素材卡(pg, 文案提示, 后端):
    """素材/_步.json M3：文件/prompt/模型/尺寸/来源轨 写入素材卡.jsonl，不登记=不存在。"""
    import datetime
    卡path = os.path.join(LIB_DIR, "素材", "素材卡.jsonl")
    today = datetime.date.today().strftime("%Y%m%d")
    seq = 1
    if os.path.isfile(卡path):
        for line in io.open(卡path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                rid = json.loads(line).get("id", "")
            except ValueError:
                continue
            if rid.startswith("素材-" + today + "-"):
                try:
                    seq = max(seq, int(rid.rsplit("-", 1)[1]) + 1)
                except ValueError:
                    pass
    row = {"id": "素材-%s-%03d" % (today, seq), "卡型": "素材卡",
           "标题": pg["文件"], "来源轨": "内容生成层", "生产者": "内容生成.py",
           "状态": "可用", "一句话": (文案提示 or "")[:60],
           "文件": pg["文件"], "prompt": pg["prompt"],
           "模型": 后端模型[后端], "尺寸": "1664x928"}
    with io.open(卡path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row["id"]


def cmd_生图(a):
    """占位图 → 真实生图（素材/_步.json M1–M4 进流水线）。

    每页配图：prompt规约 --检查（M2 强制）→ 后端生图 →
    素材/ + 素材卡登记（M3）→ 配图.状态=已生图。状态写回 fill.json，可续跑。
    生图后须重跑 页面生成.py + 截图.py（素材 base64 内嵌进 HTML）。
    """
    if a.后端 not in 生图后端:
        die("后端 %r 非法，可选：%s" % (a.后端, sorted(生图后端)))
    fill = read_json(a.填写)
    proj = os.path.normpath(os.path.join(WORKFLOW, a.项目))
    素材dir = os.path.join(proj, "素材")
    os.makedirs(素材dir, exist_ok=True)
    只 = set(a.只.split(",")) if a.只 else None

    ok, fail, skip = 0, 0, 0
    for p in fill["页"]:
        pg = p.get("配图")
        if not pg:
            continue
        if 只 and p["页"] not in 只:
            continue
        if pg.get("状态", "").startswith("已生图"):
            print("跳过 %s：%s" % (p["页"], pg["状态"]))
            skip += 1
            continue
        prompt = pg["prompt"]
        # M2：生成前必须过 prompt 规约
        r = subprocess.run(
            [sys.executable, os.path.join(HERE, "生图", "prompt规约.py"),
             "--检查", prompt],
            capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL %s：prompt 未过规约：%s" % (p["页"], r.stdout.strip()[:120]))
            fail += 1
            continue
        out = os.path.join(素材dir, pg["文件"])
        cmd = [sys.executable, os.path.join(HERE, "生图", 生图后端[a.后端]),
               "--prompt", prompt, "--out", out]
        if a.演练:
            print("演练 %s：%s --prompt … --out %s" %
                  (p["页"], 生图后端[a.后端], pg["文件"]))
            ok += 1
            continue
        print("生图 %s（%s）…" % (p["页"], a.后端), flush=True)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        except subprocess.TimeoutExpired:
            print("FAIL %s：后端超时（900s）" % p["页"])
            fail += 1
            continue
        if r.returncode == 0 and os.path.isfile(out):
            pg["状态"] = "已生图（%s）" % a.后端
            卡id = 登记素材卡(pg, p.get("文案提示"), a.后端)
            print("OK %s：%s（%s）" % (p["页"], pg["文件"], 卡id))
            ok += 1
        else:
            print("FAIL %s：%s" % (p["页"], (r.stdout + r.stderr).strip()[-200:]))
            fail += 1
    写文件(a.填写, fill)  # 状态落盘，可续跑
    print("生图完成：成功 %d，失败 %d，跳过 %d" % (ok, fail, skip))
    if ok and not a.演练:
        print("下一步：重跑 页面生成.py + 截图.py（素材已换，HTML 内嵌须重渲染）")
    return OK if fail == 0 else FAIL


def main():
    ap = argparse.ArgumentParser(prog="内容生成.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("大纲", help="一句话 → 大纲 JSON")
    s.add_argument("--输入", required=True)
    s.add_argument("--输出", default=None)

    s = sub.add_parser("填写单", help="大纲 → fill.json（agent 填写用）")
    s.add_argument("--大纲", required=True)
    s.add_argument("--输出", required=True)
    s.add_argument("--主题", default=None, help="覆盖主题选用")

    s = sub.add_parser("组装", help="filled.json → pages.json → 校验")
    s.add_argument("--填写", required=True)
    s.add_argument("--项目", required=True, help="相对 工作流/ 的项目目录")
    s.add_argument("--主题", default=None, help="图表主题（默认 fill.json 主题选用）")
    s.add_argument("--主题校验", action="store_true", help="校验时追加 --主题（主题卡+CSS 令牌闸）")

    s = sub.add_parser("配图", help="打印配图 prompt 清单")
    s.add_argument("--填写", required=True)

    s = sub.add_parser("生图", help="占位图 → 真实生图（进素材流水线）")
    s.add_argument("--填写", required=True, help="fill.json（状态写回此文件，可续跑）")
    s.add_argument("--项目", required=True, help="相对 工作流/ 的项目目录")
    s.add_argument("--后端", default="gemini", help="gemini|千问（默认 gemini：Playwright 连谷歌）")
    s.add_argument("--只", default=None, help="只跑指定页，如 P1,P3")
    s.add_argument("--演练", action="store_true", help="只走检查不调后端")

    a = ap.parse_args()
    fn = {"大纲": cmd_大纲, "填写单": cmd_填写单, "组装": cmd_组装,
          "配图": cmd_配图, "生图": cmd_生图}[a.cmd]
    sys.exit(fn(a))


if __name__ == "__main__":
    main()
