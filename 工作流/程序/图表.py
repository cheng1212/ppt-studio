#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图表工厂 —— matplotlib 图表生成，专家规则焊死在代码里。

设计学派：Tufte（data-ink）/Few（颜色规则）/Knaflic（declutter）。
焊死的规则：
  - 无3D/无阴影/无背景渐变/无边框（Few规则#1：背景一致）
  - 网格线默认关；坐标轴只留左/下
  - bar/column 基线必须为零（Lie Factor≈1）
  - pie ≤5片（超了直接FAIL，让调用方分组为Other）
  - 排序：bar按值降序（时间/序数除外）
  - 颜色：灰底+单强调（Knaflic）；分类色用Okabe-Ito（色盲安全）
  - 数字：tabular lining；单位进标题不逐值重复
  - 中文：Noto Sans CJK SC；主题感知（读主题CSS取色）

用法：
    from 图表 import bar, line, pie
    bar(主题='dianshang', 数据={'华东':120,'华南':95}, 标题='GMV by region (¥M)',
        强调='华东', 输出='chart.png')
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, USAGE, LIB_DIR, die
from 配色 import OKABE_ITO as _OI  # 色盲安全分类调色板，单一来源（无#前缀）
OKABE_ITO = ["#" + c for c in _OI]

# 上下文灰（Knaflic：gray the context）
CONTEXT_GRAY = "#9AA3B2"


def 主题色(主题):
    """读主题CSS，返回图表用色 dict。"""
    css = io.open(os.path.join(LIB_DIR, "theme-%s.css" % 主题), encoding="utf-8").read()
    t = dict(re.findall(r"--([\w-]+)\s*:\s*#([0-9a-fA-F]{6})", css))
    dark = t.get("bg", "FFFFFF").lower() < "888888"  # 简单深浅判
    # 用亮度判
    bg = t.get("bg", "FFFFFF")
    lum = sum(int(bg[i:i+2], 16) for i in (0, 2, 4)) / 3
    dark = lum < 128
    return {
        "bg": "#" + t.get("bg", "FFFFFF"),
        "ink": "#" + t.get("ink", "000000"),
        "muted": "#" + t.get("muted", t.get("silver", "888888")),
        "accent": "#" + t.get("gold", "E69F00"),
        "accent2": "#" + t.get("green", "56B4E9"),
        "line": "#" + t.get("line", "DDDDDD"),
        "dark": dark,
    }


def _mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Source Han Sans SC",
                                      "Microsoft YaHei", "PingFang SC", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    return plt


def _declutter(ax, C):
    """Few/Knaflic declutter：去边框/网格/刻度装饰，只留左下轴。"""
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(C["line"])
    ax.spines["bottom"].set_color(C["line"])
    ax.tick_params(colors=C["muted"], length=0)
    ax.set_axisbelow(True)
    ax.grid(False)


def bar(主题, 数据, 标题="", 输出="chart-bar.png", 强调=None, 单位="",
        横向=True, 排序=True, 宽=12, 高=6.75):
    """横向bar（分类对比）。数据：dict{类别:值}。强调：要突出的类别名（单强调色，其余灰）。"""
    if not 数据:
        die("bar：数据为空", code=USAGE)
    C = 主题色(主题)
    items = list(数据.items())
    if 排序:
        items.sort(key=lambda kv: kv[1], reverse=True)
    labels = [k for k, _ in items]
    vals = [v for _, v in items]
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(宽, 高), dpi=150)
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    colors = [C["accent"] if (强调 and lb == 强调) else CONTEXT_GRAY for lb in labels]
    if 横向:
        bars = ax.barh(labels, vals, color=colors, height=0.55, edgecolor="none")
        ax.set_xlim(0, max(vals) * 1.15)  # 基线为零（Lie Factor）
        ax.invert_yaxis()
        # 直接标值（右端），不用图例
        for b, v in zip(bars, vals):
            ax.text(b.get_width() * 1.01, b.get_y() + b.get_height() / 2,
                    _fmt(v), va="center", ha="left", fontsize=13, color=C["ink"])
        ax.set_xlabel("")
    else:
        bars = ax.bar(labels, vals, color=colors, width=0.55, edgecolor="none")
        ax.set_ylim(0, max(vals) * 1.15)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() * 1.01,
                    _fmt(v), va="bottom", ha="center", fontsize=13, color=C["ink"])
    _declutter(ax, C)
    if 标题:
        t = 标题 + ("（%s）" % 单位 if 单位 else "")
        ax.set_title(t, loc="left", fontsize=17, fontweight="bold",
                     color=C["ink"], pad=14)
    for lbl in ax.get_yticklabels() + ax.get_xticklabels():
        lbl.set_fontsize(12)
    fig.tight_layout()
    fig.savefig(输出, facecolor=C["bg"], bbox_inches="tight")
    plt.close(fig)
    print("OK bar → %s（%d类%s）" % (输出, len(labels), "，强调「%s」" % 强调 if 强调 else ""))
    return 输出


def line(主题, x, 系列, 标题="", 输出="chart-line.png", 单位="", 宽=12, 高=6.75):
    """折线（仅时间序列）。系列：dict{名:[值]}，≤4系列直接标注。"""
    if len(系列) > 4:
        die("line：系列%d>4，拆小multiples或只留关键线（灰掉其余）" % len(系列), code=FAIL)
    C = 主题色(主题)
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(宽, 高), dpi=150)
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    palette = [C["accent"], C["accent2"]] + OKABE_ITO[1:3]
    for i, (name, vals) in enumerate(系列.items()):
        col = palette[0] if i == 0 else CONTEXT_GRAY if len(系列) > 2 else palette[i % len(palette)]
        ax.plot(x, vals, color=col, linewidth=2.6 if i == 0 else 1.8)
        # 直接标注系列名在线尾（Knaflic：direct labels > legends）
        ax.text(len(x) - 1, vals[-1], " " + name, va="center", ha="left",
                fontsize=12, color=col, fontweight="bold" if i == 0 else "normal")
    _declutter(ax, C)
    if 标题:
        t = 标题 + ("（%s）" % 单位 if 单位 else "")
        ax.set_title(t, loc="left", fontsize=17, fontweight="bold", color=C["ink"], pad=14)
    for lbl in ax.get_yticklabels() + ax.get_xticklabels():
        lbl.set_fontsize(12)
    fig.tight_layout()
    fig.savefig(输出, facecolor=C["bg"], bbox_inches="tight")
    plt.close(fig)
    print("OK line → %s（%d系列）" % (输出, len(系列)))
    return 输出


def pie(主题, 数据, 标题="", 输出="chart-pie.png", 单位="", 宽=8, 高=6):
    """饼图：≤5片硬限制（超了FAIL，调用方先分组为Other）。按降序，无3D。"""
    if len(数据) > 5:
        die("pie：%d片>5，先分组为Other或改用bar（专家硬限制）" % len(数据), code=FAIL)
    if any(v < 0 for v in 数据.values()):
        die("pie：含负值，饼图要求全正数", code=FAIL)
    C = 主题色(主题)
    items = sorted(数据.items(), key=lambda kv: kv[1], reverse=True)
    labels = [k for k, _ in items]
    vals = [v for _, v in items]
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(宽, 高), dpi=150)
    fig.patch.set_facecolor(C["bg"])
    # 第一片用强调色，其余Okabe-Ito（色盲安全）
    colors = [C["accent"]] + OKABE_ITO[1:len(vals)]
    wedges, _, autotexts = ax.pie(vals, colors=colors, startangle=90,
                                  autopct=lambda p: _fmt_pct(p),
                                  pctdistance=0.78, wedgeprops={"edgecolor": C["bg"], "linewidth": 3})
    # 标签放外部引线（不用图例）
    ax.legend(wedges, ["%s %s" % (lb, _fmt(v)) for lb, v in items],
              loc="center left", bbox_to_anchor=(1, 0.5), frameon=False,
              labelcolor=C["ink"], fontsize=12)
    for t in autotexts:
        t.set_color(C["bg"] if C["dark"] else "white")
        t.set_fontsize(11)
        t.set_fontweight("bold")
    if 标题:
        t = 标题 + ("（%s）" % 单位 if 单位 else "")
        ax.set_title(t, loc="left", fontsize=17, fontweight="bold", color=C["ink"], pad=14)
    fig.tight_layout()
    fig.savefig(输出, facecolor=C["bg"], bbox_inches="tight")
    plt.close(fig)
    print("OK pie → %s（%d片）" % (输出, len(labels)))
    return 输出



def funnel(主题, 数据, 标题="", 输出="chart-funnel.png", 单位="", 宽=10, 高=7):
    """漏斗图（转化流程）。数据：dict{阶段:值}，按顺序从上到下递减。显示阶段转化率。"""
    labels = list(数据.keys())
    vals = list(数据.values())
    n = len(labels)
    if n < 2 or n > 6:
        die("funnel：阶段数%d，须 2–6（太多拆页）" % n, code=FAIL)
    if any(v < 0 for v in vals):
        die("funnel：含负值", code=FAIL)
    C = 主题色(主题)
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(宽, 高), dpi=150)
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    vmax = max(vals)
    ys = list(range(n - 1, -1, -1))
    # 梯度色：越靠上越强调（accent），向下渐变为 accent2/灰
    for i, (lb, v) in enumerate(zip(labels, vals)):
        w = v / vmax
        col = C["accent"] if i == 0 else (C["accent2"] if i == n - 1 else CONTEXT_GRAY)
        left = (1 - w) / 2
        ax.barh(ys[i], w, left=left, height=0.62, color=col, edgecolor=C["bg"], linewidth=2)
        ax.text(0.5, ys[i], "%s  %s" % (lb, _fmt(v)), ha="center", va="center",
                fontsize=13, fontweight="bold", color="#FFFFFF" if i == 0 else C["ink"])
        if i > 0 and vals[i - 1]:
            conv = vals[i] / vals[i - 1] * 100
            ax.text(1.02, ys[i] + 0.5, "↓ %.0f%%" % conv, ha="left", va="center",
                    fontsize=11, color=C["muted"])
    ax.set_xlim(0, 1.18)
    ax.set_ylim(-0.8, n - 0.2)
    ax.axis("off")
    if 标题:
        t = 标题 + ("（%s）" % 单位 if 单位 else "")
        ax.set_title(t, loc="left", fontsize=17, fontweight="bold", color=C["ink"], pad=14)
    fig.tight_layout()
    fig.savefig(输出, facecolor=C["bg"], bbox_inches="tight")
    plt.close(fig)
    print("OK funnel → %s（%d阶段）" % (输出, n))
    return 输出


def waterfall(主题, 数据, 标题="", 输出="chart-waterfall.png", 单位="", 宽=12, 高=6.75):
    """瀑布图（增减构成→总计）。数据：dict{标签:增减值} 或 list[(标签,增减值)]，最后一项为总计（自动算）。"""
    if isinstance(数据, dict):
        数据 = list(数据.items())
    if len(数据) < 2:
        die("waterfall：至少 2 项", code=FAIL)
    C = 主题色(主题)
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(宽, 高), dpi=150)
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    labels = [k for k, _ in 数据]
    deltas = [v for _, v in 数据]
    # 累积画
    cum = 0
    xs = list(range(len(deltas)))
    for i, (lb, d) in enumerate(zip(labels, deltas)):
        if i == len(deltas) - 1:
            # 总计柱：从 0 画到总和
            total = sum(deltas[:-1])
            ax.bar(i, total, color=C["accent"], edgecolor=C["bg"], linewidth=1)
            ax.text(i, total, _fmt(total), ha="center", va="bottom",
                    fontsize=12, fontweight="bold", color=C["ink"])
        else:
            bottom = cum
            col = C["accent2"] if d >= 0 else "#D55E00"
            ax.bar(i, d, bottom=bottom, color=col, edgecolor=C["bg"], linewidth=1)
            y = bottom + d
            ax.text(i, y + (max(deltas) * 0.02 if d >= 0 else -max(deltas) * 0.02),
                    "%+s" % _fmt(d), ha="center",
                    va="bottom" if d >= 0 else "top",
                    fontsize=11, color=C["ink"])
            # 连接线
            if i < len(deltas) - 2:
                ax.plot([i - 0.4, i + 0.4], [y, y], color=C["muted"],
                        linewidth=1, linestyle=(0, (3, 3)))
            cum += d
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=12, color=C["muted"])
    _declutter(ax, C)
    if 标题:
        t = 标题 + ("（%s）" % 单位 if 单位 else "")
        ax.set_title(t, loc="left", fontsize=17, fontweight="bold", color=C["ink"], pad=14)
    fig.tight_layout()
    fig.savefig(输出, facecolor=C["bg"], bbox_inches="tight")
    plt.close(fig)
    print("OK waterfall → %s（%d项）" % (输出, len(deltas)))
    return 输出


def scatter(主题, x, y, 标题="", 输出="chart-scatter.png", 单位="",
            x名="", y名="", 趋势线=True, 宽=10, 高=7):
    """散点图（相关性）。x/y：等长数组，≥5 点。"""
    if len(x) != len(y):
        die("scatter：x/y 长度不一致", code=FAIL)
    if len(x) < 5:
        die("scatter：%d点<5，点太少看不出相关性" % len(x), code=FAIL)
    C = 主题色(主题)
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(宽, 高), dpi=150)
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    ax.scatter(x, y, s=90, color=C["accent"], alpha=0.75,
               edgecolors=C["bg"], linewidth=1.2, zorder=3)
    if 趋势线 and len(x) >= 3:
        import numpy as np
        try:
            k, b = np.polyfit(x, y, 1)
            xs = [min(x), max(x)]
            ax.plot(xs, [k * v + b for v in xs], color=C["muted"],
                    linewidth=1.5, linestyle="--", zorder=2)
        except Exception:
            pass
    if x名:
        ax.set_xlabel(x名, fontsize=12, color=C["muted"])
    if y名:
        ax.set_ylabel(y名, fontsize=12, color=C["muted"])
    _declutter(ax, C)
    if 标题:
        t = 标题 + ("（%s）" % 单位 if 单位 else "")
        ax.set_title(t, loc="left", fontsize=17, fontweight="bold", color=C["ink"], pad=14)
    for lbl in ax.get_yticklabels() + ax.get_xticklabels():
        lbl.set_fontsize(11)
    fig.tight_layout()
    fig.savefig(输出, facecolor=C["bg"], bbox_inches="tight")
    plt.close(fig)
    print("OK scatter → %s（%d点）" % (输出, len(x)))
    return 输出


def bullet(主题, 实际, 目标, 区间, 标题="", 输出="chart-bullet.png", 单位="", 宽=12, 高=3.2):
    """子弹图（实际 vs 目标）。区间：list[(上限, 标签)] 如 [(60,'差'),(80,'中'),(100,'优')]。"""
    if not 区间 or 实际 < 0 or 目标 < 0:
        die("bullet：区间为空或含负值", code=FAIL)
    C = 主题色(主题)
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(宽, 高), dpi=150)
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    vmax = max(区间[-1][0], 实际, 目标) * 1.08
    # 定性区间底（灰阶三档）
    grays = [C["line"], CONTEXT_GRAY, C["muted"]]
    prev = 0
    for i, (up, _) in enumerate(区间):
        ax.barh(0, up - prev, left=prev, height=0.55,
                color=grays[min(i, 2)], alpha=0.45, edgecolor="none")
        prev = up
    # 实际值（粗黑条）
    ax.barh(0, 实际, height=0.28, color=C["ink"], edgecolor="none", zorder=3)
    # 目标线
    ax.plot([目标, 目标], [-0.45, 0.45], color=C["accent"], linewidth=4, zorder=4)
    ax.text(目标, 0.55, "目标 %s" % _fmt(目标), ha="center", va="bottom",
            fontsize=11, fontweight="bold", color=C["accent"])
    ax.text(实际 / 2 if 实际 else 0.5, 0, "实际 %s" % _fmt(实际),
            ha="center", va="center", fontsize=11, fontweight="bold", color=C["bg"])
    ax.set_xlim(0, vmax)
    ax.set_ylim(-0.8, 0.8)
    ax.axis("off")
    if 标题:
        t = 标题 + ("（%s）" % 单位 if 单位 else "")
        ax.set_title(t, loc="left", fontsize=17, fontweight="bold", color=C["ink"], pad=14)
    fig.tight_layout()
    fig.savefig(输出, facecolor=C["bg"], bbox_inches="tight")
    plt.close(fig)
    print("OK bullet → %s" % 输出)
    return 输出


def radar(主题, 数据, 标题="", 输出="chart-radar.png", 单位="", 宽=8, 高=8):
    """雷达图（多维对比）。数据：dict{系列名: dict{维度:值}} 或 dict{维度:值}（单系列）。
    维度 3-8 个，值归一化到 0-100。"""
    import math
    if not 数据:
        die("radar：数据为空", code=FAIL)
    vals = list(数据.values())
    if isinstance(vals[0], dict):
        系列 = 数据
        维度s = list(vals[0].keys())
    else:
        系列 = {"": 数据}
        维度s = list(数据.keys())
    n = len(维度s)
    if n < 3 or n > 8:
        die("radar：维度%d，须 3-8" % n, code=FAIL)
    # 归一化
    vmax = max(max(s.values()) for s in 系列.values()) or 1
    C = 主题色(主题)
    plt = _mpl()
    fig, ax = plt.subplots(figsize=(宽, 高), dpi=150, subplot_kw={"polar": True})
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    angles = [i / n * 2 * math.pi for i in range(n)] + [0]
    色s = [C["accent"], C["accent2"], "#D55E00", "#CC79A7"]
    for si, (名, s) in enumerate(系列.items()):
        vs = [s[d] / vmax * 100 for d in 维度s] + [s[维度s[0]] / vmax * 100]
        col = 色s[si % len(色s)]
        ax.plot(angles, vs, color=col, linewidth=2.5)
        ax.fill(angles, vs, color=col, alpha=0.18)
        if 名:
            ax.text(angles[-2], vs[-2] + 6, 名, color=col, fontsize=12,
                    fontweight="bold", ha="center")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(维度s, fontsize=12, color=C["muted"])
    ax.set_ylim(0, 110)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels([], fontsize=1)
    ax.grid(color=C["line"], linewidth=0.8, alpha=0.7)
    ax.spines["polar"].set_color(C["line"])
    if 标题:
        t = 标题 + ("（%s）" % 单位 if 单位 else "")
        ax.set_title(t, loc="left", fontsize=17, fontweight="bold", color=C["ink"], pad=20)
    fig.tight_layout()
    fig.savefig(输出, facecolor=C["bg"], bbox_inches="tight")
    plt.close(fig)
    print("OK radar → %s（%d维×%d系列）" % (输出, n, len(系列)))
    return 输出

def _fmt(v):
    if isinstance(v, float) and not v.is_integer():
        return "%.1f" % v
    return "%d" % v if isinstance(v, float) else str(v)


def _fmt_pct(p):
    return "%.0f%%" % p if p >= 5 else ""


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(prog="图表.py")
    ap.add_argument("--demo", action="store_true", help="跑三张demo图")
    ap.add_argument("--主题", default="dianshang")
    a = ap.parse_args()
    if a.demo:
        bar(主题=a.主题, 数据={"华东": 128, "华南": 96, "华北": 84, "西南": 62},
            标题="GMV by region", 单位="¥M", 强调="华东", 输出="/tmp/demo-bar.png")
        line(主题=a.主题, x=["10/20", "10/25", "10/31", "11/05", "11/11"],
             系列={"2026": [12, 18, 31, 55, 128], "2025": [10, 15, 26, 44, 102]},
             标题="GMV trend", 单位="¥M", 输出="/tmp/demo-line.png")
        pie(主题=a.主题, 数据={"服饰": 42, "美妆": 28, "3C": 18, "食品": 12},
            标题="Category mix", 输出="/tmp/demo-pie.png")
        funnel(主题=a.主题, 数据={"曝光": 1000, "点击": 320, "加购": 128, "下单": 64, "支付": 52},
               标题="Conversion funnel", 单位="万人", 输出="/tmp/demo-funnel.png")
        waterfall(主题=a.主题, 数据={"期初": 100, "新增": 45, "流失": -20, "复购": 30, "期末": 0},
                  标题="GMV bridge", 单位="¥M", 输出="/tmp/demo-waterfall.png")
        scatter(主题=a.主题, x=[10, 20, 30, 40, 50, 60, 70, 80],
                y=[12, 25, 28, 45, 52, 61, 68, 82],
                标题="Ad spend vs GMV", x名="投放(万)", y名="GMV(万)",
                输出="/tmp/demo-scatter.png")
        bullet(主题=a.主题, 实际=82, 目标=100, 区间=[(60, "差"), (80, "中"), (100, "优")],
               标题="Q4 目标达成", 输出="/tmp/demo-bullet.png")
        print("demo done")
