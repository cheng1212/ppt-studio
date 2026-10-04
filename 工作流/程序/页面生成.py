# -*- coding: utf-8 -*-
"""page.py — SODIUM 课件页面生成器：页面=数据，布局=模板函数。

用法:
  python page.py                 # 按 pages.json 重新生成全部 HTML
  python page.py P4              # 只生成指定页 id

布局模板（对应库内页型卡）:
  cover        封面（满版图压字）
  toc_grid     目录（2×2 带图卡）
  section      章节页（深底 ghost 编号）
  photo_props  图文性质页（左图右色块标签行 + 结论条）
  photo_chain  图文因果页（左图右编号链 + 提示框）
"""
import io, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, USAGE, ERR, read_json, die, project_dir, theme_css_path, WORKFLOW

HERE = os.path.dirname(os.path.abspath(__file__))

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


def esc(s):
    return s  # 内容自信，不做转义（内部数据）


def img(name):
    """素材图 → base64 data URI 内嵌（file:// 中文路径外链会被 Chromium 拦）"""
    if not name:
        return "none"
    import base64
    path = os.path.normpath(os.path.join(project_dir(), "素材", name))
    raw = open(path, "rb").read()
    return "url(data:image/png;base64," + base64.b64encode(raw).decode() + ")"


# ---------- 模板:封面 ----------
def t_cover(p):
    extra = """
  .hero{position:absolute;inset:0;background:{hero_img} center/cover no-repeat}
  .scrim{position:absolute;inset:0;background:linear-gradient(90deg,
         rgba(37,44,43,.95) 0%%,rgba(37,44,43,.88) 36%%,rgba(37,44,43,.45) 58%%,rgba(37,44,43,0) 78%%)}
  .block{position:absolute;left:130px;top:340px;width:900px}
  .eyebrow{font-family:Georgia,serif;font-size:26px;color:var(--silver);letter-spacing:.42em;text-transform:uppercase}
  .block .gold-rule{margin:34px 0 44px}
  h1{font-size:118px;line-height:1.06;letter-spacing:.03em}
  .en{margin-top:22px;font-family:Georgia,serif;font-size:40px;color:var(--gold);letter-spacing:.16em}
  .sub{margin-top:46px;font-size:30px;color:var(--silver);letter-spacing:.12em}
  .na{position:absolute;right:130px;bottom:74px;font-family:Georgia,serif;font-size:26px;color:var(--gold-soft);letter-spacing:.5em}
  .footline2{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .footline2 .line{width:56px;height:2px;background:var(--gold)}
  .footline2 span{font-size:21px;color:var(--silver);letter-spacing:.28em}
""".replace("{hero_img}", img(p["bg"]))
    h = HEAD.format(theme=THEME, extra=extra, bodycls="dark")
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


# ---------- 模板:目录(2×2 带图卡) ----------
def t_toc_grid(p):
    extra = """
  .hd{position:absolute;left:var(--mx);top:118px}
  .hd h1{font-size:72px;letter-spacing:.1em}
  .hd .sub{margin-top:14px;font-size:24px;color:var(--muted);letter-spacing:.06em}
  .hd .en{margin-top:10px;font-family:Georgia,serif;font-size:20px;color:var(--gold);letter-spacing:.34em;text-transform:uppercase}
  .grid{position:absolute;left:var(--mx);top:352px;width:1680px;height:620px;
        display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:26px}
  .cell{background:var(--card);display:flex;overflow:hidden}
  .ph{width:300px;height:100%%;flex:none;background-position:center;background-size:cover}
  .ph.contain{background-size:contain;background-repeat:no-repeat;background-color:var(--bg-dark)}
  .ct{padding:30px 34px;display:flex;flex-direction:column;justify-content:center}
  .eb{font-family:Georgia,serif;font-size:19px;color:var(--gold);letter-spacing:.26em;font-weight:700}
  .zh{margin-top:10px;font-size:34px;color:var(--green);font-weight:800;letter-spacing:.06em}
  .desc{margin-top:12px;font-size:19px;color:var(--muted);letter-spacing:.05em;line-height:1.7}
  .foot-left{bottom:52px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
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
    extra = """
  .block{position:absolute;left:130px;top:400px;width:1000px}
  .eb{font-family:Georgia,serif;font-size:26px;color:var(--gold);letter-spacing:.4em;text-transform:uppercase}
  .block .gold-rule{margin:36px 0 46px}
  h1{font-size:118px;letter-spacing:.04em;line-height:1.15}
  .sub{margin-top:44px;font-size:29px;color:var(--silver);letter-spacing:.1em;line-height:1.8}
  .footline2{position:absolute;left:130px;bottom:74px;display:flex;align-items:center;gap:22px}
  .footline2 .line{width:56px;height:2px;background:var(--gold)}
  .footline2 span{font-size:21px;color:var(--silver);letter-spacing:.28em;opacity:.8}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="dark")
    sub = "<br>".join(esc(x) for x in p["sub"])
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
  .photo{position:absolute;left:var(--mx);top:352px;width:760px;height:600px}
  .cap{position:absolute;left:var(--mx);top:962px;width:760px}
  .props{position:absolute;left:952px;top:346px;width:848px}
  .prop{display:flex;align-items:center;padding:24px 0 22px}
  .badge{width:118px;height:52px;flex:none;margin-right:30px;font-size:22px}
  .v{flex:1}
  .v .n{font-size:29px;font-weight:700;letter-spacing:.03em;color:var(--ink)}
  .v .n em{font-style:normal;color:var(--green)}
  .v .d{margin-top:6px;font-size:19px;color:var(--muted);line-height:1.6}
  .concl{margin-top:26px}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    rows = ""
    for r in p["rows"]:
        rows += f"""    <div class="prop hairline"><div class="badge badge {r['b']}">{esc(r['k'])}</div>
      <div class="v"><div class="n">{esc(r['n'])}</div>
      <div class="d">{esc(r['d'])}</div></div></div>\n"""
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="photo photo" style="background-image:{img(p['img'])}">
    <div class="tag" style="position:absolute;left:24px;top:28px">{esc(p['tag'])}</div>
  </div>
  <div class="cap cap" style="position:absolute">{esc(p['cap'])}</div>
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
  .photo{position:absolute;left:var(--mx);top:352px;width:760px;height:600px}
  .cap{position:absolute;left:var(--mx);top:962px;width:760px}
  .chain{position:absolute;left:952px;top:368px;width:848px}
  .step{display:flex;gap:26px;align-items:flex-start}
  .st{flex:1}
  .st .t{font-size:27px;color:var(--ink);font-weight:700}
  .st .d{margin-top:8px;font-size:20px;color:var(--muted);line-height:1.7}
  .arrow{margin:14px 0 14px 14px;color:var(--gold);font-size:30px;font-family:Georgia,serif;line-height:1}
  .warn{margin-top:36px;background:var(--card);border-left:6px solid var(--gold);
        padding:24px 30px;font-size:22px;color:var(--ink);line-height:1.8}
  .warn b{color:var(--green)}
"""
    h = HEAD.format(theme=THEME, extra=extra, bodycls="")
    steps = ""
    for i, s in enumerate(p["steps"]):
        steps += f"""    <div class="step"><div class="numdot">{i+1}</div>
      <div class="st"><div class="t">{esc(s['t'])}</div>
      <div class="d">{esc(s['d'])}</div></div></div>\n"""
        if i < len(p["steps"]) - 1:
            steps += '    <div class="arrow">↓</div>\n'
    b = f"""  <div class="brow">{esc(p['brow'])}</div><div class="pageno">{esc(p['no'])}</div>
  <div class="head"><div class="kick">{esc(p['kick'])}</div>
    <h1>{esc(p['title'])}</h1></div>
  <div class="photo photo" style="background-image:{img(p['img'])}"></div>
  <div class="cap cap" style="position:absolute">{esc(p['cap'])}</div>
  <div class="chain">
{steps}    <div class="warn">{esc(p['warn'])}</div>
  </div>
  <div class="foot-line"></div>
  <div class="foot">{esc(p['foot'])}</div>
</body>
</html>
"""
    return h + b


TEMPLATES = {
    "cover": t_cover,
    "toc_grid": t_toc_grid,
    "section": t_section,
    "photo_props": t_photo_props,
    "photo_chain": t_photo_chain,
}


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
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
