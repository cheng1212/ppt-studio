# -*- coding: utf-8 -*-
"""svg.py — 主题感知的 SVG 图元工具库（流程图技能的固定执行层）。

定位：把"画图"从各页型模板的手写 SVG 字符串里抽出来，固定成可复用的
函数。数据进、SVG 字符串出；颜色全部走主题 CSS 变量。注意：var() 必须
写在 style 属性里（presentation attribute 不支持 CSS 变量），本库统一用
style 写法，换主题不碰本程序（定案 D1）。

图元：
  fork()  — 分支分叉线（flow_branch 用）
  cycle() — 环形节点 + 带标签箭头（flow_cycle 用）

用法：
  from svg import fork, cycle
  svg_str = fork([550, 1130])                      # 各分支中心 x 坐标
  svg_str = cycle(["Na", "Na2O"], [{"from": "Na", "to": "Na2O", "label": "O2"}])
"""
import html as _html
import math

import svgwrite


def _esc(s):
    """与 页面生成.py esc() 同语义的行内转义（SVG 文本节点用）。"""
    return _html.escape(str(s), quote=False)


def _arrow_marker(dwg, mid, color, ref=7):
    """箭头 marker，颜色走 style（var() 在 presentation attribute 里无效）。"""
    m = dwg.marker(id=mid, markerWidth=10, markerHeight=10,
                   refX=ref, refY=3, orient="auto")
    p = dwg.path(d=f"M0,0 L{ref},3 L0,6 Z")
    p.update({"style": f"fill:{color}"})
    m.add(p)
    dwg.defs.add(m)
    return f"url(#{mid})"


def fork(centers, width=1680, height=66, y_split=30,
         color="var(--gold)", stroke_width=4):
    """分叉线：顶部中心垂线 → 横线 → 每个分支中心的垂线箭头。

    centers: 各分支卡片中心 x 坐标（从左到右）。
    起点中心固定为 width/2（与模板 .root 居中对齐）。
    """
    dwg = svgwrite.Drawing(size=(width, height))
    dwg.update({"style": "display:block"})
    x0 = width / 2
    url = _arrow_marker(dwg, "fork-ah", color, ref=6)
    for d in (f"M{x0:.0f},0 V{y_split}",
              f"M{centers[0]:.0f},{y_split} H{centers[-1]:.0f}"):
        p = dwg.path(d=d, fill="none")
        p.update({"style": f"stroke:{color};stroke-width:{stroke_width}"})
        dwg.add(p)
    for cx in centers:
        p = dwg.path(d=f"M{cx:.0f},{y_split} V{height - 8}", fill="none",
                     marker_end=url)
        p.update({"style": f"stroke:{color};stroke-width:{stroke_width}"})
        dwg.add(p)
    return dwg.tostring()


def cycle(nodes, edges, width=1680, height=600, center=(840, 290),
          rx=430, ry=190, node_r=86,
          line_color="var(--green)", node_fill="var(--card)",
          node_text="var(--green)", label_color="var(--muted)",
          halo="var(--bg)",
          font="'思源黑体','Noto Sans CJK SC','Source Han Sans SC','Microsoft YaHei','PingFang SC',sans-serif"):
    """环形关系图：nodes 按顺时针从顶部开始环形排布，edges 为带标签箭头。

    nodes: 节点名数组（3–6 项）。
    edges: [{from, to, label}]，from/to 必须命中 nodes。
    箭头为二次贝塞尔曲线（向外 bow），标签位于弧线中点外侧，带光晕描边。
    """
    n = len(nodes)
    cx, cy = center
    dwg = svgwrite.Drawing(size=(width, height))
    dwg.update({"style": "display:block;overflow:visible"})
    url = _arrow_marker(dwg, "cycle-ah", line_color)
    pos = {}
    for i, name in enumerate(nodes):
        th = math.radians(-90 + i * 360 / n)
        pos[name] = (cx + rx * math.cos(th), cy + ry * math.sin(th))

    for e in edges:
        ax, ay = pos[e["from"]]
        bx, by = pos[e["to"]]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        sx, sy = ax + ux * (node_r + 6), ay + uy * (node_r + 6)
        ex, ey = bx - ux * (node_r + 6), by - uy * (node_r + 6)
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        ox, oy = mx - cx, my - cy
        ol = math.hypot(ox, oy) or 1
        k = 52
        qx, qy = mx + ox / ol * k, my + oy / ol * k
        p = dwg.path(
            d=f"M{sx:.0f},{sy:.0f} Q{qx:.0f},{qy:.0f} {ex:.0f},{ey:.0f}",
            fill="none", marker_end=url)
        p.update({"style": f"stroke:{line_color};stroke-width:4"})
        dwg.add(p)
        lx = 0.25 * sx + 0.5 * qx + 0.25 * ex + ox / ol * 30
        ly = 0.25 * sy + 0.5 * qy + 0.25 * ey + oy / ol * 30
        t = dwg.text(_esc(e["label"]), insert=(round(lx), round(ly)),
                     text_anchor="middle", dominant_baseline="central",
                     font_size=22, font_family=font)  # cap档
        t.update({"style": f"fill:{label_color};paint-order:stroke;"
                           f"stroke:{halo};stroke-width:7px"})
        dwg.add(t)

    for name, (x, y) in pos.items():
        c = dwg.circle(center=(round(x), round(y)), r=node_r)
        c.update({"style": f"fill:{node_fill};stroke:{line_color};"
                           f"stroke-width:4"})
        dwg.add(c)
        t = dwg.text(_esc(name), insert=(round(x), round(y)),
                     text_anchor="middle", dominant_baseline="central",
                     font_size=34, font_weight=800, font_family=font)  # body档
        t.update({"style": f"fill:{node_text}"})
        dwg.add(t)
    return dwg.tostring()


def timeline_axis(cxs, y, x0, x1, ups, line="var(--line)", dot="var(--gold)",
                  dot_ring="var(--bg)"):
    """横向时间轴：直线 + 节点圆点 + 上下短桩线。

    cxs: 节点 x 坐标数组；y: 轴线 y；x0/x1: 轴线起止；
    ups: 与 cxs 等长的 bool 数组，True=桩线朝上。
    颜色走主题 CSS 变量（写 style 属性）。
    """
    dwg = svgwrite.Drawing(size=("100%", "100%"))
    ln = dwg.line(start=(x0, y), end=(x1, y))
    ln.update({"style": f"stroke:{line};stroke-width:3"})
    dwg.add(ln)
    for cx, up in zip(cxs, ups):
        y2 = y - 46 if up else y + 46
        stub = dwg.line(start=(cx, y), end=(cx, y2))
        stub.update({"style": f"stroke:{line};stroke-width:3"})
        dwg.add(stub)
        c = dwg.circle(center=(cx, y), r=13)
        c.update({"style": f"fill:{dot};stroke:{dot_ring};stroke-width:5"})
        dwg.add(c)
    return dwg.tostring()
