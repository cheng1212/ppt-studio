#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v4-edu 最终验收：CSS↔卡色值一致、蓝系差异化、文件计数。"""
import io, json, os, re, colorsys

WF = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(WF, "库")

def lum(h):
    h = h.lstrip('#'); r, g, b = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b)

def cr(a, b):
    x, y = sorted([lum(a), lum(b)])
    return (y+0.05)/(x+0.05)

def hue(h):
    h = h.lstrip('#'); r, g, b = [int(h[i:i+2], 16)/255 for i in (0, 2, 4)]
    return colorsys.rgb_to_hsv(r, g, b)[0]

# 1. 文件计数
css = [f for f in os.listdir(LIB) if re.match(r"theme-(yuwen|math|english|physics|chemistry|biology|history|geography|politics|music|art|pe|it)-(xx|zx|dx)\.css", f)]
cards = [f for f in os.listdir(os.path.join(LIB, "主题", "卡片")) if re.match(r"主题卡-(yuwen|math|english|physics|chemistry|biology|history|geography|politics|music|art|pe|it)\.md", f)]
print("CSS: %d/39, 卡: %d/13" % (len(css), len(cards)))

# 2. 卡配色表 vs CSS :root 一致（zx 基准）
def css_tokens(path):
    txt = io.open(path, encoding="utf-8").read()
    m = re.search(r":root\s*\{(.*?)\}", txt, re.S)
    return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)))

def card_table(path):
    txt = io.open(path, encoding="utf-8").read()
    rows = re.findall(r"\|\s*(--[\w-]+)\s*\|\s*(#[0-9A-Fa-f]{6})\s*\|", txt)
    return dict((k, v.upper()) for k, v in rows)

mismatch = []
for slug in ["yuwen","math","english","physics","chemistry","biology","history","geography","politics","music","art","pe","it"]:
    ct = css_tokens(os.path.join(LIB, "theme-%s-zx.css" % slug))
    kt = card_table(os.path.join(LIB, "主题", "卡片", "主题卡-%s.md" % slug))
    for tok in ["--bg","--bg-dark","--gold","--gold-soft","--ink","--green","--silver","--muted","--line","--line-dark","--card","--ox","--ink-dark"]:
        cv = ct.get(tok, "").strip().upper()
        kv = kt.get(tok, "")
        if cv != kv:
            mismatch.append((slug, tok, cv, kv))
print("色值一致性: %s" % ("169/169 全对" if not mismatch else "MISMATCH %s" % mismatch[:5]))

# 3. 每文件对比度闸
bad = []
for f in css:
    t = css_tokens(os.path.join(LIB, f))
    bg = t["--bg"].strip()
    for name, fg, bgc, need in [("ink/bg", t["--ink"], bg, 7.0), ("gold/bg", t["--gold"], bg, 3.0),
                                ("muted/bg", t["--muted"], bg, 4.5),
                                ("ink-dark/bg-dark", t["--ink-dark"], t["--bg-dark"], 4.5)]:
        r = cr(fg.strip(), bgc.strip())
        if r < need:
            bad.append((f, name, round(r, 2)))
print("对比度闸: %s" % ("39 文件全过" if not bad else "FAIL %s" % bad[:5]))

# 4. 蓝系 6 学科 gold 色相分散（防一锅蓝）
blues = {}
for slug in ["math","english","physics","history","geography","it"]:
    t = css_tokens(os.path.join(LIB, "theme-%s-zx.css" % slug))
    blues[slug] = (t["--gold"].strip(), hue(t["--gold"].strip()))
print("蓝系 gold:", " ".join("%s=%s" % kv for kv in blues.items()))
hs = sorted(v[1] for v in blues.values())
gaps = [round((hs[i+1]-hs[i])*360, 1) for i in range(len(hs)-1)]
print("色相间隔(度):", gaps)
