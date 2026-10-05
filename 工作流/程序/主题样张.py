#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主题样张 —— 把主题穿到所有结构件上，渲染浅/深/封面三张样张给用户拍板（T4）。

只摆主题 CSS 自己的组件（页眉/标题/徽章/结论条/编号圆/发丝线/图注/
深色反转/章节 ghost），不管页面模板；封面样张复用 t_cover 真实模板，
罩子按主题 --bg 深浅自适应（2026-10-05 复盘补：封面定调页必须进主题拍板）。

用法:
  python 主题样张.py --主题 sodium
产物:
  库/主题/_样张/theme-sodium-浅.html / -浅.png
  库/主题/_样张/theme-sodium-深.html / -深.png
  库/主题/_样张/theme-sodium-封面.html / -封面.png
"""
import argparse
import io
import os
import subprocess
import sys
from urllib.parse import quote as _urlquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, USAGE, die, LIB_DIR

HERE = os.path.dirname(os.path.abspath(__file__))

SAMPLE_CSS = """
.sheet{position:absolute;left:120px;top:300px;width:1680px}
.row{margin:26px 0;display:flex;gap:28px;align-items:center}
.lbl{font-size:20px;color:var(--muted);letter-spacing:.2em;width:220px;flex:none}
.dark .lbl{color:var(--silver)}
.box{background:var(--card);border:1px solid var(--line);padding:26px 30px;
     font-size:22px;color:var(--ink);line-height:1.8}
.dark .box{background:#2E3533;border-color:#3A423F;color:var(--bg)}
"""

LIGHT_BODY = """
<div class="brow">THEME SAMPLE</div><div class="pageno">样张</div>
<div class="head"><div class="kick">SAMPLE</div>
<h1>主题样张，<span class="q">只看样式不管内容</span></h1></div>
<div class="sheet">
  <div class="row"><div class="lbl">徽章</div>
    <span class="badge ink" style="padding:12px 30px;font-size:22px">INK 徽章</span>
    <span class="badge green" style="padding:12px 30px;font-size:22px">GREEN 徽章</span>
    <span class="badge gold" style="padding:12px 30px;font-size:22px">GOLD 徽章</span></div>
  <div class="row"><div class="lbl">编号圆</div>
    <span class="numdot">1</span><span class="numdot">2</span><span class="numdot">3</span></div>
  <div class="row"><div class="lbl">结论条</div>
    <div class="concl" style="flex:1">结论条样张：<b>加粗走绿</b>，左边金边是主题强调色</div></div>
  <div class="row"><div class="lbl">卡片/发丝线</div>
    <div class="box hairline" style="flex:1">卡片底 var(--card)＋发丝线 var(--line)＋弱化字 var(--muted)</div></div>
  <div class="row"><div class="lbl">图注</div><div class="cap" style="flex:1">图注样式 var(--muted)</div></div>
</div>
<div class="foot-line"></div><div class="foot">主题样张 · 浅</div>
"""

DARK_BODY = """
<div class="brow">THEME SAMPLE</div><div class="pageno">样张</div>
<div class="ghost">01</div>
<div class="head"><div class="kick">SAMPLE</div>
<h1>深色反转样张</h1>
<div class="gold-rule" style="margin-top:26px"></div></div>
<div class="sheet">
  <div class="row"><div class="lbl">徽章（深底）</div>
    <span class="badge ink" style="padding:12px 30px;font-size:22px">INK 徽章</span>
    <span class="badge green" style="padding:12px 30px;font-size:22px">GREEN 徽章</span>
    <span class="badge gold" style="padding:12px 30px;font-size:22px">GOLD 徽章</span></div>
  <div class="row"><div class="lbl">结论条（深底）</div>
    <div class="concl" style="flex:1">深底上的结论条：<b>加粗走绿</b></div></div>
  <div class="row"><div class="lbl">发丝线（深底）</div>
    <div class="box hairline" style="flex:1">深底发丝线与辅助字</div></div>
</div>
<div class="foot-line"></div><div class="foot">主题样张 · 深</div>
"""


def build(theme_css, body, dark=False):
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<style>\n%s\n%s\n</style></head>"
            "<body%s>%s</body></html>"
            % (theme_css, SAMPLE_CSS, ' class="dark"' if dark else "", body))


# 封面样张底图：中性灰渐变内联 SVG（替身照片，只为看罩子与字色）
_COVER_BG_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='1920' height='1080'>"
    "<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='0'>"
    "<stop offset='0' stop-color='#8b95a1'/><stop offset='1' stop-color='#4c565f'/>"
    "</linearGradient></defs><rect width='1920' height='1080' fill='url(#g)'/></svg>"
)
COVER_SAMPLE = {
    "id": "样张封面", "tpl": "cover",
    "bg": "data:image/svg+xml;utf8," + _urlquote(_COVER_BG_SVG, safe=""),
    "eyebrow": "SAMPLE COVER", "title": "样张封面标题",
    "en": "SAMPLE", "sub": "副标题行 · 只看罩子与字色",
    "foot": "主题样张 · 封面", "corner": "⇌",
}


def main():
    ap = argparse.ArgumentParser(prog="主题样张.py")
    ap.add_argument("--主题", required=True, help="主题名，如 sodium")
    a = ap.parse_args()
    css_path = os.path.join(LIB_DIR, "theme-%s.css" % a.主题)
    if not os.path.isfile(css_path):
        die("找不到主题 CSS：%s" % css_path, code=USAGE)
    theme_css = io.open(css_path, encoding="utf-8").read()
    outdir = os.path.join(LIB_DIR, "主题", "_样张")
    os.makedirs(outdir, exist_ok=True)
    outs = []
    for name, body, dark in (("浅", LIGHT_BODY, False), ("深", DARK_BODY, True)):
        html = os.path.join(outdir, "theme-%s-%s.html" % (a.主题, name))
        io.open(html, "w", encoding="utf-8").write(build(theme_css, body, dark))
        outs.append(html)
        print("样张", html)
    # 封面样张：复用 t_cover 真实模板，主题从环境变量穿入
    os.environ["PPT_THEME_CSS"] = "theme-%s.css" % a.主题
    sys.path.insert(0, HERE)
    from 页面生成 import t_cover
    cover_html = os.path.join(outdir, "theme-%s-封面.html" % a.主题)
    io.open(cover_html, "w", encoding="utf-8").write(t_cover(COVER_SAMPLE))
    outs.append(cover_html)
    print("样张", cover_html)
    r = subprocess.run([sys.executable, os.path.join(HERE, "截图.py")] + outs,
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout or "")
    if r.returncode != 0:
        die("截图失败:\n%s" % (r.stderr or ""), code=FAIL)
    for h in outs:
        print("PNG", h[:-5] + ".png")
    print("\n---- T4 主题拍板：三张样张（浅/深/封面）看完没问题，主题卡可转定稿 ----")
    sys.exit(OK)


if __name__ == "__main__":
    main()
