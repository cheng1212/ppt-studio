# -*- coding: utf-8 -*-
"""page.py — SODIUM 课件页面生成器：页面=数据，布局=模板函数。

用法:
  python page.py                 # 按 pages.json 重新生成全部 HTML
  python page.py P4              # 只生成指定页 id
  python page.py --预览 草案.json [预览目录]
                                 # 布局预览：渲染草案数据到 页/_预览/，不碰 pages.json

布局模板（对应库内页型卡，共 32 种）:
  cover / cover_split / toc_grid / section / photo_props / photo_chain /
  table_compare / flow_branch / flow_cycle / timeline / cards3 / stepper /
  equation_hero / chart / kpi_hero / infographic / compare_bars / number_hero /
  cover_typo / cover_minimal / cover_block / cover_duo / cover_diagonal /
  cover_brand / cover_magazine / cover_lux / cover_collage / cover_crop /
  cover_anchor / cover_fusion / cover_band / cover_brush /
  statement_assertion / statement_dotdash / statement_golden / quote_full /
  quote_card / definition_dict / definition_terms / problem_pain /
  solution_pillars / solution_features / solution_how / checklist_tasks /
  scorecard_status / cta_single / cta_next / scr_brief / framework_hub /
  framework_sipoc / closing_qa / compare_vs / compare_beforeafter /
  compare_proscons / matrix_2x2 / scorecard_decision / flow_chevron /
  flow_swimlane / timeline_vertical / roadmap_swimlane / case_psr / case_arc /
  testimonial / problem_snapshot
"""
import io, json, os, sys
import html as _html
import re as _re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import FAIL, USAGE, read_json, die, project_dir, theme_css_path
from svg import fork as svg_fork, cycle as svg_cycle, timeline_axis

# 主题 CSS 内联（file:// 下中文目录外链 CSS 会被 Chromium 跨源拦截）。
# 主题可切换：环境变量 PPT_THEME_CSS（相对 库/），默认 theme-sodium.css。
# ——改主题 = 换 CSS 文件 + 换主题卡，不碰本程序（定案 D1）。
THEME = io.open(theme_css_path(), encoding="utf-8").read()
# 2026-10-06：主题名（去 theme- 前缀/.css 后缀），供 body th-<主题> 装饰门控
THEME_NAME = os.path.basename(theme_css_path())[len("theme-"):-len(".css")]

HEAD = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<style>
{theme}
</style>
<style>{extra}</style>
</head>
<body class="{bodycls}">
"""

# 背景系统：pages.json "bg" 字段 → body class（dots/grid/diagonal/mesh/glow）
_BG_OK = {"dots", "grid", "diagonal", "mesh", "glow"}
def _bgcls(p, bodycls=""):
    bg = p.get("bg")
    if bg in _BG_OK:
        return (bodycls + " bg-" + bg).strip()
    return bodycls


_MASK_OK = {"circle", "rounded", "blob", "arch"}
def _maskcls(p):
    """图片蒙版：pages.json "mask" → mask-<值> class，拼到图片容器。"""
    m = p.get("mask")
    return " mask-" + m if m in _MASK_OK else ""



def esc(s):
    """数据只写纯文本；转义由程序做，白名单行内标签放行。

    页型卡允许的行内标签：<span class="q">（标题半句标绿）、
    <b>（结论/提示标金）、<em>（要点标绿）、<sub>/<sup>（化学式上下标）。其他 <>& 原样转义。
    """
    e = _html.escape(s, quote=False)
    for tag in ("span", "b", "em", "sub", "sup"):
        e = _re.sub(r"&lt;(%s)(\s[^&<>]*)?&gt;" % tag, r"<\1\2>", e)
        e = e.replace("&lt;/%s&gt;" % tag, "</%s>" % tag)
    return e


def img(name):
    """素材图 → base64 data URI 内嵌（file:// 中文路径外链会被 Chromium 拦）；
    data:/http 开头的值直接透传（主题样张等场景用内联图）"""
    if not name:
        return "none"
    if name.startswith("data:") or name.startswith("http"):
        return "url(" + name + ")"
    import base64
    path = os.path.normpath(os.path.join(project_dir(), "素材", name))
    raw = open(path, "rb").read()
    return "url(data:image/png;base64," + base64.b64encode(raw).decode() + ")"


# ---------- 模板:封面 ----------
def _theme_bg_rgb():
    """从主题 CSS 解析 --bg 的 RGB，供封面罩按主题深浅自适应。"""
    m = _re.search(r"--bg:\s*#([0-9a-fA-F]{6})", THEME)
    h = m.group(1) if m else "F7F9F8"
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _theme_is_light():
    r, g, b = _theme_bg_rgb()
    return (0.2126*r + 0.7152*g + 0.0722*b) / 255 > 0.5


def t_cover(p):
    # 罩子按主题 --bg 深浅自适应：浅底主题用浅色雾面罩+深色字（与内页同语言），
    # 深底主题保持深色罩+浅色字（老项目渲染不变）。
    r, g, b = _theme_bg_rgb()
    if _theme_is_light():
        scrim = (f"linear-gradient(90deg, rgba({r},{g},{b},.97) 0%, rgba({r},{g},{b},.90) 36%,"
                 f"rgba({r},{g},{b},.45) 58%, rgba({r},{g},{b},0) 78%)")
        bodycls = ""
        eyebrow_c, sub_c, foot_c, na_c = "var(--gold)", "var(--muted)", "var(--muted)", "var(--gold)"
    else:
        scrim = ("linear-gradient(90deg, rgba(37,44,43,.95) 0%, rgba(37,44,43,.88) 36%,"
                 "rgba(37,44,43,.45) 58%, rgba(37,44,43,0) 78%)")
        bodycls = "dark"
        eyebrow_c, sub_c, foot_c, na_c = "var(--silver)", "var(--silver)", "var(--silver)", "var(--gold-soft)"
    extra = (
        "  .hero{position:absolute;inset:0;background:" + img(p["bg"]) + " center/cover no-repeat}\n"
        "  .scrim{position:absolute;inset:0;background:" + scrim + "}\n"
        "  .block{position:absolute;left:130px;top:340px;width:900px}\n"
        "  .eyebrow{font-family:Georgia,serif;font-size:var(--fs-cap);color:" + eyebrow_c + ";letter-spacing:.42em;text-transform:uppercase}\n"
        "  .block .gold-rule{margin:34px 0 44px}\n"
        "  h1{font-size:var(--fs-section-title);line-height:1.06;letter-spacing:.03em}\n"
        "  .en{margin-top:22px;font-family:Georgia,serif;font-size:var(--fs-body-n);color:var(--gold);letter-spacing:.16em}\n"
        "  .sub{margin-top:46px;font-size:var(--fs-body);color:" + sub_c + ";letter-spacing:.12em}\n"
        "  .na{position:absolute;right:130px;bottom:74px;font-family:Georgia,serif;font-size:var(--fs-cap);color:" + na_c + ";letter-spacing:.5em}\n"
        "  .footline2{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}\n"
        "  .footline2 .line{width:56px;height:2px;background:var(--gold)}\n"
        "  .footline2 span{font-size:var(--fs-cap);color:" + foot_c + ";letter-spacing:.28em}\n"
    )
    h = HEAD.format(theme=THEME, extra=extra, bodycls=bodycls)
    b = f"""  <div class="hero"></div><div class="scrim"></div>
  <div class="block">
    <div class="eyebrow">{esc(p['eyebrow'])}</div>
    <div class="gold-rule"></div>
    <h1>{esc(p['title'])}</h1>
    <div class="en">{esc(p['en'])}</div>
    <div class="sub">{esc(p['sub'])}</div>
  </div>
  <div class="footline2"><div class="line"></div><span>{esc(p['foot'])}</span></div>
  <div class="na">{esc(p.get('corner', ''))}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(左右分栏:左文右图 60/40) ----------
def t_cover_split(p):
    # 与 t_cover(满版图压字) 的区别：右图独立成栏，不用 scrim；
    # 分界 2px 金线；文字区走主题 --bg，与内页同语言。
    extra = """
  .cs-wrap{position:absolute;inset:0;display:flex}
  .cs-left{flex:0 0 60%;background:var(--bg);position:relative}
  .cs-right{flex:1;background:""" + img(p["img"]) + """ center/cover no-repeat;position:relative}
  .cs-div{position:absolute;left:60%;top:0;bottom:0;width:2px;background:var(--gold);z-index:2}
  .cs-block{position:absolute;left:130px;top:340px;width:760px}
  .cs-eyebrow{font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .cs-block .gold-rule{margin:34px 0 44px}
  .cs-block h1{font-size:var(--fs-section-title);line-height:1.06;letter-spacing:.03em;color:var(--ink)}
  .cs-en{margin-top:22px;font-family:Georgia,serif;font-size:var(--fs-body-n);color:var(--gold);letter-spacing:.16em}
  .cs-sub{margin-top:46px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.12em}
  .cs-foot{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .cs-foot .line{width:56px;height:2px;background:var(--gold)}
  .cs-foot span{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
  .cs-na{position:absolute;right:70px;bottom:74px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em;margin-right:-.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = f"""  <div class="cs-wrap">
    <div class="cs-left">
      <div class="cs-block">
        <div class="cs-eyebrow">{esc(p['eyebrow'])}</div>
        <div class="gold-rule"></div>
        <h1>{esc(p['title'])}</h1>
        <div class="cs-en">{esc(p['en'])}</div>
        <div class="cs-sub">{esc(p['sub'])}</div>
      </div>
      <div class="cs-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
    </div>
    <div class="cs-right"></div>
    <div class="cs-div"></div>
  </div>
  <div class="cs-na">{esc(p.get('corner', ''))}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录(2×2 带图卡) ----------
def t_toc_grid(p):
    extra = """
  .hd{position:absolute;left:var(--mx);top:118px}
  .hd h1{font-size:var(--fs-page-title);letter-spacing:.1em}
  .hd .sub{margin-top:14px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.06em}
  .hd .en{margin-top:10px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .grid{position:absolute;left:var(--mx);top:352px;width:var(--cw);height:620px;
        display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:26px}
  .cell{background:var(--card);display:flex;overflow:hidden}
  .ph{width:300px;height:100%;flex:none;background-position:center;background-size:cover}
  .ph.contain{background-size:contain;background-repeat:no-repeat;background-color:var(--bg-dark)}
  .ct{padding:30px 34px;display:flex;flex-direction:column;justify-content:center}
  .eb{font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.26em;font-weight:700}
  .zh{margin-top:10px;font-size:var(--fs-body);color:var(--green);font-weight:800;letter-spacing:.06em}
  .desc{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.05em;line-height:1.7}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cells = ""
    for c in p["cards"]:
        contain = " contain" if c.get("contain") else ""
        cells += f"""    <div class="cell">
      <div class="ph{contain}" style="background-image:{img(c['img'])}"></div>
      <div class="ct"><div class="eb">{esc(c['no'])}</div>
        <div class="zh">{esc(c['zh'])}</div>
        <div class="desc">{esc(c['desc'])}</div></div>
    </div>\n"""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="hd"><h1>{esc(p['title'])}</h1>
    <div class="sub">{esc(p['sub'])}</div>
    <div class="en">{esc(p['en'])}</div></div>
  <div class="grid">
{cells}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录-数字列表式 ----------
def t_toc_list(p):
    extra = """
  .hd{position:absolute;left:var(--mx);top:118px}
  .hd h1{font-size:var(--fs-page-title);letter-spacing:.1em}
  .hd .sub{margin-top:14px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.06em}
  .hd .en{margin-top:10px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .rows{position:absolute;left:var(--mx);top:372px;width:var(--cw)}
  .row{display:flex;align-items:center;gap:36px;padding:24px 8px;border-bottom:1px solid var(--gold-soft)}
  .row:last-child{border-bottom:none}
  .no{font-size:var(--fs-page-title);font-weight:800;color:var(--gold);min-width:130px;letter-spacing:.05em;line-height:1}
  .zh{font-size:var(--fs-body);font-weight:800;color:var(--ink);min-width:300px;letter-spacing:.06em}
  .desc{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.05em}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for it in p["items"]:
        rows += f"""    <div class="row"><div class="no">{esc(it['no'])}</div>
      <div class="zh">{esc(it['zh'])}</div>
      <div class="desc">{esc(it['desc'])}</div></div>\n"""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="hd"><h1>{esc(p['title'])}</h1>
    <div class="sub">{esc(p['sub'])}</div>
    <div class="en">{esc(p['en'])}</div></div>
  <div class="rows">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录-大字数字式 ----------
def t_toc_bignum(p):
    extra = """
  .hd{position:absolute;left:var(--mx);top:118px}
  .hd h1{font-size:var(--fs-page-title);letter-spacing:.1em}
  .hd .sub{margin-top:14px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.06em}
  .hd .en{margin-top:10px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .rows{position:absolute;left:var(--mx);top:360px;width:var(--cw)}
  .row{position:relative;min-height:150px;padding:30px 0 30px 300px}
  .no{position:absolute;left:0;top:50%;transform:translateY(-50%);font-size:var(--fs-hero);
      font-weight:900;color:var(--gold);opacity:.16;line-height:1;letter-spacing:0}
  .zh{font-size:var(--fs-body-n);font-weight:800;color:var(--ink);letter-spacing:.08em}
  .desc{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.05em}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for it in p["items"]:
        rows += f"""    <div class="row"><div class="no">{esc(it['no'])}</div>
      <div class="zh">{esc(it['zh'])}</div>
      <div class="desc">{esc(it['desc'])}</div></div>\n"""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="hd"><h1>{esc(p['title'])}</h1>
    <div class="sub">{esc(p['sub'])}</div>
    <div class="en">{esc(p['en'])}</div></div>
  <div class="rows">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录-左右分栏式 ----------
def t_toc_split(p):
    extra = """
  .left{position:absolute;left:var(--mx);top:330px;width:520px;bottom:130px;
        background:var(--card);padding:60px 52px}
  .left .vbar{width:6px;height:110px;background:var(--gold);margin-bottom:34px}
  .left .kick{font-size:var(--fs-desc);letter-spacing:.42em;color:var(--gold);font-weight:700}
  .left h2{margin-top:22px;font-size:var(--fs-page-title);font-weight:900;letter-spacing:.1em;color:var(--ink)}
  .left .en{margin-top:16px;font-family:Georgia,serif;font-size:var(--fs-cap);
            color:var(--gold);letter-spacing:.3em;text-transform:uppercase}
  .left .sub{margin-top:26px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.06em;line-height:1.9}
  .right{position:absolute;left:760px;top:356px;width:1040px}
  .row{display:flex;align-items:center;gap:30px;padding:26px 8px;border-bottom:1px solid var(--gold-soft)}
  .row:last-child{border-bottom:none}
  .no{font-size:var(--fs-page-title);font-weight:800;color:var(--gold);min-width:104px;letter-spacing:.04em;line-height:1}
  .zh{font-size:var(--fs-body);font-weight:800;color:var(--ink);min-width:230px;letter-spacing:.06em}
  .desc{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.05em}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for it in p["items"]:
        rows += f"""    <div class="row"><div class="no">{esc(it['no'])}</div>
      <div class="zh">{esc(it['zh'])}</div>
      <div class="desc">{esc(it['desc'])}</div></div>\n"""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="left"><div class="vbar"></div>
    <div class="kick">目录</div>
    <h2>{esc(p['title'])}</h2>
    <div class="en">{esc(p['en'])}</div>
    <div class="sub">{esc(p['sub'])}</div></div>
  <div class="right">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录-上下分割式 ----------
def t_toc_tb(p):
    extra = """
  .banner{position:absolute;left:0;top:0;width:1920px;height:340px;background:var(--card)}
  .banner .in{position:absolute;left:var(--mx);top:128px}
  .banner h1{font-size:var(--fs-page-title);letter-spacing:.12em;color:var(--ink)}
  .banner .en{margin-top:14px;font-family:Georgia,serif;font-size:var(--fs-cap);
              color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .banner .sub{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.08em}
  .cols{position:absolute;left:var(--mx);top:436px;width:var(--cw);display:flex}
  .col{flex:1;padding:6px 40px;border-left:1px solid var(--gold-soft)}
  .col:first-child{border-left:none;padding-left:0}
  .col .no{font-size:var(--fs-page-title);font-weight:800;color:var(--gold);letter-spacing:.04em;line-height:1}
  .col .zh{margin-top:18px;font-size:var(--fs-body);font-weight:800;color:var(--ink);letter-spacing:.06em}
  .col .desc{margin-top:14px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.05em;line-height:1.8}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cols = ""
    for it in p["items"]:
        cols += f"""    <div class="col"><div class="no">{esc(it['no'])}</div>
      <div class="zh">{esc(it['zh'])}</div>
      <div class="desc">{esc(it['desc'])}</div></div>\n"""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="banner"><div class="in"><h1>{esc(p['title'])}</h1>
    <div class="en">{esc(p['en'])}</div>
    <div class="sub">{esc(p['sub'])}</div></div></div>
  <div class="cols">
{cols}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录-横向条带式 ----------
def t_toc_tabs(p):
    extra = """
  .hd{position:absolute;left:var(--mx);top:118px}
  .hd h1{font-size:var(--fs-page-title);letter-spacing:.1em}
  .hd .sub{margin-top:14px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.06em}
  .hd .en{margin-top:10px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .rows{position:absolute;left:var(--mx);top:396px;width:var(--cw)}
  .strip{display:flex;align-items:center;gap:30px;background:var(--card);
         border-left:8px solid var(--gold);padding:0 40px;height:104px;margin-bottom:26px}
  .strip .badge{width:56px;height:56px;border-radius:50%;font-size:var(--fs-desc);flex:none}
  .strip .zh{font-size:var(--fs-body);font-weight:800;color:var(--ink);letter-spacing:.1em}
  .strip .desc{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.05em}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for i, it in enumerate(p["items"]):
        desc = f'<div class="desc">{esc(it["desc"])}</div>' if it.get("desc") else ""
        rows += (f"""    <div class="strip" style="margin-left:{i * 90}px">"""
                 f"""<span class="badge gold">{esc(it['no'])}</span>"""
                 f"""<div class="zh">{esc(it['zh'])}</div>{desc}</div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="hd"><h1>{esc(p['title'])}</h1>
    <div class="sub">{esc(p['sub'])}</div>
    <div class="en">{esc(p['en'])}</div></div>
  <div class="rows">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录-图标式 ----------
def t_toc_icon(p):
    from 图标 import icon as _icon
    extra = """
  .hd{position:absolute;left:var(--mx);top:118px}
  .hd h1{font-size:var(--fs-page-title);letter-spacing:.1em}
  .hd .sub{margin-top:14px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.06em}
  .hd .en{margin-top:10px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .grid{position:absolute;left:var(--mx);top:400px;width:var(--cw);
        display:grid;grid-template-columns:repeat(4,1fr);gap:26px}
  .cell{background:var(--card);padding:44px 30px;text-align:center}
  .cell .ic{margin-bottom:18px}
  .cell .ic svg{width:56px;height:56px}
  .cell .no{font-family:Georgia,serif;font-size:var(--fs-desc);color:var(--gold);letter-spacing:.3em;font-weight:700}
  .cell .zh{margin-top:14px;font-size:var(--fs-body-n);font-weight:800;color:var(--ink);letter-spacing:.08em}
  .cell .desc{margin-top:14px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.05em;line-height:1.8}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cells = ""
    for it in p["items"]:
        cells += (f"""    <div class="cell"><div class="ic">{_icon(it['icon'], 56)}</div>"""
                  f"""<div class="no">{esc(it['no'])}</div>"""
                  f"""<div class="zh">{esc(it['zh'])}</div>"""
                  f"""<div class="desc">{esc(it['desc'])}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="hd"><h1>{esc(p['title'])}</h1>
    <div class="sub">{esc(p['sub'])}</div>
    <div class="en">{esc(p['en'])}</div></div>
  <div class="grid">
{cells}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录-图片驱动式 ----------
def t_toc_image(p):
    extra = """
  .bg{position:absolute;inset:0;background-size:cover;background-position:center}
  .mask{position:absolute;inset:0;
        background:linear-gradient(90deg,var(--bg) 30%,transparent 75%);
        background:linear-gradient(90deg,var(--bg) 28%,color-mix(in srgb,var(--bg) 70%,transparent) 48%,transparent 78%)}
  .hd{position:absolute;left:var(--mx);top:118px}
  .hd h1{font-size:var(--fs-page-title);letter-spacing:.1em}
  .hd .sub{margin-top:14px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.06em}
  .hd .en{margin-top:10px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .rows{position:absolute;left:var(--mx);top:392px;width:880px}
  .row{display:flex;align-items:center;gap:30px;padding:22px 8px;border-bottom:1px solid var(--gold-soft)}
  .row:last-child{border-bottom:none}
  .no{font-size:var(--fs-page-title);font-weight:800;color:var(--gold);min-width:110px;letter-spacing:.04em;line-height:1}
  .zh{font-size:var(--fs-body);font-weight:800;color:var(--ink);min-width:220px;letter-spacing:.06em}
  .desc{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.05em}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for it in p["items"]:
        desc = f'<div class="desc">{esc(it["desc"])}</div>' if it.get("desc") else ""
        rows += f"""    <div class="row"><div class="no">{esc(it['no'])}</div>
      <div class="zh">{esc(it['zh'])}</div>{desc}</div>\n"""
    b = f"""  <div class="bg" style="background-image:{img(p['img'])}"></div>
  <div class="mask"></div>
  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="hd"><h1>{esc(p['title'])}</h1>
    <div class="sub">{esc(p['sub'])}</div>
    <div class="en">{esc(p['en'])}</div></div>
  <div class="rows">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录-路线图/进度式 ----------
def t_toc_roadmap(p):
    items = p["items"]
    n = len(items)
    cur = min(max(int(p["current"]), 1), n)
    pct = round((cur - 1) / (n - 1) * 100, 1) if n > 1 else 100
    extra = """
  .hd{position:absolute;left:var(--mx);top:118px}
  .hd h1{font-size:var(--fs-page-title);letter-spacing:.1em}
  .hd .sub{margin-top:14px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.06em}
  .hd .en{margin-top:10px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .rail{position:absolute;left:var(--mx);top:477px;width:var(--cw);height:6px;background:var(--gold-soft)}
  .rail .fill{position:absolute;left:0;top:0;bottom:0;background:var(--gold)}
  .nodes{position:absolute;left:var(--mx);top:444px;width:var(--cw);display:flex}
  .node{flex:1;text-align:center}
  .dot{width:72px;height:72px;border-radius:50%;margin:0 auto;display:flex;align-items:center;
       justify-content:center;font-size:var(--fs-body);font-weight:800;letter-spacing:.02em}
  .dot.done{background:var(--card);color:var(--muted);border:2px solid var(--gold-soft)}
  .dot.cur{background:var(--gold);color:var(--bg);box-shadow:0 0 0 10px color-mix(in srgb,var(--gold) 22%,transparent)}
  .dot.todo{background:transparent;color:var(--muted);border:2px solid var(--gold-soft)}
  .node .zh{margin-top:26px;font-size:var(--fs-body);font-weight:800;color:var(--ink);letter-spacing:.08em}
  .node.cur .zh{color:var(--gold)}
  .node .desc{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.05em;line-height:1.8;padding:0 18px}
  .prog{position:absolute;left:var(--mx);top:400px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.24em}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    nodes = ""
    for i, it in enumerate(items):
        idx = i + 1
        if idx < cur:
            cls, mark = "done", "✓"
        elif idx == cur:
            cls, mark = "cur", esc(it["no"])
        else:
            cls, mark = "todo", esc(it["no"])
        desc = f'<div class="desc">{esc(it["desc"])}</div>' if it.get("desc") else ""
        nodes += (f"""    <div class="node {cls}"><div class="dot {cls}">{mark}</div>"""
                  f"""<div class="zh">{esc(it['zh'])}</div>{desc}</div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="hd"><h1>{esc(p['title'])}</h1>
    <div class="sub">{esc(p['sub'])}</div>
    <div class="en">{esc(p['en'])}</div></div>
  <div class="prog">PROGRESS&nbsp;&nbsp;{cur} / {n}</div>
  <div class="rail"><div class="fill" style="width:{pct}%"></div></div>
  <div class="nodes">
{nodes}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录-杂志索引式 ----------
def t_toc_magazine(p):
    extra = """
  .hd{position:absolute;left:var(--mx);top:118px}
  .hd h1{font-size:var(--fs-page-title);letter-spacing:.1em}
  .hd .sub{margin-top:14px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.06em}
  .hd .en{margin-top:10px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .rows{position:absolute;left:var(--mx);top:384px;width:var(--cw)}
  .row{margin-bottom:40px}
  .line1{display:flex;align-items:baseline;gap:20px}
  .zh{font-size:var(--fs-body-n);font-weight:800;color:var(--ink);letter-spacing:.06em;white-space:nowrap}
  .leader{flex:1;border-bottom:3px dotted var(--gold-soft);height:10px;min-width:60px}
  .no{font-family:Georgia,serif;font-size:var(--fs-body);color:var(--gold);font-weight:700;white-space:nowrap}
  .desc{margin-top:10px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.05em}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for it in p["items"]:
        desc = f'<div class="desc">{esc(it["desc"])}</div>' if it.get("desc") else ""
        rows += f"""    <div class="row"><div class="line1"><div class="zh">{esc(it['zh'])}</div>
        <div class="leader"></div><div class="no">{esc(it['no'])}</div></div>{desc}</div>\n"""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="hd"><h1>{esc(p['title'])}</h1>
    <div class="sub">{esc(p['sub'])}</div>
    <div class="en">{esc(p['en'])}</div></div>
  <div class="rows">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录-曲线路径式 ----------
def t_toc_curve(p):
    # S 形贝塞尔曲线：P0(840,20) C1(1300,120) C2(380,480) P3(840,580)，节点按 t 等距取点
    p0 = (840.0, 20.0); c1 = (1300.0, 120.0); c2 = (380.0, 480.0); p3 = (840.0, 580.0)

    def bez(t):
        u = 1 - t
        x = u**3 * p0[0] + 3 * u**2 * t * c1[0] + 3 * u * t**2 * c2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u**2 * t * c1[1] + 3 * u * t**2 * c2[1] + t**3 * p3[1]
        return x, y

    items = p["items"]
    n = len(items)
    extra = """
  .hd{position:absolute;left:var(--mx);top:118px}
  .hd h1{font-size:var(--fs-page-title);letter-spacing:.1em}
  .hd .sub{margin-top:14px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.06em}
  .hd .en{margin-top:10px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .stage{position:absolute;left:var(--mx);top:356px;width:var(--cw);height:600px}
  .stage svg{position:absolute;inset:0;width:100%;height:100%}
  .nd{position:absolute;transform:translate(-50%,-50%);width:64px;height:64px;border-radius:50%;
      background:var(--gold);color:var(--bg);display:flex;align-items:center;justify-content:center;
      font-size:var(--fs-body);font-weight:800}
  .tx{position:absolute;transform:translateY(-50%);width:470px}
  .tx.r{text-align:left}
  .tx.l{text-align:right}
  .tx .zh{font-size:var(--fs-body-n);font-weight:800;color:var(--ink);letter-spacing:.08em}
  .tx .desc{margin-top:10px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.05em;line-height:1.8}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    svg = ('<svg viewBox="0 0 1680 600" preserveAspectRatio="none">'
           '<path d="M 840 20 C 1300 120, 380 480, 840 580" fill="none" '
           'stroke="var(--gold)" stroke-width="3" opacity=".45"/></svg>')
    pts = ""
    for i, it in enumerate(items):
        x, y = bez((i + 0.5) / n)
        pts += (f"""    <div class="nd" style="left:{x:.0f}px;top:{y:.0f}px">{esc(it['no'])}</div>\n""")
        if i % 2 == 0:
            pts += (f"""    <div class="tx r" style="left:{x + 52:.0f}px;top:{y:.0f}px">"""
                    f"""<div class="zh">{esc(it['zh'])}</div>"""
                    f"""<div class="desc">{esc(it['desc'])}</div></div>\n""")
        else:
            pts += (f"""    <div class="tx l" style="left:{x - 52 - 470:.0f}px;top:{y:.0f}px">"""
                    f"""<div class="zh">{esc(it['zh'])}</div>"""
                    f"""<div class="desc">{esc(it['desc'])}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="hd"><h1>{esc(p['title'])}</h1>
    <div class="sub">{esc(p['sub'])}</div>
    <div class="en">{esc(p['en'])}</div></div>
  <div class="stage">{svg}
{pts}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:目录-极简文字式 ----------
def t_toc_minimal(p):
    extra = """
  .hd{position:absolute;left:var(--mx);top:118px}
  .hd h1{font-size:var(--fs-page-title);letter-spacing:.14em;color:var(--ink)}
  .hd .en{margin-top:12px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .hd .sub{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.08em}
  .items{position:absolute;left:var(--mx);top:360px;width:var(--cw)}
  .it{margin-bottom:54px}
  .it .n{display:block;font-size:var(--fs-desc);color:var(--gold);letter-spacing:.32em;margin-bottom:14px;font-weight:700}
  .it .zh{font-size:var(--fs-page-title);font-weight:800;color:var(--ink);letter-spacing:.1em;line-height:1.25}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    sub = f'<div class="sub">{esc(p["sub"])}</div>' if p.get("sub") else ""
    items = ""
    for it in p["items"]:
        n = f'<span class="n">{esc(it["no"])}</span>' if it.get("no") else ""
        items += f"""    <div class="it">{n}<div class="zh">{esc(it['zh'])}</div></div>\n"""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="hd"><h1>{esc(p['title'])}</h1>
    <div class="en">{esc(p['en'])}</div>{sub}</div>
  <div class="items">
{items}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页-全出血图片式 ----------
def t_section_image(p):
    extra = """
  .bg{position:absolute;inset:0;background-size:cover;background-position:center}
  .mask{position:absolute;inset:0;background:linear-gradient(180deg,transparent 34%,rgba(0,0,0,.66) 100%)}
  .brow,.pageno{text-shadow:0 1px 10px rgba(0,0,0,.5)}
  .brow{color:#fff;opacity:.85}
  .pageno{color:#fff;opacity:.6}
  .kick{position:absolute;left:var(--mx);bottom:410px;font-size:var(--fs-desc);letter-spacing:.42em;
        color:#fff;opacity:.8;font-weight:700}
  h1{position:absolute;left:var(--mx);bottom:300px;max-width:1400px;font-size:var(--fs-page-title);font-weight:900;
     color:#fff;letter-spacing:.06em;line-height:1.2;text-shadow:0 2px 18px rgba(0,0,0,.45)}
  .en{position:absolute;left:var(--mx);bottom:252px;font-family:Georgia,serif;font-size:var(--fs-cap);
      color:var(--gold);letter-spacing:.3em;text-transform:uppercase;text-shadow:0 1px 10px rgba(0,0,0,.5)}
  .sub{position:absolute;left:var(--mx);bottom:196px;max-width:1200px;font-size:var(--fs-desc);
       color:#fff;opacity:.82;letter-spacing:.06em}
  .foot-line{background:rgba(255,255,255,.25)}
  .foot-left{bottom:52px;color:rgba(255,255,255,.7)}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    sub = f'<div class="sub">{esc(p["sub"])}</div>' if p.get("sub") else ""
    b = f"""  <div class="bg" style="background-image:{img(p['img'])}"></div>
  <div class="mask"></div>
  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="kick">{esc(p['kick'])}</div>
  <h1>{esc(p['title'])}</h1>
  <div class="en">{esc(p['en'])}</div>
  {sub}
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页-左右分栏式 ----------
def t_section_split(p):
    extra = """
  .ph{position:absolute;left:0;top:0;width:864px;height:1080px;background-size:cover;background-position:center}
  .tx{position:absolute;left:864px;top:0;right:0;bottom:0;background:var(--card);padding:120px 110px}
  .tx .bar{width:6px;height:96px;background:var(--gold);margin:150px 0 40px}
  .tx .kick{font-size:var(--fs-desc);letter-spacing:.42em;color:var(--gold);font-weight:700}
  .tx h2{margin-top:24px;font-size:var(--fs-page-title);font-weight:900;color:var(--ink);letter-spacing:.08em;line-height:1.25}
  .tx .en{margin-top:18px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);
          letter-spacing:.3em;text-transform:uppercase}
  .tx .sub{margin-top:30px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.06em;line-height:1.9}
  .brow,.pageno{text-shadow:0 1px 10px rgba(0,0,0,.5)}
  .brow{color:#fff;opacity:.85}
  .pageno{color:#fff;opacity:.6}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = f"""  <div class="ph" style="background-image:{img(p['img'])}"></div>
  <div class="tx"><div class="bar"></div>
    <div class="kick">{esc(p['kick'])}</div>
    <h2>{esc(p['title'])}</h2>
    <div class="en">{esc(p['en'])}</div>
    <div class="sub">{esc(p['sub'])}</div></div>
  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页-极简留白式 ----------
def t_section_minimal(p):
    extra = """
  .mid{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);text-align:center;padding:0 240px}
  .mid .kick{font-size:var(--fs-desc);letter-spacing:.42em;color:var(--muted);font-weight:700}
  .mid h1{margin-top:30px;font-size:var(--fs-page-title);font-weight:900;color:var(--ink);letter-spacing:.1em;line-height:1.3}
  .mid .rule{width:64px;height:3px;background:var(--gold);margin:44px auto}
  .mid .en{font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .mid .sub{margin-top:22px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.08em}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    sub = f'<div class="sub">{esc(p["sub"])}</div>' if p.get("sub") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="mid">
    <div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1>
    <div class="rule"></div>
    <div class="en">{esc(p['en'])}</div>
    {sub}</div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页-深色强调条式 ----------
def t_section_accent(p):
    extra = """
  .bar{position:absolute;left:120px;top:110px;bottom:0;width:6px;background:var(--gold)}
  .kick{position:absolute;left:200px;top:330px;font-size:var(--fs-desc);letter-spacing:.42em;color:var(--gold);font-weight:700}
  .no{position:absolute;left:196px;top:380px;font-size:var(--fs-section-title);font-weight:900;color:var(--gold);line-height:1;letter-spacing:.02em}
  h1{position:absolute;left:200px;top:520px;font-size:var(--fs-page-title);font-weight:900;color:var(--ink-dark);letter-spacing:.08em}
  .en{position:absolute;left:200px;top:610px;font-family:Georgia,serif;font-size:var(--fs-cap);
      color:var(--gold);letter-spacing:.3em;text-transform:uppercase}
  .sub{position:absolute;left:200px;top:664px;font-size:var(--fs-cap);color:var(--silver);letter-spacing:.06em}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, "dark"))
    num = p.get("num") or p["kick"].split()[-1]
    sub = f'<div class="sub">{esc(p["sub"])}</div>' if p.get("sub") else ""
    b = f"""  <div class="bar"></div>
  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="kick">{esc(p['kick'])}</div>
  <div class="no">{esc(num)}</div>
  <h1>{esc(p['title'])}</h1>
  <div class="en">{esc(p['en'])}</div>
  {sub}
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页-图片横带式 ----------
def t_section_band(p):
    extra = """
  .hd{position:absolute;left:var(--mx);top:150px}
  .hd .kick{font-size:var(--fs-desc);letter-spacing:.42em;color:var(--gold);font-weight:700}
  .hd h1{margin-top:22px;font-size:var(--fs-page-title);font-weight:900;color:var(--ink);letter-spacing:.08em}
  .hd .en{margin-top:16px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);
          letter-spacing:.3em;text-transform:uppercase}
  .hd .sub{margin-top:18px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.06em}
  .band{position:absolute;left:0;right:0;top:560px;height:340px;background-size:cover;background-position:center;
        border-top:1px solid var(--gold-soft);border-bottom:1px solid var(--gold-soft)}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    sub = f'<div class="sub">{esc(p["sub"])}</div>' if p.get("sub") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="hd">
    <div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1>
    <div class="en">{esc(p['en'])}</div>
    {sub}</div>
  <div class="band" style="background-image:{img(p['img'])}"></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页-金句落锤式 ----------
def t_section_statement(p):
    extra = """
  .mid{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);text-align:center;padding:0 260px}
  .mid .kick{font-size:var(--fs-desc);letter-spacing:.42em;color:var(--gold);font-weight:700}
  .mid h1{margin-top:36px;font-size:var(--fs-page-title);font-weight:900;color:var(--ink);letter-spacing:.08em;line-height:1.4}
  .mid .sub{margin-top:30px;font-size:var(--fs-desc);color:var(--muted);letter-spacing:.06em}
  .corner{position:absolute;right:120px;bottom:120px;font-size:var(--fs-body);color:var(--gold);
          letter-spacing:.24em;font-weight:700}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="mid">
    <div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1>
    <div class="sub">{esc(p['sub'])}</div></div>
  <div class="corner">{esc(p['en'])}</div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页-进度指示式 ----------
def t_section_progress(p):
    items = p["items"]
    n = len(items)
    cur = min(max(int(p["current"]), 1), n)
    pct = round(cur / n * 100, 1)
    extra = """
  .mid{position:absolute;left:0;right:0;top:400px;text-align:center;padding:0 240px}
  .mid .kick{font-size:var(--fs-desc);letter-spacing:.42em;color:var(--gold);font-weight:700}
  .mid h1{margin-top:28px;font-size:var(--fs-page-title);font-weight:900;color:var(--ink);letter-spacing:.08em}
  .mid .en{margin-top:18px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);
           letter-spacing:.3em;text-transform:uppercase}
  .prog{margin:56px auto 0;width:760px}
  .prog .lbl{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.3em;margin-bottom:16px}
  .prog .rail{height:6px;background:var(--gold-soft);position:relative}
  .prog .rail .fill{position:absolute;left:0;top:0;bottom:0;background:var(--gold)}
  .seq{margin-top:44px;display:flex;justify-content:center;gap:44px}
  .seq .s{font-size:var(--fs-body);color:var(--muted);letter-spacing:.1em;font-weight:700}
  .seq .s.cur{color:var(--gold);font-size:var(--fs-body-n)}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    seq = ""
    for i, it in enumerate(items):
        cls = "cur" if i + 1 == cur else ""
        seq += f'<span class="s {cls}">{esc(it["no"])}</span>'
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="mid">
    <div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1>
    <div class="en">{esc(p['en'])}</div>
    <div class="prog">
      <div class="lbl">{cur} / {n}</div>
      <div class="rail"><div class="fill" style="width:{pct}%"></div></div>
    </div>
    <div class="seq">{seq}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页-撞色块式 ----------
def t_section_duo(p):
    extra = """
  .L{position:absolute;left:0;top:0;width:960px;bottom:0;background:var(--bg-dark)}
  .R{position:absolute;left:960px;top:0;right:0;bottom:0;background:var(--gold);overflow:hidden}
  .R .ghost{position:absolute;right:60px;top:50%;transform:translateY(-50%);font-size:var(--fs-hero);
            font-weight:900;color:var(--bg-dark);opacity:.16;line-height:1}
  .L .kick{position:absolute;left:120px;top:380px;font-size:var(--fs-desc);letter-spacing:.42em;color:var(--gold);font-weight:700}
  .L h1{position:absolute;left:120px;top:440px;font-size:var(--fs-page-title);font-weight:900;color:var(--ink-dark);letter-spacing:.08em}
  .L .en{position:absolute;left:120px;top:540px;font-family:Georgia,serif;font-size:var(--fs-cap);
         color:var(--gold);letter-spacing:.3em;text-transform:uppercase}
  .L .sub{position:absolute;left:120px;top:596px;max-width:640px;font-size:var(--fs-cap);
          color:var(--silver);letter-spacing:.06em;line-height:1.9}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, "dark"))
    num = p.get("num") or p["kick"].split()[-1]
    sub = f'<div class="sub">{esc(p["sub"])}</div>' if p.get("sub") else ""
    b = f"""  <div class="L">
    <div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1>
    <div class="en">{esc(p['en'])}</div>
    {sub}</div>
  <div class="R"><div class="ghost">{esc(num)}</div></div>
  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页-目录复用高亮式 ----------
def t_section_reuse(p):
    items = p["items"]
    n = len(items)
    cur = min(max(int(p["current"]), 1), n)
    extra = """
  .left{position:absolute;left:var(--mx);top:330px;width:620px}
  .left .kick{font-size:var(--fs-desc);letter-spacing:.42em;color:var(--gold);font-weight:700}
  .left h2{margin-top:24px;font-size:var(--fs-page-title);font-weight:900;color:var(--ink);letter-spacing:.08em;line-height:1.3}
  .left .en{margin-top:18px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);
            letter-spacing:.3em;text-transform:uppercase}
  .left .hint{margin-top:30px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.06em}
  .right{position:absolute;left:900px;top:350px;width:780px}
  .row{position:relative;display:flex;align-items:baseline;gap:28px;padding:20px 0 20px 28px}
  .row .bar{position:absolute;left:0;top:18px;bottom:18px;width:5px;background:transparent}
  .row.cur .bar{background:var(--gold)}
  .row .no{font-size:var(--fs-body-n);font-weight:800;color:var(--muted);min-width:70px;letter-spacing:.04em}
  .row.cur .no{color:var(--gold)}
  .row .zh{font-size:var(--fs-body-n);font-weight:700;color:var(--muted);letter-spacing:.06em}
  .row.cur .zh{color:var(--ink);font-weight:900}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for i, it in enumerate(items):
        cls = "cur" if i + 1 == cur else ""
        rows += (f"""    <div class="row {cls}"><div class="bar"></div>"""
                 f"""<div class="no">{esc(it['no'])}</div>"""
                 f"""<div class="zh">{esc(it['zh'])}</div></div>\n""")
    cur_it = items[cur - 1]
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="left">
    <div class="kick">{esc(p['kick'])}</div>
    <h2>{esc(p['title'])}</h2>
    <div class="en">{esc(p['en'])}</div>
    <div class="hint">当前：{esc(cur_it['zh'])}</div></div>
  <div class="right">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页-图标印章式 ----------
def t_section_icon(p):
    from 图标 import icon as _icon
    extra = """
  .mid{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);text-align:center}
  .mid .ic svg{width:120px;height:120px}
  .mid .kick{margin-top:30px;font-size:var(--fs-desc);letter-spacing:.42em;color:var(--gold);font-weight:700}
  .mid h1{margin-top:24px;font-size:var(--fs-page-title);font-weight:900;color:var(--ink);letter-spacing:.08em}
  .mid .en{margin-top:16px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);
           letter-spacing:.3em;text-transform:uppercase}
  .mid .sub{margin-top:20px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.06em}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    sub = f'<div class="sub">{esc(p["sub"])}</div>' if p.get("sub") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="mid">
    <div class="ic">{_icon(p['icon'], 120)}</div>
    <div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1>
    <div class="en">{esc(p['en'])}</div>
    {sub}</div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页-引导过渡式 ----------
def t_section_bridge(p):
    extra = """
  .mid{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);padding:0 200px}
  .mid .kick{font-size:var(--fs-desc);letter-spacing:.42em;color:var(--gold);font-weight:700}
  .mid .rule{width:72px;height:4px;background:var(--gold);margin:34px 0}
  .mid h1{font-size:var(--fs-page-title);font-weight:900;color:var(--ink-dark);letter-spacing:.06em;line-height:1.25}
  .mid .sub{margin-top:30px;font-size:var(--fs-body-n);color:var(--ink-dark);opacity:.9;letter-spacing:.06em}
  .mid .en{margin-top:20px;font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);
           letter-spacing:.3em;text-transform:uppercase}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, "dark"))
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="mid">
    <div class="kick">{esc(p['kick'])}</div>
    <div class="rule"></div>
    <h1>{esc(p['title'])}</h1>
    <div class="sub">{esc(p['sub'])}</div>
    <div class="en">{esc(p['en'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节页 ----------
def t_section(p):
    light = p.get("tone") == "light"  # 浅色章节页（A 方案）：米白底 + 浅青大数字
    extra = """
  .block{position:absolute;left:130px;top:400px;width:1000px}
  .eb{font-family:Georgia,serif;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.4em;text-transform:uppercase}
  .block .gold-rule{margin:36px 0 46px}
  h1{font-size:var(--fs-section-title);letter-spacing:.04em;line-height:1.15}
  .sub{margin-top:44px;font-size:var(--fs-body);color:var(--silver);letter-spacing:.1em;line-height:1.8}
  .footline2{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .footline2 .line{width:56px;height:2px;background:var(--gold)}
  .footline2 span{font-size:var(--fs-cap);color:var(--silver);letter-spacing:.28em;opacity:.8}
""" + ("""
  .ghost{color:var(--gold-soft);opacity:.32}
  .sub{color:var(--muted)}
  .footline2 span{color:var(--muted);opacity:1}
""" if light else "")
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, "") if light else "dark")
    sub_raw = p["sub"]
    subs = sub_raw if isinstance(sub_raw, list) else [sub_raw]
    sub = "<br>".join(esc(x) for x in subs)
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="ghost">{esc(p['ghost'])}</div>
  <div class="block">
    <div class="eb">{esc(p['eb'])}</div>
    <div class="gold-rule"></div>
    <h1>{esc(p['title'])}</h1>
    <div class="sub">{sub}</div>
  </div>
  <div class="footline2"><div class="line"></div><span>{esc(p['foot'])}</span></div>
</body>
</html>
"""
    return h + b


# ---------- 模板:图文性质页(左图右色块行+结论条) ----------
def t_photo_props(p):
    extra = """
  .photo{position:absolute;left:var(--mx);top:352px;width:760px;height:600px;
        background-size:contain;background-color:var(--card)}
  .cap{position:absolute;left:var(--mx);top:962px;width:760px}
  .props{position:absolute;left:952px;top:346px;width:848px}
  .prop{display:flex;align-items:center;padding:24px 0 22px}
  .badge{width:118px;height:52px;flex:none;margin-right:30px;font-size:var(--fs-cap)}
  .v{flex:1}
  .v .n{font-size:var(--fs-body-n);font-weight:700;letter-spacing:.03em;color:var(--ink)}
  .v .n em{font-style:normal;color:var(--green)}
  .v .d{margin-top:6px;font-size:var(--fs-cap);color:var(--muted);line-height:1.6}
  .concl{margin-top:26px}
  body.noimg .props{left:var(--mx);width:var(--cw)}
"""
    noimg = not p.get("img")
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, "noimg") if noimg else "")
    rows = ""
    for r in p["rows"]:
        rows += f"""    <div class="prop hairline"><div class="badge badge {r['b']}">{esc(r['k'])}</div>
      <div class="v"><div class="n">{esc(r['n'])}</div>
      <div class="d">{esc(r['d'])}</div></div></div>\n"""
    if p.get("img"):
        photo_props_img = f"""  <div class="photo photo{_maskcls(p)}" style="background-image:{img(p['img'])}">
    <div class="tag" style="position:absolute;left:24px;top:28px">{esc(p.get('tag',''))}</div>
  </div>"""
        photo_props_cap = f"""  <div class="cap cap" style="position:absolute">{esc(p.get('cap',''))}</div>"""
    else:
        photo_props_img = ""
        photo_props_cap = ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
{photo_props_img}
{photo_props_cap}
  <div class="props">
{rows}    <div class="concl concl">{esc(p['concl'])}</div>
  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:图文因果页(左图右编号链+提示框) ----------
def t_photo_chain(p):
    extra = """
  .photo{position:absolute;left:var(--mx);top:352px;width:760px;height:600px;
        background-size:contain;background-color:var(--card)}
  .cap{position:absolute;left:var(--mx);top:962px;width:760px}
  .chain{position:absolute;left:952px;top:368px;width:848px}
  .step{display:flex;gap:26px;align-items:flex-start}
  .st{flex:1}
  .st .t{font-size:var(--fs-body);color:var(--ink);font-weight:700}
  .st .d{margin-top:8px;font-size:var(--fs-body);color:var(--muted);line-height:1.7}
  .arrow{margin:14px 0 14px 14px;color:var(--gold);font-size:var(--fs-body-n);font-family:Georgia,serif;line-height:1}
  .warn{margin-top:36px;background:var(--card);border-left:6px solid var(--gold);
        padding:24px 30px;font-size:var(--fs-cap);color:var(--ink);line-height:1.8}
  .warn b{color:var(--green)}
  body.noimg .chain{left:var(--mx);width:var(--cw)}
"""
    noimg = not p.get("img")
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, "noimg") if noimg else "")
    steps = ""
    for i, s in enumerate(p["steps"]):
        steps += f"""    <div class="step"><div class="numdot">{i+1}</div>
      <div class="st"><div class="t">{esc(s['t'])}</div>
      <div class="d">{esc(s['d'])}</div></div></div>\n"""
        if i < len(p["steps"]) - 1:
            steps += '    <div class="arrow">↓</div>\n'
    if p.get("img"):
        photo_chain_img = f"""  <div class="photo photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
  <div class="cap cap" style="position:absolute">{esc(p.get('cap',''))}</div>"""
    else:
        photo_chain_img = ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
{photo_chain_img}
  <div class="chain">
{steps}    <div class="warn">{esc(p['warn'])}</div>
  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:对比表页(多对象横向对比+结论条) ----------
def t_table_compare(p):
    has_img = bool(p.get("img"))
    tw_w = "1080px" if has_img else "var(--cw)"
    fig_css = (".fig{position:absolute;right:var(--mx);top:352px;width:480px}"
               ".fig .photo{width:480px;height:270px;background-size:contain;background-color:var(--card)}"
               ".fig .cap{margin-top:14px}" if has_img else "")
    # 行数≤4：行距宽松 + 结论条沉底做"地基"；行数多时保持紧凑流式，避免与结论条重叠
    roomy = len(p["rows"]) <= 4
    td_pad = "30px 28px" if roomy else "20px 28px"
    concl_css = (".concl{position:absolute;left:var(--mx);right:var(--mx);bottom:110px}"
                 if roomy else ".concl{margin-top:30px}")
    extra = f"""
  .twrap{{position:absolute;left:var(--mx);top:352px;width:{tw_w}}}
  table{{width:100%;border-collapse:collapse}}
  th{{background:var(--green);color:var(--bg);font-size:var(--fs-body);font-weight:700;
     letter-spacing:.14em;padding:20px 28px;text-align:left}}
  td{{font-size:var(--fs-body);color:var(--ink);letter-spacing:.04em;line-height:1.6;
     padding:{td_pad};border-bottom:1px solid var(--line);vertical-align:top}}
  td.c0{{color:var(--green);font-weight:800;white-space:nowrap}}
  td em{{font-style:normal;color:var(--green)}}
  td b{{color:var(--gold)}}
  {concl_css}
  {fig_css}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    ths = "".join(f"<th>{esc(c)}</th>" for c in p["cols"])
    trs = ""
    for r in p["rows"]:
        tds = "".join(
            f'<td class="c0">{esc(c)}</td>' if i == 0 else f"<td>{esc(c)}</td>"
            for i, c in enumerate(r))
        trs += f"    <tr>{tds}</tr>\n"
    concl_in = "" if roomy else '    <div class="concl concl">%s</div>\n' % esc(p['concl'])
    concl_out = ('  <div class="concl concl">%s</div>\n' % esc(p['concl'])) if roomy else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="twrap"><table>
    <tr>{ths}</tr>
{trs}  </table>
{concl_in}  </div>
{concl_out}"""
    if has_img:
        b += f"""  <div class="fig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <div class="cap">{esc(p.get('cap', ''))}</div></div>
"""
    b += f"""  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:横向三卡片(并列三条横向排布+结论条沉底) ----------
def t_cards3(p):
    extra = """
  .cards3{position:absolute;left:var(--mx);top:360px;width:var(--cw);display:flex;gap:36px;flex-wrap:wrap}
  .card3{flex:1 1 0;background:var(--card);border:1px solid var(--line);border-top:8px solid var(--gold);
         padding:52px 44px;min-height:430px}
  .card3 .badge{display:inline-block;padding:10px 28px;font-size:var(--fs-cap);font-weight:800;letter-spacing:.12em}
  .card3 .n{margin:30px 0 18px;font-size:var(--fs-body);font-weight:800;color:var(--ink);line-height:1.5}
  .card3 .n em{font-style:normal;color:var(--green)}
  .card3 .n .ox{color:var(--ox)}
  .card3 .d{font-size:var(--fs-body);color:var(--muted);line-height:1.85}
  .concl3{flex:1 1 100%;margin-top:4px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cards = ""
    for c in p["cards"]:
        cards += f"""    <div class="card3" style="border-top-color:var(--{c['b']})">
      <span class="badge badge {c['b']}">{esc(c['k'])}</span>
      <div class="n">{esc(c['n'])}</div>
      <div class="d">{esc(c['d'])}</div></div>\n"""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cards3">
{cards}  <div class="concl concl3">{esc(p['concl'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:横向步骤条(流程横向排布+提示框沉底) ----------
def t_stepper(p):
    extra = """
  .steps3{position:absolute;left:var(--mx);top:370px;width:var(--cw);display:flex;align-items:stretch}
  .step3{flex:1;background:var(--card);border:1px solid var(--line);padding:48px 42px;min-height:400px}
  .step3 .num{width:72px;height:72px;border-radius:50%;background:var(--green);color:#fff;
              display:flex;align-items:center;justify-content:center;font-size:var(--fs-body-n);font-weight:800}
  .step3 .t{margin:26px 0 14px;font-size:var(--fs-body);font-weight:800;color:var(--ink)}
  .step3 .d{font-size:var(--fs-body);color:var(--muted);line-height:1.8}
  .arr3{align-self:center;flex:none;font-size:var(--fs-body-n);color:var(--gold);padding:0 14px;font-family:Georgia,serif}
  .warn3{position:absolute;left:var(--mx);right:var(--mx);bottom:110px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    steps = ""
    for i, s in enumerate(p["steps"]):
        if i > 0:
            steps += '    <div class="arr3">→</div>\n'
        steps += f"""    <div class="step3"><div class="num">{i+1}</div>
      <div class="t">{esc(s['t'])}</div>
      <div class="d">{esc(s['d'])}</div></div>\n"""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="steps3">
{steps}  </div>
  <div class="warn warn3">{esc(p['warn'])}</div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:方程式 hero(中央大方程式+三横卡+结论条沉底) ----------
def t_equation_hero(p):
    extra = """
  .eqhero{position:absolute;left:var(--mx);right:var(--mx);top:330px;text-align:center}
  .eqhero .eq{font-size:var(--fs-section-title);font-weight:900;color:var(--ink);letter-spacing:.03em;line-height:1.25}
  .eqhero .eq sub{font-size:.55em}
  .eqhero .eqlabel{margin-top:20px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.24em}
  .eqcards{position:absolute;left:var(--mx);top:650px;width:var(--cw);display:flex;gap:36px;flex-wrap:wrap}
  .eqcard{flex:1;background:var(--card);border:1px solid var(--line);border-left:8px solid var(--gold);padding:32px 36px}
  .eqcard .k{font-size:var(--fs-cap);font-weight:800;letter-spacing:.14em;margin-bottom:12px}
  .eqcard .n{font-size:var(--fs-body);font-weight:700;color:var(--ink);line-height:1.55}
  .eqcard .n em{font-style:normal;color:var(--green)}
  .eqcard .n .ox{color:var(--ox)}
  .eqcard .d{margin-top:10px;font-size:var(--fs-cap);color:var(--muted);line-height:1.7}
  .concl3{flex:1 1 100%;margin-top:4px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cards = ""
    for c in p["cards"]:
        cards += f"""    <div class="eqcard" style="border-left-color:var(--{c['b']})">
      <div class="k" style="color:var(--{c['b']})">{esc(c['k'])}</div>
      <div class="n">{esc(c['n'])}</div>
      <div class="d">{esc(c['d'])}</div></div>\n"""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="eqhero">
    <div class="eq">{esc(p['eq'])}</div>
    <div class="eqlabel">{esc(p.get('eqlabel', ''))}</div>
  </div>
  <div class="eqcards">
{cards}  <div class="concl concl3">{esc(p['concl'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:分支流程图(同一起点→条件分支→不同结果) ----------
def t_flow_branch(p):
    n = len(p["branches"])
    gap = 60
    bw = 520  # 分支 ≤3 时的舒适卡宽；4 分支时自适应收缩以免溢出
    if bw * n + gap * (n - 1) > 1680:
        bw = (1680 - gap * (n - 1)) / n
    total = bw * n + gap * (n - 1)
    off = (1680 - total) / 2
    cxs = [off + bw / 2 + i * (bw + gap) for i in range(n)]
    fork_svg = svg_fork(cxs)  # 分叉线走 程序/svg.py 图元
    extra = """
  .twrap{position:absolute;left:var(--mx);top:340px;width:var(--cw)}
  .root{margin:0 auto;width:520px;background:var(--green);color:#F5F3ED;
        text-align:center;padding:26px 30px}
  .root .t{font-size:var(--fs-body);font-weight:800;letter-spacing:.06em}
  .root .d{margin-top:8px;font-size:var(--fs-cap);opacity:.85;letter-spacing:.04em}
  .forkrow{display:flex;justify-content:center;gap:60px}
  .branch{width:WIDpx;flex:none;background:var(--card);outline:1px solid var(--line);
          padding:30px 34px}
  .cond{display:inline-block;background:var(--gold);color:var(--ink);font-weight:800;
        font-size:var(--fs-cap);letter-spacing:.14em;padding:10px 26px}
  .res{margin-top:16px;font-size:var(--fs-body-n);color:var(--green);font-weight:800;letter-spacing:.04em}
  .bd{margin-top:10px;font-size:var(--fs-body);color:var(--muted);line-height:1.7}
  .concl{margin-top:30px}
""".replace("WIDpx", f"{bw:.0f}px")
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    brs = ""
    for b in p["branches"]:
        brs += (f'    <div class="branch"><div class="cond">{esc(b["cond"])}</div>\n'
                f'      <div class="res">{esc(b["result"])}</div>\n'
                f'      <div class="bd">{esc(b["d"])}</div></div>\n')
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="twrap">
    <div class="root"><div class="t">{esc(p['root']['t'])}</div>
      <div class="d">{esc(p['root']['d'])}</div></div>
    {fork_svg}
    <div class="forkrow">
{brs}    </div>
    <div class="concl concl">{esc(p['concl'])}</div>
  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:循环关系图(节点环形排布+带标签箭头) ----------
def t_flow_cycle(p):
    svg = svg_cycle(p["nodes"], p["edges"])  # 环形图走 程序/svg.py 图元
    extra = """
  .twrap{position:absolute;left:var(--mx);top:340px;width:var(--cw)}
  .concl{margin-top:8px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="twrap">{svg}
    <div class="concl concl">{esc(p['concl'])}</div>
  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:时间线(横向轴线 + 上下交错里程碑卡) ----------
def t_timeline(p):
    nodes = p["nodes"]
    n = len(nodes)
    axis_y = 580
    # 节点 x：在内容宽内均匀分布（≤4 个居中散开，5–6 个撑满）
    if n <= 4:
        cxs = [round(840 + (i - (n - 1) / 2) * 420) for i in range(n)]
    else:
        cxs = [round(120 + i * (1680 - 240) / (n - 1)) for i in range(n)]
    ups = [i % 2 == 0 for i in range(n)]  # 偶数上、奇数下交错
    axis_svg = timeline_axis(cxs, axis_y, cxs[0], cxs[-1], ups)
    extra = """
  .tlwrap{position:absolute;left:0;top:0;width:1920px;height:1080px}
  .tlwrap svg{position:absolute;left:120px;top:0;width:1680px;height:1080px}
  /* 注：1680px 是 SVG 内部坐标系（timeline_axis 按 1680 算点），不是内容宽，不跟 var(--cw) */
  .node{position:absolute;width:340px}
  .node.up{text-align:center}
  .node.dn{text-align:center}
  .node .t{font-family:Georgia,serif;font-size:var(--fs-body);font-weight:700;
           color:var(--gold);letter-spacing:.12em}
  .node .h{margin-top:10px;font-size:var(--fs-body);font-weight:800;color:var(--ink);
           letter-spacing:.04em;line-height:1.4}
  .node .d{margin-top:10px;font-size:var(--fs-body);color:var(--muted);
           letter-spacing:.04em;line-height:1.7}
  .concl{position:absolute;left:var(--mx);bottom:120px;width:var(--cw)}
"""
    cards = ""
    for i, nd in enumerate(nodes):
        x = 120 + cxs[i] - 170
        if ups[i]:
            style = f"left:{x}px;bottom:{1080 - axis_y + 58}px"
            cls = "node up"
        else:
            style = f"left:{x}px;top:{axis_y + 58}px"
            cls = "node dn"
        cards += (f'    <div class="{cls}" style="{style}">'
                  f'<div class="t">{esc(nd["t"])}</div>'
                  f'<div class="h">{esc(nd["h"])}</div>'
                  f'<div class="d">{esc(nd["d"])}</div></div>\n')
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="tlwrap">{axis_svg}
{cards}  </div>
  <div class="concl concl">{esc(p['concl'])}</div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:图表页(图表+断言标题+解读) ----------
def t_chart(p):
    # 图表由 程序/图表.py 生成（declutter 焊死）；本模板只负责版式
    # 版式：图左1080 + 右480解读栏；无解读时图占全宽
    has_insight = bool(p.get("insight"))
    cw = "1080px" if has_insight else "var(--cw)"
    ar = "16/9" if has_insight else "16/5.2"  # 全宽 16/9 会顶穿页脚
    extra = """
  .cwrap{position:absolute;left:var(--mx);top:352px;width:var(--cw);display:flex;gap:var(--space-3)}
  .cfig{flex:none;width:%s}
  .cfig .photo{width:100%%;aspect-ratio:%s;background-size:contain;background-color:transparent;outline:none}
  .cfig .cap{margin-top:12px;text-align:left}
  .cside{flex:1;min-width:0}
  .cside .take{font-size:var(--fs-body);font-weight:800;color:var(--ink);line-height:1.5;
              border-left:6px solid var(--gold);padding-left:20px}
  .cside ul{margin:20px 0 0 22px;font-size:var(--fs-body);color:var(--muted);line-height:1.6}
  .cside li{margin-bottom:10px}
  .cside li::marker{color:var(--gold)}
""" % (cw, ar)
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    side = ""
    if has_insight:
        ins = p["insight"]
        lis = "".join(f"<li>{esc(x)}</li>" for x in ins.get("bullets", []))
        side = (f'  <div class="cside"><div class="take">{esc(ins.get("take", ""))}</div>\n'
                f'    <ul>{lis}</ul></div>\n')
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cwrap">
    <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
      <div class="cap">{esc(p.get('cap', ''))}</div></div>
{side}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:图表页-洞察侧边栏 ----------
def t_chart_rail(p):
    extra = """
  .cwrap{position:absolute;left:var(--mx);top:352px;width:var(--cw);display:flex;gap:var(--space-3)}
  .cfig{flex:none;width:1080px}
  .cfig .photo{width:100%;aspect-ratio:16/5.2;background-size:contain;background-color:transparent;outline:none}
  .cfig .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
  .rail{flex:1;min-width:0;background:var(--card);padding:36px 32px;align-self:flex-start}
  .rail .rlabel{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.24em;font-weight:700}
  .rail .rhero{margin-top:14px;font-size:var(--fs-page-title);font-weight:900;color:var(--gold);letter-spacing:.02em}
  .rail .rbody{margin-top:16px;font-size:var(--fs-body);color:var(--ink);line-height:1.7;letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    r = p["rail"]
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cwrap">
    <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
      <div class="cap">{esc(p['cap'])}</div></div>
    <div class="rail"><div class="rlabel">{esc(r['label'])}</div>
      <div class="rhero">{esc(r['hero'])}</div>
      <div class="rbody">{esc(r['body'])}</div></div>
  </div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-小多图矩阵 ----------
def t_chart_multiples(p):
    extra = """
  .cfig{position:absolute;left:var(--mx);top:352px;width:var(--cw)}
  .cfig .photo{width:100%;aspect-ratio:16/5.2;background-size:contain;background-color:transparent;outline:none}
  .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <div class="cap">{esc(p['cap'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-瀑布 ----------
def t_chart_waterfall(p):
    extra = """
  .cfig{position:absolute;left:var(--mx);top:352px;width:var(--cw)}
  .cfig .photo{width:100%;aspect-ratio:16/5.2;background-size:contain;background-color:transparent;outline:none}
  .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <div class="cap">{esc(p['cap'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-组合双轴 ----------
def t_chart_combo(p):
    extra = """
  .cfig{position:absolute;left:var(--mx);top:352px;width:var(--cw)}
  .cfig .photo{width:100%;aspect-ratio:16/5.2;background-size:contain;background-color:transparent;outline:none}
  .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <div class="cap">{esc(p['cap'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-图表+数据表 ----------
def t_chart_table(p):
    extra = """
  .cfig{position:absolute;left:var(--mx);top:340px;width:var(--cw)}
  .cfig .photo{width:100%;aspect-ratio:16/4.2;background-size:contain;background-color:transparent;outline:none}
  .ctab{margin-top:12px;width:100%;border-collapse:collapse;font-size:var(--fs-desc)}
  .ctab th{font-size:var(--fs-cap);color:var(--muted);font-weight:700;letter-spacing:.08em;
           text-align:left;padding:5px 14px;border-bottom:2px solid var(--line)}
  .ctab td{padding:5px 14px;border-bottom:1px solid var(--line);color:var(--ink);letter-spacing:.03em}
  .ctab th:nth-child(n+2),.ctab td:nth-child(n+2){text-align:right}
  .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    ths = "".join(f"<th>{esc(c)}</th>" for c in p["headers"])
    trs = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>"
                  for row in p["rows"])
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <table class="ctab"><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>
    <div class="cap">{esc(p['cap'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-标注型 ----------
def t_chart_annotated(p):
    extra = """
  .cfig{position:absolute;left:var(--mx);top:352px;width:var(--cw)}
  .cfig .photo{width:100%;aspect-ratio:16/5.2;background-size:contain;background-color:transparent;outline:none}
  .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <div class="cap">{esc(p['cap'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-仪表盘 ----------
def t_chart_dashboard(p):
    extra = """
  .kpis{position:absolute;left:var(--mx);top:340px;width:var(--cw);display:flex;gap:var(--space-2)}
  .kpi{flex:1;background:var(--card);padding:26px 28px;border-top:4px solid var(--gold)}
  .kpi .kn{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.14em;font-weight:700}
  .kpi .kv{margin-top:10px;font-size:var(--fs-page-title);font-weight:900;color:var(--ink);letter-spacing:.02em}
  .kpi .kc{margin-top:8px;font-size:var(--fs-body);font-weight:700;letter-spacing:.04em}
  .kpi .kc.up{color:var(--green)} .kpi .kc.dn{color:#D55E00}
  .cfig{position:absolute;left:var(--mx);top:580px;width:var(--cw)}
  .cfig .photo{width:100%;aspect-ratio:16/3.2;background-size:contain;background-color:transparent;outline:none}
  .cap{margin-top:10px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cards = ""
    for k in p["kpis"]:
        ch = k["变化"]
        cls = "up" if ch.strip().startswith("+") else ("dn" if ch.strip().startswith("-") else "")
        arrow = "▲" if cls == "up" else ("▼" if cls == "dn" else "")
        cards += (f"""    <div class="kpi"><div class="kn">{esc(k['名'])}</div>"""
                  f"""<div class="kv">{esc(k['值'])}</div>"""
                  f"""<div class="kc {cls}">{arrow} {esc(ch)}</div></div>\n""")
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="kpis">
{cards}  </div>
  <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <div class="cap">{esc(p['cap'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-哑铃对比 ----------
def t_chart_dumbbell(p):
    extra = """
  .cfig{position:absolute;left:var(--mx);top:352px;width:var(--cw)}
  .cfig .photo{width:100%;aspect-ratio:16/5.2;background-size:contain;background-color:transparent;outline:none}
  .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <div class="cap">{esc(p['cap'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-排名条形榜 ----------
def t_chart_ranked(p):
    extra = """
  .cfig{position:absolute;left:var(--mx);top:352px;width:var(--cw)}
  .cfig .photo{width:100%;aspect-ratio:16/5.2;background-size:contain;background-color:transparent;outline:none}
  .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <div class="cap">{esc(p['cap'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-地图页 ----------
def t_chart_map(p):
    extra = """
  .mapbox{position:absolute;left:var(--mx);top:352px;width:var(--cw);height:560px;
          border:2px dashed var(--line);display:flex;flex-direction:column;
          align-items:center;justify-content:center;gap:18px;background:var(--card)}
  .mapbox .m1{font-size:var(--fs-body-n);font-weight:800;color:var(--ink);letter-spacing:.1em}
  .mapbox .m2{font-size:var(--fs-body);color:var(--muted);letter-spacing:.06em}
  .mapbox .legend{display:flex;gap:0;margin-top:8px}
  .mapbox .legend i{display:block;width:72px;height:14px}
  .mapbox .legend span{font-size:var(--fs-cap);color:var(--muted);margin:0 10px;align-self:center}
  .cap{position:absolute;left:var(--mx);top:930px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    note = f'<div class="m2">{esc(p["note"])}</div>' if p.get("note") else ""
    # 图例条：浅→深 5 阶（示意）
    cells = "".join(
        f'<i style="background:{c}"></i>' for c in
        ["#F6E8E4", "#EFC9BE", "#E5A58F", "#D97F63", "var(--gold)"])
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="mapbox">
    <div class="m1">{esc(p['metric'])}</div>
    <div class="m2">省级分级设色地图 · 地理边界数据待接入</div>
    {note}
    <div class="legend"><span>低</span>{cells}<span>高</span></div>
  </div>
  <div class="cap">{esc(p['cap'])}</div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-构成双面板 ----------
def t_chart_dualpanel(p):
    extra = """
  .panels{position:absolute;left:var(--mx);top:352px;width:var(--cw);display:flex;gap:var(--space-3)}
  .panel{flex:1;min-width:0}
  .panel .plabel{font-size:var(--fs-cap);color:var(--gold);font-weight:800;letter-spacing:.24em;margin-bottom:12px}
  .panel .photo{width:100%;aspect-ratio:16/10;background-size:contain;background-color:transparent;outline:none}
  .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="panels">
    <div class="panel"><div class="plabel">绝对值</div>
      <div class="photo{_maskcls(p)}" style="background-image:{img(p['img_abs'])}"></div></div>
    <div class="panel"><div class="plabel">占比</div>
      <div class="photo{_maskcls(p)}" style="background-image:{img(p['img_share'])}"></div></div>
  </div>
  <div class="cap" style="position:absolute;left:var(--mx);top:880px">{esc(p['cap'])}</div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-实际vs目标 ----------
def t_chart_bullet(p):
    extra = """
  .cfig{position:absolute;left:var(--mx);top:352px;width:var(--cw)}
  .cfig .photo{width:100%;aspect-ratio:16/5.2;background-size:contain;background-color:transparent;outline:none}
  .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <div class="cap">{esc(p['cap'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-帕累托 ----------
def t_chart_pareto(p):
    extra = """
  .cfig{position:absolute;left:var(--mx);top:352px;width:var(--cw)}
  .cfig .photo{width:100%;aspect-ratio:16/5.2;background-size:contain;background-color:transparent;outline:none}
  .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <div class="cap">{esc(p['cap'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:图表页-堆叠构成 ----------
def t_chart_stacked(p):
    extra = """
  .cfig{position:absolute;left:var(--mx);top:352px;width:var(--cw)}
  .cfig .photo{width:100%;aspect-ratio:16/5.2;background-size:contain;background-color:transparent;outline:none}
  .cap{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = (f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cfig"><div class="photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>
    <div class="cap">{esc(p['cap'])}</div></div>
  <div class="foot-line"></div>
  <div class="foot-left">{esc(p['foot'])}</div>
</body>
</html>
""")
    return h + b


# ---------- 模板:KPI英雄(巨型数字+上下文) ----------
def t_kpi_hero(p):
    # 1个→居中英雄(118px)；2-4个→等分网格(64px)，hero卡 accent 顶边标记
    kpis = p["kpis"]
    n = len(kpis)
    single = n == 1
    extra = """
  .kwrap{position:absolute;left:var(--mx);top:360px;width:var(--cw)}
  .kgrid{display:flex;gap:var(--space-3)}
  .kcard{flex:1;background:var(--card);border:1px solid var(--line);border-radius:6px;
         padding:44px 40px;position:relative}
  .kcard.hero{border-top:6px solid var(--gold)}
  .kcard .v{font-size:var(--fs-page-title);font-weight:800;color:var(--ink);
            font-variant-numeric:tabular-nums lining-nums;letter-spacing:.01em}
  .kcard.hero .v{color:var(--gold)}
  .kcard .lb{margin-top:14px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.14em}
  .kcard .cx{margin-top:10px;font-size:var(--fs-body);color:var(--green);font-weight:700}
  .ksingle{text-align:center;padding:60px 0}
  .ksingle .v{font-size:var(--fs-section-title);font-weight:800;color:var(--gold);
              font-variant-numeric:tabular-nums lining-nums}
  .ksingle .lb{margin-top:18px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.14em}
  .ksingle .cx{margin-top:12px;font-size:var(--fs-body-n);color:var(--green);font-weight:700}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    if single:
        k = kpis[0]
        cards = (f'    <div class="ksingle"><div class="v">{esc(k["v"])}</div>\n'
                 f'      <div class="lb">{esc(k["label"])}</div>\n'
                 f'      <div class="cx">{esc(k.get("ctx", ""))}</div></div>\n')
    else:
        parts = []
        for k in kpis:
            hc = " hero" if k.get("hero") else ""
            parts.append(
                f'    <div class="kcard{hc}"><div class="v">{esc(k["v"])}</div>\n'
                f'      <div class="lb">{esc(k["label"])}</div>\n'
                f'      <div class="cx">{esc(k.get("ctx", ""))}</div></div>\n')
        cards = '  <div class="kgrid">\n' + "".join(parts) + "  </div>\n"
    concl = f'  <div class="concl" style="margin-top:32px">{esc(p["concl"])}</div>\n' if p.get("concl") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="kwrap">
{cards}{concl}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


def t_infographic(p):
    """信息图：图标+数字+说明，2-4项横向。items: [{icon,v,label,d}]"""
    from 图标 import icon as _icon
    items = p["items"]
    n = len(items)
    if n < 2 or n > 4:
        raise ValueError("infographic: items须2-4项")
    extra = """
  .iwrap{position:absolute;left:var(--mx);top:360px;width:var(--cw)}
  .igrid{display:flex;gap:var(--space-4)}
  .icard{flex:1;text-align:center;padding:56px 32px;background:var(--card);
         border:1px solid var(--line);border-radius:12px;position:relative}
  .icard .ic{width:88px;height:88px;margin:0 auto 28px;border-radius:50%;
             background:var(--gold-soft);display:flex;align-items:center;justify-content:center}
  .icard .v{font-size:var(--fs-page-title);font-weight:800;color:var(--ink);
            font-variant-numeric:tabular-nums lining-nums}
  .icard .lb{margin-top:12px;font-size:var(--fs-cap);color:var(--gold);
             letter-spacing:.18em;font-weight:700}
  .icard .d{margin-top:14px;font-size:var(--fs-body);color:var(--muted);line-height:1.7}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    parts = []
    for it in items:
        parts.append(
            f'    <div class="icard"><div class="ic">{_icon(it.get("icon", "星"), 44)}</div>\n'
            f'      <div class="v">{esc(it["v"])}</div>\n'
            f'      <div class="lb">{esc(it["label"])}</div>\n'
            f'      <div class="d">{esc(it.get("d", ""))}</div></div>\n')
    cards = '  <div class="igrid">\n' + "".join(parts) + "  </div>\n"
    concl = f'  <div class="concl" style="margin-top:36px">{esc(p["concl"])}</div>\n' if p.get("concl") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="iwrap">
{cards}{concl}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


def t_compare_bars(p):
    """对比条：两组数据横向条形对比。rows: [{label, a, b}]，a_name/b_name 为组名。"""
    rows = p["rows"]
    if not rows or len(rows) > 6:
        raise ValueError("compare_bars: rows须1-6行")
    vmax = max(max(r["a"], r["b"]) for r in rows) or 1
    extra = """
  .cwrap{position:absolute;left:var(--mx);top:340px;width:var(--cw)}
  .chead{display:flex;margin-bottom:8px}
  .chead .sp{flex:1}
  .chead .nm{width:280px;text-align:center;font-size:var(--fs-body-n);
             font-weight:800;letter-spacing:.1em}
  .crow{display:flex;align-items:center;margin:26px 0}
  .crow .bl{width:280px;text-align:right;font-size:var(--fs-body);color:var(--muted);padding-right:32px}
  .crow .br{flex:1;display:flex;flex-direction:column;gap:10px}
  .bar{height:38px;border-radius:6px;display:flex;align-items:center;
       padding:0 18px;font-size:var(--fs-body-n);font-weight:700;min-width:64px}
  .bar.a{background:var(--gold);color:#fff}
  .bar.b{background:var(--line);color:var(--ink)}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    chead = (f'  <div class="chead"><div class="sp"></div>'
             f'<div class="nm" style="color:var(--gold)">{esc(p.get("a_name", "A"))}</div>'
             f'<div class="nm">{esc(p.get("b_name", "B"))}</div><div class="sp"></div></div>\n')
    parts = []
    for r in rows:
        wa, wb = r["a"] / vmax * 100, r["b"] / vmax * 100
        parts.append(
            f'    <div class="crow"><div class="bl">{esc(r["label"])}</div><div class="br">\n'
            f'      <div class="bar a" style="width:{wa:.1f}%">{esc(str(r["a"]))}</div>\n'
            f'      <div class="bar b" style="width:{wb:.1f}%">{esc(str(r["b"]))}</div>\n'
            f'    </div></div>\n')
    concl = f'  <div class="concl" style="margin-top:36px">{esc(p["concl"])}</div>\n' if p.get("concl") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cwrap">
{chead}{"".join(parts)}{concl}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


def t_number_hero(p):
    """大数字：一页一个数字做视觉 hammer。v: 大数字，label: 说明，d: 补充，icon 可选。"""
    from 图标 import icon as _icon
    extra = """
  .nwrap{position:absolute;left:var(--mx);top:300px;width:var(--cw);text-align:center}
  .nwrap .ic{width:110px;height:110px;margin:0 auto 36px;border-radius:50%;
             background:var(--gold-soft);display:flex;align-items:center;justify-content:center}
  .nwrap .v{font-size:var(--fs-hero);font-weight:800;color:var(--gold);line-height:1;
            font-variant-numeric:tabular-nums lining-nums;letter-spacing:.01em}
  .nwrap .lb{margin-top:28px;font-size:var(--fs-page-title);color:var(--ink);font-weight:700}
  .nwrap .d{margin-top:18px;font-size:var(--fs-body-n);color:var(--muted);line-height:1.8}
  .nwrap .ctx{margin-top:24px;font-size:var(--fs-body);color:var(--green);font-weight:700}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    ic = f'    <div class="ic">{_icon(p.get("icon", "增长"), 54)}</div>\n' if p.get("icon") else ""
    ctx = f'      <div class="ctx">{esc(p["ctx"])}</div>\n' if p.get("ctx") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="nwrap">
{ic}    <div class="v">{esc(p['v'])}</div>
      <div class="lb">{esc(p['label'])}</div>
      <div class="d">{esc(p.get('d', ''))}</div>
{ctx}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# -*- coding: utf-8 -*-
"""封面16 · 14 个新封面模板（插入 页面生成.py，TEMPLATES 字典之前）。"""

# ---------- 模板:封面(大字报式纯文字) ----------
def t_cover_typo(p):
    # 文字即图形：零图片依赖；标题 --fs-hero，长标题拆行，关键词 <b> 标强调色。
    extra = """
  .ty-wrap{position:absolute;inset:0;background:var(--bg)}
  .ty-block{position:absolute;left:130px;right:130px;top:320px}
  .ty-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .ty-block .gold-rule{margin:34px 0 44px}
  .ty-block h1{font-size:var(--fs-hero);line-height:1.08;letter-spacing:.02em;color:var(--ink);font-weight:800}
  .ty-en{margin-top:26px;font-size:var(--fs-body-n);color:var(--gold);letter-spacing:.14em}
  .ty-sub{margin-top:40px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.08em;line-height:var(--lh-body)}
  .ty-foot{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .ty-foot .line{width:56px;height:2px;background:var(--gold)}
  .ty-foot span{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
  .ty-na{position:absolute;right:130px;bottom:74px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="ty-wrap">
    <div class="ty-block">
      <div class="ty-eyebrow">{esc(p['eyebrow'])}</div>
      <div class="gold-rule"></div>
      <h1>{esc(p['title'])}</h1>
      <div class="ty-en">{esc(p.get('en', ''))}</div>
      <div class="ty-sub">{esc(p['sub'])}</div>
    </div>
    <div class="ty-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
    <div class="ty-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(留白主导极简) ----------
def t_cover_minimal(p):
    # 空白≥40%，内容收进中央 70%；全页只一处装饰（细金线）。
    extra = """
  .mn-wrap{position:absolute;inset:0;background:var(--bg);text-align:center}
  .mn-block{position:absolute;left:288px;right:288px;top:360px}
  .mn-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .mn-block h1{margin-top:36px;font-size:var(--fs-page-title);line-height:1.2;letter-spacing:.06em;color:var(--ink);font-weight:700}
  .mn-rule{width:64px;height:3px;background:var(--gold);margin:44px auto 0}
  .mn-sub{margin-top:36px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.08em;line-height:var(--lh-body)}
  .mn-foot{position:absolute;left:0;right:0;bottom:74px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
  .mn-na{position:absolute;right:130px;bottom:74px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="mn-wrap">
    <div class="mn-block">
      <div class="mn-eyebrow">{esc(p['eyebrow'])}</div>
      <h1>{esc(p['title'])}</h1>
      <div class="mn-rule"></div>
      <div class="mn-sub">{esc(p['sub'])}</div>
    </div>
    <div class="mn-foot">{esc(p['foot'])}</div>
    <div class="mn-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(图片独立色块) ----------
def t_cover_block(p):
    # 图片不铺满：右侧独立色块（rect/arch/circle），左侧干净文字区。
    shape = p.get("shape", "rect")
    radius = {"arch": "320px 320px 28px 28px", "circle": "50%",
              "rect": "28px"}.get(shape, "28px")
    extra = """
  .bl-wrap{position:absolute;inset:0;background:var(--bg)}
  .bl-block{position:absolute;left:130px;top:360px;width:780px}
  .bl-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .bl-block .gold-rule{margin:34px 0 44px}
  .bl-block h1{font-size:var(--fs-section-title);line-height:1.08;letter-spacing:.03em;color:var(--ink)}
  .bl-en{margin-top:22px;font-size:var(--fs-body-n);color:var(--gold);letter-spacing:.14em}
  .bl-sub{margin-top:40px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.08em;line-height:var(--lh-body)}
  .bl-img{position:absolute;right:130px;top:180px;width:760px;height:720px;background:""" + img(p["img"]) + """ center/cover no-repeat;border-radius:""" + radius + """}
  .bl-foot{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .bl-foot .line{width:56px;height:2px;background:var(--gold)}
  .bl-foot span{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
  .bl-na{position:absolute;right:130px;bottom:74px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="bl-wrap">
    <div class="bl-block">
      <div class="bl-eyebrow">{esc(p['eyebrow'])}</div>
      <div class="gold-rule"></div>
      <h1>{esc(p['title'])}</h1>
      <div class="bl-en">{esc(p.get('en', ''))}</div>
      <div class="bl-sub">{esc(p['sub'])}</div>
    </div>
    <div class="bl-img"></div>
    <div class="bl-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
    <div class="bl-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(双色拼接) ----------
def t_cover_duo(p):
    # 左 45% 纯色面板（--ink）放字 + 右 55% 双色调图；彻底不用罩子。
    extra = """
  .du-wrap{position:absolute;inset:0;display:flex}
  .du-left{flex:0 0 45%;background:var(--ink);position:relative}
  .du-right{flex:1;position:relative;background:""" + img(p["img"]) + """ center/cover no-repeat;filter:grayscale(1) contrast(1.06)}
  .du-tint{position:absolute;inset:0;background:var(--gold);mix-blend-mode:multiply;opacity:.5}
  .du-block{position:absolute;left:120px;top:360px;width:620px}
  .du-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .du-block .gold-rule{margin:34px 0 44px}
  .du-block h1{font-size:var(--fs-section-title);line-height:1.08;letter-spacing:.03em;color:var(--bg)}
  .du-en{margin-top:22px;font-size:var(--fs-body-n);color:var(--gold);letter-spacing:.14em}
  .du-sub{margin-top:40px;font-size:var(--fs-body);color:var(--bg);opacity:.72;letter-spacing:.08em;line-height:var(--lh-body)}
  .du-foot{position:absolute;left:120px;bottom:74px;display:flex;align-items:center;gap:22px}
  .du-foot .line{width:56px;height:2px;background:var(--gold)}
  .du-foot span{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.28em}
  .du-na{position:absolute;right:70px;bottom:74px;font-size:var(--fs-cap);color:var(--bg);letter-spacing:.5em;opacity:.8}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="du-wrap">
    <div class="du-left">
      <div class="du-block">
        <div class="du-eyebrow">{esc(p['eyebrow'])}</div>
        <div class="gold-rule"></div>
        <h1>{esc(p['title'])}</h1>
        <div class="du-en">{esc(p.get('en', ''))}</div>
        <div class="du-sub">{esc(p['sub'])}</div>
      </div>
      <div class="du-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
    </div>
    <div class="du-right"><div class="du-tint"></div></div>
    <div class="du-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(斜切对角) ----------
def t_cover_diagonal(p):
    # 15° 斜切：图片沿对角线占据右上，文字区在左下水平基线上，不跟斜。
    extra = """
  .dg-wrap{position:absolute;inset:0;background:var(--bg);overflow:hidden}
  .dg-img{position:absolute;inset:0;background:""" + img(p["img"]) + """ center/cover no-repeat;
    clip-path:polygon(42% 0,100% 0,100% 100%,58% 100%)}
  .dg-line{position:absolute;inset:0;pointer-events:none}
  .dg-block{position:absolute;left:130px;top:380px;width:700px}
  .dg-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .dg-block .gold-rule{margin:34px 0 44px}
  .dg-block h1{font-size:var(--fs-section-title);line-height:1.08;letter-spacing:.03em;color:var(--ink)}
  .dg-en{margin-top:22px;font-size:var(--fs-body-n);color:var(--gold);letter-spacing:.14em}
  .dg-sub{margin-top:40px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.08em;line-height:var(--lh-body)}
  .dg-foot{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .dg-foot .line{width:56px;height:2px;background:var(--gold)}
  .dg-foot span{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
  .dg-na{position:absolute;right:130px;bottom:74px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="dg-wrap">
    <div class="dg-img"></div>
    <svg class="dg-line" width="1920" height="1080" viewBox="0 0 1920 1080">
      <line x1="806" y1="0" x2="1114" y2="1080" stroke="var(--gold)" stroke-width="4"/>
    </svg>
    <div class="dg-block">
      <div class="dg-eyebrow">{esc(p['eyebrow'])}</div>
      <div class="gold-rule"></div>
      <h1>{esc(p['title'])}</h1>
      <div class="dg-en">{esc(p.get('en', ''))}</div>
      <div class="dg-sub">{esc(p['sub'])}</div>
    </div>
    <div class="dg-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
    <div class="dg-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(品牌色底+图形) ----------
def t_cover_brand(p):
    # --gold 主导大色块 + 几何图形（圆/环/斜条），标题放在 --bg 文字区。
    extra = """
  .br-wrap{position:absolute;inset:0;background:var(--bg);overflow:hidden}
  .br-shape{position:absolute;right:-260px;top:-260px;width:1060px;height:1060px;border-radius:50%;background:var(--gold)}
  .br-ring{position:absolute;right:180px;top:120px;width:420px;height:420px;border-radius:50%;border:3px solid var(--bg);opacity:.55}
  .br-bar{position:absolute;right:0;bottom:180px;width:560px;height:26px;background:var(--gold);opacity:.35;transform:skewX(-18deg)}
  .br-block{position:absolute;left:130px;top:360px;width:820px}
  .br-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .br-block .gold-rule{margin:34px 0 44px}
  .br-block h1{font-size:var(--fs-section-title);line-height:1.08;letter-spacing:.03em;color:var(--ink)}
  .br-en{margin-top:22px;font-size:var(--fs-body-n);color:var(--gold);letter-spacing:.14em}
  .br-sub{margin-top:40px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.08em;line-height:var(--lh-body)}
  .br-foot{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .br-foot .line{width:56px;height:2px;background:var(--gold)}
  .br-foot span{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
  .br-na{position:absolute;left:130px;bottom:130px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="br-wrap">
    <div class="br-shape"></div>
    <div class="br-ring"></div>
    <div class="br-bar"></div>
    <div class="br-block">
      <div class="br-eyebrow">{esc(p['eyebrow'])}</div>
      <div class="gold-rule"></div>
      <h1>{esc(p['title'])}</h1>
      <div class="br-en">{esc(p.get('en', ''))}</div>
      <div class="br-sub">{esc(p['sub'])}</div>
    </div>
    <div class="br-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
    <div class="br-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(杂志编辑风) ----------
def t_cover_magazine(p):
    # 主图右置，masthead 式大标题横跨图界，kicker 行 2–4 条，顶部元信息。
    ks = "".join('<div class="mg-k">%s</div>' % esc(it["t"]) for it in p["kickers"])
    extra = """
  .mg-wrap{position:absolute;inset:0;background:var(--bg)}
  .mg-img{position:absolute;right:0;top:0;width:1152px;height:1080px;background:""" + img(p["img"]) + """ center/cover no-repeat}
  .mg-meta{position:absolute;left:90px;top:90px;right:90px;display:flex;justify-content:space-between;
    font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .mg-block{position:absolute;left:90px;top:380px;width:1060px}
  .mg-block h1{font-size:var(--fs-hero);line-height:1.06;letter-spacing:.02em;color:var(--ink);font-weight:800}
  .mg-ks{margin-top:40px;border-left:4px solid var(--gold);padding-left:28px}
  .mg-k{font-size:var(--fs-desc);color:var(--ink);font-weight:700;letter-spacing:.1em;line-height:2}
  .mg-sub{margin-top:30px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.08em}
  .mg-foot{position:absolute;left:90px;bottom:74px;display:flex;align-items:center;gap:22px}
  .mg-foot .line{width:56px;height:2px;background:var(--gold)}
  .mg-foot span{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="mg-wrap">
    <div class="mg-img"></div>
    <div class="mg-meta"><span>{esc(p['eyebrow'])}</span><span>{esc(p.get('corner', ''))}</span></div>
    <div class="mg-block">
      <h1>{esc(p['title'])}</h1>
      <div class="mg-ks">{ks}</div>
      <div class="mg-sub">{esc(p['sub'])}</div>
    </div>
    <div class="mg-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(暗黑奢华) ----------
def t_cover_lux(p):
    # 固定近黑画布（不跟主题走）+ 单一金色点缀 + 大量留白。
    extra = """
  .lx-wrap{position:absolute;inset:0;background:#0B0D12;text-align:center}
  .lx-block{position:absolute;left:360px;right:360px;top:360px}
  .lx-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em;text-transform:uppercase}
  .lx-block h1{margin-top:44px;font-size:var(--fs-hero);line-height:1.1;letter-spacing:.12em;color:#F4F1EA;font-weight:700}
  .lx-rule{width:84px;height:2px;background:var(--gold);margin:52px auto 0}
  .lx-en{margin-top:34px;font-size:var(--fs-body-n);color:var(--gold);letter-spacing:.3em}
  .lx-sub{margin-top:30px;font-size:var(--fs-desc);color:#A8A29A;letter-spacing:.2em;line-height:var(--lh-body)}
  .lx-foot{position:absolute;left:0;right:0;bottom:74px;font-size:var(--fs-cap);color:#6E6A63;letter-spacing:.34em}
  .lx-no{position:absolute;right:130px;top:90px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="lx-wrap">
    <div class="lx-no">{esc(p.get('corner', ''))}</div>
    <div class="lx-block">
      <div class="lx-eyebrow">{esc(p['eyebrow'])}</div>
      <h1>{esc(p['title'])}</h1>
      <div class="lx-rule"></div>
      <div class="lx-en">{esc(p.get('en', ''))}</div>
      <div class="lx-sub">{esc(p['sub'])}</div>
    </div>
    <div class="lx-foot">{esc(p['foot'])}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(多图拼贴) ----------
def t_cover_collage(p):
    # 左文右图：右侧 2 列网格拼贴 2–4 张图，标题在干净文字带。
    cells = "".join(
        '<div class="cg-cell" style="background:%s center/cover no-repeat"></div>' % img(it["src"])
        for it in p["imgs"])
    extra = """
  .cg-wrap{position:absolute;inset:0;background:var(--bg)}
  .cg-block{position:absolute;left:130px;top:360px;width:620px}
  .cg-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .cg-block .gold-rule{margin:34px 0 44px}
  .cg-block h1{font-size:var(--fs-page-title);line-height:1.15;letter-spacing:.04em;color:var(--ink)}
  .cg-sub{margin-top:36px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.08em;line-height:var(--lh-body)}
  .cg-grid{position:absolute;right:130px;top:180px;width:920px;height:720px;
    display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:16px}
  .cg-cell{border-radius:18px}
  .cg-foot{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .cg-foot .line{width:56px;height:2px;background:var(--gold)}
  .cg-foot span{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
  .cg-na{position:absolute;right:130px;bottom:74px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="cg-wrap">
    <div class="cg-block">
      <div class="cg-eyebrow">{esc(p['eyebrow'])}</div>
      <div class="gold-rule"></div>
      <h1>{esc(p['title'])}</h1>
      <div class="cg-sub">{esc(p['sub'])}</div>
    </div>
    <div class="cg-grid">{cells}</div>
    <div class="cg-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
    <div class="cg-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(超大裁切) ----------
def t_cover_crop(p):
    # 图片放大 1.35×、一侧出血被裁，只取局部做视觉主体。
    extra = """
  .cr-wrap{position:absolute;inset:0;background:var(--bg);overflow:hidden}
  .cr-img{position:absolute;left:700px;top:-140px;width:1360px;height:1360px;background:""" + img(p["img"]) + """ center/cover no-repeat}
  .cr-block{position:absolute;left:130px;top:380px;width:640px}
  .cr-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .cr-block .gold-rule{margin:34px 0 44px}
  .cr-block h1{font-size:var(--fs-section-title);line-height:1.08;letter-spacing:.03em;color:var(--ink)}
  .cr-en{margin-top:22px;font-size:var(--fs-body-n);color:var(--gold);letter-spacing:.14em}
  .cr-sub{margin-top:40px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.08em;line-height:var(--lh-body)}
  .cr-foot{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .cr-foot .line{width:56px;height:2px;background:var(--gold)}
  .cr-foot span{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
  .cr-na{position:absolute;left:130px;bottom:130px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="cr-wrap">
    <div class="cr-img"></div>
    <div class="cr-block">
      <div class="cr-eyebrow">{esc(p['eyebrow'])}</div>
      <div class="gold-rule"></div>
      <h1>{esc(p['title'])}</h1>
      <div class="cr-en">{esc(p.get('en', ''))}</div>
      <div class="cr-sub">{esc(p['sub'])}</div>
    </div>
    <div class="cr-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
    <div class="cr-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(单锚点) ----------
def t_cover_anchor(p):
    # 一个巨型视觉锚点（年份/数字/关键词）+ 极简标题。
    extra = """
  .an-wrap{position:absolute;inset:0;background:var(--bg)}
  .an-num{position:absolute;left:120px;top:230px;font-size:var(--fs-hero);color:var(--gold);font-weight:800;letter-spacing:.02em;line-height:1}
  .an-num span{font-size:2em}
  .an-block{position:absolute;left:130px;top:600px;width:1100px}
  .an-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .an-block h1{margin-top:26px;font-size:var(--fs-page-title);line-height:1.15;letter-spacing:.04em;color:var(--ink)}
  .an-sub{margin-top:28px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.08em}
  .an-foot{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .an-foot .line{width:56px;height:2px;background:var(--gold)}
  .an-foot span{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
  .an-na{position:absolute;right:130px;bottom:74px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="an-wrap">
    <div class="an-num"><span>{esc(p['num'])}</span></div>
    <div class="an-block">
      <div class="an-eyebrow">{esc(p['eyebrow'])}</div>
      <h1>{esc(p['title'])}</h1>
      <div class="an-sub">{esc(p['sub'])}</div>
    </div>
    <div class="an-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
    <div class="an-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(图字融合/双重曝光) ----------
def t_cover_fusion(p):
    # img2 以 mix-blend 融入 img；文字放在底部局部平静带（必要罩子）。
    extra = """
  .fu-wrap{position:absolute;inset:0;background:var(--ink);overflow:hidden}
  .fu-base{position:absolute;inset:0;background:""" + img(p["img"]) + """ center/cover no-repeat}
  .fu-top{position:absolute;inset:0;background:""" + img(p["img2"]) + """ center/cover no-repeat;
    mix-blend-mode:screen;opacity:.8}
  .fu-band{position:absolute;left:0;right:0;bottom:0;height:460px;
    background:linear-gradient(180deg,rgba(20,26,24,0) 0%,rgba(20,26,24,.66) 62%)}
  .fu-block{position:absolute;left:130px;bottom:120px;width:1100px}
  .fu-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .fu-block h1{margin-top:26px;font-size:var(--fs-section-title);line-height:1.08;letter-spacing:.03em;color:var(--ink-dark)}
  .fu-sub{margin-top:26px;font-size:var(--fs-body);color:var(--ink-dark);opacity:.78;letter-spacing:.08em}
  .fu-foot{position:absolute;left:130px;bottom:48px;font-size:var(--fs-cap);color:var(--ink-dark);opacity:.6;letter-spacing:.28em}
  .fu-na{position:absolute;right:130px;bottom:48px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="fu-wrap">
    <div class="fu-base"></div>
    <div class="fu-top"></div>
    <div class="fu-band"></div>
    <div class="fu-block">
      <div class="fu-eyebrow">{esc(p['eyebrow'])}</div>
      <h1>{esc(p['title'])}</h1>
      <div class="fu-sub">{esc(p['sub'])}</div>
    </div>
    <div class="fu-foot">{esc(p['foot'])}</div>
    <div class="fu-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(半出血图片带) ----------
def t_cover_band(p):
    # 顶部 42% 图片带（一边出血），金线分割，下部纯文字区。
    extra = """
  .bd-wrap{position:absolute;inset:0;background:var(--bg)}
  .bd-img{position:absolute;left:0;right:0;top:0;height:450px;background:""" + img(p["img"]) + """ center/cover no-repeat}
  .bd-div{position:absolute;left:0;right:0;top:450px;height:4px;background:var(--gold)}
  .bd-block{position:absolute;left:130px;top:560px;width:1300px}
  .bd-eyebrow{font-size:var(--fs-cap);color:var(--gold);letter-spacing:.42em;text-transform:uppercase}
  .bd-block h1{margin-top:26px;font-size:var(--fs-page-title);line-height:1.15;letter-spacing:.04em;color:var(--ink)}
  .bd-en{margin-top:18px;font-size:var(--fs-body-n);color:var(--gold);letter-spacing:.14em}
  .bd-sub{margin-top:28px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.08em}
  .bd-foot{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .bd-foot .line{width:56px;height:2px;background:var(--gold)}
  .bd-foot span{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
  .bd-na{position:absolute;right:130px;bottom:74px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="bd-wrap">
    <div class="bd-img"></div>
    <div class="bd-div"></div>
    <div class="bd-block">
      <div class="bd-eyebrow">{esc(p['eyebrow'])}</div>
      <h1>{esc(p['title'])}</h1>
      <div class="bd-en">{esc(p.get('en', ''))}</div>
      <div class="bd-sub">{esc(p['sub'])}</div>
    </div>
    <div class="bd-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
    <div class="bd-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ---------- 模板:封面(笔刷书法) ----------
def t_cover_brush(p):
    # 宣纸底 + 宋体大标题 + 朱红印章 + 笔触背景层次。
    extra = """
  .br2-wrap{position:absolute;inset:0;background:var(--bg);overflow:hidden}
  .br2-stroke{position:absolute;inset:0;opacity:.12;pointer-events:none}
  .br2-block{position:absolute;left:130px;top:330px;width:1250px}
  .br2-eyebrow{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.42em}
  .br2-block h1{margin-top:40px;font-family:"Noto Serif SC","Songti SC",serif;font-weight:700;
    font-size:var(--fs-hero);line-height:1.15;letter-spacing:.14em;color:var(--ink)}
  .br2-en{margin-top:30px;font-size:var(--fs-body-n);color:var(--gold);letter-spacing:.3em}
  .br2-sub{margin-top:36px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.12em}
  .br2-seal{position:absolute;width:104px;height:104px;background:#A93226;border-radius:10px;
    display:flex;align-items:center;justify-content:center;
    font-family:"Noto Serif SC","Songti SC",serif;font-weight:700;font-size:var(--fs-body-n);
    color:#F7F3E8;letter-spacing:.1em;box-shadow:0 6px 24px rgba(169,50,38,.35)}
  .br2-foot{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .br2-foot .line{width:56px;height:2px;background:var(--gold)}
  .br2-foot span{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.28em}
  .br2-na{position:absolute;right:130px;bottom:74px;font-size:var(--fs-cap);color:var(--gold);letter-spacing:.5em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    b = f"""  <div class="br2-wrap">
    <svg class="br2-stroke" width="1920" height="1080" viewBox="0 0 1920 1080" preserveAspectRatio="none">
      <path d="M120,880 C480,830 760,970 1120,900 S1620,830 1840,900" stroke="var(--gold)" stroke-width="40" fill="none" stroke-linecap="round"/>
      <path d="M240,980 C600,940 900,1020 1300,970" stroke="var(--ink)" stroke-width="18" fill="none" stroke-linecap="round"/>
    </svg>
    <div class="br2-block">
      <div class="br2-eyebrow">{esc(p.get('eyebrow', ''))}</div>
      <h1>{esc(p['title'])}</h1>
      <div class="br2-en">{esc(p.get('en', ''))}</div>
      <div class="br2-sub">{esc(p['sub'])}</div>
    </div>
    <div class="br2-seal" style="right:260px;top:420px">{esc(p.get('seal', '印'))}</div>
    <div class="br2-foot"><div class="line"></div><span>{esc(p['foot'])}</span></div>
    <div class="br2-na">{esc(p.get('corner', ''))}</div>
  </div>
</body>
</html>
"""
    return h + b


# ================= 内容页32（草案 2026-10-06）：观点族 =================

def _status_badge(status):
    """状态文本 → badge 颜色闭集（ink/green/gold/ox），全部走主题令牌。"""
    s = str(status or "")
    if any(k in s for k in ("风险", "延迟", "延期", "超标", "失败", "异常", "预警", "未达", "不足")):
        return "ox"
    if any(k in s for k in ("完成", "达标", "通过", "正常", "优秀", "合格")):
        return "green"
    if any(k in s for k in ("待", "未", "计划")):
        return "ink"
    return "gold"


# ---------- 模板:观点-行动标题页 ----------
def t_statement_assertion(p):
    extra = """
  .sa-sub{position:absolute;left:var(--mx);top:330px;width:var(--cw);font-size:var(--fs-body);
          color:var(--muted);letter-spacing:.06em;line-height:var(--lh-body)}
  .sa-list{position:absolute;left:var(--mx);top:440px;width:var(--cw)}
  .sa-it{padding:28px 0;border-bottom:1px solid var(--line)}
  .sa-it:last-child{border-bottom:none}
  .sa-line{display:flex;align-items:center;gap:26px}
  .sa-num{width:54px;height:54px;flex:none;border-radius:50%;background:var(--gold);color:var(--bg);
          display:flex;align-items:center;justify-content:center;font-size:var(--fs-body-n);font-weight:800}
  .sa-t{font-size:var(--fs-body);font-weight:800;color:var(--ink);line-height:var(--lh-title)}
  .sa-d{margin-top:12px;padding-left:80px;font-size:var(--fs-body);color:var(--muted);line-height:var(--lh-body)}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for i, pt in enumerate(p.get("points") or []):
        d = f'<div class="sa-d">{esc(pt["d"])}</div>' if pt.get("d") else ""
        rows += (f"""    <div class="sa-it"><div class="sa-line"><div class="sa-num">{i+1}</div>"""
                 f"""<div class="sa-t">{esc(pt.get('t', ''))}</div></div>{d}</div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="sa-sub">{esc(p.get('sub', ''))}</div>
  <div class="sa-list">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-点线式 ----------
def t_statement_dotdash(p):
    extra = """
  .dd-list{position:absolute;left:var(--mx);top:380px;width:var(--cw)}
  .dd-it{margin-bottom:46px}
  .dd-b{display:flex;align-items:center;gap:26px}
  .dd-dot{width:22px;height:22px;flex:none;border-radius:50%;background:var(--gold)}
  .dd-btxt{font-size:var(--fs-body);font-weight:800;color:var(--ink);letter-spacing:.04em}
  .dd-ds{margin:14px 0 0 48px}
  .dd-d{display:flex;align-items:center;gap:20px;margin-top:12px}
  .dd-dash{width:34px;height:4px;flex:none;background:var(--gold-soft)}
  .dd-dtxt{font-size:var(--fs-body);color:var(--muted);line-height:var(--lh-body)}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for it in (p.get("items") or []):
        ds = ""
        for d in (it.get("ds") or [])[:4]:
            ds += (f"""      <div class="dd-d"><div class="dd-dash"></div>"""
                   f"""<div class="dd-dtxt">{esc(d)}</div></div>\n""")
        ds = f'    <div class="dd-ds">\n{ds}    </div>\n' if ds else ""
        rows += (f"""    <div class="dd-it"><div class="dd-b"><div class="dd-dot"></div>"""
                 f"""<div class="dd-btxt">{esc(it.get('b', ''))}</div></div>\n{ds}    </div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="dd-list">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-金句独白 ----------
def t_statement_golden(p):
    extra = """
  .gd-mid{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);
          text-align:center;padding:0 220px}
  .gd-rule{width:84px;height:4px;background:var(--gold);margin:0 auto 54px}
  .gd-phrase{font-size:var(--fs-section-title);font-weight:900;color:var(--ink);
             line-height:1.35;letter-spacing:.06em}
  .gd-sub{margin-top:44px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.08em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    sub = f'<div class="gd-sub">{esc(p["sub"])}</div>' if p.get("sub") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  <div class="gd-mid">
    <div class="gd-rule"></div>
    <div class="gd-phrase">{esc(p.get('phrase', ''))}</div>
    {sub}</div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-全幅引言 ----------
def t_quote_full(p):
    extra = """
  .qf-bg{position:absolute;inset:0;background-size:cover;background-position:center}
  .qf-panel{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:1400px;
            padding:90px 110px;text-align:center}
  .qf-panel.box{background:color-mix(in srgb, var(--bg) 88%, transparent)}
  .qf-mark{font-family:Georgia,serif;font-size:var(--fs-hero);color:var(--gold);
           line-height:.6;opacity:.85}
  .qf-quote{margin-top:30px;font-size:var(--fs-body-n);font-weight:700;color:var(--ink);
            line-height:1.7;letter-spacing:.04em}
  .qf-rule{width:120px;height:2px;background:var(--gold);margin:44px auto}
  .qf-author{font-size:var(--fs-body);color:var(--ink);font-weight:700;letter-spacing:.1em}
  .qf-source{margin-top:14px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.1em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    bg = f"""  <div class="qf-bg" style="background-image:{img(p['bgimg'])}"></div>\n""" if p.get("bgimg") else ""
    panel_cls = "qf-panel box" if p.get("bgimg") else "qf-panel"
    src = f'<div class="qf-source">{esc(p["source"])}</div>' if p.get("source") else ""
    b = f"""{bg}  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  <div class="{panel_cls}">
    <div class="qf-mark">&ldquo;</div>
    <div class="qf-quote">{esc(p.get('quote', ''))}</div>
    <div class="qf-rule"></div>
    <div class="qf-author">{esc(p.get('author', ''))}</div>
    {src}</div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-卡片式引用 ----------
def t_quote_card(p):
    extra = """
  .qc-point{position:absolute;left:0;right:0;top:230px;text-align:center;font-size:var(--fs-cap);
            color:var(--gold);letter-spacing:.24em;font-weight:700}
  .qc-card{position:absolute;left:50%;top:54%;transform:translate(-50%,-50%);width:1300px;
           background:var(--card);border:1px solid var(--line);border-top:10px solid var(--gold);
           padding:80px 100px;text-align:center}
  .qc-mark{font-family:Georgia,serif;font-size:var(--fs-hero);color:var(--gold);line-height:.6}
  .qc-quote{margin-top:26px;font-size:var(--fs-body-n);color:var(--ink);line-height:1.75;letter-spacing:.03em}
  .qc-by{margin-top:40px;font-size:var(--fs-body);font-weight:800;color:var(--ink);letter-spacing:.08em}
  .qc-src{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.08em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    point = f'<div class="qc-point">{esc(p["point"])}</div>' if p.get("point") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  {point}
  <div class="qc-card">
    <div class="qc-mark">&ldquo;</div>
    <div class="qc-quote">{esc(p.get('quote', ''))}</div>
    <div class="qc-by">{esc(p.get('by', ''))}</div>
    <div class="qc-src">{esc(p.get('src', ''))}</div></div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-词典条目式 ----------
def t_definition_dict(p):
    extra = """
  .dx-term{position:absolute;left:var(--mx);top:320px;font-size:var(--fs-section-title);
           font-weight:900;color:var(--ink);letter-spacing:.06em;line-height:1.2}
  .dx-en{margin-top:18px;font-family:Georgia,serif;font-size:var(--fs-body-n);
         color:var(--gold);letter-spacing:.2em}
  .dx-rule{position:absolute;left:var(--mx);top:640px;width:var(--cw);height:3px;background:var(--gold)}
  .dx-def{position:absolute;left:var(--mx);top:700px;width:var(--cw);font-size:var(--fs-body-n);
          color:var(--ink);line-height:1.9;letter-spacing:.03em}
  .dx-note{position:absolute;left:var(--mx);right:var(--mx);bottom:130px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    en = f'<div class="dx-en">{esc(p["en"])}</div>' if p.get("en") else ""
    note = (f'  <div class="dx-note concl">{esc(p["note"])}</div>\n') if p.get("note") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  <div class="dx-term">{esc(p.get('term', ''))}{en}</div>
  <div class="dx-rule"></div>
  <div class="dx-def">{esc(p.get('def', ''))}</div>
{note}  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-术语卡片 ----------
def t_definition_terms(p):
    extra = """
  .dt-grid{position:absolute;left:var(--mx);top:400px;width:var(--cw);display:flex;gap:32px}
  .dt-card{flex:1;background:var(--card);border:1px solid var(--line);
           border-top:8px solid var(--green);padding:52px 44px}
  .dt-t{font-size:var(--fs-body-n);font-weight:800;color:var(--ink);letter-spacing:.04em}
  .dt-d{margin-top:20px;font-size:var(--fs-body);color:var(--muted);line-height:1.85}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cards = ""
    for tm in (p.get("terms") or []):
        cards += (f"""    <div class="dt-card"><div class="dt-t">{esc(tm.get('t', ''))}</div>"""
                  f"""<div class="dt-d">{esc(tm.get('d', ''))}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="dt-grid">
{cards}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-痛点图标阵列 ----------
def t_problem_pain(p):
    extra = """
  .pp-grid{position:absolute;left:var(--mx);top:400px;width:var(--cw);display:flex;gap:32px}
  .pp-card{flex:1;background:var(--card);border:1px solid var(--line);padding:56px 40px;text-align:center}
  .pp-ic{width:88px;height:88px;border-radius:50%;border:3px solid var(--ox);color:var(--ox);
         display:flex;align-items:center;justify-content:center;font-size:var(--fs-body-n);
         font-weight:800;margin:0 auto 30px}
  .pp-k{font-size:var(--fs-body);font-weight:800;color:var(--ink);line-height:1.6}
  .pp-q{margin-top:18px;font-size:var(--fs-body-n);font-weight:800;color:var(--ox)}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cards = ""
    for i, pn in enumerate(p.get("pains") or []):
        cards += (f"""    <div class="pp-card"><div class="pp-ic">{i+1}</div>"""
                  f"""<div class="pp-k">{esc(pn.get('k', ''))}</div>"""
                  f"""<div class="pp-q">{esc(pn.get('q', ''))}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="pp-grid">
{cards}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-方案支柱总览 ----------
def t_solution_pillars(p):
    extra = """
  .sp-grid{position:absolute;left:var(--mx);top:400px;width:var(--cw);display:flex;gap:32px}
  .sp-card{flex:1;background:var(--card);border:1px solid var(--line);
           border-top:8px solid var(--gold);padding:56px 44px;text-align:center}
  .sp-badge{width:96px;height:96px;border-radius:50%;background:var(--gold);color:var(--bg);
            display:flex;align-items:center;justify-content:center;
            font-size:var(--fs-body-n);font-weight:800;margin:0 auto}
  .sp-k{margin-top:30px;font-size:var(--fs-body);font-weight:800;color:var(--ink);letter-spacing:.04em}
  .sp-d{margin-top:16px;font-size:var(--fs-cap);color:var(--muted);line-height:1.8}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cards = ""
    for i, pl in enumerate(p.get("pillars") or []):
        cards += (f"""    <div class="sp-card"><div class="sp-badge">{i+1}</div>"""
                  f"""<div class="sp-k">{esc(pl.get('k', ''))}</div>"""
                  f"""<div class="sp-d">{esc(pl.get('d', ''))}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="sp-grid">
{cards}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-特性—价值行 ----------
def t_solution_features(p):
    extra = """
  .sf-list{position:absolute;left:var(--mx);top:380px;width:var(--cw)}
  .sf-row{display:flex;align-items:center;gap:30px;padding:30px 8px;border-bottom:1px solid var(--line)}
  .sf-row:last-child{border-bottom:none}
  .sf-ic{width:64px;height:64px;flex:none;border-radius:16px;background:var(--gold-soft);
         color:var(--bg);display:flex;align-items:center;justify-content:center;
         font-size:var(--fs-body);font-weight:800}
  .sf-f{font-size:var(--fs-body);font-weight:800;color:var(--ink);min-width:280px}
  .sf-v{flex:1;font-size:var(--fs-body);color:var(--muted);line-height:1.7}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for i, ft in enumerate(p.get("feats") or []):
        rows += (f"""    <div class="sf-row"><div class="sf-ic">{i+1}</div>"""
                 f"""<div class="sf-f">{esc(ft.get('f', ''))}</div>"""
                 f"""<div class="sf-v">{esc(ft.get('v', ''))}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="sf-list">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-原理解剖 ----------
def t_solution_how(p):
    extra = """
  .sh-flow{position:absolute;left:var(--mx);top:420px;width:var(--cw);display:flex;align-items:stretch}
  .sh-box{flex:1;background:var(--card);border:2px solid var(--line);padding:48px 40px;position:relative}
  .sh-box.hot{border-color:var(--gold);
              box-shadow:0 0 0 6px color-mix(in srgb, var(--gold) 22%, transparent)}
  .sh-tag{position:absolute;top:-26px;left:40px;background:var(--gold);color:var(--bg);
          font-size:var(--fs-cap);font-weight:800;padding:8px 24px;letter-spacing:.14em}
  .sh-t{font-size:var(--fs-body);font-weight:800;color:var(--ink)}
  .sh-box.hot .sh-t{color:var(--gold)}
  .sh-d{margin-top:16px;font-size:var(--fs-cap);color:var(--muted);line-height:1.8}
  .sh-arr{align-self:center;flex:none;font-size:var(--fs-body-n);color:var(--gold);
          padding:0 18px;font-family:Georgia,serif}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    steps = p.get("steps") or []
    flow = ""
    for i, s in enumerate(steps):
        if i > 0:
            flow += '    <div class="sh-arr">&rarr;</div>\n'
        hot = " hot" if s.get("hot") else ""
        tag = '<div class="sh-tag">改变点</div>' if s.get("hot") else ""
        flow += (f"""    <div class="sh-box{hot}">{tag}<div class="sh-t">{esc(s.get('t', ''))}</div>"""
                 f"""<div class="sh-d">{esc(s.get('d', ''))}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="sh-flow">
{flow}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-任务清单 ----------
def t_checklist_tasks(p):
    extra = """
  .ck-list{position:absolute;left:var(--mx);top:380px;width:var(--cw)}
  .ck-row{display:flex;align-items:center;gap:28px;padding:26px 8px;border-bottom:1px solid var(--line)}
  .ck-row:last-child{border-bottom:none}
  .ck-box{width:40px;height:40px;flex:none;border:3px solid var(--gold);border-radius:8px}
  .ck-t{flex:1;font-size:var(--fs-body);font-weight:700;color:var(--ink)}
  .ck-owner{font-size:var(--fs-cap);color:var(--muted);min-width:220px;letter-spacing:.06em}
  .ck-due{font-size:var(--fs-cap);color:var(--gold);font-weight:700;min-width:240px;
          text-align:right;letter-spacing:.06em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for t in (p.get("tasks") or []):
        rows += (f"""    <div class="ck-row"><div class="ck-box"></div>"""
                 f"""<div class="ck-t">{esc(t.get('t', ''))}</div>"""
                 f"""<div class="ck-owner">{esc(t.get('owner', ''))}</div>"""
                 f"""<div class="ck-due">{esc(t.get('due', ''))}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="ck-list">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-状态记分卡 ----------
def t_scorecard_status(p):
    extra = """
  .ss-list{position:absolute;left:var(--mx);top:380px;width:var(--cw)}
  .ss-row{display:flex;align-items:center;gap:28px;padding:24px 8px;border-bottom:1px solid var(--line)}
  .ss-row:last-child{border-bottom:none}
  .ss-k{flex:1;font-size:var(--fs-body);font-weight:700;color:var(--ink)}
  .ss-badge{flex:none}
  .ss-badge .badge{padding:10px 28px;font-size:var(--fs-cap)}
  .ss-barw{flex:none;display:flex;align-items:center;gap:16px}
  .ss-bar{width:300px;height:16px;background:var(--line);border-radius:8px;overflow:hidden}
  .ss-fill{height:100%;background:var(--gold)}
  .ss-pct{font-size:var(--fs-cap);color:var(--muted);min-width:70px;text-align:right}
  .ss-legend{margin-top:26px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.06em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for it in (p.get("items") or []):
        badge = (f"""<span class="ss-badge"><span class="badge badge {_status_badge(it.get('status'))}">"""
                 f"""{esc(str(it.get('status', '')))}</span></span>""")
        bar = ""
        if it.get("prog") is not None:
            try:
                pv = max(0, min(100, float(it["prog"])))
            except (TypeError, ValueError):
                pv = 0
            bar = (f"""<span class="ss-barw"><span class="ss-bar"><span class="ss-fill" """
                   f"""style="display:block;width:{pv:.0f}%"></span></span>"""
                   f"""<span class="ss-pct">{pv:.0f}%</span></span>""")
        rows += (f"""    <div class="ss-row"><div class="ss-k">{esc(it.get('k', ''))}</div>"""
                 f"""{badge}{bar}</div>\n""")
    legend = f'  <div class="ss-legend">{esc(p["legend"])}</div>\n' if p.get("legend") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="ss-list">
{rows}{legend}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-单一行动 ----------
def t_cta_single(p):
    extra = """
  .ca-mid{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);
          text-align:center;padding:0 200px}
  .ca-action{font-size:var(--fs-section-title);font-weight:900;color:var(--ink);
             line-height:1.35;letter-spacing:.04em}
  .ca-rule{width:84px;height:4px;background:var(--gold);margin:48px auto}
  .ca-meta{display:flex;justify-content:center;gap:100px}
  .ca-m .k{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.24em}
  .ca-m .v{margin-top:12px;font-size:var(--fs-body);font-weight:800;color:var(--ink)}
  .ca-ask{margin-top:44px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    ask = f'<div class="ca-ask">{esc(p["ask"])}</div>' if p.get("ask") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  <div class="ca-mid">
    <div class="ca-action">{esc(p.get('action', ''))}</div>
    <div class="ca-rule"></div>
    <div class="ca-meta">
      <div class="ca-m"><div class="k">责任人</div><div class="v">{esc(p.get('who', ''))}</div></div>
      <div class="ca-m"><div class="k">截止时间</div><div class="v">{esc(p.get('when', ''))}</div></div>
    </div>
    {ask}</div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-下一步清单 ----------
def t_cta_next(p):
    extra = """
  .cn-list{position:absolute;left:var(--mx);top:380px;width:var(--cw)}
  .cn-row{display:flex;align-items:center;gap:30px;padding:28px 0;border-bottom:1px solid var(--line)}
  .cn-row:last-child{border-bottom:none}
  .cn-num{width:72px;height:72px;flex:none;border-radius:50%;background:var(--green);color:var(--bg);
          display:flex;align-items:center;justify-content:center;
          font-size:var(--fs-body-n);font-weight:800}
  .cn-t{flex:1;font-size:var(--fs-body);font-weight:700;color:var(--ink)}
  .cn-od{font-size:var(--fs-cap);color:var(--muted);text-align:right;min-width:380px;letter-spacing:.06em}
  .cn-contact{position:absolute;left:var(--mx);right:var(--mx);bottom:130px;background:var(--card);
              border-left:6px solid var(--gold);padding:26px 34px;
              font-size:var(--fs-body);color:var(--ink);letter-spacing:.04em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for i, s in enumerate(p.get("steps") or []):
        rows += (f"""    <div class="cn-row"><div class="cn-num">{i+1}</div>"""
                 f"""<div class="cn-t">{esc(s.get('t', ''))}</div>"""
                 f"""<div class="cn-od">{esc(s.get('owner', ''))}&nbsp;&nbsp;/&nbsp;&nbsp;{esc(s.get('due', ''))}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="cn-list">
{rows}  </div>
  <div class="cn-contact">{esc(p.get('contact', ''))}</div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-SCR 一页纸 ----------
def t_scr_brief(p):
    extra = """
  .scr-list{position:absolute;left:var(--mx);top:380px;width:var(--cw)}
  .scr-sec{display:flex;gap:36px;margin-bottom:44px;align-items:flex-start}
  .scr-tag{width:96px;height:96px;flex:none;border-radius:50%;display:flex;align-items:center;
           justify-content:center;font-family:Georgia,serif;font-size:var(--fs-body-n);font-weight:800}
  .scr-tag.s{background:var(--green);color:var(--bg)}
  .scr-tag.c{background:var(--ox);color:var(--bg)}
  .scr-tag.r{background:var(--gold);color:var(--bg)}
  .scr-tx{flex:1;font-size:var(--fs-body);color:var(--ink);line-height:1.9;padding-top:14px}
  .scr-sec.r{background:color-mix(in srgb, var(--gold) 10%, transparent);
             border:1px solid var(--gold-soft);padding:28px 32px}
  .scr-sec.r .scr-tx{font-weight:700;padding-top:6px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="scr-list">
    <div class="scr-sec"><div class="scr-tag s">S</div>
      <div class="scr-tx">{esc(p.get('s', ''))}</div></div>
    <div class="scr-sec"><div class="scr-tag c">C</div>
      <div class="scr-tx">{esc(p.get('c', ''))}</div></div>
    <div class="scr-sec r"><div class="scr-tag r">R</div>
      <div class="scr-tx">{esc(p.get('r', ''))}</div></div>
  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-枢纽辐射 ----------
def t_framework_hub(p):
    import math
    spokes = p.get("spokes") or []
    n = len(spokes)
    cx, cy, rx, ry = 960, 620, 600, 250
    lines, nodes = "", ""
    for i, sp in enumerate(spokes):
        a = math.radians(-90 + i * 360.0 / n) if n else 0
        x = cx + rx * math.cos(a)
        y = cy + ry * math.sin(a)
        lines += (f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" '
                  f'stroke="var(--gold-soft)" stroke-width="2"/>')
        d = f'<div class="fh-d">{esc(sp["d"])}</div>' if sp.get("d") else ""
        nodes += (f"""    <div class="fh-node" style="left:{x:.0f}px;top:{y:.0f}px">"""
                  f"""<div class="fh-t">{esc(sp.get('t', ''))}</div>{d}</div>\n""")
    svg = (f'<svg viewBox="0 0 1920 1080" preserveAspectRatio="none">{lines}</svg>') if lines else ""
    extra = """
  .fh-stage{position:absolute;inset:0}
  .fh-stage svg{position:absolute;inset:0;width:100%;height:100%}
  .fh-hub{position:absolute;left:960px;top:620px;transform:translate(-50%,-50%);
          width:340px;height:340px;border-radius:50%;background:var(--green);color:var(--bg);
          display:flex;align-items:center;justify-content:center;text-align:center;
          font-size:var(--fs-body);font-weight:800;padding:44px;letter-spacing:.06em;line-height:1.5}
  .fh-node{position:absolute;transform:translate(-50%,-50%);width:330px;background:var(--card);
           border:1px solid var(--line);border-top:6px solid var(--gold);padding:28px 30px;text-align:center}
  .fh-t{font-size:var(--fs-body);font-weight:800;color:var(--ink)}
  .fh-d{margin-top:10px;font-size:var(--fs-cap);color:var(--muted);line-height:1.7}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="fh-stage">{svg}
    <div class="fh-hub">{esc(p.get('hub', ''))}</div>
{nodes}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-SIPOC ----------
def t_framework_sipoc(p):
    cols = (("供应商", "suppliers", ""), ("输入", "inputs", ""), ("流程", "process", "mid"),
            ("输出", "outputs", ""), ("客户", "customers", ""))
    extra = """
  .sipoc{position:absolute;left:var(--mx);top:380px;width:var(--cw);display:flex;gap:24px}
  .sipoc-col{flex:1;background:var(--card);border:1px solid var(--line)}
  .sipoc-h{background:var(--green);color:var(--bg);text-align:center;padding:18px 8px;
           font-size:var(--fs-body);font-weight:800;letter-spacing:.14em}
  .sipoc-col.mid .sipoc-h{background:var(--gold)}
  .sipoc-it{padding:16px 20px;font-size:var(--fs-cap);color:var(--ink);
            border-bottom:1px solid var(--line);line-height:1.6}
  .sipoc-it:last-child{border-bottom:none}
  .sipoc-it .n{color:var(--gold);font-weight:800;margin-right:10px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    html_cols = ""
    for label, key, cls in cols:
        items = ""
        for j, it in enumerate(p.get(key) or []):
            items += (f"""      <div class="sipoc-it"><span class="n">{j+1}</span>{esc(it)}</div>\n""")
        html_cols += (f"""    <div class="sipoc-col {cls}"><div class="sipoc-h">{label}</div>\n{items}    </div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="sipoc">
{html_cols}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-致谢＋问答 ----------
def t_closing_qa(p):
    extra = """
  .qa-mid{position:absolute;left:0;right:0;top:190px;text-align:center;padding:0 200px}
  .qa-thanks{font-size:var(--fs-section-title);font-weight:900;color:var(--ink);letter-spacing:.1em}
  .qa-contact{margin-top:30px;font-size:var(--fs-body-n);font-weight:700;
              color:var(--gold);letter-spacing:.08em}
  .qa-take{margin:44px auto 0;max-width:1200px;
           background:color-mix(in srgb, var(--gold) 12%, transparent);
           border:1px solid var(--gold-soft);padding:24px 40px;
           font-size:var(--fs-body);color:var(--ink);line-height:1.8}
  .qa-seeds{position:absolute;left:var(--mx);top:770px;width:var(--cw)}
  .qa-seeds .h{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.24em;margin-bottom:14px}
  .qa-seed{display:flex;gap:20px;margin-top:14px;font-size:var(--fs-body);color:var(--ink)}
  .qa-seed .q{color:var(--gold);font-weight:800;flex:none}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    take = f'<div class="qa-take">{esc(p["takeaway"])}</div>' if p.get("takeaway") else ""
    seeds = ""
    if p.get("seeds"):
        seeds = '  <div class="qa-seeds"><div class="h">Q &amp; A</div>\n'
        for i, s in enumerate(p["seeds"]):
            seeds += (f"""    <div class="qa-seed"><span class="q">Q{i+1}</span>"""
                      f"""<span>{esc(s)}</span></div>\n""")
        seeds += "  </div>\n"
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  <div class="qa-mid">
    <div class="qa-thanks">{esc(p.get('thanks', ''))}</div>
    <div class="qa-contact">{esc(p.get('contact', ''))}</div>
    {take}</div>
{seeds}  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ================= 内容页32（草案 2026-10-06）：对比族 =================

# ---------- 模板:对比-镜像双栏 VS ----------
def t_compare_vs(p):
    a_pts = p.get("a_points") or []
    b_pts = p.get("b_points") or []
    extra = """
  .vs-wrap{position:absolute;left:var(--mx);top:400px;width:var(--cw)}
  .vs-line{position:absolute;top:0;bottom:0;left:50%;width:3px;
           background:var(--gold-soft);transform:translateX(-50%)}
  .vs-badge{position:absolute;top:-100px;left:50%;transform:translateX(-50%);
            width:110px;height:110px;border-radius:50%;background:var(--gold);color:var(--bg);
            display:flex;align-items:center;justify-content:center;
            font-family:Georgia,serif;font-size:var(--fs-body-n);font-weight:800}
  .vs-heads{display:grid;grid-template-columns:1fr 140px 1fr;margin-bottom:8px}
  .vs-hta{text-align:right;font-size:var(--fs-body-n);font-weight:800;color:var(--muted);
          letter-spacing:.08em;padding-right:30px}
  .vs-htb{font-size:var(--fs-body-n);font-weight:800;color:var(--green);
          letter-spacing:.08em;padding-left:30px}
  .vs-row{display:grid;grid-template-columns:1fr 140px 1fr;padding:20px 0;
          border-bottom:1px solid var(--line)}
  .vs-row:last-child{border-bottom:none}
  .vs-a{text-align:right;font-size:var(--fs-body);color:var(--muted);padding-right:30px;line-height:1.7}
  .vs-b{font-size:var(--fs-body);color:var(--ink);font-weight:700;padding-left:30px;line-height:1.7}
  .vs-c{text-align:center;color:var(--gold-soft);font-size:var(--fs-body)}
  .vs-verdict{position:absolute;left:var(--mx);right:var(--mx);bottom:130px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for i in range(max(len(a_pts), len(b_pts))):
        a = esc(a_pts[i]) if i < len(a_pts) else ""
        b_ = esc(b_pts[i]) if i < len(b_pts) else ""
        rows += (f"""    <div class="vs-row"><div class="vs-a">{a}</div><div class="vs-c">&middot;</div>"""
                 f"""<div class="vs-b">{b_}</div></div>\n""")
    verdict = (f'  <div class="vs-verdict concl">{esc(p["verdict"])}</div>\n') if p.get("verdict") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="vs-wrap">
    <div class="vs-line"></div><div class="vs-badge">VS</div>
    <div class="vs-heads"><div class="vs-hta">{esc(p.get('a_title', ''))}</div><div></div>
      <div class="vs-htb">{esc(p.get('b_title', ''))}</div></div>
{rows}  </div>
{verdict}  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:对比-前后对比 ----------
def t_compare_beforeafter(p):
    before = p.get("before") or {}
    after = p.get("after") or {}
    extra = """
  .ba-wrap{position:absolute;left:var(--mx);top:380px;width:var(--cw);display:flex;align-items:stretch}
  .ba-panel{flex:1;padding:52px 56px}
  .ba-panel.before{background:var(--card);border:1px solid var(--line)}
  .ba-panel.before .ba-t{color:var(--muted)}
  .ba-panel.after{background:color-mix(in srgb, var(--green) 10%, var(--card));
                  border:2px solid var(--green)}
  .ba-panel.after .ba-t{color:var(--green)}
  .ba-t{font-size:var(--fs-body-n);font-weight:800;letter-spacing:.08em}
  .ba-pt{margin-top:18px;font-size:var(--fs-body);line-height:1.75}
  .ba-panel.before .ba-pt{color:var(--muted)}
  .ba-panel.after .ba-pt{color:var(--ink)}
  .ba-arrow{align-self:center;flex:none;font-size:var(--fs-hero);color:var(--gold);
            padding:0 30px;font-family:Georgia,serif;line-height:1}
  .ba-delta{position:absolute;left:var(--mx);right:var(--mx);bottom:130px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    bpts = "".join(f"""      <div class="ba-pt">{esc(x)}</div>\n""" for x in (before.get("points") or []))
    apts = "".join(f"""      <div class="ba-pt">{esc(x)}</div>\n""" for x in (after.get("points") or []))
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="ba-wrap">
    <div class="ba-panel before"><div class="ba-t">{esc(before.get('t', ''))}</div>
{bpts}    </div>
    <div class="ba-arrow">&rarr;</div>
    <div class="ba-panel after"><div class="ba-t">{esc(after.get('t', ''))}</div>
{apts}    </div>
  </div>
  <div class="ba-delta concl">{esc(p.get('delta', ''))}</div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:对比-优劣清单 ----------
def t_compare_proscons(p):
    extra = """
  .pc-topic{position:absolute;left:var(--mx);top:330px;width:var(--cw);font-size:var(--fs-body);
            color:var(--muted);letter-spacing:.06em}
  .pc-wrap{position:absolute;left:var(--mx);top:400px;width:var(--cw);display:flex;gap:40px}
  .pc-col{flex:1;background:var(--card);border:1px solid var(--line);padding:44px 48px}
  .pc-h{font-size:var(--fs-body-n);font-weight:800;letter-spacing:.1em;margin-bottom:16px}
  .pc-h.pro{color:var(--green)}
  .pc-h.con{color:var(--ox)}
  .pc-it{display:flex;gap:18px;margin-top:16px;font-size:var(--fs-body);line-height:1.7;color:var(--ink)}
  .pc-mark{flex:none;font-weight:800;font-size:var(--fs-body-n)}
  .pc-mark.pro{color:var(--green)}
  .pc-mark.con{color:var(--ox)}
  .pc-verdict{position:absolute;left:var(--mx);right:var(--mx);bottom:130px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    pros = "".join(f"""      <div class="pc-it"><span class="pc-mark pro">&check;</span>"""
                   f"""<span>{esc(x)}</span></div>\n""" for x in (p.get("pros") or []))
    cons = "".join(f"""      <div class="pc-it"><span class="pc-mark con">&times;</span>"""
                   f"""<span>{esc(x)}</span></div>\n""" for x in (p.get("cons") or []))
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="pc-topic">{esc(p.get('topic', ''))}</div>
  <div class="pc-wrap">
    <div class="pc-col"><div class="pc-h pro">优势 PROS</div>
{pros}    </div>
    <div class="pc-col"><div class="pc-h con">劣势 CONS</div>
{cons}    </div>
  </div>
  <div class="pc-verdict concl">{esc(p.get('verdict', ''))}</div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:对比-2×2 矩阵 ----------
def t_matrix_2x2(p):
    quads = list(p.get("quads") or [])
    while len(quads) < 4:
        quads.append({})
    extra = """
  .mx2-stage{position:absolute;left:var(--mx);top:360px;width:var(--cw);height:590px}
  .mx2-y{position:absolute;left:0;top:0;bottom:70px;width:120px;
         display:flex;align-items:center;justify-content:center}
  .mx2-y span{writing-mode:vertical-rl;font-size:var(--fs-cap);color:var(--muted);
              letter-spacing:.24em;font-weight:700}
  .mx2-grid{position:absolute;left:140px;top:0;width:1380px;height:500px;display:grid;
            grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:3px;
            background:var(--line);border:3px solid var(--line)}
  .mx2-q{background:var(--bg);padding:36px 40px;overflow:hidden}
  .mx2-qn{font-size:var(--fs-body);font-weight:800;color:var(--gold);letter-spacing:.08em}
  .mx2-qd{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);line-height:1.7}
  .mx2-qi{margin-top:10px;font-size:var(--fs-body);color:var(--ink);line-height:1.7}
  .mx2-x{position:absolute;left:140px;top:520px;width:1380px;text-align:center;
         font-size:var(--fs-cap);color:var(--muted);letter-spacing:.24em;font-weight:700}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cells = ""
    for q in quads[:4]:
        d = f'<div class="mx2-qd">{esc(q["d"])}</div>' if q.get("d") else ""
        items = "".join(f"""<div class="mx2-qi">&middot;&nbsp;{esc(x)}</div>\n"""
                        for x in (q.get("items") or []))
        cells += (f"""      <div class="mx2-q"><div class="mx2-qn">{esc(q.get('n', ''))}</div>"""
                  f"""{d}\n{items}      </div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="mx2-stage">
    <div class="mx2-y"><span>{esc(p.get('y_axis', ''))}</span></div>
    <div class="mx2-grid">
{cells}    </div>
    <div class="mx2-x">{esc(p.get('x_axis', ''))}</div>
  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:对比-决策记分卡 ----------
def t_scorecard_decision(p):
    extra = """
  .dc-list{position:absolute;left:var(--mx);top:380px;width:var(--cw)}
  .dc-row{display:flex;align-items:center;gap:30px;padding:24px 8px;border-bottom:1px solid var(--line)}
  .dc-row:last-child{border-bottom:none}
  .dc-name{font-size:var(--fs-body);font-weight:800;color:var(--ink);min-width:240px}
  .dc-bar{flex:1;height:22px;background:var(--line);border-radius:11px;overflow:hidden}
  .dc-fill{display:block;height:100%;background:var(--green)}
  .dc-score{font-size:var(--fs-body-n);font-weight:800;color:var(--ink);min-width:200px;text-align:right}
  .dc-note{font-size:var(--fs-cap);color:var(--muted);min-width:340px;text-align:right}
  .dc-winner{position:absolute;left:var(--mx);right:var(--mx);bottom:130px;
             background:color-mix(in srgb, var(--gold) 10%, transparent);
             border:2px solid var(--gold);padding:28px 36px;display:flex;gap:24px;align-items:center}
  .dc-wt{flex:none;font-size:var(--fs-body);font-weight:800;color:var(--gold);letter-spacing:.12em}
  .dc-wx{font-size:var(--fs-body);color:var(--ink);line-height:1.7}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for c in (p.get("cands") or []):
        m = _re.search(r"(\d+(?:\.\d+)?)", str(c.get("score", "")))
        pct = min(100.0, float(m.group(1))) if m else 0.0
        rows += (f"""    <div class="dc-row"><div class="dc-name">{esc(c.get('name', ''))}</div>"""
                 f"""<div class="dc-bar"><span class="dc-fill" style="width:{pct:.0f}%"></span></div>"""
                 f"""<div class="dc-score">{esc(str(c.get('score', '')))}</div>"""
                 f"""<div class="dc-note">{esc(c.get('note', ''))}</div></div>\n""")
    w = p.get("winner")
    if isinstance(w, dict):
        wtxt = esc(w.get("name", "")) + ("：" + esc(w["reason"]) if w.get("reason") else "")
    else:
        wtxt = esc(str(w or ""))
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="dc-list">
{rows}  </div>
  <div class="dc-winner"><div class="dc-wt">胜出</div><div class="dc-wx">{wtxt}</div></div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ================= 内容页32（草案 2026-10-06）：流程族 =================

# ---------- 模板:流程-箭形管道 ----------
def t_flow_chevron(p):
    steps = p.get("steps") or []
    palette = ["green", "gold", "ox", "ink"]
    extra = """
  .chv-flow{position:absolute;left:var(--mx);top:430px;width:var(--cw);display:flex}
  .chv{flex:1;display:flex;flex-direction:column;justify-content:center;min-height:340px;
       padding:44px 64px 44px 88px;
       clip-path:polygon(0 0, calc(100% - 48px) 0, 100% 50%, calc(100% - 48px) 100%, 0 100%, 48px 50%)}
  .chv:first-child{clip-path:polygon(0 0, calc(100% - 48px) 0, 100% 50%, calc(100% - 48px) 100%, 0 100%);
                   padding-left:52px}
  .chv:last-child{clip-path:polygon(0 0, 100% 0, 100% 100%, 0 100%, 48px 50%)}
  .chv + .chv{margin-left:-48px}
  .chv-t{font-size:var(--fs-body);font-weight:800;color:var(--bg);letter-spacing:.06em}
  .chv-d{margin-top:14px;font-size:var(--fs-cap);color:var(--bg);opacity:.85;line-height:1.7}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    segs = ""
    for i, s in enumerate(steps):
        c = palette[i % len(palette)]
        d = f'<div class="chv-d">{esc(s["d"])}</div>' if s.get("d") else ""
        segs += (f"""    <div class="chv" style="background:var(--{c})">"""
                 f"""<div class="chv-t">{esc(s.get('t', ''))}</div>{d}</div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="chv-flow">
{segs}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:流程-泳道图 ----------
def t_flow_swimlane(p):
    extra = """
  .sw-lanes{position:absolute;left:var(--mx);top:380px;width:var(--cw)}
  .sw-lane{display:flex;align-items:stretch}
  .sw-role{flex:none;width:230px;background:var(--green);color:var(--bg);display:flex;
           align-items:center;justify-content:center;font-size:var(--fs-body);font-weight:800;
           letter-spacing:.08em;padding:30px 16px;text-align:center}
  .sw-steps{flex:1;display:flex;align-items:stretch;background:var(--card);
            border:1px solid var(--line);border-left:none;padding:24px 28px}
  .sw-step{flex:1;display:flex;align-items:center;justify-content:center;text-align:center;
           border:2px solid var(--gold-soft);padding:22px 16px;font-size:var(--fs-cap);
           color:var(--ink);line-height:1.6}
  .sw-arr{align-self:center;flex:none;color:var(--gold);font-size:var(--fs-body);
          padding:0 12px;font-family:Georgia,serif}
  .sw-hand{height:54px;display:flex;align-items:center;justify-content:center;gap:16px}
  .sw-hand .ln{width:2px;height:100%;
               background:repeating-linear-gradient(180deg, var(--gold-soft) 0 8px, transparent 8px 16px)}
  .sw-hand .tx{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.2em}
  .sw-note{margin-top:18px;font-size:var(--fs-cap);color:var(--muted);letter-spacing:.06em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    lanes = p.get("lanes") or []
    html = ""
    for li, ln in enumerate(lanes):
        steps = ""
        sts = ln.get("steps") or []
        for si, st in enumerate(sts):
            if si > 0:
                steps += '        <div class="sw-arr">&rarr;</div>\n'
            steps += f"""        <div class="sw-step">{esc(st)}</div>\n"""
        html += (f"""    <div class="sw-lane"><div class="sw-role">{esc(ln.get('role', ''))}</div>"""
                 f"""<div class="sw-steps">\n{steps}      </div></div>\n""")
        if li < len(lanes) - 1:
            html += ('    <div class="sw-hand"><div class="ln"></div>'
                     '<div class="tx">&darr;&nbsp;交接</div><div class="ln"></div></div>\n')
    note = f'    <div class="sw-note">{esc(p["note"])}</div>\n' if p.get("note") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="sw-lanes">
{html}{note}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:流程-纵向时间线 ----------
def t_timeline_vertical(p):
    extra = """
  .tv-list{position:absolute;left:var(--mx);top:380px;width:var(--cw)}
  .tv-rail{position:absolute;left:180px;top:392px;bottom:120px;width:4px;background:var(--gold-soft)}
  .tv-node{position:relative;padding:0 0 60px 280px}
  .tv-node:last-child{padding-bottom:0}
  .tv-dot{position:absolute;left:171px;top:10px;width:22px;height:22px;border-radius:50%;
          background:var(--gold);
          box-shadow:0 0 0 8px color-mix(in srgb, var(--gold) 20%, transparent)}
  .tv-t{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.14em;font-weight:700}
  .tv-h{margin-top:8px;font-size:var(--fs-body);font-weight:800;color:var(--ink)}
  .tv-d{margin-top:8px;font-size:var(--fs-body);color:var(--muted);line-height:var(--lh-body)}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    nodes = ""
    for nd in (p.get("nodes") or []):
        d = f'<div class="tv-d">{esc(nd["d"])}</div>' if nd.get("d") else ""
        nodes += (f"""    <div class="tv-node"><div class="tv-dot"></div>"""
                  f"""<div class="tv-t">{esc(nd.get('t', ''))}</div>"""
                  f"""<div class="tv-h">{esc(nd.get('h', ''))}</div>{d}</div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="tv-rail"></div>
  <div class="tv-list">
{nodes}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:流程-泳道式路线图 ----------
def t_roadmap_swimlane(p):
    quarters = p.get("quarters") or []
    lanes = p.get("lanes") or []
    nq = len(quarters)
    label_w = 300
    cw = 1680
    extra = """
  .rsw{position:absolute;left:var(--mx);top:360px;width:var(--cw)}
  .rsw-ms{position:relative;height:70px;margin-bottom:6px}
  .rsw-ms-it{position:absolute;transform:translateX(-50%);text-align:center}
  .rsw-ms-it .dia{width:18px;height:18px;background:var(--gold);transform:rotate(45deg);margin:0 auto}
  .rsw-ms-it .t{margin-top:8px;font-size:var(--fs-cap);color:var(--muted);white-space:nowrap;letter-spacing:.06em}
  .rsw-grid{position:relative;display:grid}
  .rsw-qh{text-align:center;font-size:var(--fs-cap);color:var(--muted);font-weight:700;
          letter-spacing:.1em;padding:14px 4px;border-left:1px solid var(--line)}
  .rsw-corner{padding:14px 20px}
  .rsw-lname{background:var(--card);border:1px solid var(--line);border-right:none;
             display:flex;align-items:center;padding:20px 24px;
             font-size:var(--fs-body);font-weight:800;color:var(--ink)}
  .rsw-track{position:relative;border:1px solid var(--line);min-height:88px;background:var(--bg)}
  .rsw-bar{position:absolute;top:16px;bottom:16px;background:var(--green);color:var(--bg);
           border-radius:34px;display:flex;align-items:center;padding:0 26px;
           font-size:var(--fs-cap);font-weight:700;white-space:nowrap;overflow:hidden;letter-spacing:.04em}
  .rsw-bar.prop{background:color-mix(in srgb, var(--gold) 18%, var(--card));
               border:2px dashed var(--gold);color:var(--ink)}
  .rsw-now{position:absolute;top:0;bottom:0;width:3px;background:var(--ox);z-index:2}
  .rsw-now .tag{position:absolute;top:-6px;left:50%;transform:translate(-50%,-100%);
                background:var(--ox);color:var(--bg);font-size:var(--fs-cap);font-weight:800;
                padding:6px 16px;letter-spacing:.1em;white-space:nowrap}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    body = ""
    if nq and lanes:
        grid_style = f"grid-template-columns:{label_w}px repeat({nq},1fr)"
        # 里程碑
        ms = ""
        for m_ in (p.get("milestones") or []):
            try:
                q = max(0, min(nq - 1, int(m_.get("q", 0))))
            except (TypeError, ValueError):
                q = 0
            x = label_w + (q + 0.5) / nq * (cw - label_w)
            ms += (f"""    <div class="rsw-ms-it" style="left:{x:.0f}px">"""
                   f"""<div class="dia"></div><div class="t">{esc(m_.get('t', ''))}</div></div>\n""")
        ms = f'  <div class="rsw-ms">\n{ms}  </div>\n' if ms else ""
        # 表头
        qh = '    <div class="rsw-corner"></div>\n' + "".join(
            f"""    <div class="rsw-qh">{esc(q)}</div>\n""" for q in quarters)
        # 泳道
        rows = ""
        for ln in lanes:
            bars = ""
            for b_ in (ln.get("bars") or []):
                try:
                    q0 = max(0, min(nq - 1, int(b_.get("q0", 0))))
                    q1 = max(q0, min(nq - 1, int(b_.get("q1", q0))))
                except (TypeError, ValueError):
                    q0, q1 = 0, 0
                left = (q0 / nq) * 100
                width = ((q1 - q0 + 1) / nq) * 100
                cls = "" if b_.get("confirmed", True) else " prop"
                bars += (f"""        <div class="rsw-bar{cls}" style="left:{left:.1f}%;width:{width:.1f}%">"""
                         f"""{esc(b_.get('t', ''))}</div>\n""")
            rows += (f"""    <div class="rsw-lname">{esc(ln.get('name', ''))}</div>"""
                     f"""<div class="rsw-track">\n{bars}    </div>\n""")
        # NOW 线
        nowline = ""
        if p.get("now") is not None:
            try:
                nq_now = max(0, min(nq - 1, int(p["now"])))
                x = label_w + (nq_now + 0.5) / nq * (cw - label_w)
                nowline = (f"""    <div class="rsw-now" style="left:{x:.0f}px">"""
                           f"""<div class="tag">NOW</div></div>\n""")
            except (TypeError, ValueError):
                pass
        body = (f"{ms}  <div class=\"rsw-grid\" style=\"{grid_style}\">\n{qh}{rows}{nowline}  </div>\n")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="rsw">
{body}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ================= 内容页32（草案 2026-10-06）：图文族 =================

# ---------- 模板:图文-PSR 三段面板 ----------
def t_case_psr(p):
    results = p.get("results") or []
    extra = """
  .psr-img{position:absolute;left:var(--mx);top:350px;width:var(--cw);height:270px;
           background-size:cover;background-position:center}
  .psr-cap{position:absolute;left:var(--mx);top:630px;width:var(--cw)}
  .psr-panels{position:absolute;left:var(--mx);top:690px;width:var(--cw);display:flex;gap:28px}
  .psr-p{flex:1;padding:34px 38px}
  .psr-p.problem{background:var(--card);border:1px solid var(--line)}
  .psr-p.solution{background:var(--card);border-left:8px solid var(--gold)}
  .psr-p.results{background:color-mix(in srgb, var(--green) 8%, var(--card));
                 border:1px solid var(--green)}
  .psr-h{font-size:var(--fs-cap);font-weight:800;letter-spacing:.24em;margin-bottom:16px}
  .psr-p.problem .psr-h{color:var(--muted)}
  .psr-p.solution .psr-h{color:var(--gold)}
  .psr-p.results .psr-h{color:var(--green)}
  .psr-tx{font-size:var(--fs-body);color:var(--ink);line-height:1.8}
  .psr-kpi{margin-bottom:22px}
  .psr-kpi:last-child{margin-bottom:0}
  .psr-k{font-size:var(--fs-cap);color:var(--muted);letter-spacing:.1em}
  .psr-v{margin-top:6px;font-size:var(--fs-body-n);font-weight:800;color:var(--ink)}
  .psr-v .arr{color:var(--gold);margin:0 14px}
  .psr-v .after{color:var(--green)}
  .psr-tb{display:inline-block;margin-left:16px;padding:6px 18px;background:var(--green);
          color:var(--bg);font-size:var(--fs-cap);font-weight:700;letter-spacing:.1em}
  .psr-quote{position:absolute;left:var(--mx);right:var(--mx);bottom:130px;
             border-left:6px solid var(--gold-soft);padding:6px 0 6px 28px;
             font-size:var(--fs-cap);color:var(--muted);line-height:1.8}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cap = f'  <div class="psr-cap cap">{esc(p["cap"])}</div>\n' if p.get("cap") else ""
    kpis = ""
    for r in results:
        kpis += (f"""      <div class="psr-kpi"><div class="psr-k">{esc(r.get('k', ''))}</div>"""
                 f"""<div class="psr-v">{esc(r.get('before', ''))}"""
                 f"""<span class="arr">&rarr;</span>"""
                 f"""<span class="after">{esc(r.get('after', ''))}</span></div></div>\n""")
    tb = f'<span class="psr-tb">{esc(p["timebox"])}</span>' if p.get("timebox") else ""
    quote = (f'  <div class="psr-quote">&ldquo;{esc(p["quote"])}&rdquo;</div>\n') if p.get("quote") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="psr-img photo{_maskcls(p)}" style="background-image:{img(p.get('img'))}"></div>
{cap}  <div class="psr-panels">
    <div class="psr-p problem"><div class="psr-h">PROBLEM</div>
      <div class="psr-tx">{esc(p.get('problem', ''))}</div></div>
    <div class="psr-p solution"><div class="psr-h">SOLUTION</div>
      <div class="psr-tx">{esc(p.get('solution', ''))}</div></div>
    <div class="psr-p results"><div class="psr-h">RESULTS{tb}</div>
{kpis}    </div>
  </div>
{quote}  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:图文-转变弧 ----------
def t_case_arc(p):
    import math
    stages = p.get("stages") or []
    n = len(stages)
    x0, x1, base_y, amp = 90, 1590, 780, 210
    svg, nodes, dots = "", "", ""
    if n >= 2:
        pts = []
        for i in range(n):
            t = i / (n - 1)
            x = x0 + t * (x1 - x0)
            y = base_y - math.sin(math.pi * t) * amp
            pts.append((x, y))
        d = (f"M {pts[0][0]:.0f},{pts[0][1]:.0f} Q 840,{base_y - 2 * amp:.0f} "
             f"{pts[-1][0]:.0f},{pts[-1][1]:.0f}")
        svg = (f'<svg viewBox="0 0 1920 1080" preserveAspectRatio="none">'
               f'<path d="{d}" fill="none" stroke="var(--gold-soft)" '
               f'stroke-width="4"/></svg>')
        for i, st in enumerate(stages):
            x, y = pts[i]
            tp = (i == 1)
            cls = " arc-node tp" if tp else " arc-node"
            tag = '<div class="arc-tag">转折点</div>' if tp else ""
            nodes += (f"""    <div class="{cls.strip()}" style="left:{x:.0f}px;top:{y - 30:.0f}px">"""
                      f"""{tag}<div class="arc-k">{esc(st.get('k', ''))}</div>"""
                      f"""<div class="arc-d">{esc(st.get('d', ''))}</div></div>\n""")
            dots += (f"""    <div class="arc-dot" style="left:{x:.0f}px;top:{y:.0f}px"></div>\n""")
    extra = """
  .arc-stage{position:absolute;inset:0}
  .arc-stage svg{position:absolute;inset:0;width:100%;height:100%}
  .arc-node{position:absolute;transform:translate(-50%,-100%);width:330px;background:var(--card);
            border:1px solid var(--line);padding:30px 32px}
  .arc-node.tp{border:2px solid var(--gold);
               box-shadow:0 0 0 6px color-mix(in srgb, var(--gold) 18%, transparent)}
  .arc-tag{display:inline-block;background:var(--gold);color:var(--bg);font-size:var(--fs-cap);
           font-weight:800;letter-spacing:.14em;padding:6px 18px;margin-bottom:14px}
  .arc-k{font-size:var(--fs-body);font-weight:800;color:var(--ink)}
  .arc-node.tp .arc-k{color:var(--gold)}
  .arc-d{margin-top:12px;font-size:var(--fs-cap);color:var(--muted);line-height:1.8}
  .arc-dot{position:absolute;transform:translate(-50%,-50%);width:26px;height:26px;
           border-radius:50%;background:var(--gold);z-index:2}
  .arc-fig{position:absolute;right:var(--mx);top:360px;width:380px;height:220px;
           background-size:cover;background-position:center}
  .arc-figcap{position:absolute;right:var(--mx);top:590px;width:380px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    fig = ""
    if p.get("img"):
        fig = (f"""  <div class="arc-fig photo{_maskcls(p)}" style="background-image:{img(p['img'])}"></div>\n"""
               f"""  <div class="arc-figcap cap">{esc(p.get('cap', ''))}</div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
{fig}  <div class="arc-stage">{svg}
{dots}{nodes}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:图文-证言式 ----------
def t_testimonial(p):
    extra = """
  .tm-photo{position:absolute;left:var(--mx);top:400px;width:380px;height:380px;
            border-radius:50%;background-size:cover;background-position:center;
            outline:1px solid var(--line)}
  .tm-cap{position:absolute;left:var(--mx);top:800px;width:380px}
  .tm-body{position:absolute;left:620px;top:380px;width:1180px}
  .tm-mark{font-family:Georgia,serif;font-size:var(--fs-hero);color:var(--gold);line-height:.6}
  .tm-quote{margin-top:20px;font-size:var(--fs-body-n);color:var(--ink);line-height:1.8;letter-spacing:.02em}
  .tm-name{margin-top:36px;font-size:var(--fs-body);font-weight:800;color:var(--ink);letter-spacing:.04em}
  .tm-result{margin-top:26px;display:flex;align-items:baseline;gap:24px}
  .tm-rv{font-size:var(--fs-section-title);font-weight:900;color:var(--gold);line-height:1}
  .tm-rd{font-size:var(--fs-body);color:var(--muted);line-height:1.7}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    mask = _maskcls(p)
    radius = "" if mask else 'border-radius:50%;'
    photo = (f"""  <div class="tm-photo{mask}" style="background-image:{img(p.get('photo'))};{radius}"></div>\n""")
    cap = f'  <div class="tm-cap cap">{esc(p["cap"])}</div>\n' if p.get("cap") else ""
    r = p.get("result")
    if isinstance(r, dict):
        result = (f"""    <div class="tm-result"><div class="tm-rv">{esc(r.get('v', ''))}</div>"""
                  f"""<div class="tm-rd">{esc(r.get('d', ''))}</div></div>\n""")
    else:
        result = (f"""    <div class="tm-result"><div class="tm-rd" style="font-size:var(--fs-body-n);"""
                  f"""font-weight:800;color:var(--ink)">{esc(str(r or ''))}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
{photo}{cap}  <div class="tm-body">
    <div class="tm-mark">&ldquo;</div>
    <div class="tm-quote">{esc(p.get('quote', ''))}</div>
    <div class="tm-name">{esc(p.get('name', ''))}</div>
{result}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:图文-现状快照分屏 ----------
def t_problem_snapshot(p):
    extra = """
  .psnap-img{position:absolute;left:var(--mx);top:360px;width:780px;height:560px;
             background-size:cover;background-position:center;filter:grayscale(1)}
  .psnap-cap{position:absolute;left:var(--mx);top:930px;width:780px}
  .psnap-list{position:absolute;left:1020px;top:390px;width:780px}
  .psnap-it{display:flex;gap:24px;margin-bottom:44px}
  .psnap-it:last-child{margin-bottom:0}
  .psnap-sq{width:26px;height:26px;flex:none;background:var(--ox);margin-top:14px}
  .psnap-tx{font-size:var(--fs-body);color:var(--ink);line-height:1.8;font-weight:700}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cap = f'  <div class="psnap-cap cap">{esc(p["cap"])}</div>\n' if p.get("cap") else ""
    items = ""
    for pn in (p.get("pains") or []):
        items += (f"""    <div class="psnap-it"><div class="psnap-sq"></div>"""
                  f"""<div class="psnap-tx">{esc(pn)}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="psnap-img photo{_maskcls(p)}" style="background-image:{img(p.get('img'))}"></div>
{cap}  <div class="psnap-list">
{items}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b



# ================= 结束页3（草案 2026-10-06）：回顾锚点 / 行动收尾·决策型 / 转附录 =================

# ---------- 模板:观点-回顾锚点 ----------
def t_closing_takeaway(p):
    extra = """
  .tk-mid{position:absolute;left:0;right:0;top:330px;text-align:center;padding:0 220px}
  .tk-take{font-size:var(--fs-hero);font-weight:900;color:var(--ink);line-height:1.5}
  .tk-thanks{margin-top:36px;font-size:var(--fs-body);color:var(--muted);letter-spacing:.2em}
  .tk-contact{margin-top:18px;font-size:var(--fs-body-n);font-weight:700;color:var(--gold);
              letter-spacing:.06em}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    thanks = (f'<div class="tk-thanks">{esc(p["thanks"])}</div>') if p.get("thanks") else ""
    contact = (f'<div class="tk-contact">{esc(p["contact"])}</div>') if p.get("contact") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  <div class="tk-mid">
    <div class="tk-take">{esc(p['takeaway'])}</div>
    {thanks}
    {contact}</div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-行动收尾·决策型 ----------
def t_closing_cta(p):
    pts = p.get("points") or []
    extra = """
  .cc-dec{position:absolute;left:var(--mx);top:290px;width:var(--cw);
          font-size:var(--fs-section-title);font-weight:900;color:var(--ink);line-height:1.5}
  .cc-pts{position:absolute;left:var(--mx);top:460px;width:var(--cw)}
  .cc-pt{display:flex;gap:18px;margin-top:16px;font-size:var(--fs-body);color:var(--ink);
         line-height:1.7}
  .cc-pt .n{color:var(--gold);font-weight:800;flex:none}
  .cc-ask{position:absolute;left:var(--mx);right:var(--mx);bottom:300px;
          background:color-mix(in srgb, var(--gold) 12%, transparent);
          border:1px solid var(--gold-soft);padding:26px 40px;
          font-size:var(--fs-body-n);font-weight:800;color:var(--ink);line-height:1.7}
  .cc-bliss{position:absolute;left:var(--mx);right:var(--mx);bottom:170px;text-align:center;
            font-size:var(--fs-body);color:var(--muted);font-style:italic}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for i, s in enumerate(pts):
        rows += (f"""    <div class="cc-pt"><span class="n">{i+1}</span>"""
                 f"""<span>{esc(s)}</span></div>\n""")
    bliss = (f'  <div class="cc-bliss">{esc(p["bliss"])}</div>\n') if p.get("bliss") else ""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  <div class="cc-dec">{esc(p['decision'])}</div>
  <div class="cc-pts">
{rows}  </div>
  <div class="cc-ask">{esc(p['ask'])}</div>
{bliss}  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:章节-转附录 ----------
def t_closing_appendix(p):
    items = p.get("items") or []
    extra = """
  .ap-title{position:absolute;left:var(--mx);top:300px;font-size:var(--fs-section-title);
            font-weight:900;color:var(--ink);letter-spacing:.1em}
  .ap-note{position:absolute;left:var(--mx);top:400px;font-size:var(--fs-body);color:var(--muted)}
  .ap-items{position:absolute;left:var(--mx);top:500px;width:var(--cw)}
  .ap-it{display:flex;gap:20px;align-items:baseline;padding:20px 0;
         border-bottom:1px solid var(--line)}
  .ap-it .idx{color:var(--gold);font-weight:800;font-size:var(--fs-body-n);flex:none}
  .ap-it .t{font-size:var(--fs-body-n);font-weight:800;color:var(--ink)}
  .ap-it .d{font-size:var(--fs-body);color:var(--muted)}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    note = (f'<div class="ap-note">{esc(p["note"])}</div>') if p.get("note") else ""
    rows = ""
    for i, it in enumerate(items):
        t = esc(it.get("t", "")) if isinstance(it, dict) else esc(it)
        d = esc(it.get("d", "")) if isinstance(it, dict) and it.get("d") else ""
        dhtml = f'<span class="d">{d}</span>' if d else ""
        rows += (f"""    <div class="ap-it"><span class="idx">A{i+1}</span>"""
                 f"""<span class="t">{t}</span>{dhtml}</div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  <div class="ap-title">{esc(p['title'])}</div>
  {note}
  <div class="ap-items">
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b



    return h + b


# ================= 补缺4（草案 2026-10-06）：组织架构 / 交集图 / 人物介绍 / 纵向步骤 =================

# ---------- 模板:观点-组织架构 ----------
def t_org_chart(p):
    tiers = p.get("tiers") or []
    extra = """
  .oc-tiers{position:absolute;left:var(--mx);top:360px;width:var(--cw);
            display:flex;flex-direction:column;align-items:center}
  .oc-tier{display:flex;gap:48px;justify-content:center;flex-wrap:wrap}
  .oc-node{min-width:200px;max-width:340px;text-align:center;background:var(--card);
           border-top:4px solid var(--gold);padding:20px 30px;
           font-size:var(--fs-body-n);font-weight:800;color:var(--ink);line-height:1.6}
  .oc-tier:first-child .oc-node{border-top-color:var(--green)}
  .oc-link{width:2px;height:44px;background:var(--line);flex:none}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    body = ""
    for ti, tier in enumerate(tiers):
        nodes = "".join(f'<div class="oc-node">{esc(str(n))}</div>' for n in tier)
        body += f'    <div class="oc-tier">{nodes}</div>\n'
        if ti < len(tiers) - 1:
            body += '    <div class="oc-link"></div>\n'
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  <div class="hd"><h1>{esc(p['title'])}</h1></div>
  <div class="oc-tiers">
{body}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:观点-交集图 ----------
def t_venn(p):
    sets = p.get("sets") or []
    zones = p.get("zones") or []
    n = len(sets)
    # 圆位置：2圆左右交叠；3圆品字形
    if n == 2:
        pos = [(250, 60), (590, 60)]
    else:
        pos = [(330, 40), (610, 40), (470, 250)]
    cols = ["gold", "green", "ink"]
    extra = """
  .vn-stage{position:absolute;left:360px;top:340px;width:1200px;height:560px}
  .vn-c{position:absolute;width:440px;height:440px;border-radius:50%;
        display:flex;align-items:flex-start;justify-content:center}
  .vn-c .lb{margin-top:36px;font-size:var(--fs-body-n);font-weight:800;color:var(--ink);
            background:var(--bg);padding:6px 18px}
  .vn-zones{position:absolute;left:var(--mx);top:940px;width:var(--cw)}
  .vn-z{display:flex;gap:20px;margin-top:14px;font-size:var(--fs-body);color:var(--ink);
        line-height:1.7}
  .vn-z .zl{color:var(--gold);font-weight:800;flex:none}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    circles = ""
    for i, s in enumerate(sets[:3]):
        x, y = pos[i]
        c = cols[i % 3]
        label = esc(s.get("label", "")) if isinstance(s, dict) else esc(str(s))
        circles += (f"""    <div class="vn-c" style="left:{x}px;top:{y}px;"""
                    f"""background:color-mix(in srgb, var(--{c}) 18%, transparent);"""
                    f"""border:3px solid var(--{c});">"""
                    f"""<div class="lb">{label}</div></div>\n""")
    zrows = ""
    for z in zones:
        zl = esc(z.get("label", "")) if isinstance(z, dict) else ""
        zd = esc(z.get("d", "")) if isinstance(z, dict) else esc(str(z))
        zrows += (f"""    <div class="vn-z"><span class="zl">{zl}</span>"""
                  f"""<span>{zd}</span></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  <div class="hd"><h1>{esc(p['title'])}</h1></div>
  <div class="vn-stage">
{circles}  </div>
  <div class="vn-zones">
{zrows}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:图文-人物介绍 ----------
def t_team_grid(p):
    # 2026-10-06 跑即完善：标题曾放在无定位的 .hd div（骨架无此样式），导致顶到页眉区；现与其它模板一致放 .head 内
    ms = p.get("members") or []
    mask = _maskcls(p)
    radius = "" if mask else "border-radius:50%;"
    extra = """
  .tg-row{position:absolute;left:var(--mx);top:400px;width:var(--cw);
          display:flex;gap:60px;justify-content:center}
  .tg-card{width:380px;text-align:center}
  .tg-photo{width:240px;height:240px;margin:0 auto;background-size:cover;
            background-position:center;outline:1px solid var(--line)}
  .tg-name{margin-top:28px;font-size:var(--fs-body-n);font-weight:900;color:var(--ink);
           letter-spacing:.04em}
  .tg-role{margin-top:10px;font-size:var(--fs-body);font-weight:700;color:var(--gold)}
  .tg-bio{margin-top:14px;font-size:var(--fs-body);color:var(--muted);line-height:1.8}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    cards = ""
    for m in ms[:4]:
        photo = (f"""<div class="tg-photo{mask}" """
                 f"""style="background-image:{img(m.get('photo'))};{radius}"></div>""")
        bio = (f'<div class="tg-bio">{esc(m.get("bio", ""))}</div>'
               if m.get("bio") else "")
        cards += (f"""    <div class="tg-card">{photo}"""
                  f"""<div class="tg-name">{esc(m.get('name', ''))}</div>"""
                  f"""<div class="tg-role">{esc(m.get('role', ''))}</div>{bio}</div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="tg-row">
{cards}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


# ---------- 模板:流程-纵向步骤 ----------
def t_flow_vertical(p):
    steps = p.get("steps") or []
    extra = """
  .fv-list{position:absolute;left:var(--mx);top:360px;width:var(--cw)}
  .fv-rail{position:absolute;left:34px;top:20px;bottom:20px;width:3px;background:var(--line)}
  .fv-it{position:relative;display:flex;gap:36px;margin-bottom:52px}
  .fv-it:last-child{margin-bottom:0}
  .fv-dot{width:72px;height:72px;flex:none;border-radius:50%;background:var(--gold);
          color:var(--bg);display:flex;align-items:center;justify-content:center;
          font-size:var(--fs-body-n);font-weight:900;z-index:1}
  .fv-tx{padding-top:6px}
  .fv-t{font-size:var(--fs-body-n);font-weight:800;color:var(--ink)}
  .fv-d{margin-top:10px;font-size:var(--fs-body);color:var(--muted);line-height:1.8}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls=_bgcls(p, ""))
    rows = ""
    for i, s in enumerate(steps):
        t = esc(s.get("t", "")) if isinstance(s, dict) else esc(str(s))
        d = esc(s.get("d", "")) if isinstance(s, dict) else ""
        dhtml = f'<div class="fv-d">{d}</div>' if d else ""
        rows += (f"""    <div class="fv-it"><div class="fv-dot">{i+1}</div>"""
                 f"""<div class="fv-tx"><div class="fv-t">{t}</div>{dhtml}</div></div>\n""")
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div></div>
  <div class="hd"><h1>{esc(p['title'])}</h1></div>
  <div class="fv-list"><div class="fv-rail"></div>
{rows}  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


TEMPLATES = {
    "cover": t_cover,
    "cover_split": t_cover_split,
    "toc_grid": t_toc_grid,
    "toc_bignum": t_toc_bignum,
    "toc_curve": t_toc_curve,
    "toc_icon": t_toc_icon,
    "toc_image": t_toc_image,
    "toc_list": t_toc_list,
    "toc_magazine": t_toc_magazine,
    "toc_minimal": t_toc_minimal,
    "toc_roadmap": t_toc_roadmap,
    "toc_split": t_toc_split,
    "toc_tabs": t_toc_tabs,
    "toc_tb": t_toc_tb,
    "section": t_section,
    "section_accent": t_section_accent,
    "section_band": t_section_band,
    "section_bridge": t_section_bridge,
    "section_duo": t_section_duo,
    "section_icon": t_section_icon,
    "section_image": t_section_image,
    "section_minimal": t_section_minimal,
    "section_progress": t_section_progress,
    "section_reuse": t_section_reuse,
    "section_split": t_section_split,
    "section_statement": t_section_statement,
    "photo_props": t_photo_props,
    "photo_chain": t_photo_chain,
    "table_compare": t_table_compare,
    "flow_branch": t_flow_branch,
    "flow_cycle": t_flow_cycle,
    "timeline": t_timeline,
    "cards3": t_cards3,
    "stepper": t_stepper,
    "equation_hero": t_equation_hero,
    "chart": t_chart,
    "chart_annotated": t_chart_annotated,
    "chart_bullet": t_chart_bullet,
    "chart_combo": t_chart_combo,
    "chart_dashboard": t_chart_dashboard,
    "chart_dualpanel": t_chart_dualpanel,
    "chart_dumbbell": t_chart_dumbbell,
    "chart_map": t_chart_map,
    "chart_multiples": t_chart_multiples,
    "chart_pareto": t_chart_pareto,
    "chart_rail": t_chart_rail,
    "chart_ranked": t_chart_ranked,
    "chart_stacked": t_chart_stacked,
    "chart_table": t_chart_table,
    "chart_waterfall": t_chart_waterfall,
    "kpi_hero": t_kpi_hero,
    "infographic": t_infographic,
    "compare_bars": t_compare_bars,
    "number_hero": t_number_hero,
    "cover_typo": t_cover_typo,
    "cover_minimal": t_cover_minimal,
    "cover_block": t_cover_block,
    "cover_duo": t_cover_duo,
    "cover_diagonal": t_cover_diagonal,
    "cover_brand": t_cover_brand,
    "cover_magazine": t_cover_magazine,
    "cover_lux": t_cover_lux,
    "cover_collage": t_cover_collage,
    "cover_crop": t_cover_crop,
    "cover_anchor": t_cover_anchor,
    "cover_fusion": t_cover_fusion,
    "cover_band": t_cover_band,
    "cover_brush": t_cover_brush,
    # ---- 内容页32（草案 2026-10-06）----
    "statement_assertion": t_statement_assertion,
    "statement_dotdash": t_statement_dotdash,
    "statement_golden": t_statement_golden,
    "quote_full": t_quote_full,
    "quote_card": t_quote_card,
    "definition_dict": t_definition_dict,
    "definition_terms": t_definition_terms,
    "problem_pain": t_problem_pain,
    "solution_pillars": t_solution_pillars,
    "solution_features": t_solution_features,
    "solution_how": t_solution_how,
    "checklist_tasks": t_checklist_tasks,
    "scorecard_status": t_scorecard_status,
    "cta_single": t_cta_single,
    "cta_next": t_cta_next,
    "scr_brief": t_scr_brief,
    "framework_hub": t_framework_hub,
    "framework_sipoc": t_framework_sipoc,
    "closing_qa": t_closing_qa,
    "closing_takeaway": t_closing_takeaway,
    "closing_cta": t_closing_cta,
    "closing_appendix": t_closing_appendix,
    "org_chart": t_org_chart,
    "venn": t_venn,
    "team_grid": t_team_grid,
    "flow_vertical": t_flow_vertical,
    "compare_vs": t_compare_vs,
    "compare_beforeafter": t_compare_beforeafter,
    "compare_proscons": t_compare_proscons,
    "matrix_2x2": t_matrix_2x2,
    "scorecard_decision": t_scorecard_decision,
    "flow_chevron": t_flow_chevron,
    "flow_swimlane": t_flow_swimlane,
    "timeline_vertical": t_timeline_vertical,
    "roadmap_swimlane": t_roadmap_swimlane,
    "case_psr": t_case_psr,
    "case_arc": t_case_arc,
    "testimonial": t_testimonial,
    "problem_snapshot": t_problem_snapshot,
}


def _body_deco(html, tpl):
    # 2026-10-06：body 追加 t-<tpl> / th-<主题> 类，供骨架"主题装饰层"做页型级点缀（印章/红日等）。
    # 2026-10-06 修：必须锚定 </head> 后的真 body——主题 CSS 注释里含有 "<body class=" 示例文本，
    # 直接 replace 会误命中注释，导致真 body 没挂类、装饰全灭。
    tag = '</head>\n<body class="'
    if tag in html:
        return html.replace(tag, '</head>\n<body class="t-%s th-%s '
                            % (tpl, THEME_NAME), 1)
    return html.replace('<body class="', '<body class="t-%s th-%s '
                        % (tpl, THEME_NAME), 1)


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == "--预览":
        # 布局预览模式：python 页面生成.py --预览 草案.json [预览目录]
        # 草案.json 为单个页面 dict 或 list；只渲染布局，不管最终文案；
        # 不碰 pages.json，HTML 输出到 <项目>/页/_预览/。
        if len(argv) < 2:
            die("用法: python 页面生成.py --预览 <草案.json> [预览目录]", code=USAGE)
        proj = project_dir()
        drafts = read_json(argv[1])
        if isinstance(drafts, dict):
            drafts = [drafts]
        outdir = (argv[2] if len(argv) > 2
                  else os.path.join(proj, "页", "_预览"))
        os.makedirs(outdir, exist_ok=True)
        for p in drafts:
            if p["tpl"] not in TEMPLATES:
                die("未知页型 tpl=%r，合法取值为: %s"
                    % (p["tpl"], sorted(TEMPLATES)), code=FAIL)
            html = _body_deco(TEMPLATES[p["tpl"]](p), p["tpl"])
            out = os.path.join(outdir, p["id"] + ".html")
            io.open(out, "w", encoding="utf-8").write(html)
            print("预览", out)
        return
    only = argv[0] if argv else None
    proj = project_dir()
    print("项目:", proj)
    print("主题:", theme_css_path())
    pages = read_json(os.path.join(proj, "页", "pages.json"))
    for p in pages:
        if only and p["id"] != only:
            continue
        if p["tpl"] not in TEMPLATES:
            # 未知页型：直接拒，不抛 KeyError（数据规约：tpl 为闭集）
            die("未知页型 tpl=%r（页面 %s），合法取值为: %s"
                % (p["tpl"], p.get("id"), sorted(TEMPLATES)), code=FAIL)
        html = _body_deco(TEMPLATES[p["tpl"]](p), p["tpl"])
        out = os.path.join(proj, "页", p["id"] + ".html")
        io.open(out, "w", encoding="utf-8").write(html)
        print("生成", p["id"] + ".html")


if __name__ == "__main__":
    main()
