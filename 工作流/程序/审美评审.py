#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""审美评审 v3 —— 预览截图 → 外部视觉模型（Gemini/ChatGPT）评审闸。

提问哲学分则：话术模板固定（规约/审美评审提示词.md v3），输出必过闸。

管线位置：截图.py 之后。模型只给评审意见 + 修改清单；合格与否由用户判定
（用户定案 2026-10-06），用户说合格才收工。
分工（用户定案）：提示词与评审文字只给 agent 看，不呈给用户；
agent 按修改清单改完、重渲染重截图后，直接把 PPT 图呈给用户目视判定。
应用记录追加到评审意见.md 末尾 "## 应用记录"（哪条改了/哪条没改+一句话理由）。

用法:
  python 程序/审美评审.py --项目 示例-化学/原电池·墨蓝 --主题 ink-navy [--页 P01,P04] [--后端 gemini]
  python 程序/审美评审.py --项目 <项目> --主题 <主题> --过闸 页/_评审/评审意见.md

提交路由约定（用户定案）：
  程序探测本机 127.0.0.1:9222，有 → submit_route=playwright-cdp（本机 Playwright 直连）；
  无 → submit_route=playwright-managed（托管 Playwright 会话，经 browser 任务）。
  真正发图提问由 agent 执行（浏览器工具在 agent 侧），程序只备料 + 定路由。

本程序做：
  1. 收集截图；2. 从 pages.json+主题卡自动生成项目背景，渲染最终提示词
     → 页/_评审/提示词.txt（agent 原样发送）；3. 写 manifest（含路由与背景）。
过闸做：每页 ## Pxx + "评分：x/5" 全覆盖；## 修改清单 存在；
  通过 → 打印"评审齐全，请用户判定"，agent 把意见呈给用户定夺。
  缺页/缺评分/缺清单 → FAIL 打回重出，不脑补。
"""
import argparse
import io
import json
import os
import re
import socket
import sys

WORKFLOW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_DIR = os.path.join(WORKFLOW, "库")
sys.path.insert(0, os.path.join(WORKFLOW, "程序"))
from 基座 import die  # noqa: E402

TPL_CN = {
    "cover": "封面", "cover_split": "封面", "toc": "目录", "section": "章节页",
    "bullets": "要点页", "photo_text": "图文页", "photo_props": "图文页",
    "photo_chain": "步骤页", "compare_bars": "对比页", "chart": "数据图表",
    "number_hero": "数字页", "equation_hero": "公式页", "infographic": "信息图",
    "quiz": "练习页", "summary": "总结页", "agenda": "议程页", "kpi": "指标页",
    "kpi_hero": "总结页",
}


def 提交路由():
    """探测本机 CDP 9222，决定 Playwright 提交路由。"""
    s = socket.socket()
    s.settimeout(1.5)
    try:
        s.connect(("127.0.0.1", 9222))
        s.close()
        return "playwright-cdp"
    except OSError:
        return "playwright-managed"


def 项目背景(proj, 页目录, theme):
    """从 pages.json + 主题卡自动生成背景块（不许手写，不许改写）。"""
    pages = json.load(io.open(os.path.join(页目录, "pages.json"), encoding="utf-8"))
    p01 = next((p for p in pages if p.get("id") == "P01"), pages[0] if pages else {})
    题 = p01.get("title", "").strip() or "（未知标题）"
    副 = p01.get("sub", "").strip()  # 如 "高中化学 · 必修二"
    课 = p01.get("brow", "").strip() or (副.split("·")[0].strip() if "·" in 副 else "") or "（未知课程）"
    页构成 = " / ".join(
        "%s %s" % (p.get("id"), TPL_CN.get(p.get("tpl"), p.get("tpl")))
        for p in pages)
    card_p = os.path.join(LIB_DIR, "主题", "卡片", "主题卡-%s.md" % theme)
    主题行 = theme
    if os.path.isfile(card_p):
        txt = io.open(card_p, encoding="utf-8").read()
        m = re.search(r"^- 标题:\s*(.+)$", txt, re.M)
        m2 = re.search(r"^# 角色.*$", txt, re.M)
        一句话 = ""
        m3 = re.search(r"## 一句话\n\n(.+?)\n", txt, re.S)
        if m3:
            一句话 = m3.group(1).strip()
        深浅 = re.search(r"^- 深浅:\s*(.+)$", txt, re.M)
        主题行 = "%s（%s）%s" % (
            m.group(1).strip() if m else theme,
            深浅.group(1).strip() if 深浅 else "",
            " —— " + 一句话 if 一句话 else "")
    css_p = os.path.join(LIB_DIR, "theme-%s.css" % theme)
    令牌 = ""
    if os.path.isfile(css_p):
        css = io.open(css_p, encoding="utf-8").read()
        t = dict(re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{6})", css))
        令牌 = "底 %s / 强调 %s / 语义橙 %s / 正文 %s" % (
            t.get("bg", "?"), t.get("gold", "?"), t.get("ox", "?"), t.get("ink", "?"))
    副注 = ""
    if 副:
        副注 = 副[len(课):].lstrip(" ·") if 副.startswith(课) else 副
        副注 = "（%s）" % 副注 if 副注 else ""
    return (
        "# 项目背景（程序自动生成）\n"
        "- 课件：%s《%s》%s，共 %d 页\n"
        "- 用途：课堂投影播放（第一排到最后一排都要看清）；HTML/PNG 为预览，PPTX 为最终交付\n"
        "- 受众：高中生（预习）+ 老师课堂讲解\n"
        "- 主题：%s；关键令牌：%s\n"
        "- 页面构成：%s\n"
    ) % (课, 题, 副注, len(pages), 主题行, 令牌, 页构成)


def cmd_过闸(a, 页目录):
    """v3：覆盖全页 + 每页有评分 + 有 ## 修改清单 → 请用户判定。终审权在用户。"""
    p = a.过闸
    if not os.path.isfile(p):
        die("评审意见文件不存在: %s" % p)
    txt = io.open(p, encoding="utf-8").read()
    pngs = sorted(f[:-4] for f in os.listdir(页目录) if re.fullmatch(r"P\d+\.png", f))
    缺 = []
    for pg in pngs:
        sec = txt.split("## " + pg, 1)
        if len(sec) < 2 or "评分" not in sec[1].split("## ", 1)[0]:
            缺.append(pg)
    if 缺:
        die("评审意见缺页/缺评分（打回重出，不脑补）: %s" % "、".join(缺))
    m = re.search(r"## 修改清单\s*\n(.*)", txt, re.S)
    if not m or not m.group(1).strip():
        die("评审意见缺 ## 修改清单（打回重出）")
    n = 0
    for line in m.group(1).splitlines():
        core = re.sub(r"^[-*·\d.、\s]+", "", line.strip())
        if core.startswith("【P") or core == "无":
            n += 1
    print("审美评审过闸：%d 页全覆盖，修改清单 %d 条 ✓" % (len(pngs), n))
    print("终审权在用户：请把评审意见呈给用户，由用户判定合格/打回。")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--项目", required=True, help="相对 工作流/ 的项目目录")
    ap.add_argument("--主题", default=None, help="主题 slug（默认从 manifest 或猜）")
    ap.add_argument("--页", default=None, help="逗号分隔的页 id，默认全部")
    ap.add_argument("--后端", default="gemini", choices=["gemini", "chatgpt"])
    ap.add_argument("--提示词", default=None, help="默认 规约/审美评审提示词.md")
    ap.add_argument("--过闸", default=None, help="校验 页/_评审/评审意见.md")
    a = ap.parse_args()

    proj = os.path.normpath(os.path.join(WORKFLOW, a.项目))
    页目录 = os.path.join(proj, "页")
    if not os.path.isdir(页目录):
        die("项目页目录不存在: %s" % 页目录)

    if a.过闸:
        return cmd_过闸(a, 页目录)

    prompt = a.提示词 or os.path.join(WORKFLOW, "规约", "审美评审提示词.md")
    if not os.path.isfile(prompt):
        die("提示词文件不存在: %s" % prompt)

    pngs = sorted(f for f in os.listdir(页目录) if re.fullmatch(r"P\d+\.png", f))
    if a.页:
        want = [p.strip() for p in a.页.split(",") if p.strip()]
        missing = [p for p in want if p + ".png" not in pngs]
        if missing:
            die("缺少截图: %s（先跑 截图.py）" % "、".join(missing))
        pngs = [f for f in pngs if f[:-4] in want]
    if not pngs:
        die("没有可评审的截图（先跑 截图.py）")

    theme = a.主题
    if not theme:
        mp0 = os.path.join(页目录, "_评审", "manifest.json")
        if os.path.isfile(mp0):
            theme = json.load(open(mp0, encoding="utf-8")).get("theme", "unknown")
        else:
            theme = "unknown"

    背景 = 项目背景(proj, 页目录, theme)
    tpl = io.open(prompt, encoding="utf-8").read()
    # 只发送 ## 正文 之后的内容（去掉文件头的版本说明与 wrapper 行）
    if "## 正文" in tpl:
        body = tpl.split("## 正文", 1)[1].splitlines()
        body = "\n".join(body[1:]).lstrip("\n")  # 去掉 wrapper 行
    else:
        body = tpl
    最终 = body.replace("{{项目背景}}", 背景).replace("N 张", "%d 张" % len(pngs))
    最终 = re.sub(r"P01–P0N", "P01–P%02d" % len(pngs), 最终)
    最终 = re.sub(r"P02–P0N", "P02–P%02d" % len(pngs), 最终)

    outdir = os.path.join(页目录, "_评审")
    os.makedirs(outdir, exist_ok=True)
    pp = os.path.join(outdir, "提示词.txt")
    io.open(pp, "w", encoding="utf-8").write(最终)

    route = 提交路由()
    manifest = {
        "version": 3,
        "backend": a.后端,
        "target": ("https://gemini.google.com/app" if a.后端 == "gemini"
                   else "https://chatgpt.com/"),
        "submit_route": route,
        "submit_contract": ("本机 Playwright 直连 CDP 127.0.0.1:9222（登录态复用）"
                            if route == "playwright-cdp"
                            else "托管 Playwright 会话（经 agent browser 任务，保持登录态）"),
        "theme": theme,
        "prompt_template": prompt,
        "prompt_final": pp,
        "background": 背景,
        "images": [{"page": f[:-4], "path": os.path.join(页目录, f)} for f in pngs],
        "opinion_file": os.path.join(outdir, "评审意见.md"),
        "pages": [f[:-4] for f in pngs],
    }
    mp = os.path.join(outdir, "manifest.json")
    io.open(mp, "w", encoding="utf-8").write(
        json.dumps(manifest, ensure_ascii=False, indent=2))
    print("manifest v3 → %s" % mp)
    print("提交路由：%s" % manifest["submit_contract"])
    print("图片 %d 张：%s" % (len(manifest["images"]), "、".join(manifest["pages"])))
    print("最终提示词 → %s（agent 原样发送，不许改写）" % pp)
    if a.后端 == "chatgpt":
        print("注意：chatgpt 后端需浏览器已登录 ChatGPT，否则改用 --后端 gemini")
    print("AGENT步骤: 按 submit_route 经 Playwright 发图+提示词全文，收回存 opinion_file，"
          "再跑 --过闸；通过后把评审意见呈给用户，由用户判定合格（收工）或打回改版。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
