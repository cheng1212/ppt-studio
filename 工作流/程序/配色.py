#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配色 —— 主题 T3 填令牌时的对比度助手。

输入底色 + 候选色，输出每个候选的 WCAG 对比度；未过闸的自动推荐
同色相最近过闸值（2026-10-05 审计优化：替代手算，如 chemlab 的 #F4A261→#C1804C）。

阈值读 规约/卡型规约.json·主题令牌·对比度（ink 系≥4.5，gold/ox 系≥3.0）。

用法:
  python 配色.py --bg F7F9F8 --候选 F4A261,2A9D8F --角色 gold
  python 配色.py --bg F7F9F8 --候选 263238 --角色 ink
"""
import argparse
import colorsys
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, read_json, RULES_DIR, die

阈值 = read_json(os.path.join(RULES_DIR, "卡型规约.json"))["主题令牌"]["对比度"]
角色闸 = {"ink": 阈值["ink/bg"], "green": 阈值["ink/bg"],
          "gold": 阈值["gold/bg"], "ox": 阈值["ox/bg"]}

# Okabe-Ito 色盲安全分类调色板（8色，专家报告 Topic 2.4）
# 禁止单用红绿编码；关键区分必须配非颜色线索
OKABE_ITO = ["E69F00", "56B4E9", "009E73", "F0E442",
             "0072B2", "D55E00", "CC79A7", "000000"]

# 中国语义色映射（专家报告 Topic 2.8）：红=喜庆/增长（非警示），绿=利好，蓝=最安全
# 全篇一色一义；关键区分配文字/形状，不单靠颜色
中国语义 = {"涨/好/通过": "绿或蓝", "强调/喜庆": "红", "注意": "小面积黄",
            "警示": "红+文字（中国语境红非危险，须配文字）"}


def 分类色(n, bg="FFFFFF"):
    """取 n 个色盲安全的分类色（≤7，超了先分组）。返回 hex 列表。"""
    if n > 7:
        die("分类色 n=%d>7：先分组为Other或改小multiples（专家硬限制）" % n, code=FAIL)
    return OKABE_ITO[:n]


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lum(h):
    def f(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hex_of(r, g, b):
    return "%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def full_scheme(bg):
    """由主色生成完整 12 令牌方案（T2 主题卡骨架 / T3 CSS 落盘共用）。
    60-30-10：bg=60% 主色；green=30% 副色；gold=10% 强调色。"""
    r, g, b = rgb(bg)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    dark = l < 0.5
    # 副色 30%：近邻 +40°，明度取与底对比 ~2.8（标题级可见）
    hh2, ss2 = shift_hue(h, 40), max(s, 0.35)
    副 = None
    lo, hi = (0.0, 1.0) if dark else (1.0, 0.0)
    for _ in range(24):
        m = (lo + hi) / 2
        c = hex_of(*colorsys.hls_to_rgb(hh2, m, ss2))
        cr = contrast(c, bg)
        if abs(cr - 2.8) < 0.05:
            副 = c
            break
        if dark:
            (lo, hi) = (m, hi) if cr < 2.8 else (lo, m)
        else:
            (lo, hi) = (lo, m) if cr < 2.8 else (m, hi)
    副 = 副 or hex_of(*colorsys.hls_to_rgb(hh2, 0.55 if dark else 0.35, ss2))
    # 强调色 10%：对比 180°
    hh3, ss3 = shift_hue(h, 180), max(s, 0.8)
    cand3 = hex_of(*colorsys.hls_to_rgb(hh3, 0.55, ss3))
    强调 = cand3 if contrast(cand3, bg) >= 3.0 else 最近过闸值(cand3, bg, 3.0)
    # 强调柔版：强调色提亮
    rh, rl, rs = colorsys.rgb_to_hls(*rgb(强调))
    强调柔 = hex_of(*colorsys.hls_to_rgb(rh, min(0.95, rl + 0.18), rs))
    # ox 语义色：强调色相往暖红偏 -30°（警示/热销），过 3.0 闸
    hh4 = (rh - 30 / 360.0) % 1.0
    cand4 = hex_of(*colorsys.hls_to_rgb(hh4, rl, rs))
    ox = cand4 if contrast(cand4, bg) >= 3.0 else 最近过闸值(cand4, bg, 3.0) or 强调
    # 中性
    ink_cand = "F5F7FA" if dark else "1A1A1A"
    ink = ink_cand if contrast(ink_cand, bg) >= 7.0 else 最近过闸值(ink_cand, bg, 7.0)
    mut_cand = "9AA3B2" if dark else "5A6472"
    muted = mut_cand if contrast(mut_cand, bg) >= 4.5 else 最近过闸值(mut_cand, bg, 4.5)
    silver = muted  # 深底辅助字与弱化字同源（深底主题）
    card = hex_of(*colorsys.hls_to_rgb(h, min(1, max(0, l + (0.06 if dark else -0.05))), s))
    line = hex_of(*colorsys.hls_to_rgb(h, min(1, max(0, l + (0.12 if dark else -0.10))), s))
    bg_dark = hex_of(*colorsys.hls_to_rgb(h, l * 0.35 if not dark else max(0, l - 0.06), s))
    # line-dark：深底上的发丝线（bg-dark 提亮一档）
    rh2, rl2, rs2 = colorsys.rgb_to_hls(*rgb(bg_dark))
    line_dark = hex_of(*colorsys.hls_to_rgb(rh2, min(0.95, rl2 + 0.14), rs2))
    ink_dark = "F5F7FA"
    if contrast(ink_dark, bg_dark) < 4.5:
        ink_dark = 最近过闸值(ink_dark, bg_dark, 4.5) or ink_dark
    return {"--bg": bg.upper(), "--bg-dark": bg_dark, "--gold": 强调,
            "--gold-soft": 强调柔, "--ink": ink, "--green": 副,
            "--silver": silver, "--muted": muted, "--line": line, "--line-dark": line_dark,
            "--card": card, "--ox": ox, "--ink-dark": ink_dark}


def shift_hue(h, deg):
    return (h + deg / 360.0) % 1.0


def 调色板(bg):
    """60-30-10 调色板生成（设计规约·配色）：输入 60% 主色（底色），
    输出副色（近邻 40°）/强调色（对比 180°）/中性色系，各带对比度。"""
    scheme = full_scheme(bg)
    dark = int(bg.lstrip("#")[:2], 16) / 255 < 0.5 or \
        sum(int(bg.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) / 3 < 128
    print("60-30-10 调色板（主色 #%s，%s底）：" % (bg.upper(), "深" if dark else "浅"))
    rows = [("60% 主色·底", "--bg", None), ("30% 副色·标题", "--green", "--bg"),
            ("10% 强调色", "--gold", "--bg"), ("ink 正文", "--ink", "--bg"),
            ("muted 弱化字", "--muted", "--bg"), ("card 卡底", "--card", None),
            ("line 发丝线", "--line", None)]
    for name, tok, bg_tok in rows:
        hx = scheme[tok]
        extra = "（对比度 %.2f）" % contrast(hx, scheme[bg_tok]) if bg_tok else ""
        print("  %-14s #%s%s" % (name, hx, extra))
    print("  完整 12 令牌见 full_scheme()；用法：60% 铺底 → 30% 做标题/表头 → 10% 只落关键数字/焦点（每页一个）")
    return scheme


def 最近过闸值(cand, bg, need):
    """保持色相/饱和度，二分搜明度找最近过闸值；压暗/提亮两边都试，取变化最小者。"""
    r, g, b = rgb(cand)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    best = None  # (hex, 明度)
    for extreme in (0.0, 1.0):  # 压暗到底 / 提亮到顶
        c_ext = hex_of(*colorsys.hls_to_rgb(h, extreme, s))
        if contrast(c_ext, bg) < need:
            continue  # 这一边到顶都不行
        a, z = extreme, l  # a=已知过闸端，z=原值（未过闸端），向原值逼近找边界
        for _ in range(24):
            m = (a + z) / 2
            if contrast(hex_of(*colorsys.hls_to_rgb(h, m, s)), bg) >= need:
                a = m
            else:
                z = m
        hit = (hex_of(*colorsys.hls_to_rgb(h, a, s)), a)
        if best is None or abs(hit[1] - l) < abs(best[1] - l):
            best = hit
    return best[0] if best else None


def main():
    ap = argparse.ArgumentParser(prog="配色.py")
    ap.add_argument("--bg", help="底色 hex，如 F7F9F8")
    ap.add_argument("--候选", help="候选色 hex，逗号分隔")
    ap.add_argument("--角色", choices=sorted(角色闸),
                    help="令牌角色：ink/green（闸≥%.1f）gold/ox（闸≥%.1f）"
                         % (阈值["ink/bg"], 阈值["gold/bg"]))
    ap.add_argument("--调色板", default=None, metavar="主色hex",
                    help="60-30-10 调色板生成模式：输入 60%% 主色，输出完整方案")
    a = ap.parse_args()
    if a.调色板:
        调色板(a.调色板.strip().lstrip("#"))
        sys.exit(OK)
    if not a.bg or not a.候选 or not a.角色:
        ap.error("--bg/--候选/--角色 必填（或用 --调色板 模式）")
    need = 角色闸[a.角色]
    print("底色 #%s · 角色 %s · 闸 ≥%.1f" % (a.bg.upper(), a.角色, need))
    for c in a.候选.split(","):
        c = c.strip().lstrip("#")
        r = contrast(c, a.bg)
        ok = "PASS" if r >= need else "FAIL"
        line = "  #%s 对比度 %.2f → %s" % (c.upper(), r, ok)
        if r < need:
            near = 最近过闸值(c, a.bg, need)
            line += ("；最近过闸值 #%s（对比度 %.2f）" % (near, contrast(near, a.bg))
                     if near else "；同色相内无过闸值，换色相")
        print(line)
    sys.exit(OK)


if __name__ == "__main__":
    main()
