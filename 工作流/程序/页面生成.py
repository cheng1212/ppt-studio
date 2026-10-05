# -*- coding: utf-8 -*-
"""page.py — SODIUM 课件页面生成器：页面=数据，布局=模板函数。

用法:
  python page.py                 # 按 pages.json 重新生成全部 HTML
  python page.py P4              # 只生成指定页 id
  python page.py --预览 草案.json [预览目录]
                                 # 布局预览：渲染草案数据到 页/_预览/，不碰 pages.json

布局模板（对应库内页型卡）:
  cover        封面（满版图压字）
  toc_grid     目录（2×2 带图卡）
  section      章节页（深底 ghost 编号）
  photo_props  图文性质页（左图右色块标签行 + 结论条）
  photo_chain  图文因果页（左图右编号链 + 提示框）
  table_compare 对比表页（多对象横向对比 + 结论条）
  flow_branch  分支流程图（同一起点 → 条件分支 → 不同结果）
  flow_cycle   循环关系图（节点环形排布 + 带标签箭头）
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
  .cards3{position:absolute;left:var(--mx);top:360px;width:var(--cw);display:flex;gap:36px}
  .card3{flex:1;background:var(--card);border:1px solid var(--line);border-top:8px solid var(--gold);
         padding:52px 44px;min-height:430px}
  .card3 .badge{display:inline-block;padding:10px 28px;font-size:var(--fs-cap);font-weight:800;letter-spacing:.12em}
  .card3 .n{margin:30px 0 18px;font-size:var(--fs-body);font-weight:800;color:var(--ink);line-height:1.5}
  .card3 .n em{font-style:normal;color:var(--green)}
  .card3 .n .ox{color:var(--ox)}
  .card3 .d{font-size:var(--fs-body);color:var(--muted);line-height:1.85}
  .concl3{position:absolute;left:var(--mx);right:var(--mx);bottom:110px}
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
{cards}  </div>
  <div class="concl concl concl3">{esc(p['concl'])}</div>
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
  .eqcards{position:absolute;left:var(--mx);top:650px;width:var(--cw);display:flex;gap:36px}
  .eqcard{flex:1;background:var(--card);border:1px solid var(--line);border-left:8px solid var(--gold);padding:32px 36px}
  .eqcard .k{font-size:var(--fs-cap);font-weight:800;letter-spacing:.14em;margin-bottom:12px}
  .eqcard .n{font-size:var(--fs-body);font-weight:700;color:var(--ink);line-height:1.55}
  .eqcard .n em{font-style:normal;color:var(--green)}
  .eqcard .n .ox{color:var(--ox)}
  .eqcard .d{margin-top:10px;font-size:var(--fs-cap);color:var(--muted);line-height:1.7}
  .concl3{position:absolute;left:var(--mx);right:var(--mx);bottom:110px}
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
{cards}  </div>
  <div class="concl concl concl3">{esc(p['concl'])}</div>
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
    extra = """
  .cwrap{position:absolute;left:var(--mx);top:352px;width:var(--cw);display:flex;gap:var(--space-3)}
  .cfig{flex:none;width:%s}
  .cfig .photo{width:100%%;aspect-ratio:16/9;background-size:contain;background-color:transparent;outline:none}
  .cfig .cap{margin-top:12px;text-align:left}
  .cside{flex:1;min-width:0}
  .cside .take{font-size:var(--fs-body);font-weight:800;color:var(--ink);line-height:1.5;
              border-left:6px solid var(--gold);padding-left:20px}
  .cside ul{margin:20px 0 0 22px;font-size:var(--fs-body);color:var(--muted);line-height:1.6}
  .cside li{margin-bottom:10px}
  .cside li::marker{color:var(--gold)}
""" % cw
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


TEMPLATES = {
    "cover": t_cover,
    "cover_split": t_cover_split,
    "toc_grid": t_toc_grid,
    "section": t_section,
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
    "kpi_hero": t_kpi_hero,
    "infographic": t_infographic,
    "compare_bars": t_compare_bars,
    "number_hero": t_number_hero,
}


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
            html = TEMPLATES[p["tpl"]](p)
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
        html = TEMPLATES[p["tpl"]](p)
        out = os.path.join(proj, "页", p["id"] + ".html")
        io.open(out, "w", encoding="utf-8").write(html)
        print("生成", p["id"] + ".html")


if __name__ == "__main__":
    main()
