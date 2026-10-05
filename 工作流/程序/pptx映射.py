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
    图片    {"组件":"图片","字段":"img","x":..,"y":..,"w":..,"h":..,"fit":"cover|contain"}
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
        E.pic_cover(slide, path, x, y, w, h)
    elif kind == "矩形":
        x, y, w, h = _xy(组件, ctx, "x", "y", "w", "h")
        E.rect(slide, x, y, w, h,
               fill=组件.get("fill"), line=组件.get("line"))
    elif kind == "线条":
        E.arrow_line(slide, 组件["x1"], 组件["y1"], 组件["x2"], 组件["y2"],
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
}
