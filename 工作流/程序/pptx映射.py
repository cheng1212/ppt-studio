#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pptx映射.py —— PPTX 导出的声明式映射框架。

问题：pptx导出.py 里每个页型都要手写一个 r_* 函数（15 个页型 = 15 份手工代码），
新页型（chart/kpi_hero/cover_split…）根本没有导出器。

解法：页面 = 组件列表（数据，不是代码）。新增页型只需写一份映射声明，
通用渲染器负责执行。HTML 模板仍是视觉源，映射里的坐标从 HTML 版式数值抄。

组件闭集：
    底色    {"组件":"底色","fill":"bg"}
    文本    {"组件":"文本","字段":"title","x":..,"y":..,"w":..,"h":..,
             "size":45,"color":"ink","bold":True,"align":"left"}
            字段值支持行内 <b>/<em>/<span class="q|ox">（复用 segs 解析）
    图片    {"组件":"图片","字段":"img","x":..,"y":..,"w":..,"h":..,"fit":"cover|contain",
             "alpha":55}  （alpha 可选：0–100 不透明度，双重曝光叠加用）
    矩形    {"组件":"矩形","x":..,"y":..,"w":..,"h":..,"fill":"card","line":None}
    线条    {"组件":"线条","x1":..,"y1":..,"x2":..,"y2":..,"color":"gold","w":2}
    徽章    {"组件":"徽章","字段":"k","x":..,"y":..,"kind":"gold"}
    页眉    {"组件":"页眉"}  （复用 page_head）
    页脚    {"组件":"页脚"}  （复用 page_foot）
    结论条  {"组件":"结论条","字段":"concl","x":..,"y":..,"w":..}
    循环    {"组件":"循环","字段":"kpis","模板":[{...}]}  （对数组字段重复渲染一组组件，
             组内可用 {i} 序号、{it.xxx} 取当前项字段）
             可选 "极值":["a","b"] → 注入 _max（全部项指定字段最大值），
             _n 恒为项数；算术表达式支持 it.数值字段/_max/_n，
             例："w":"{1240*it.a/_max}"（条形图归一化宽度）

用法（pptx导出.py）：
    from pptx映射 import 映射表, 渲染声明式
    fn = 映射表.get(p["tpl"]) or RENDER.get(p["tpl"])
"""
import copy
import os
import re

# 这些从 pptx导出 import（避免循环 import，渲染时动态传）
_exp = None


def _E():
    global _exp
    if _exp is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pptx导出", os.path.join(os.path.dirname(os.path.abspath(__file__)), "pptx导出.py"))
        _exp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_exp)
    return _exp


def _字段(ctx, key):
    """字段解析：{模板} 走 _val；裸字段名先查 p/it，查不到返回 None（不渲染），
    不再回退为字面量（旧行为会导致缺 concl 时画出 "concl" 字样）。"""
    if isinstance(key, str) and key.startswith("{"):
        return _val({"字段": key}, ctx, "字段")
    p, it = ctx.get("p", {}), ctx.get("it")
    if isinstance(it, dict) and key in it:
        return it[key]
    if key in p:
        return p[key]
    return None


def _val(组件, ctx, key, default=None):
    v = 组件.get(key, default)
    if isinstance(v, str) and v.startswith("{"):
        # {字段} / {it.xxx} / {a.b.c} / {i} / {x+592*i} 模板变量
        m = re.fullmatch(r"\{([^}]+)\}", v)
        if m:
            expr = m.group(1)
            if re.fullmatch(r"[\w.]+", expr):
                # 纯字段路径；{it} 即当前项本身
                if expr == "it":
                    return ctx.get("it", default)
                cur = ctx.get("it", {}) if expr.startswith("it.") else ctx.get("p", {})
                if expr.startswith("it."):
                    expr = expr[3:]
                for part in expr.split("."):
                    cur = (cur or {}).get(part, default) if isinstance(cur, dict) else default
                return cur
            # 简单算术：允许数字/i/it.数值字段/_max/_n/+/-/*///()
            # 例："{1240*it.a/_max}"（条形图按极值归一化宽度）
            expr2 = expr
            _it = ctx.get("it") if isinstance(ctx.get("it"), dict) else {}

            def _numf(m):
                try:
                    return str(float(_it.get(m.group(1), 0) or 0))
                except (TypeError, ValueError):
                    return "0"

            expr2 = re.sub(r"it\.([A-Za-z_][\w]*)", _numf, expr2)
            expr2 = expr2.replace("_max", str(ctx.get("_max", 1) or 1))
            expr2 = expr2.replace("_n", str(ctx.get("_n", 1) or 1))
            expr2 = expr2.replace("i", str(ctx.get("i", 0) - 1))
            if re.fullmatch(r"[0-9+\-*/(). ]+", expr2):
                try:
                    return eval(expr2)
                except Exception:
                    return default
            # 旧格式：只允许数字/i/+/-/*/()
            if re.fullmatch(r"[0-9i+\-*/() ]+", expr):
                return eval(expr.replace("i", str(ctx.get("i", 0) - 1)))
    return v


def _xy(组件, ctx, *keys):
    """解析坐标字段（支持 {算术} 模板）。"""
    out = []
    for k in keys:
        v = 组件.get(k)
        if isinstance(v, str) and v.startswith("{"):
            v = _val({"v": v}, ctx, "v")
        out.append(v)
    return out[0] if len(out) == 1 else out


def 渲染组件(slide, 组件, ctx):
    E = _E()
    p = ctx.get("p", {})
    kind = 组件["组件"]
    if kind == "底色":
        E.rect(slide, 0, 0, 1920, 1080, fill=_val(组件, ctx, "fill", "bg"))
    elif kind == "文本":
        v = _字段(ctx, 组件.get("字段"))
        if v is None:
            return
        if isinstance(v, list):
            # 数组字段（如表格行）：用 ｜ 连接，避免打出 Python repr
            v = " ｜ ".join(str(x) for x in v)
        from pptx.enum.text import PP_ALIGN as _PA
        _align = {"left": _PA.LEFT, "center": _PA.CENTER,
                  "right": _PA.RIGHT}.get(组件.get("align", "left"), _PA.LEFT)
        x, y, w, h = _xy(组件, ctx, "x", "y", "w", "h")
        tf = E.textbox(slide, x, y, w, h)
        E.para(tf, str(v), 组件.get("size", 22),
               base=组件.get("color", "ink"),
               bold=组件.get("bold", False),
               align=_align)
    elif kind == "图片":
        v = _字段(ctx, 组件.get("字段"))
        if not v:
            return
        # data URI 或路径都支持：相对路径走项目 素材/ 目录（与 _img_path 一致）
        path = v
        if (isinstance(v, str) and not v.startswith("data:")
                and not v.startswith("http") and not os.path.isabs(v)):
            base = ctx.get("_素材dir")
            if base:
                path = os.path.normpath(os.path.join(base, v))
        if isinstance(v, str) and v.startswith("data:"):
            import base64
            m = re.match(r"data:image/(\w+);base64,(.*)", v, re.S)
            ext = m.group(1) if m else "png"
            path = "/tmp/pptxmap-%s.%s" % (abs(hash(v)) % 10**8, ext)
            if not os.path.exists(path):
                io = __import__("io")
                open(path, "wb").write(base64.b64decode(m.group(2)))
        x, y, w, h = _xy(组件, ctx, "x", "y", "w", "h")
        pic = E.pic_cover(slide, path, x, y, w, h)
        alpha = 组件.get("alpha")  # 0–100 不透明度（双重曝光叠加用）
        if alpha:
            E.set_pic_alpha(pic, alpha)
    elif kind == "矩形":
        x, y, w, h = _xy(组件, ctx, "x", "y", "w", "h")
        E.rect(slide, x, y, w, h,
               fill=组件.get("fill"), line=组件.get("line"))
    elif kind == "线条":
        x1, y1, x2, y2 = _xy(组件, ctx, "x1", "y1", "x2", "y2")
        E.arrow_line(slide, x1, y1, x2, y2,
                     color=组件.get("color", "gold"), w_pt=组件.get("w", 2),
                     head=0)
    elif kind == "徽章":
        v = _字段(ctx, 组件.get("字段"))
        x, y = _xy(组件, ctx, "x", "y")
        E.badge(slide, x, y, str(v or ""),
                组件.get("kind", "gold"))
    elif kind == "页眉":
        E.page_head(slide, p)
    elif kind == "页脚":
        E.page_foot(slide, p)
    elif kind == "结论条":
        v = _字段(ctx, 组件.get("字段"))
        if not v:
            return
        x, y, w = _xy(组件, ctx, "x", "y", "w")
        E.concl_bar(slide, x, y, w, str(v))
    elif kind == "循环":
        items = _字段(ctx, 组件.get("字段")) or []
        # _n 写回父 ctx：循环后的组件（如结论条定位）也能用 "{430+150*_n}"
        ctx["_n"] = len(items) or 1
        sub0 = dict(ctx)
        # 极值：{"极值": ["a","b"]} → _max = 全部项指定字段的最大值（条形图归一化用）
        jz = 组件.get("极值") or []
        if jz:
            mx = 0
            for _it in items:
                if isinstance(_it, dict):
                    for f in jz:
                        try:
                            mx = max(mx, float(_it.get(f, 0) or 0))
                        except (TypeError, ValueError):
                            pass
            sub0["_max"] = mx or 1
            ctx["_max"] = sub0["_max"]
        for i, it in enumerate(items):
            sub = dict(sub0, i=i + 1, it=it)
            for c in 组件["模板"]:
                渲染组件(slide, c, sub)
    else:
        raise ValueError("未知组件：%s" % kind)


def 渲染声明式(slide, p, 映射):
    from 基座 import project_dir
    ctx = {"p": p,
           "_素材dir": os.path.normpath(os.path.join(project_dir(), "素材"))}
    for c in 映射:
        渲染组件(slide, copy.deepcopy(c), ctx)


# ============================================================
# 各页型映射（坐标从 HTML 模板版式数值抄）
# ============================================================
映射表 = {
    "cover_split": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "图片", "字段": "img", "x": 1152, "y": 0, "w": 768, "h": 1080, "fit": "cover"},
        {"组件": "线条", "x1": 1152, "y1": 120, "x2": 1152, "y2": 960, "color": "gold", "w": 2},
        {"组件": "文本", "字段": "eyebrow", "x": 96, "y": 200, "w": 900, "h": 40,
         "size": 20, "color": "gold"},
        {"组件": "文本", "字段": "title", "x": 96, "y": 260, "w": 900, "h": 300,
         "size": 64, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "en", "x": 96, "y": 580, "w": 900, "h": 60,
         "size": 22, "color": "muted"},
        {"组件": "文本", "字段": "sub", "x": 96, "y": 660, "w": 900, "h": 60,
         "size": 22, "color": "muted"},
        {"组件": "文本", "字段": "foot", "x": 96, "y": 980, "w": 900, "h": 40,
         "size": 18, "color": "muted"},
        {"组件": "文本", "字段": "corner", "x": 1000, "y": 980, "w": 120, "h": 40,
         "size": 20, "color": "gold", "align": "right"},
    ],
    "kpi_hero": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "kpis", "模板": [
            # 3 卡横向：x = 96 + (i-1)*592
            {"组件": "矩形", "x": "{96+592*i}", "y": 320, "w": 560, "h": 380, "fill": "card"},
            {"组件": "文本", "字段": "{it.v}", "x": "{140+592*i}", "y": 380, "w": 472, "h": 120,
             "size": 64, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.label}", "x": "{140+592*i}", "y": 510, "w": 472, "h": 50,
             "size": 22, "color": "muted"},
            {"组件": "文本", "字段": "{it.ctx}", "x": "{140+592*i}", "y": 560, "w": 472, "h": 50,
             "size": 22, "color": "green"},
        ]},
        {"组件": "结论条", "字段": "concl", "x": 96, "y": 760, "w": 1728},
    ],
    "chart": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 300, "w": 1080, "h": 610, "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 920, "w": 1080, "h": 40,
         "size": 18, "color": "muted"},
        {"组件": "矩形", "x": 1240, "y": 300, "w": 584, "h": 610, "fill": "card"},
        {"组件": "文本", "字段": "{insight.take}", "x": 1280, "y": 340, "w": 504, "h": 100,
         "size": 24, "color": "ink", "bold": True},
        {"组件": "循环", "字段": "{insight.bullets}", "模板": [
            {"组件": "文本", "字段": "{it}", "x": 1300, "y": "{480+60*i}", "w": 484, "h": 60,
             "size": 20, "color": "muted"},
        ]},
    ],
    "chart_rail": [
        # 左65%图表 + 右35%结论栏（标签/英雄数字/解读）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 340, "w": 1080, "h": 560,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1080, "h": 40,
         "size": 18, "color": "muted"},
        {"组件": "矩形", "x": 1240, "y": 340, "w": 584, "h": 420, "fill": "card"},
        {"组件": "文本", "字段": "{rail.label}", "x": 1280, "y": 380, "w": 504,
         "h": 40, "size": 20, "color": "muted", "bold": True},
        {"组件": "文本", "字段": "{rail.hero}", "x": 1280, "y": 430, "w": 504,
         "h": 90, "size": 54, "color": "gold", "bold": True},
        {"组件": "文本", "字段": "{rail.body}", "x": 1280, "y": 540, "w": 504,
         "h": 200, "size": 20, "color": "ink"},
    ],
    "chart_multiples": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 340, "w": 1728, "h": 560,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "chart_waterfall": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 340, "w": 1728, "h": 560,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "chart_combo": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 340, "w": 1728, "h": 560,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "chart_table": [
        # 上图 + 下表（表降级为文本行）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 330, "w": 1728, "h": 420,
         "fit": "contain"},
        {"组件": "循环", "字段": "rows", "模板": [
            {"组件": "文本", "字段": "{it}", "x": 96, "y": "{790+44*i}",
             "w": 1728, "h": 44, "size": 20, "color": "ink"},
        ]},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 950, "w": 1728, "h": 36,
         "size": 18, "color": "muted"},
    ],
    "chart_annotated": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 340, "w": 1728, "h": 560,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "chart_dashboard": [
        # KPI 卡片行 + 下方支撑图表
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "kpis", "模板": [
            {"组件": "矩形", "x": "{96+i*(1728/_n)}", "y": 340,
             "w": "{1728/_n-24}", "h": 200, "fill": "card"},
            {"组件": "文本", "字段": "{it.名}", "x": "{124+i*(1728/_n)}", "y": 360,
             "w": "{1728/_n-80}", "h": 36, "size": 20, "color": "muted", "bold": True},
            {"组件": "文本", "字段": "{it.值}", "x": "{124+i*(1728/_n)}", "y": 400,
             "w": "{1728/_n-80}", "h": 70, "size": 44, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.变化}", "x": "{124+i*(1728/_n)}", "y": 480,
             "w": "{1728/_n-80}", "h": 40, "size": 20, "color": "gold", "bold": True},
        ]},
        {"组件": "图片", "字段": "img", "x": 96, "y": 580, "w": 1728, "h": 320,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "chart_dumbbell": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 340, "w": 1728, "h": 560,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "chart_ranked": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 340, "w": 1728, "h": 560,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "chart_map": [
        # 地图占位：指标 + 待接入说明（地理数据接入后替换为真实地图）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "矩形", "x": 96, "y": 340, "w": 1728, "h": 560, "fill": "card"},
        {"组件": "文本", "字段": "metric", "x": 96, "y": 560, "w": 1728, "h": 60,
         "size": 30, "color": "ink", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "note", "x": 96, "y": 630, "w": 1728, "h": 50,
         "size": 20, "color": "muted", "align": "center"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "chart_dualpanel": [
        # 左右双面板：绝对值 + 占比
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "kick", "x": 96, "y": 330, "w": 840, "h": 36,
         "size": 20, "color": "gold", "bold": True},
        {"组件": "图片", "字段": "img_abs", "x": 96, "y": 376, "w": 840, "h": 520,
         "fit": "contain"},
        {"组件": "文本", "字段": "kick", "x": 984, "y": 330, "w": 840, "h": 36,
         "size": 20, "color": "gold", "bold": True},
        {"组件": "图片", "字段": "img_share", "x": 984, "y": 376, "w": 840, "h": 520,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "chart_bullet": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 340, "w": 1728, "h": 560,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "chart_pareto": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 340, "w": 1728, "h": 560,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "chart_stacked": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 96, "y": 340, "w": 1728, "h": 560,
         "fit": "contain"},
        {"组件": "文本", "字段": "cap", "x": 96, "y": 915, "w": 1728, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "infographic": [
        # 信息图：2-4项横向卡片（图标在PPTX中省略，数字/标签/说明承载信息）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "矩形", "x": "{96+i*(1728/_n)}", "y": 360,
             "w": "{1728/_n-24}", "h": 420, "fill": "card"},
            {"组件": "文本", "字段": "{it.v}", "x": "{120+i*(1728/_n)}", "y": 500,
             "w": "{1728/_n-72}", "h": 90,
             "size": 64, "color": "ink", "bold": True, "align": "center"},
            {"组件": "文本", "字段": "{it.label}", "x": "{120+i*(1728/_n)}", "y": 600,
             "w": "{1728/_n-72}", "h": 40,
             "size": 22, "color": "gold", "bold": True, "align": "center"},
            {"组件": "文本", "字段": "{it.d}", "x": "{120+i*(1728/_n)}", "y": 650,
             "w": "{1728/_n-72}", "h": 110,
             "size": 20, "color": "muted", "align": "center"},
        ]},
        {"组件": "结论条", "字段": "concl", "x": 96, "y": 820, "w": 1728},
    ],
    "compare_bars": [
        # 对比条：rows[{label,a,b}]，条宽按极值归一化（金底字用 bg-dark，沿用 .badge.gold 约定）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "矩形", "x": 1300, "y": 348, "w": 36, "h": 20, "fill": "gold"},
        {"组件": "文本", "字段": "a_name", "x": 1344, "y": 340, "w": 200, "h": 36,
         "size": 20, "color": "ink", "bold": True},
        {"组件": "矩形", "x": 1560, "y": 348, "w": 36, "h": 20, "fill": "line"},
        {"组件": "文本", "字段": "b_name", "x": 1604, "y": 340, "w": 200, "h": 36,
         "size": 20, "color": "ink", "bold": True},
        {"组件": "循环", "字段": "rows", "极值": ["a", "b"], "模板": [
            {"组件": "文本", "字段": "{it.label}", "x": 96, "y": "{420+150*i}",
             "w": 248, "h": 60, "size": 22, "color": "muted", "align": "right"},
            {"组件": "矩形", "x": 376, "y": "{400+150*i}",
             "w": "{1240*it.a/_max}", "h": 38, "fill": "gold"},
            {"组件": "文本", "字段": "{it.a}", "x": 390, "y": "{400+150*i}",
             "w": 300, "h": 38, "size": 20, "color": "bg-dark", "bold": True},
            {"组件": "矩形", "x": 376, "y": "{448+150*i}",
             "w": "{1240*it.b/_max}", "h": 38, "fill": "line"},
            {"组件": "文本", "字段": "{it.b}", "x": 390, "y": "{448+150*i}",
             "w": 300, "h": 38, "size": 20, "color": "ink", "bold": True},
        ]},
        {"组件": "结论条", "字段": "concl", "x": 96, "y": "{430+150*_n}", "w": 1728},
    ],
    "number_hero": [
        # 大数字：一页一个数字做视觉锤（图标省略）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "v", "x": 96, "y": 360, "w": 1728, "h": 220,
         "size": 200, "color": "gold", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "label", "x": 96, "y": 600, "w": 1728, "h": 70,
         "size": 45, "color": "ink", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "{d}", "x": 360, "y": 690, "w": 1200, "h": 100,
         "size": 22, "color": "muted", "align": "center"},
        {"组件": "文本", "字段": "{ctx}", "x": 96, "y": 810, "w": 1728, "h": 50,
         "size": 22, "color": "green", "bold": True, "align": "center"},
    ],
    "toc_grid": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 副标题 + 金色英文行（HTML .hd 区）
        {"组件": "文本", "字段": "sub", "x": 120, "y": 300, "w": 1680, "h": 44,
         "size": 34, "color": "muted"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 344, "w": 1680, "h": 32,
         "size": 22, "color": "gold"},
        # 2×2 网格：col=i-2*(i//2), row=i//2；格 827×287，gap 26
        {"组件": "循环", "字段": "cards", "模板": [
            {"组件": "矩形", "x": "{120+853*(i-2*(i//2))}", "y": "{390+313*(i//2)}",
             "w": 827, "h": 287, "fill": "card"},
            {"组件": "图片", "字段": "{it.img}", "x": "{120+853*(i-2*(i//2))}",
             "y": "{390+313*(i//2)}", "w": 300, "h": 287, "fit": "cover"},
            {"组件": "文本", "字段": "{it.no}", "x": "{454+853*(i-2*(i//2))}",
             "y": "{430+313*(i//2)}", "w": 460, "h": 32,
             "size": 22, "color": "gold"},
            {"组件": "文本", "字段": "{it.zh}", "x": "{454+853*(i-2*(i//2))}",
             "y": "{466+313*(i//2)}", "w": 460, "h": 50,
             "size": 34, "color": "green", "bold": True},
            {"组件": "文本", "字段": "{it.desc}", "x": "{454+853*(i-2*(i//2))}",
             "y": "{522+313*(i//2)}", "w": 460, "h": 130,
             "size": 22, "color": "muted"},
        ]},
    ],
    "toc_list": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 纵向编号行：y=390+118*i；编号 60pt 主题色 + 标题 + 描述，行间细线
        {"组件": "文本", "字段": "sub", "x": 120, "y": 300, "w": 1680, "h": 44,
         "size": 34, "color": "muted"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 344, "w": 1680, "h": 32,
         "size": 22, "color": "gold"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "线条", "x1": 120, "y1": "{502+118*i}", "x2": 1800,
             "y2": "{502+118*i}", "color": "gold", "w": 1},
            {"组件": "文本", "字段": "{it.no}", "x": 120, "y": "{390+118*i}",
             "w": 170, "h": 100, "size": 60, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.zh}", "x": 310, "y": "{412+118*i}",
             "w": 400, "h": 60, "size": 30, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.desc}", "x": 730, "y": "{420+118*i}",
             "w": 1030, "h": 60, "size": 20, "color": "muted"},
        ]},
    ],
    "toc_bignum": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 大数字行：y=370+150*i；120pt 主题色数字 + 右侧标题/描述
        # （HTML 的数字叠印幽灵效果在 PPTX 中退化为实色大数字）
        {"组件": "文本", "字段": "sub", "x": 120, "y": 300, "w": 1680, "h": 44,
         "size": 34, "color": "muted"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 344, "w": 1680, "h": 32,
         "size": 22, "color": "gold"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "文本", "字段": "{it.no}", "x": 120, "y": "{370+150*i}",
             "w": 300, "h": 150, "size": 120, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.zh}", "x": 440, "y": "{400+150*i}",
             "w": 1300, "h": 60, "size": 40, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.desc}", "x": 440, "y": "{468+150*i}",
             "w": 1300, "h": 50, "size": 20, "color": "muted"},
        ]},
    ],
    "toc_split": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 左标题区：卡片 + 竖金条 + 标题/英文/副标题
        {"组件": "矩形", "x": 120, "y": 330, "w": 520, "h": 620, "fill": "card"},
        {"组件": "矩形", "x": 172, "y": 390, "w": 6, "h": 110, "fill": "gold"},
        {"组件": "文本", "字段": "title", "x": 172, "y": 530, "w": 416, "h": 140,
         "size": 54, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "en", "x": 172, "y": 690, "w": 416, "h": 40,
         "size": 22, "color": "gold"},
        {"组件": "文本", "字段": "sub", "x": 172, "y": 750, "w": 416, "h": 150,
         "size": 20, "color": "muted"},
        # 右条目：y=360+130*i
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "文本", "字段": "{it.no}", "x": 760, "y": "{360+130*i}",
             "w": 150, "h": 80, "size": 46, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.zh}", "x": 930, "y": "{372+130*i}",
             "w": 330, "h": 60, "size": 30, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.desc}", "x": 1280, "y": "{380+130*i}",
             "w": 480, "h": 90, "size": 20, "color": "muted"},
        ]},
    ],
    "toc_tb": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 上部通栏标题横幅
        {"组件": "矩形", "x": 0, "y": 0, "w": 1920, "h": 340, "fill": "card"},
        {"组件": "文本", "字段": "title", "x": 120, "y": 150, "w": 1680, "h": 80,
         "size": 54, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "en", "x": 120, "y": 245, "w": 1680, "h": 36,
         "size": 22, "color": "gold"},
        {"组件": "文本", "字段": "sub", "x": 120, "y": 288, "w": 1680, "h": 36,
         "size": 20, "color": "muted"},
        # 下部等宽列：x=140+420*i
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "文本", "字段": "{it.no}", "x": "{140+420*i}", "y": 450,
             "w": 340, "h": 70, "size": 44, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.zh}", "x": "{140+420*i}", "y": 530,
             "w": 340, "h": 60, "size": 30, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.desc}", "x": "{140+420*i}", "y": 600,
             "w": 340, "h": 220, "size": 20, "color": "muted"},
        ]},
    ],
    "toc_tabs": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 阶梯条带：y=400+130*i，每条右缩 90
        {"组件": "文本", "字段": "sub", "x": 120, "y": 300, "w": 1680, "h": 44,
         "size": 34, "color": "muted"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 344, "w": 1680, "h": 32,
         "size": 22, "color": "gold"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "矩形", "x": "{120+90*i}", "y": "{400+130*i}",
             "w": "{1680-90*i}", "h": 104, "fill": "card"},
            {"组件": "矩形", "x": "{120+90*i}", "y": "{400+130*i}",
             "w": 8, "h": 104, "fill": "gold"},
            {"组件": "徽章", "字段": "{it.no}", "x": "{180+90*i}",
             "y": "{428+130*i}", "kind": "gold"},
            {"组件": "文本", "字段": "{it.zh}", "x": "{310+90*i}",
             "y": "{428+130*i}", "w": 700, "h": 60,
             "size": 34, "color": "ink", "bold": True},
        ]},
    ],
    "toc_icon": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 4 列图标卡：图标在 PPTX 中省略，大编号承载信息；x=120+420*i
        {"组件": "文本", "字段": "sub", "x": 120, "y": 300, "w": 1680, "h": 44,
         "size": 34, "color": "muted"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 344, "w": 1680, "h": 32,
         "size": 22, "color": "gold"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "矩形", "x": "{120+420*i}", "y": 400, "w": 394, "h": 440,
             "fill": "card"},
            {"组件": "文本", "字段": "{it.no}", "x": "{120+420*i}", "y": 470,
             "w": 394, "h": 40, "size": 24, "color": "gold", "bold": True,
             "align": "center"},
            {"组件": "文本", "字段": "{it.zh}", "x": "{120+420*i}", "y": 530,
             "w": 394, "h": 60, "size": 28, "color": "ink", "bold": True,
             "align": "center"},
            {"组件": "文本", "字段": "{it.desc}", "x": "{150+420*i}", "y": 610,
             "w": 334, "h": 200, "size": 20, "color": "muted",
             "align": "center"},
        ]},
    ],
    "toc_image": [
        # 全幅背景图 + 左侧实色面板（近似 HTML 定向渐变蒙版的文字侧）
        {"组件": "图片", "字段": "img", "x": 0, "y": 0, "w": 1920, "h": 1080,
         "fit": "cover"},
        {"组件": "矩形", "x": 0, "y": 0, "w": 1060, "h": 1080, "fill": "bg"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "title", "x": 120, "y": 140, "w": 880, "h": 80,
         "size": 54, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 120, "y": 240, "w": 880, "h": 44,
         "size": 26, "color": "muted"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 296, "w": 880, "h": 36,
         "size": 22, "color": "gold"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "文本", "字段": "{it.no}", "x": 120, "y": "{392+118*i}",
             "w": 150, "h": 80, "size": 48, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.zh}", "x": 290, "y": "{406+118*i}",
             "w": 300, "h": 60, "size": 30, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.desc}", "x": 610, "y": "{414+118*i}",
             "w": 400, "h": 60, "size": 20, "color": "muted"},
        ]},
    ],
    "toc_roadmap": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 横向轨道 + 均匀节点（进度高亮状态在 PPTX 中简化为统一金色节点）
        {"组件": "文本", "字段": "sub", "x": 120, "y": 300, "w": 1680, "h": 44,
         "size": 34, "color": "muted"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 344, "w": 1680, "h": 32,
         "size": 22, "color": "gold"},
        {"组件": "线条", "x1": 120, "y1": 480, "x2": 1800, "y2": 480,
         "color": "gold", "w": 6},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "徽章", "字段": "{it.no}",
             "x": "{120+1680*i/(_n-1)-58}", "y": 452, "kind": "gold"},
            {"组件": "文本", "字段": "{it.zh}",
             "x": "{120+1680*i/(_n-1)-170}", "y": 545, "w": 340, "h": 50,
             "size": 26, "color": "ink", "bold": True, "align": "center"},
            {"组件": "文本", "字段": "{it.desc}",
             "x": "{120+1680*i/(_n-1)-170}", "y": 605, "w": 340, "h": 150,
             "size": 20, "color": "muted", "align": "center"},
        ]},
    ],
    "toc_magazine": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 索引行：标题左、编号右，细线近似引导线；y=390+130*i
        {"组件": "文本", "字段": "sub", "x": 120, "y": 300, "w": 1680, "h": 44,
         "size": 34, "color": "muted"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 344, "w": 1680, "h": 32,
         "size": 22, "color": "gold"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "文本", "字段": "{it.zh}", "x": 120, "y": "{390+130*i}",
             "w": 700, "h": 56, "size": 32, "color": "ink", "bold": True},
            {"组件": "线条", "x1": 850, "y1": "{418+130*i}", "x2": 1540,
             "y2": "{418+130*i}", "color": "gold", "w": 2},
            {"组件": "文本", "字段": "{it.no}", "x": 1560, "y": "{390+130*i}",
             "w": 240, "h": 56, "size": 26, "color": "gold", "bold": True,
             "align": "right"},
            {"组件": "文本", "字段": "{it.desc}", "x": 120, "y": "{450+130*i}",
             "w": 1400, "h": 60, "size": 20, "color": "muted"},
        ]},
    ],
    "toc_curve": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # PPTX 中退化为纵向中线 + 编号节点（HTML 保留 S 形曲线）
        {"组件": "文本", "字段": "sub", "x": 120, "y": 300, "w": 1680, "h": 44,
         "size": 34, "color": "muted"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 344, "w": 1680, "h": 32,
         "size": 22, "color": "gold"},
        {"组件": "线条", "x1": 960, "y1": 360, "x2": 960, "y2": 980,
         "color": "gold", "w": 3},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "徽章", "字段": "{it.no}", "x": 902, "y": "{380+100*i}",
             "kind": "gold"},
            {"组件": "文本", "字段": "{it.zh}", "x": 1040, "y": "{384+100*i}",
             "w": 700, "h": 50, "size": 28, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.desc}", "x": 1040, "y": "{434+100*i}",
             "w": 700, "h": 60, "size": 20, "color": "muted"},
        ]},
    ],
    "toc_minimal": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 极简大字：y=370+135*i
        {"组件": "文本", "字段": "title", "x": 120, "y": 140, "w": 1680, "h": 70,
         "size": 40, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "en", "x": 120, "y": 225, "w": 1680, "h": 36,
         "size": 22, "color": "gold"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "文本", "字段": "{it.zh}", "x": 120, "y": "{370+135*i}",
             "w": 1680, "h": 100, "size": 54, "color": "ink", "bold": True},
        ]},
    ],
    "section_image": [
        # 全幅背景图 + 底部深色带（近似 HTML 底部渐变遮罩）
        {"组件": "图片", "字段": "img", "x": 0, "y": 0, "w": 1920, "h": 1080,
         "fit": "cover"},
        {"组件": "矩形", "x": 0, "y": 640, "w": 1920, "h": 440,
         "fill": "bg-dark"},
        {"组件": "文本", "字段": "brow", "x": 120, "y": 60, "w": 800, "h": 36,
         "size": 22, "color": "#FFFFFF"},
        {"组件": "文本", "字段": "no", "x": 1420, "y": 60, "w": 380, "h": 36,
         "size": 22, "color": "#FFFFFF", "align": "right"},
        {"组件": "文本", "字段": "kick", "x": 120, "y": 680, "w": 1400, "h": 40,
         "size": 20, "color": "#FFFFFF", "bold": True},
        {"组件": "文本", "字段": "title", "x": 120, "y": 730, "w": 1400, "h": 110,
         "size": 64, "color": "#FFFFFF", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 120, "y": 855, "w": 1400, "h": 60,
         "size": 20, "color": "#FFFFFF"},
    ],
    "section_split": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 左 45% 图片 + 右文字区
        {"组件": "图片", "字段": "img", "x": 0, "y": 0, "w": 864, "h": 1080,
         "fit": "cover"},
        {"组件": "矩形", "x": 864, "y": 0, "w": 1056, "h": 1080, "fill": "card"},
        {"组件": "矩形", "x": 974, "y": 530, "w": 6, "h": 96, "fill": "gold"},
        {"组件": "文本", "字段": "kick", "x": 974, "y": 650, "w": 800, "h": 40,
         "size": 20, "color": "gold", "bold": True},
        {"组件": "文本", "字段": "title", "x": 974, "y": 700, "w": 800, "h": 130,
         "size": 52, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "en", "x": 974, "y": 845, "w": 800, "h": 36,
         "size": 22, "color": "gold"},
        {"组件": "文本", "字段": "sub", "x": 974, "y": 895, "w": 800, "h": 120,
         "size": 20, "color": "muted"},
    ],
    "section_minimal": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 居中极简：小 kick + 巨型标题 + 金线
        {"组件": "文本", "字段": "kick", "x": 120, "y": 400, "w": 1680, "h": 40,
         "size": 20, "color": "muted", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "title", "x": 120, "y": 460, "w": 1680, "h": 130,
         "size": 64, "color": "ink", "bold": True, "align": "center"},
        {"组件": "矩形", "x": 928, "y": 625, "w": 64, "h": 3, "fill": "gold"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 650, "w": 1680, "h": 36,
         "size": 22, "color": "gold", "align": "center"},
        {"组件": "文本", "字段": "sub", "x": 120, "y": 700, "w": 1680, "h": 60,
         "size": 20, "color": "muted", "align": "center"},
    ],
    "section_accent": [
        # 深底 + 左侧通高金条（页眉页脚在深底上用 silver，已由 body.dark 语义覆盖；
        # 此处为声明式直绘，页眉页脚组件省略，改用底部注）
        {"组件": "矩形", "x": 0, "y": 0, "w": 1920, "h": 1080, "fill": "bg-dark"},
        {"组件": "矩形", "x": 120, "y": 110, "w": 6, "h": 970, "fill": "gold"},
        {"组件": "文本", "字段": "kick", "x": 200, "y": 330, "w": 1400, "h": 40,
         "size": 20, "color": "gold", "bold": True},
        {"组件": "文本", "字段": "num", "x": 196, "y": 380, "w": 600, "h": 160,
         "size": 96, "color": "gold", "bold": True},
        {"组件": "文本", "字段": "title", "x": 200, "y": 560, "w": 1400, "h": 110,
         "size": 52, "color": "ink-dark", "bold": True},
        {"组件": "文本", "字段": "en", "x": 200, "y": 690, "w": 1400, "h": 36,
         "size": 22, "color": "gold"},
        {"组件": "文本", "字段": "sub", "x": 200, "y": 740, "w": 1400, "h": 60,
         "size": 20, "color": "silver"},
        {"组件": "文本", "字段": "foot", "x": 200, "y": 980, "w": 1400, "h": 36,
         "size": 20, "color": "silver"},
    ],
    "section_band": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 标题区 + 中部图片带
        {"组件": "文本", "字段": "kick", "x": 120, "y": 170, "w": 1400, "h": 40,
         "size": 20, "color": "gold", "bold": True},
        {"组件": "文本", "字段": "title", "x": 120, "y": 220, "w": 1400, "h": 110,
         "size": 56, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "en", "x": 120, "y": 345, "w": 1400, "h": 36,
         "size": 22, "color": "gold"},
        {"组件": "文本", "字段": "sub", "x": 120, "y": 390, "w": 1400, "h": 60,
         "size": 20, "color": "muted"},
        {"组件": "图片", "字段": "img", "x": 0, "y": 560, "w": 1920, "h": 340,
         "fit": "cover"},
    ],
    "section_statement": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 金句居中 + 角落编号
        {"组件": "文本", "字段": "kick", "x": 120, "y": 330, "w": 1680, "h": 40,
         "size": 20, "color": "gold", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "title", "x": 260, "y": 400, "w": 1400, "h": 200,
         "size": 60, "color": "ink", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "sub", "x": 260, "y": 620, "w": 1400, "h": 80,
         "size": 22, "color": "muted", "align": "center"},
        {"组件": "文本", "字段": "en", "x": 1500, "y": 900, "w": 300, "h": 50,
         "size": 26, "color": "gold", "bold": True, "align": "right"},
    ],
    "section_progress": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 标题居中 + 进度条 + 章节序列（高亮态在 PPTX 中简化为统一金色）
        {"组件": "文本", "字段": "kick", "x": 120, "y": 400, "w": 1680, "h": 40,
         "size": 20, "color": "gold", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "title", "x": 120, "y": 455, "w": 1680, "h": 120,
         "size": 60, "color": "ink", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 590, "w": 1680, "h": 36,
         "size": 22, "color": "gold", "align": "center"},
        {"组件": "矩形", "x": 580, "y": 700, "w": 760, "h": 6, "fill": "gold"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "文本", "字段": "{it.no}",
             "x": "{960-50*_n+100*i}", "y": 740, "w": 100, "h": 50,
             "size": 26, "color": "gold", "bold": True, "align": "center"},
        ]},
    ],
    "section_duo": [
        # 左深右金撞色
        {"组件": "矩形", "x": 0, "y": 0, "w": 960, "h": 1080, "fill": "bg-dark"},
        {"组件": "矩形", "x": 960, "y": 0, "w": 960, "h": 1080, "fill": "gold"},
        {"组件": "文本", "字段": "num", "x": 960, "y": 340, "w": 960, "h": 400,
         "size": 200, "color": "bg-dark", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "kick", "x": 120, "y": 380, "w": 760, "h": 40,
         "size": 20, "color": "gold", "bold": True},
        {"组件": "文本", "字段": "title", "x": 120, "y": 440, "w": 760, "h": 150,
         "size": 60, "color": "ink-dark", "bold": True},
        {"组件": "文本", "字段": "en", "x": 120, "y": 610, "w": 760, "h": 36,
         "size": 22, "color": "gold"},
        {"组件": "文本", "字段": "sub", "x": 120, "y": 660, "w": 700, "h": 120,
         "size": 20, "color": "silver"},
        {"组件": "文本", "字段": "foot", "x": 120, "y": 980, "w": 760, "h": 36,
         "size": 20, "color": "silver"},
    ],
    "section_reuse": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 目录复用：左当前章大标题 + 右章节列表
        # （高亮态在 PPTX 中简化为统一列表）
        {"组件": "文本", "字段": "kick", "x": 120, "y": 350, "w": 700, "h": 40,
         "size": 20, "color": "gold", "bold": True},
        {"组件": "文本", "字段": "title", "x": 120, "y": 405, "w": 700, "h": 200,
         "size": 54, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "en", "x": 120, "y": 620, "w": 700, "h": 36,
         "size": 22, "color": "gold"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "文本", "字段": "{it.no}", "x": 900, "y": "{350+68*i}",
             "w": 110, "h": 56, "size": 30, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.zh}", "x": 1030, "y": "{354+68*i}",
             "w": 750, "h": 56, "size": 28, "color": "ink", "bold": True},
        ]},
    ],
    "section_icon": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 图标在 PPTX 中省略；kick + 标题 + 英文 + 副标题居中
        {"组件": "文本", "字段": "kick", "x": 120, "y": 420, "w": 1680, "h": 40,
         "size": 20, "color": "gold", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "title", "x": 120, "y": 480, "w": 1680, "h": 130,
         "size": 56, "color": "ink", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "en", "x": 120, "y": 630, "w": 1680, "h": 36,
         "size": 22, "color": "gold", "align": "center"},
        {"组件": "文本", "字段": "sub", "x": 120, "y": 685, "w": 1680, "h": 60,
         "size": 20, "color": "muted", "align": "center"},
    ],
    "section_bridge": [
        # 深底 + 金线 + 大标题 + 引导语
        {"组件": "矩形", "x": 0, "y": 0, "w": 1920, "h": 1080, "fill": "bg-dark"},
        {"组件": "文本", "字段": "kick", "x": 200, "y": 380, "w": 1400, "h": 40,
         "size": 20, "color": "gold", "bold": True},
        {"组件": "矩形", "x": 200, "y": 445, "w": 72, "h": 4, "fill": "gold"},
        {"组件": "文本", "字段": "title", "x": 200, "y": 480, "w": 1520, "h": 220,
         "size": 68, "color": "ink-dark", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 200, "y": 720, "w": 1520, "h": 90,
         "size": 28, "color": "ink-dark"},
        {"组件": "文本", "字段": "en", "x": 200, "y": 825, "w": 1520, "h": 36,
         "size": 22, "color": "gold"},
        {"组件": "文本", "字段": "foot", "x": 200, "y": 980, "w": 1400, "h": 36,
         "size": 20, "color": "silver"},
    ],
    "timeline": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 横向轴线
        {"组件": "线条", "x1": 120, "y1": 580, "x2": 1800, "y2": 580,
         "color": "gold", "w": 3},
        # 里程碑上下交错：偶数上(y=350)、奇数下(y=680)；x 按 _n 均匀铺开
        {"组件": "循环", "字段": "nodes", "模板": [
            {"组件": "文本", "字段": "{it.t}", "x": "{120+(1680-340)/(_n-1)*i}",
             "y": "{680-330*(1-i+2*(i//2))}", "w": 340, "h": 44,
             "size": 28, "color": "gold", "align": "center"},
            {"组件": "文本", "字段": "{it.h}", "x": "{120+(1680-340)/(_n-1)*i}",
             "y": "{730-330*(1-i+2*(i//2))}", "w": 340, "h": 80,
             "size": 28, "color": "ink", "bold": True, "align": "center"},
            {"组件": "文本", "字段": "{it.d}", "x": "{120+(1680-340)/(_n-1)*i}",
             "y": "{800-330*(1-i+2*(i//2))}", "w": 340, "h": 110,
             "size": 20, "color": "muted", "align": "center"},
        ]},
        {"组件": "结论条", "字段": "concl", "x": 120, "y": 890, "w": 1680},
    ],
    "cards3": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 3 卡横向：x = 120 + (i-1)*572，卡 536×440
        {"组件": "循环", "字段": "cards", "模板": [
            {"组件": "矩形", "x": "{120+572*i}", "y": 360, "w": 536, "h": 440,
             "fill": "card"},
            {"组件": "矩形", "x": "{120+572*i}", "y": 360, "w": 536, "h": 8,
             "fill": "gold"},
            {"组件": "徽章", "字段": "{it.k}", "x": "{172+572*i}", "y": 412,
             "kind": "gold"},
            {"组件": "文本", "字段": "{it.n}", "x": "{172+572*i}", "y": 496,
             "w": 432, "h": 110, "size": 34, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.d}", "x": "{172+572*i}", "y": 620,
             "w": 432, "h": 160, "size": 22, "color": "muted"},
        ]},
        {"组件": "结论条", "字段": "concl", "x": 120, "y": 860, "w": 1680},
    ],
    "stepper": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 2–4 步横向：x = 120 + (i-1)*460，卡 400×400，编号徽章
        {"组件": "循环", "字段": "steps", "模板": [
            {"组件": "矩形", "x": "{120+460*i}", "y": 370, "w": 400, "h": 400,
             "fill": "card"},
            {"组件": "徽章", "字段": "{i+1}", "x": "{168+460*i}", "y": 418,
             "kind": "green"},
            {"组件": "文本", "字段": "{it.t}", "x": "{168+460*i}", "y": 506,
             "w": 304, "h": 80, "size": 34, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.d}", "x": "{168+460*i}", "y": 596,
             "w": 304, "h": 150, "size": 22, "color": "muted"},
        ]},
        # 提示框沉底：用结论条近似（卡底 + 金色左边条）
        {"组件": "结论条", "字段": "warn", "x": 120, "y": 860, "w": 1680},
    ],
    "equation_hero": [
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        # 中央大方程式 + 下标注
        {"组件": "文本", "字段": "eq", "x": 120, "y": 330, "w": 1680, "h": 150,
         "size": 118, "color": "ink", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "eqlabel", "x": 120, "y": 490, "w": 1680, "h": 36,
         "size": 22, "color": "muted", "align": "center"},
        # 三横卡：x = 120 + (i-1)*572，卡 536×210，左 8px 金条
        {"组件": "循环", "字段": "cards", "模板": [
            {"组件": "矩形", "x": "{120+572*i}", "y": 650, "w": 536, "h": 210,
             "fill": "card"},
            {"组件": "矩形", "x": "{120+572*i}", "y": 650, "w": 8, "h": 210,
             "fill": "gold"},
            {"组件": "文本", "字段": "{it.k}", "x": "{172+572*i}", "y": 682,
             "w": 448, "h": 30, "size": 22, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.n}", "x": "{172+572*i}", "y": 720,
             "w": 448, "h": 70, "size": 34, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.d}", "x": "{172+572*i}", "y": 796,
             "w": 448, "h": 60, "size": 22, "color": "muted"},
        ]},
        {"组件": "结论条", "字段": "concl", "x": 120, "y": 890, "w": 1680},
    ],
    "cover_typo": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "文本", "字段": "eyebrow", "x": 130, "y": 300, "w": 1200, "h": 40, "size": 14, "color": "gold"},
        {"组件": "线条", "x1": 130, "y1": 368, "x2": 214, "y2": 368, "color": "gold", "w": 4},
        {"组件": "文本", "字段": "title", "x": 130, "y": 400, "w": 1500, "h": 260, "size": 64, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "en", "x": 130, "y": 680, "w": 1200, "h": 50, "size": 24, "color": "gold"},
        {"组件": "文本", "字段": "sub", "x": 130, "y": 750, "w": 1200, "h": 90, "size": 20, "color": "muted"},
        {"组件": "文本", "字段": "foot", "x": 130, "y": 980, "w": 800, "h": 40, "size": 14, "color": "muted"},
        {"组件": "文本", "字段": "corner", "x": 1700, "y": 980, "w": 120, "h": 40, "size": 14, "color": "gold", "align": "right"},
    ],
    "cover_minimal": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "文本", "字段": "eyebrow", "x": 360, "y": 360, "w": 1200, "h": 40, "size": 14, "color": "gold", "align": "center"},
        {"组件": "文本", "字段": "title", "x": 210, "y": 430, "w": 1500, "h": 130, "size": 40, "color": "ink", "bold": True, "align": "center"},
        {"组件": "线条", "x1": 928, "y1": 600, "x2": 992, "y2": 600, "color": "gold", "w": 3},
        {"组件": "文本", "字段": "sub", "x": 360, "y": 640, "w": 1200, "h": 90, "size": 20, "color": "muted", "align": "center"},
        {"组件": "文本", "字段": "foot", "x": 760, "y": 980, "w": 400, "h": 40, "size": 14, "color": "muted", "align": "center"},
    ],
    "cover_block": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "文本", "字段": "eyebrow", "x": 130, "y": 360, "w": 760, "h": 40, "size": 14, "color": "gold"},
        {"组件": "线条", "x1": 130, "y1": 428, "x2": 214, "y2": 428, "color": "gold", "w": 4},
        {"组件": "文本", "字段": "title", "x": 130, "y": 460, "w": 760, "h": 260, "size": 54, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 130, "y": 750, "w": 760, "h": 90, "size": 20, "color": "muted"},
        {"组件": "图片", "字段": "img", "x": 1030, "y": 180, "w": 760, "h": 720},
        {"组件": "文本", "字段": "foot", "x": 130, "y": 980, "w": 700, "h": 40, "size": 14, "color": "muted"},
        {"组件": "文本", "字段": "corner", "x": 1700, "y": 980, "w": 120, "h": 40, "size": 14, "color": "gold", "align": "right"},
    ],
    "cover_duo": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "矩形", "x": 0, "y": 0, "w": 864, "h": 1080, "fill": "ink", "line": None},
        {"组件": "图片", "字段": "img", "x": 864, "y": 0, "w": 1056, "h": 1080},
        {"组件": "文本", "字段": "eyebrow", "x": 120, "y": 360, "w": 640, "h": 40, "size": 14, "color": "gold"},
        {"组件": "文本", "字段": "title", "x": 120, "y": 440, "w": 640, "h": 240, "size": 54, "color": "bg", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 120, "y": 710, "w": 640, "h": 90, "size": 20, "color": "bg"},
        {"组件": "文本", "字段": "foot", "x": 120, "y": 980, "w": 640, "h": 40, "size": 14, "color": "gold"},
    ],
    "cover_diagonal": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "图片", "字段": "img", "x": 0, "y": 0, "w": 1920, "h": 560},
        {"组件": "矩形", "x": 0, "y": 560, "w": 1920, "h": 520, "fill": "bg", "line": None},
        {"组件": "线条", "x1": 700, "y1": 0, "x2": 989, "y2": 1080, "color": "gold", "w": 4},
        {"组件": "文本", "字段": "eyebrow", "x": 130, "y": 640, "w": 900, "h": 40, "size": 14, "color": "gold"},
        {"组件": "文本", "字段": "title", "x": 130, "y": 710, "w": 1000, "h": 170, "size": 54, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 130, "y": 900, "w": 1000, "h": 60, "size": 20, "color": "muted"},
        {"组件": "文本", "字段": "foot", "x": 130, "y": 990, "w": 700, "h": 40, "size": 14, "color": "muted"},
    ],
    "cover_brand": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "矩形", "x": 1050, "y": -200, "w": 900, "h": 1480, "fill": "gold", "line": None},
        {"组件": "线条", "x1": 1050, "y1": 200, "x2": 1920, "y2": 200, "color": "gold", "w": 3},
        {"组件": "文本", "字段": "eyebrow", "x": 130, "y": 360, "w": 820, "h": 40, "size": 14, "color": "gold"},
        {"组件": "文本", "字段": "title", "x": 130, "y": 440, "w": 820, "h": 260, "size": 54, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 130, "y": 730, "w": 820, "h": 90, "size": 20, "color": "muted"},
        {"组件": "文本", "字段": "foot", "x": 130, "y": 980, "w": 700, "h": 40, "size": 14, "color": "muted"},
        {"组件": "文本", "字段": "corner", "x": 130, "y": 920, "w": 300, "h": 40, "size": 14, "color": "gold"},
    ],
    "cover_magazine": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "图片", "字段": "img", "x": 768, "y": 0, "w": 1152, "h": 1080},
        {"组件": "文本", "字段": "eyebrow", "x": 90, "y": 90, "w": 600, "h": 40, "size": 14, "color": "gold"},
        {"组件": "文本", "字段": "title", "x": 90, "y": 400, "w": 1100, "h": 280, "size": 64, "color": "ink", "bold": True},
        {"组件": "循环", "字段": "kickers", "模板": [
            {"组件": "文本", "字段": "{it.t}", "x": 118, "y": "{710+56*i}", "w": 700, "h": 44, "size": 18, "color": "ink", "bold": True},
        ]},
        {"组件": "文本", "字段": "sub", "x": 90, "y": 900, "w": 700, "h": 60, "size": 20, "color": "muted"},
        {"组件": "文本", "字段": "foot", "x": 90, "y": 990, "w": 600, "h": 40, "size": 14, "color": "muted"},
    ],
    "cover_lux": [
        {"组件": "底色", "fill": "#0B0D12"},
        {"组件": "文本", "字段": "eyebrow", "x": 660, "y": 380, "w": 600, "h": 40, "size": 16, "color": "gold", "align": "center"},
        {"组件": "文本", "字段": "title", "x": 360, "y": 450, "w": 1200, "h": 150, "size": 64, "color": "#F4F1EA", "bold": True, "align": "center"},
        {"组件": "线条", "x1": 918, "y1": 640, "x2": 1002, "y2": 640, "color": "gold", "w": 2},
        {"组件": "文本", "字段": "en", "x": 660, "y": 664, "w": 600, "h": 44, "size": 22, "color": "gold", "align": "center"},
        {"组件": "文本", "字段": "sub", "x": 560, "y": 724, "w": 800, "h": 70, "size": 22, "color": "#A8A29A", "align": "center"},
        {"组件": "文本", "字段": "foot", "x": 760, "y": 990, "w": 400, "h": 40, "size": 14, "color": "#6E6A63", "align": "center"},
    ],
    "cover_collage": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "文本", "字段": "eyebrow", "x": 130, "y": 360, "w": 620, "h": 40, "size": 14, "color": "gold"},
        {"组件": "文本", "字段": "title", "x": 130, "y": 440, "w": 620, "h": 150, "size": 40, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 130, "y": 620, "w": 620, "h": 90, "size": 20, "color": "muted"},
        {"组件": "循环", "字段": "imgs", "模板": [
            {"组件": "图片", "字段": "{it.src}", "x": "{1010+460*(i-2*(i//2))}", "y": "{180+380*(i//2)}", "w": 440, "h": 360},
        ]},
        {"组件": "文本", "字段": "foot", "x": 130, "y": 980, "w": 600, "h": 40, "size": 14, "color": "muted"},
    ],
    "cover_crop": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "图片", "字段": "img", "x": 700, "y": 0, "w": 1220, "h": 1080},
        {"组件": "文本", "字段": "eyebrow", "x": 130, "y": 380, "w": 640, "h": 40, "size": 14, "color": "gold"},
        {"组件": "文本", "字段": "title", "x": 130, "y": 460, "w": 640, "h": 260, "size": 54, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 130, "y": 750, "w": 640, "h": 90, "size": 20, "color": "muted"},
        {"组件": "文本", "字段": "foot", "x": 130, "y": 980, "w": 600, "h": 40, "size": 14, "color": "muted"},
    ],
    "cover_anchor": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "文本", "字段": "num", "x": 120, "y": 240, "w": 1100, "h": 280, "size": 130, "color": "gold", "bold": True},
        {"组件": "文本", "字段": "eyebrow", "x": 130, "y": 560, "w": 900, "h": 40, "size": 14, "color": "gold"},
        {"组件": "文本", "字段": "title", "x": 130, "y": 620, "w": 1100, "h": 130, "size": 40, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 130, "y": 770, "w": 1100, "h": 80, "size": 20, "color": "muted"},
        {"组件": "文本", "字段": "foot", "x": 130, "y": 980, "w": 800, "h": 40, "size": 14, "color": "muted"},
    ],
    "cover_fusion": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "图片", "字段": "img", "x": 0, "y": 0, "w": 1920, "h": 1080},
        {"组件": "图片", "字段": "img2", "x": 960, "y": 0, "w": 960, "h": 1080, "alpha": 55},
        {"组件": "矩形", "x": 90, "y": 600, "w": 800, "h": 400, "fill": "bg", "line": None},
        {"组件": "文本", "字段": "eyebrow", "x": 130, "y": 650, "w": 720, "h": 40, "size": 14, "color": "gold"},
        {"组件": "文本", "字段": "title", "x": 130, "y": 710, "w": 720, "h": 170, "size": 54, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 130, "y": 900, "w": 720, "h": 60, "size": 20, "color": "muted"},
        {"组件": "文本", "字段": "foot", "x": 130, "y": 990, "w": 600, "h": 40, "size": 14, "color": "muted"},
    ],
    "cover_band": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "图片", "字段": "img", "x": 0, "y": 0, "w": 1920, "h": 450},
        {"组件": "线条", "x1": 0, "y1": 450, "x2": 1920, "y2": 450, "color": "gold", "w": 4},
        {"组件": "文本", "字段": "eyebrow", "x": 130, "y": 560, "w": 1200, "h": 40, "size": 14, "color": "gold"},
        {"组件": "文本", "字段": "title", "x": 130, "y": 630, "w": 1300, "h": 150, "size": 40, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "sub", "x": 130, "y": 800, "w": 1300, "h": 60, "size": 20, "color": "muted"},
        {"组件": "文本", "字段": "foot", "x": 130, "y": 990, "w": 700, "h": 40, "size": 14, "color": "muted"},
    ],
    "cover_brush": [
        {"组件": "底色", "fill": "bg"},
        {"组件": "文本", "字段": "eyebrow", "x": 130, "y": 280, "w": 1000, "h": 40, "size": 16, "color": "muted"},
        {"组件": "文本", "字段": "title", "x": 130, "y": 360, "w": 1250, "h": 200, "size": 64, "color": "ink", "bold": True},
        {"组件": "矩形", "x": 1330, "y": 400, "w": 104, "h": 104, "fill": "#A93226", "line": None},
        {"组件": "文本", "字段": "seal", "x": 1330, "y": 400, "w": 104, "h": 104, "size": 22, "color": "#F7F3E8", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "sub", "x": 130, "y": 600, "w": 1100, "h": 80, "size": 24, "color": "ink"},
        {"组件": "文本", "字段": "foot", "x": 130, "y": 980, "w": 800, "h": 40, "size": 14, "color": "muted"},
    ],

    # ============================================================
    # 内容页 32 新页型（2026-10-06 入库，草案）
    # 坐标系：1920x1080；页眉占 y 64–308（brow/no/kick/title），页脚 y 1006；
    # 正文区 x 120–1800（w 1680），y 约 340–990。
    # 降级惯例（照抄既有条目注释写法）：icon/圆形/字形/字面量标签等画不出的，
    # 用色块占位或省略，并在注释写清；数组字段默认 ｜ 连接。
    # ============================================================
    # ---- 观点族 19 ----
    "statement_assertion": [
        # 行动标题页：title 走页眉；sub 副标题；points 纵向列表（t 加粗＋d 缩进小字）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "sub", "x": 120, "y": 330, "w": 1680, "h": 60,
         "size": 24, "color": "muted"},
        {"组件": "循环", "字段": "points", "模板": [
            {"组件": "矩形", "x": 120, "y": "{430+140*i}", "w": 8, "h": 110, "fill": "gold"},
            {"组件": "文本", "字段": "{it.t}", "x": 152, "y": "{424+140*i}", "w": 1648, "h": 54,
             "size": 28, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.d}", "x": 152, "y": "{478+140*i}", "w": 1648, "h": 60,
             "size": 22, "color": "muted"},
        ]},
    ],
    "statement_dotdash": [
        # 点线式：bullet 金点＋分论点加粗；ds 论据数组降级为同行 ｜ 连接
        #（声明式无嵌套循环二维定位，短横线形降级为金色横线）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "矩形", "x": 120, "y": "{392+150*i}", "w": 16, "h": 16, "fill": "gold"},
            {"组件": "文本", "字段": "{it.b}", "x": 156, "y": "{378+150*i}", "w": 1644, "h": 54,
             "size": 28, "color": "ink", "bold": True},
            {"组件": "线条", "x1": 156, "y1": "{452+150*i}", "x2": 196, "y2": "{452+150*i}",
             "color": "gold", "w": 3},
            {"组件": "文本", "字段": "{it.ds}", "x": 216, "y": "{432+150*i}", "w": 1584, "h": 80,
             "size": 22, "color": "muted"},
        ]},
    ],
    "statement_golden": [
        # 金句独白：phrase 超大字居中，大量留白；sub 选填
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "phrase", "x": 120, "y": 400, "w": 1680, "h": 220,
         "size": 88, "color": "ink", "bold": True, "align": "center"},
        {"组件": "线条", "x1": 896, "y1": 660, "x2": 1024, "y2": 660, "color": "gold", "w": 3},
        {"组件": "文本", "字段": "sub", "x": 360, "y": 700, "w": 1200, "h": 60,
         "size": 24, "color": "muted", "align": "center"},
    ],
    "quote_full": [
        # 全幅引言：bgimg 全幅底图（缺省跳过）；文字区卡片框压住；
        # 巨大引号装饰降级省略（声明式无字面量文本组件）
        {"组件": "底色", "fill": "bg"},
        {"组件": "图片", "字段": "bgimg", "x": 0, "y": 0, "w": 1920, "h": 1080, "fit": "cover"},
        {"组件": "矩形", "x": 360, "y": 300, "w": 1200, "h": 480, "fill": "card", "line": None},
        {"组件": "文本", "字段": "quote", "x": 420, "y": 420, "w": 1080, "h": 200,
         "size": 34, "color": "ink", "align": "center"},
        {"组件": "线条", "x1": 860, "y1": 650, "x2": 1060, "y2": 650, "color": "gold", "w": 2},
        {"组件": "文本", "字段": "author", "x": 420, "y": 670, "w": 1080, "h": 50,
         "size": 22, "color": "muted", "align": "center"},
        {"组件": "文本", "字段": "source", "x": 420, "y": 724, "w": 1080, "h": 40,
         "size": 18, "color": "muted", "align": "center"},
        {"组件": "页脚"},
    ],
    "quote_card": [
        # 卡片式引用：中央卡片；point 顶部关联论点小字（选填）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "point", "x": 120, "y": 340, "w": 1680, "h": 50,
         "size": 22, "color": "gold", "align": "center"},
        {"组件": "矩形", "x": 360, "y": 410, "w": 1200, "h": 420, "fill": "card", "line": None},
        {"组件": "文本", "字段": "quote", "x": 440, "y": 470, "w": 1040, "h": 200,
         "size": 30, "color": "ink", "align": "center"},
        {"组件": "线条", "x1": 900, "y1": 690, "x2": 1020, "y2": 690, "color": "gold", "w": 2},
        {"组件": "文本", "字段": "by", "x": 440, "y": 710, "w": 1040, "h": 50,
         "size": 22, "color": "ink", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "src", "x": 440, "y": 764, "w": 1040, "h": 40,
         "size": 18, "color": "muted", "align": "center"},
    ],
    "definition_dict": [
        # 词典条目式：term 巨大加粗；en 选填；规则线分隔；def 干净小字；note 边界说明
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "term", "x": 120, "y": 360, "w": 1680, "h": 150,
         "size": 96, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "en", "x": 120, "y": 520, "w": 1680, "h": 50,
         "size": 26, "color": "muted"},
        {"组件": "线条", "x1": 120, "y1": 600, "x2": 1800, "y2": 600, "color": "gold", "w": 3},
        {"组件": "文本", "字段": "def", "x": 120, "y": 640, "w": 1680, "h": 130,
         "size": 30, "color": "ink"},
        {"组件": "文本", "字段": "note", "x": 120, "y": 800, "w": 1680, "h": 120,
         "size": 20, "color": "muted"},
    ],
    "definition_terms": [
        # 术语卡片：2–4 横向卡（t 术语＋d 一句话定义）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "terms", "模板": [
            {"组件": "矩形", "x": "{96+i*(1728/_n)}", "y": 380,
             "w": "{1728/_n-24}", "h": 430, "fill": "card"},
            {"组件": "文本", "字段": "{it.t}", "x": "{140+i*(1728/_n)}", "y": 430,
             "w": "{1728/_n-112}", "h": 70, "size": 32, "color": "gold", "bold": True},
            {"组件": "线条", "x1": "{140+i*(1728/_n)}", "y1": 520,
             "x2": "{140+i*(1728/_n)+80}", "y2": 520, "color": "gold", "w": 3},
            {"组件": "文本", "字段": "{it.d}", "x": "{140+i*(1728/_n)}", "y": 550,
             "w": "{1728/_n-112}", "h": 230, "size": 22, "color": "ink"},
        ]},
    ],
    "problem_pain": [
        # 痛点图标阵列：icon 占位降级为金色方块；k 痛点论断加粗＋q 量化小字
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "pains", "模板": [
            {"组件": "矩形", "x": "{96+i*(1728/_n)}", "y": 380,
             "w": "{1728/_n-24}", "h": 430, "fill": "card"},
            {"组件": "矩形", "x": "{140+i*(1728/_n)}", "y": 430, "w": 64, "h": 64,
             "fill": "gold"},
            {"组件": "文本", "字段": "{it.k}", "x": "{140+i*(1728/_n)}", "y": 520,
             "w": "{1728/_n-112}", "h": 120, "size": 28, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.q}", "x": "{140+i*(1728/_n)}", "y": 660,
             "w": "{1728/_n-112}", "h": 120, "size": 22, "color": "gold"},
        ]},
    ],
    "solution_pillars": [
        # 方案支柱总览：2–4 横向 icon 卡（icon 降级为金色方块占位）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "pillars", "模板": [
            {"组件": "矩形", "x": "{96+i*(1728/_n)}", "y": 380,
             "w": "{1728/_n-24}", "h": 430, "fill": "card"},
            {"组件": "矩形", "x": "{140+i*(1728/_n)}", "y": 430, "w": 64, "h": 64,
             "fill": "gold"},
            {"组件": "文本", "字段": "{it.k}", "x": "{140+i*(1728/_n)}", "y": 520,
             "w": "{1728/_n-112}", "h": 70, "size": 30, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.d}", "x": "{140+i*(1728/_n)}", "y": 600,
             "w": "{1728/_n-112}", "h": 180, "size": 22, "color": "muted"},
        ]},
    ],
    "solution_features": [
        # 特性—价值行：纵向行列表（icon 金色方块占位＋f 特性名加粗＋v 价值小字），行间细分隔线
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "feats", "模板": [
            {"组件": "矩形", "x": 120, "y": "{380+124*i}", "w": 64, "h": 64, "fill": "gold"},
            {"组件": "文本", "字段": "{it.f}", "x": 208, "y": "{376+124*i}", "w": 700, "h": 56,
             "size": 26, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.v}", "x": 208, "y": "{430+124*i}", "w": 1496, "h": 56,
             "size": 22, "color": "muted"},
            {"组件": "线条", "x1": 120, "y1": "{500+124*i}", "x2": 1800, "y2": "{500+124*i}",
             "color": "line", "w": 1},
        ]},
    ],
    "solution_how": [
        # 原理解剖：横向 3 框；连接箭头降级为卡片间隙露出的金色基线；
        # hot 环节强调色降级：声明式框架无条件分支，统一金顶条（HTML 端按 hot 高亮）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "线条", "x1": 120, "y1": 570, "x2": 1800, "y2": 570, "color": "gold", "w": 4},
        {"组件": "循环", "字段": "steps", "模板": [
            {"组件": "矩形", "x": "{120+i*560}", "y": 420, "w": 536, "h": 300, "fill": "card"},
            {"组件": "矩形", "x": "{120+i*560}", "y": 420, "w": 536, "h": 12, "fill": "gold"},
            {"组件": "文本", "字段": "{it.t}", "x": "{160+i*560}", "y": 462, "w": 456, "h": 60,
             "size": 28, "color": "ink", "bold": True, "align": "center"},
            {"组件": "文本", "字段": "{it.d}", "x": "{160+i*560}", "y": 532, "w": 456, "h": 160,
             "size": 22, "color": "muted", "align": "center"},
        ]},
    ],
    "checklist_tasks": [
        # 任务清单：复选框（金色描边方块）＋事项＋责任人＋时间右对齐，行间分隔线
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "tasks", "模板": [
            {"组件": "矩形", "x": 120, "y": "{382+86*i}", "w": 36, "h": 36,
             "fill": "bg", "line": "gold"},
            {"组件": "文本", "字段": "{it.t}", "x": 176, "y": "{374+86*i}", "w": 900, "h": 52,
             "size": 24, "color": "ink"},
            {"组件": "文本", "字段": "{it.owner}", "x": 1100, "y": "{376+86*i}", "w": 300, "h": 48,
             "size": 22, "color": "muted"},
            {"组件": "文本", "字段": "{it.due}", "x": 1420, "y": "{376+86*i}", "w": 380, "h": 48,
             "size": 22, "color": "muted", "align": "right"},
            {"组件": "线条", "x1": 120, "y1": "{448+86*i}", "x2": 1800, "y2": "{448+86*i}",
             "color": "line", "w": 1},
        ]},
    ],
    "scorecard_status": [
        # 状态记分卡：条目＋状态徽（金色徽章）＋进度条（prog 缺省时只剩空轨道）；
        # legend 图例行（选填，_n 定位）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "文本", "字段": "{it.k}", "x": 120, "y": "{372+80*i}", "w": 680, "h": 48,
             "size": 24, "color": "ink"},
            {"组件": "徽章", "字段": "{it.status}", "x": 830, "y": "{376+80*i}", "kind": "gold"},
            {"组件": "矩形", "x": 1180, "y": "{386+80*i}", "w": 420, "h": 22, "fill": "line"},
            {"组件": "矩形", "x": 1180, "y": "{386+80*i}", "w": "{420*it.prog/100}", "h": 22,
             "fill": "gold"},
            {"组件": "线条", "x1": 120, "y1": "{440+80*i}", "x2": 1800, "y2": "{440+80*i}",
             "color": "line", "w": 1},
        ]},
        {"组件": "文本", "字段": "legend", "x": 120, "y": "{386+80*_n}", "w": 1680, "h": 40,
         "size": 18, "color": "muted"},
    ],
    "cta_single": [
        # 单一行动：action 超大字居中；who/when/ask 三行（标签字样降级省略，
        # 顺序固定：负责人/截止/所需支持，颜色区分）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "action", "x": 120, "y": 400, "w": 1680, "h": 200,
         "size": 72, "color": "ink", "bold": True, "align": "center"},
        {"组件": "线条", "x1": 896, "y1": 640, "x2": 1024, "y2": 640, "color": "gold", "w": 3},
        {"组件": "文本", "字段": "who", "x": 660, "y": 690, "w": 600, "h": 48,
         "size": 24, "color": "ink", "align": "center"},
        {"组件": "文本", "字段": "when", "x": 660, "y": 748, "w": 600, "h": 48,
         "size": 24, "color": "gold", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "ask", "x": 460, "y": 806, "w": 1000, "h": 60,
         "size": 22, "color": "muted", "align": "center"},
    ],
    "cta_next": [
        # 下一步清单：编号徽标（{i+1} 算术序号，金底方块）＋行动＋责任人＋时间；contact 底部条
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "steps", "模板": [
            {"组件": "矩形", "x": 120, "y": "{380+130*i}", "w": 56, "h": 56, "fill": "gold"},
            {"组件": "文本", "字段": "{i+1}", "x": 120, "y": "{384+130*i}", "w": 56, "h": 48,
             "size": 28, "color": "bg", "bold": True, "align": "center"},
            {"组件": "文本", "字段": "{it.t}", "x": 196, "y": "{376+130*i}", "w": 800, "h": 60,
             "size": 26, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.owner}", "x": 1020, "y": "{380+130*i}", "w": 300, "h": 50,
             "size": 22, "color": "muted"},
            {"组件": "文本", "字段": "{it.due}", "x": 1340, "y": "{380+130*i}", "w": 460, "h": 50,
             "size": 22, "color": "muted", "align": "right"},
            {"组件": "线条", "x1": 120, "y1": "{486+130*i}", "x2": 1800, "y2": "{486+130*i}",
             "color": "line", "w": 1},
        ]},
        {"组件": "结论条", "字段": "contact", "x": 120, "y": 830, "w": 1680},
    ],
    "scr_brief": [
        # SCR 一页纸：S/C/R 三段纵向（S/C 标签字样降级省略，顺序固定）；
        # R 段卡片＋金条强调
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "s", "x": 120, "y": 420, "w": 1680, "h": 130,
         "size": 24, "color": "ink"},
        {"组件": "文本", "字段": "c", "x": 120, "y": 600, "w": 1680, "h": 130,
         "size": 24, "color": "ink"},
        {"组件": "矩形", "x": 120, "y": 780, "w": 1680, "h": 170, "fill": "card"},
        {"组件": "矩形", "x": 120, "y": 780, "w": 8, "h": 170, "fill": "gold"},
        {"组件": "文本", "字段": "r", "x": 164, "y": 800, "w": 1596, "h": 130,
         "size": 26, "color": "ink", "bold": True},
    ],
    "framework_hub": [
        # 枢纽辐射：辐射连线降级为阵列排布（中心 hub 卡片置顶＋3 列网格）；
        # spokes>d 选填
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "矩形", "x": 710, "y": 350, "w": 500, "h": 130, "fill": "card"},
        {"组件": "矩形", "x": 710, "y": 350, "w": 500, "h": 10, "fill": "gold"},
        {"组件": "文本", "字段": "hub", "x": 750, "y": 380, "w": 420, "h": 80,
         "size": 32, "color": "ink", "bold": True, "align": "center"},
        {"组件": "线条", "x1": 120, "y1": 520, "x2": 1800, "y2": 520, "color": "gold", "w": 2},
        {"组件": "循环", "字段": "spokes", "模板": [
            {"组件": "矩形", "x": "{120+576*(i-3*(i//3))}", "y": "{560+170*(i//3)}",
             "w": 544, "h": 150, "fill": "card"},
            {"组件": "文本", "字段": "{it.t}", "x": "{160+576*(i-3*(i//3))}",
             "y": "{580+170*(i//3)}", "w": 464, "h": 50,
             "size": 24, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.d}", "x": "{160+576*(i-3*(i//3))}",
             "y": "{630+170*(i//3)}", "w": 464, "h": 60,
             "size": 20, "color": "muted"},
        ]},
    ],
    "framework_sipoc": [
        # SIPOC 横向五列：列头文字降级省略（声明式无字面量文本组件），
        # 以金色顶条＋纵分隔线示意五列；每列条目纵向堆叠
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "矩形", "x": 120, "y": 360, "w": 312, "h": 10, "fill": "gold"},
        {"组件": "矩形", "x": 456, "y": 360, "w": 312, "h": 10, "fill": "gold"},
        {"组件": "矩形", "x": 792, "y": 360, "w": 312, "h": 10, "fill": "gold"},
        {"组件": "矩形", "x": 1128, "y": 360, "w": 312, "h": 10, "fill": "gold"},
        {"组件": "矩形", "x": 1464, "y": 360, "w": 312, "h": 10, "fill": "gold"},
        {"组件": "线条", "x1": 444, "y1": 360, "x2": 444, "y2": 960, "color": "line", "w": 1},
        {"组件": "线条", "x1": 780, "y1": 360, "x2": 780, "y2": 960, "color": "line", "w": 1},
        {"组件": "线条", "x1": 1116, "y1": 360, "x2": 1116, "y2": 960, "color": "line", "w": 1},
        {"组件": "线条", "x1": 1452, "y1": 360, "x2": 1452, "y2": 960, "color": "line", "w": 1},
        {"组件": "循环", "字段": "suppliers", "模板": [
            {"组件": "文本", "字段": "{it}", "x": 120, "y": "{400+64*i}", "w": 312, "h": 60,
             "size": 22, "color": "ink"},
        ]},
        {"组件": "循环", "字段": "inputs", "模板": [
            {"组件": "文本", "字段": "{it}", "x": 456, "y": "{400+64*i}", "w": 312, "h": 60,
             "size": 22, "color": "ink"},
        ]},
        {"组件": "循环", "字段": "process", "模板": [
            {"组件": "文本", "字段": "{it}", "x": 792, "y": "{400+64*i}", "w": 312, "h": 60,
             "size": 22, "color": "ink"},
        ]},
        {"组件": "循环", "字段": "outputs", "模板": [
            {"组件": "文本", "字段": "{it}", "x": 1128, "y": "{400+64*i}", "w": 312, "h": 60,
             "size": 22, "color": "ink"},
        ]},
        {"组件": "循环", "字段": "customers", "模板": [
            {"组件": "文本", "字段": "{it}", "x": 1464, "y": "{400+64*i}", "w": 312, "h": 60,
             "size": 22, "color": "ink"},
        ]},
    ],
    "closing_qa": [
        # 致谢＋问答：thanks 大字居中；contact 醒目；takeaway 金句条（选填）；
        # seeds 种子问题列表（选填）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "thanks", "x": 120, "y": 380, "w": 1680, "h": 130,
         "size": 64, "color": "ink", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "contact", "x": 560, "y": 530, "w": 800, "h": 60,
         "size": 28, "color": "gold", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "takeaway", "x": 360, "y": 620, "w": 1200, "h": 80,
         "size": 26, "color": "ink", "align": "center"},
        {"组件": "循环", "字段": "seeds", "模板": [
            {"组件": "文本", "字段": "{it}", "x": 460, "y": "{740+60*i}", "w": 1000, "h": 56,
             "size": 22, "color": "muted", "align": "center"},
        ]},
    ],
    # ---- 结束页3（草案 2026-10-06） ----
    "closing_takeaway": [
        # 回顾锚点：takeaway 超大字居中；thanks 小字（选填）；contact（选填）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "takeaway", "x": 220, "y": 400, "w": 1480, "h": 200,
         "size": 54, "color": "ink", "bold": True, "align": "center"},
        {"组件": "文本", "字段": "thanks", "x": 460, "y": 640, "w": 1000, "h": 50,
         "size": 24, "color": "muted", "align": "center"},
        {"组件": "文本", "字段": "contact", "x": 460, "y": 700, "w": 1000, "h": 50,
         "size": 26, "color": "gold", "bold": True, "align": "center"},
    ],
    "closing_cta": [
        # 行动收尾·决策型：decision 断言大字；points 3 点摘要（金点）；
        # ask 强调框；bliss（选填，new bliss 一句）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "decision", "x": 120, "y": 330, "w": 1680, "h": 120,
         "size": 44, "color": "ink", "bold": True},
        {"组件": "循环", "字段": "points", "模板": [
            {"组件": "矩形", "x": 120, "y": "{494+64*i}", "w": 14, "h": 14, "fill": "gold"},
            {"组件": "文本", "字段": "{it}", "x": 150, "y": "{480+64*i}", "w": 1650, "h": 60,
             "size": 24, "color": "ink"},
        ]},
        {"组件": "矩形", "x": 120, "y": 700, "w": 1680, "h": 90, "fill": "card"},
        {"组件": "文本", "字段": "ask", "x": 160, "y": 712, "w": 1600, "h": 66,
         "size": 26, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "bliss", "x": 120, "y": 820, "w": 1680, "h": 60,
         "size": 22, "color": "muted", "align": "center"},
    ],
    "closing_appendix": [
        # 转附录：title；note 过渡语（选填）；items 附录条目（标题＋说明）；
        # A1/A2 编号徽在 PPTX 降级省略（字段表达式不支持 "A{i+1}" 字面量拼接）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "title", "x": 120, "y": 330, "w": 1680, "h": 90,
         "size": 54, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "note", "x": 120, "y": 430, "w": 1680, "h": 60,
         "size": 24, "color": "muted"},
        {"组件": "循环", "字段": "items", "模板": [
            {"组件": "文本", "字段": "{it.t}", "x": 200, "y": "{520+72*i}", "w": 1600, "h": 44,
             "size": 26, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.d}", "x": 200, "y": "{566+72*i}", "w": 1600, "h": 40,
             "size": 22, "color": "muted"},
        ]},
    ],
    # ---- 补缺4（草案 2026-10-06） ----
    "org_chart": [
        # 组织架构树：PPTX 降级为层级缩进行（tiers 每层 ｜ 连接，层间缩进递增）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "tiers", "模板": [
            {"组件": "文本", "字段": "{it}", "x": "{120+80*i}", "y": "{380+110*i}", "w": 1600, "h": 90,
             "size": 26, "color": "ink", "bold": True},
        ]},
    ],
    "venn": [
        # 交集图：圆无椭圆组件，PPTX 降级为集合列表＋交集区说明
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "sets", "模板": [
            {"组件": "矩形", "x": 120, "y": "{380+80*i}", "w": 14, "h": 14, "fill": "gold"},
            {"组件": "文本", "字段": "{it.label}", "x": 150, "y": "{366+80*i}", "w": 800, "h": 60,
             "size": 28, "color": "ink", "bold": True},
        ]},
        {"组件": "循环", "字段": "zones", "模板": [
            {"组件": "文本", "字段": "{it.label}", "x": 120, "y": "{660+72*i}", "w": 300, "h": 60,
             "size": 24, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.d}", "x": 440, "y": "{660+72*i}", "w": 1360, "h": 60,
             "size": 24, "color": "ink"},
        ]},
    ],
    "team_grid": [
        # 人物介绍：肖像圆形降级为方形裁切；姓名＋职位＋一句话
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "members", "模板": [
            {"组件": "图片", "字段": "{it.photo}", "x": "{140+440*i}", "y": 380, "w": 360, "h": 360,
             "fit": "cover"},
            {"组件": "文本", "字段": "{it.name}", "x": "{140+440*i}", "y": 760, "w": 360, "h": 50,
             "size": 26, "color": "ink", "bold": True, "align": "center"},
            {"组件": "文本", "字段": "{it.role}", "x": "{140+440*i}", "y": 812, "w": 360, "h": 44,
             "size": 22, "color": "gold", "align": "center"},
            {"组件": "文本", "字段": "{it.bio}", "x": "{140+440*i}", "y": 860, "w": 360, "h": 80,
             "size": 20, "color": "muted", "align": "center"},
        ]},
    ],
    "flow_vertical": [
        # 纵向步骤：rail＋编号节点降级为编号列表
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "steps", "模板": [
            {"组件": "文本", "字段": "{it.t}", "x": 200, "y": "{380+120*i}", "w": 1600, "h": 50,
             "size": 26, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.d}", "x": 200, "y": "{432+120*i}", "w": 1600, "h": 60,
             "size": 22, "color": "muted"},
        ]},
    ],
    # ---- 对比族 5 ----
    "compare_vs": [
        # 镜像双栏 VS：左右要点逐条平行对位（金点＋文本）；中央竖分隔线
        #（"VS"字样降级省略）；verdict 底部条（选填）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "a_title", "x": 120, "y": 340, "w": 760, "h": 60,
         "size": 30, "color": "ink", "bold": True},
        {"组件": "文本", "字段": "b_title", "x": 1040, "y": 340, "w": 760, "h": 60,
         "size": 30, "color": "ink", "bold": True, "align": "right"},
        {"组件": "线条", "x1": 960, "y1": 340, "x2": 960, "y2": 820, "color": "gold", "w": 2},
        {"组件": "循环", "字段": "a_points", "模板": [
            {"组件": "矩形", "x": 120, "y": "{434+64*i}", "w": 14, "h": 14, "fill": "gold"},
            {"组件": "文本", "字段": "{it}", "x": 150, "y": "{420+64*i}", "w": 730, "h": 60,
             "size": 24, "color": "ink"},
        ]},
        {"组件": "循环", "字段": "b_points", "模板": [
            {"组件": "文本", "字段": "{it}", "x": 990, "y": "{420+64*i}", "w": 730, "h": 60,
             "size": 24, "color": "ink", "align": "right"},
            {"组件": "矩形", "x": 1736, "y": "{434+64*i}", "w": 14, "h": 14, "fill": "gold"},
        ]},
        {"组件": "结论条", "字段": "verdict", "x": 120, "y": 850, "w": 1680},
    ],
    "compare_beforeafter": [
        # 前后对比：左右分屏卡；before 灰调弱化（muted 标题＋灰点）/after 品牌色标题＋金顶条；
        # 中央金色分隔线；delta 底部通栏
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "矩形", "x": 120, "y": 340, "w": 840, "h": 470, "fill": "card"},
        {"组件": "文本", "字段": "{before.t}", "x": 160, "y": 380, "w": 760, "h": 60,
         "size": 28, "color": "muted", "bold": True},
        {"组件": "循环", "字段": "{before.points}", "模板": [
            {"组件": "矩形", "x": 160, "y": "{474+58*i}", "w": 12, "h": 12, "fill": "muted"},
            {"组件": "文本", "字段": "{it}", "x": 188, "y": "{460+58*i}", "w": 732, "h": 54,
             "size": 22, "color": "muted"},
        ]},
        {"组件": "线条", "x1": 960, "y1": 340, "x2": 960, "y2": 810, "color": "gold", "w": 3},
        {"组件": "矩形", "x": 960, "y": 340, "w": 840, "h": 470, "fill": "card"},
        {"组件": "矩形", "x": 960, "y": 340, "w": 840, "h": 10, "fill": "gold"},
        {"组件": "文本", "字段": "{after.t}", "x": 1000, "y": 380, "w": 760, "h": 60,
         "size": 28, "color": "gold", "bold": True},
        {"组件": "循环", "字段": "{after.points}", "模板": [
            {"组件": "矩形", "x": 1000, "y": "{474+58*i}", "w": 12, "h": 12, "fill": "gold"},
            {"组件": "文本", "字段": "{it}", "x": 1028, "y": "{460+58*i}", "w": 732, "h": 54,
             "size": 22, "color": "ink"},
        ]},
        {"组件": "结论条", "字段": "delta", "x": 120, "y": 850, "w": 1680},
    ],
    "compare_proscons": [
        # 优劣清单：双栏；pros 绿点/cons 金点（✓✗ 字形降级）；topic 顶部主题；
        # verdict 底部推荐区
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "topic", "x": 120, "y": 330, "w": 1680, "h": 60,
         "size": 26, "color": "ink", "bold": True, "align": "center"},
        {"组件": "循环", "字段": "pros", "模板": [
            {"组件": "矩形", "x": 140, "y": "{434+64*i}", "w": 14, "h": 14, "fill": "green"},
            {"组件": "文本", "字段": "{it}", "x": 170, "y": "{420+64*i}", "w": 700, "h": 60,
             "size": 24, "color": "ink"},
        ]},
        {"组件": "线条", "x1": 960, "y1": 420, "x2": 960, "y2": 820, "color": "line", "w": 1},
        {"组件": "循环", "字段": "cons", "模板": [
            {"组件": "矩形", "x": 1050, "y": "{434+64*i}", "w": 14, "h": 14, "fill": "gold"},
            {"组件": "文本", "字段": "{it}", "x": 1080, "y": "{420+64*i}", "w": 700, "h": 60,
             "size": 24, "color": "ink"},
        ]},
        {"组件": "结论条", "字段": "verdict", "x": 120, "y": 850, "w": 1680},
    ],
    "matrix_2x2": [
        # 2×2 矩阵：四象限卡片网格（cover_collage 式网格算术）；轴标签降级为
        # 顶部 y_axis / 底部 x_axis 文字（无旋转）；quads>items 数组 ｜ 连接
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "y_axis", "x": 120, "y": 340, "w": 1680, "h": 44,
         "size": 20, "color": "muted"},
        {"组件": "循环", "字段": "quads", "模板": [
            {"组件": "矩形", "x": "{120+860*(i-2*(i//2))}", "y": "{400+230*(i//2)}",
             "w": 828, "h": 210, "fill": "card"},
            {"组件": "文本", "字段": "{it.n}", "x": "{160+860*(i-2*(i//2))}",
             "y": "{420+230*(i//2)}", "w": 748, "h": 50,
             "size": 26, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.d}", "x": "{160+860*(i-2*(i//2))}",
             "y": "{474+230*(i//2)}", "w": 748, "h": 50,
             "size": 20, "color": "muted"},
            {"组件": "文本", "字段": "{it.items}", "x": "{160+860*(i-2*(i//2))}",
             "y": "{528+230*(i//2)}", "w": 748, "h": 56,
             "size": 20, "color": "ink"},
        ]},
        {"组件": "文本", "字段": "x_axis", "x": 120, "y": 890, "w": 1680, "h": 44,
         "size": 20, "color": "muted", "align": "center"},
    ],
    "scorecard_decision": [
        # 决策记分卡：候选项行（名称＋评分条＋note）；score 非 0–100 数字时条宽归零、
        # 数值仍以文本呈现（优雅降级）；winner 高亮条
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "cands", "模板": [
            {"组件": "文本", "字段": "{it.name}", "x": 120, "y": "{376+110*i}", "w": 420, "h": 54,
             "size": 26, "color": "ink", "bold": True},
            {"组件": "矩形", "x": 580, "y": "{390+110*i}", "w": 620, "h": 26, "fill": "line"},
            {"组件": "矩形", "x": 580, "y": "{390+110*i}", "w": "{620*it.score/100}", "h": 26,
             "fill": "gold"},
            {"组件": "文本", "字段": "{it.score}", "x": 1220, "y": "{376+110*i}", "w": 160, "h": 54,
             "size": 24, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.note}", "x": 1400, "y": "{376+110*i}", "w": 400, "h": 96,
             "size": 20, "color": "muted"},
        ]},
        {"组件": "结论条", "字段": "winner", "x": 120, "y": 870, "w": 1680},
    ],
    # ---- 流程族 4 ----
    "flow_chevron": [
        # 箭形管道：chevron 多边形降级为矩形段（金顶条）＋间隙露出的金色基线作咬合连接
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "线条", "x1": 120, "y1": 570, "x2": 1800, "y2": 570, "color": "gold", "w": 4},
        {"组件": "循环", "字段": "steps", "模板": [
            {"组件": "矩形", "x": "{96+i*(1728/_n)}", "y": 420,
             "w": "{1728/_n-24}", "h": 300, "fill": "card"},
            {"组件": "矩形", "x": "{96+i*(1728/_n)}", "y": 420,
             "w": "{1728/_n-24}", "h": 12, "fill": "gold"},
            {"组件": "文本", "字段": "{it.t}", "x": "{136+i*(1728/_n)}", "y": 462,
             "w": "{1728/_n-104}", "h": 60, "size": 28, "color": "ink", "bold": True,
             "align": "center"},
            {"组件": "文本", "字段": "{it.d}", "x": "{136+i*(1728/_n)}", "y": 532,
             "w": "{1728/_n-104}", "h": 160, "size": 20, "color": "muted", "align": "center"},
        ]},
    ],
    "flow_swimlane": [
        # 泳道图：lane 横向条带（role 金字左列＋金条）；步骤盒＋跨道箭头降级为
        # ｜ 连接的行内文本（lanes>steps 数组）；note 选填（_n 定位）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "lanes", "模板": [
            {"组件": "矩形", "x": 120, "y": "{380+140*i}", "w": 1680, "h": 124, "fill": "card"},
            {"组件": "矩形", "x": 120, "y": "{380+140*i}", "w": 8, "h": 124, "fill": "gold"},
            {"组件": "文本", "字段": "{it.role}", "x": 152, "y": "{398+140*i}", "w": 230, "h": 88,
             "size": 24, "color": "gold", "bold": True},
            {"组件": "文本", "字段": "{it.steps}", "x": 400, "y": "{398+140*i}", "w": 1370, "h": 88,
             "size": 22, "color": "ink"},
        ]},
        {"组件": "文本", "字段": "note", "x": 120, "y": "{388+140*_n}", "w": 1680, "h": 44,
         "size": 18, "color": "muted"},
    ],
    "timeline_vertical": [
        # 纵向时间线：左侧 rail＋圆点（圆点降级为金色方块，先画文本→rail→圆点保证压住）；
        # 日期弱化＋标题加粗＋说明右列
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "循环", "字段": "nodes", "模板": [
            {"组件": "文本", "字段": "{it.t}", "x": 230, "y": "{370+76*i}", "w": 180, "h": 38,
             "size": 20, "color": "muted"},
            {"组件": "文本", "字段": "{it.h}", "x": 230, "y": "{404+76*i}", "w": 690, "h": 48,
             "size": 26, "color": "ink", "bold": True},
            {"组件": "文本", "字段": "{it.d}", "x": 950, "y": "{370+76*i}", "w": 850, "h": 80,
             "size": 20, "color": "muted"},
        ]},
        {"组件": "线条", "x1": 180, "y1": 380, "x2": 180, "y2": "{376+76*_n}",
         "color": "line", "w": 3},
        {"组件": "循环", "字段": "nodes", "模板": [
            {"组件": "矩形", "x": 168, "y": "{392+76*i}", "w": 24, "h": 24, "fill": "gold"},
        ]},
    ],
    "roadmap_swimlane": [
        # 泳道式路线图：甘特几何（bars 按 q0–q1 跨列、NOW 竖线、milestones）超出声明式框架能力，
        # 降级为文本结构 —— quarters 列头行（｜ 连接）＋ lane 分组行（name 左列金字）；
        # bars 任务条明细／now／milestones 以 HTML 预览为准，PPTX 侧省略
        #（嵌套循环无法做 lane×bar 二维定位，不硬画）
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "文本", "字段": "quarters", "x": 120, "y": 360, "w": 1680, "h": 50,
         "size": 24, "color": "gold", "bold": True},
        {"组件": "线条", "x1": 120, "y1": 424, "x2": 1800, "y2": 424, "color": "gold", "w": 2},
        {"组件": "循环", "字段": "lanes", "模板": [
            {"组件": "矩形", "x": 120, "y": "{460+96*i}", "w": 1680, "h": 76, "fill": "card"},
            {"组件": "矩形", "x": 120, "y": "{460+96*i}", "w": 8, "h": 76, "fill": "gold"},
            {"组件": "文本", "字段": "{it.name}", "x": 152, "y": "{472+96*i}", "w": 1628, "h": 52,
             "size": 26, "color": "ink", "bold": True},
        ]},
    ],
    # ---- 图文族 4 ----
    "case_psr": [
        # PSR 三段面板：上方主图＋cap；Problem（muted）→Solution（ink）→Results 卡
        #（k 指标＋before 小字＋after 金色大字；"→"字形降级省略）；timebox/quote 选填
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 120, "y": 340, "w": 1680, "h": 300, "fit": "cover"},
        {"组件": "文本", "字段": "cap", "x": 120, "y": 648, "w": 1680, "h": 36,
         "size": 18, "color": "muted"},
        {"组件": "文本", "字段": "problem", "x": 120, "y": 700, "w": 520, "h": 130,
         "size": 22, "color": "muted"},
        {"组件": "文本", "字段": "solution", "x": 680, "y": 700, "w": 520, "h": 130,
         "size": 22, "color": "ink"},
        {"组件": "循环", "字段": "results", "模板": [
            {"组件": "矩形", "x": "{1240+i*(560/_n)}", "y": 700,
             "w": "{560/_n-16}", "h": 160, "fill": "card"},
            {"组件": "文本", "字段": "{it.k}", "x": "{1264+i*(560/_n)}", "y": 716,
             "w": "{560/_n-64}", "h": 40, "size": 20, "color": "muted"},
            {"组件": "文本", "字段": "{it.before}", "x": "{1264+i*(560/_n)}", "y": 756,
             "w": "{560/_n-64}", "h": 36, "size": 20, "color": "muted"},
            {"组件": "文本", "字段": "{it.after}", "x": "{1264+i*(560/_n)}", "y": 792,
             "w": "{560/_n-64}", "h": 56, "size": 32, "color": "gold", "bold": True},
        ]},
        {"组件": "文本", "字段": "timebox", "x": 120, "y": 852, "w": 520, "h": 40,
         "size": 18, "color": "muted"},
        {"组件": "文本", "字段": "quote", "x": 680, "y": 852, "w": 1100, "h": 70,
         "size": 20, "color": "muted"},
    ],
    "case_arc": [
        # 转变弧：弧线几何降级为横向步骤卡；转折点高亮降级为统一金顶条
        #（HTML 端按语义高亮）；img 选填顶部横幅
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 120, "y": 340, "w": 1680, "h": 260, "fit": "cover"},
        {"组件": "循环", "字段": "stages", "模板": [
            {"组件": "矩形", "x": "{96+i*(1728/_n)}", "y": 640,
             "w": "{1728/_n-24}", "h": 300, "fill": "card"},
            {"组件": "矩形", "x": "{96+i*(1728/_n)}", "y": 640,
             "w": "{1728/_n-24}", "h": 10, "fill": "gold"},
            {"组件": "文本", "字段": "{it.k}", "x": "{136+i*(1728/_n)}", "y": 670,
             "w": "{1728/_n-104}", "h": 56, "size": 26, "color": "ink", "bold": True,
             "align": "center"},
            {"组件": "文本", "字段": "{it.d}", "x": "{136+i*(1728/_n)}", "y": 736,
             "w": "{1728/_n-104}", "h": 180, "size": 20, "color": "muted", "align": "center"},
        ]},
    ],
    "testimonial": [
        # 证言式：左肖像（圆形降级为方形裁切）＋右引文＋署名＋结果数字卡
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "photo", "x": 160, "y": 380, "w": 420, "h": 420, "fit": "cover"},
        {"组件": "文本", "字段": "quote", "x": 660, "y": 380, "w": 1140, "h": 220,
         "size": 30, "color": "ink"},
        {"组件": "文本", "字段": "name", "x": 660, "y": 620, "w": 1140, "h": 50,
         "size": 22, "color": "muted"},
        {"组件": "矩形", "x": 660, "y": 700, "w": 560, "h": 130, "fill": "card"},
        {"组件": "矩形", "x": 660, "y": 700, "w": 8, "h": 130, "fill": "gold"},
        {"组件": "文本", "字段": "result", "x": 700, "y": 716, "w": 500, "h": 100,
         "size": 28, "color": "gold", "bold": True},
    ],
    "problem_snapshot": [
        # 现状快照分屏：左现状图（灰调处理降级为原图呈现）＋右 pains 纵向列表
        {"组件": "底色"},
        {"组件": "页眉"}, {"组件": "页脚"},
        {"组件": "图片", "字段": "img", "x": 120, "y": 340, "w": 800, "h": 600, "fit": "cover"},
        {"组件": "文本", "字段": "cap", "x": 120, "y": 948, "w": 800, "h": 36,
         "size": 18, "color": "muted"},
        {"组件": "循环", "字段": "pains", "模板": [
            {"组件": "矩形", "x": 980, "y": "{392+140*i}", "w": 14, "h": 14, "fill": "gold"},
            {"组件": "文本", "字段": "{it}", "x": 1010, "y": "{378+140*i}", "w": 790, "h": 120,
             "size": 26, "color": "ink"},
        ]},
    ],

}
