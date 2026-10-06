# -*- coding: utf-8 -*-
"""pptx导出.py — 从 <项目>/页/pages.json 原生构建可编辑 PPTX。

纪律：
- 文本/表格/形状均为原生可编辑对象；图片为嵌入位图（非整页 PNG 贴图）。
- 配色/字号/字体走主题 CSS 令牌（与 HTML 预览同一套），不硬编码。
- 行内语义标签 <b>/<em>/<span class="q">/<span class="ox"> 解析为 run 级颜色，
  与 esc() 白名单一致。

用法:
  PPT_PROJECT=示例-氧化还原/氧化还原反应-深海 PPT_THEME_CSS=theme-deepsea.css \\
      python 程序/pptx导出.py [--out 导出.pptx]
"""
import io, json, math, os, re, sys
import html.parser as _hp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import FAIL, USAGE, die, project_dir, theme_css_path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR, MSO_SHAPE_TYPE
from pptx.oxml.ns import qn

try:
    from 动画 import 加切换, 加进入动画组
    _有动画 = True
except ImportError:
    _有动画 = False


def _是全页背景(slide, sh):
    """占满整页的图片视为背景，进入动画时跳过。"""
    try:
        if sh.shape_type != MSO_SHAPE_TYPE.PICTURE:
            return False
        return sh.width >= slide.width * 0.9 and sh.height >= slide.height * 0.9
    except Exception:
        return False

# ---------- 画布：1920x1080 @144px/in → 13.333 x 7.5 in ----------
def px(v):
    return Inches(v / 144.0)

def pt_px(v):
    return Pt(v / 2.0)  # px→pt（144px/in，72pt/in）

# ---------- 主题 ----------
def parse_theme(css_path):
    css = io.open(css_path, encoding="utf-8").read()
    toks = dict(re.findall(r"--([\w-]+)\s*:\s*#([0-9a-fA-F]{6})", css))
    fs = {k: int(v) for k, v in re.findall(r"--fs-([\w-]+)\s*:\s*(\d+)px", css)}
    m = re.search(r"font-family\s*:\s*([^;]+);", css)
    font = "Noto Sans CJK SC"
    if m:
        q = re.findall(r'"([^"]+)"', m.group(1))
        if q:
            font = q[0]
    return toks, fs, font

THEME_CSS = theme_css_path()
_TOKS, _FS, FONT = parse_theme(THEME_CSS)

def C(name):
    return RGBColor.from_string(_TOKS[name])

def blend(h1, h2, t):
    """两 hex 色混合，t=0→h1，t=1→h2。"""
    a = [int(h1[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(h2[i:i + 2], 16) for i in (0, 2, 4)]
    return RGBColor(*(round(a[i] + (b[i] - a[i]) * t) for i in range(3)))

# ---------- 行内标签 → run ----------
class _Seg(_hp.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.segs = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        self.stack.append((tag, dict(attrs).get("class", "")))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if data:
            self.segs.append((data, self._style()))

    def _style(self):
        for tag, cls in reversed(self.stack):
            if tag == "span" and "ox" in cls:
                return "ox"
            if tag == "span" and "q" in cls:
                return "q"
            if tag == "em":
                return "em"
            if tag == "b":
                return "b"
        return None

def segs(html):
    p = _Seg()
    p.feed(html or "")
    return p.segs

_STYLE_COLOR = {"b": "gold", "em": "green", "q": "green", "ox": "ox"}

# ---------- 文本 ----------
def set_ea_font(run, name=FONT):
    rPr = run._r.get_or_add_rPr()
    for e in rPr.findall(qn("a:ea")):
        rPr.remove(e)
    rPr.append(rPr.makeelement(qn("a:ea"), {"typeface": name}))

def textbox(slide, x, y, w, h):
    tb = slide.shapes.add_textbox(px(x), px(y), px(w), px(h))
    tf = tb.text_frame
    tf.word_wrap = True
    return tf

def para(tf, html, size_px, base="ink", bold=False, align=PP_ALIGN.LEFT,
         space_after_px=0, line_spacing=1.0, first=True):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = pt_px(space_after_px)
    p.line_spacing = line_spacing
    for text, sty in segs(html):
        r = p.add_run()
        r.text = text
        r.font.size = pt_px(size_px)
        r.font.name = FONT
        set_ea_font(r)
        col = _STYLE_COLOR.get(sty, base)
        r.font.color.rgb = C(col)
        r.font.bold = bold or sty == "b"
    return p

def vmid(tf):
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    return tf

# ---------- 形状 ----------
def rect(slide, x, y, w, h, fill=None, line=None, line_w=1.5):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, px(x), px(y), px(w), px(h))
    sp.line.fill.background()
    if fill:
        sp.fill.solid()
        sp.fill.fore_color.rgb = C(fill)
    else:
        sp.fill.background()
    if line:
        sp.line.color.rgb = C(line)
        sp.line.width = Pt(line_w)
    sp.shadow.inherit = False
    return sp

def badge(slide, x, y, text, kind):
    """色块徽章：亮底 + 深字（与 HTML .badge 一致）。"""
    w = 56 + 30 * len(text)
    sp = rect(slide, x, y, w, 56, fill=kind)
    tf = vmid(sp.text_frame)
    tf.word_wrap = True
    para(tf, text, _FS.get("cap", 22), base="bg", bold=True, align=PP_ALIGN.CENTER)
    return sp, w

def pic_cover(slide, path, x, y, w, h):
    """按 object-fit:cover 裁剪嵌入图片。path 为 None（无图）时直接跳过。"""
    if not path:
        return
    from PIL import Image
    pic = slide.shapes.add_picture(path, px(x), px(y), px(w), px(h))
    iw, ih = Image.open(path).size
    src, tgt = iw / ih, w / h
    if src > tgt:  # 图太宽 → 裁左右
        c = (1 - tgt / src) / 2
        pic.crop_left, pic.crop_right = c, c
    elif src < tgt:  # 图太高 → 裁上下
        c = (1 - src / tgt) / 2
        pic.crop_top, pic.crop_bottom = c, c
    pic.line.fill.background()
    return pic

def arrow_line(slide, x1, y1, x2, y2, color="green", w_pt=3, head=18):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                      px(x1), px(y1), px(x2), px(y2))
    conn.line.color.rgb = C(color)
    conn.line.width = Pt(w_pt)
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    tri = slide.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE,
                                 px(x2 - head / 2), px(y2 - head / 2),
                                 px(head), px(head))
    tri.fill.solid()
    tri.fill.fore_color.rgb = C(color)
    tri.line.fill.background()
    tri.rotation = ang + 90  # 三角形默认朝上，+90 使其朝右为 0°
    return conn

# ---------- 页眉 / 页脚 / 结论条（复用 HTML 版式数值） ----------
MX = 120
CONTENT_W = 1680

def page_head(slide, p):
    tf = textbox(slide, MX, 64, 800, 40)
    para(tf, p.get("brow", ""), _FS.get("brow", 22), base="green")
    tf = textbox(slide, MX + CONTENT_W - 400, 64, 400, 40)
    para(tf, p.get("no", ""), _FS.get("brow", 22), base="silver", align=PP_ALIGN.RIGHT)
    tf = textbox(slide, MX, 140, CONTENT_W, 40)
    para(tf, p.get("kick", ""), _FS.get("kick", 22), base="gold", bold=True)
    tf = textbox(slide, MX, 178, CONTENT_W, 130)
    para(tf, p.get("title", ""), _FS.get("page-title", 62), bold=True)

def 写备注(slide, p):
    """演讲者备注：pages.json 的 notes 字段 → PPTX 备注页。"""
    notes = p.get("notes")
    if not notes:
        return
    ns = slide.notes_slide
    ns.placeholders[1].text = notes if isinstance(notes, str) else "\n".join(notes)


def page_foot(slide, p):
    rect(slide, MX, 1006, CONTENT_W, 2, fill="line")
    if p.get("foot"):
        tf = textbox(slide, MX, 1012, CONTENT_W, 36)
        para(tf, p["foot"], _FS.get("cap", 22), base="silver", align=PP_ALIGN.RIGHT)

def concl_bar(slide, x, y, w, html, size=22):
    h = 110
    rect(slide, x, y, w, h, fill="card")
    rect(slide, x, y, 8, h, fill="gold")
    tf = vmid(textbox(slide, x + 36, y, w - 60, h))
    para(tf, html, size)

# ============================================================
# 各页型渲染（版式数值复用 HTML 模板）
# ============================================================
def _img_path(p, key="img"):
    name = p.get(key)
    if not name:
        return None
    return os.path.normpath(os.path.join(project_dir(), "素材", name))

def r_cover(slide, p):
    from PIL import Image, ImageDraw
    bg = _img_path(p, "bg")
    W, H = 1920, 1080
    im = Image.open(bg).convert("RGB")
    # cover 裁剪到 16:9
    s, t = im.width / im.height, W / H
    if s > t:
        nw = int(im.height * t)
        x0 = (im.width - nw) // 2
        im = im.crop((x0, 0, x0 + nw, im.height))
    else:
        nh = int(im.width / t)
        y0 = (im.height - nh) // 2
        im = im.crop((0, y0, im.width, y0 + nh))
    im = im.resize((W, H), Image.LANCZOS)
    # 左侧 scrim（复用 HTML 渐变 stops：0%→.95, 36%→.88, 58%→.45, 78%→0）
    stops = [(0.00, 0.95), (0.36, 0.88), (0.58, 0.45), (0.78, 0.0), (1.00, 0.0)]
    mask = Image.new("L", (W, 1), 0)
    pxm = mask.load()
    for x in range(W):
        fx = x / W
        for (x0_, a0), (x1_, a1) in zip(stops, stops[1:]):
            if x0_ <= fx <= x1_:
                t_ = (fx - x0_) / (x1_ - x0_ + 1e-9)
                pxm[x, 0] = int(255 * (a0 + (a1 - a0) * t_))
                break
    mask = mask.resize((W, H))
    dark = Image.new("RGB", (W, H), tuple(int(_TOKS["bg-dark"][i:i + 2], 16)
                                          for i in (0, 2, 4)))
    im = Image.composite(dark, im, mask)
    tmp = os.path.join("/tmp", "pptx-cover-%s.png" % p["id"])
    im.save(tmp)
    slide.shapes.add_picture(tmp, px(0), px(0), px(W), px(H))

    tf = textbox(slide, 130, 340, 900, 60)
    para(tf, p.get("eyebrow", ""), _FS.get("cap", 22), base="silver")
    rect(slide, 130, 340 + 60 + 34, 120, 6, fill="gold")  # 金线
    tf = textbox(slide, 130, 340 + 60 + 34 + 50, 900, 280)
    para(tf, p.get("title", ""), _FS.get("section-title", 118), bold=True, line_spacing=1.06)
    tf = textbox(slide, 130, 340 + 60 + 34 + 50 + 290, 900, 70)
    para(tf, p.get("en", ""), _FS.get("body-n", 45), base="gold")
    tf = textbox(slide, 130, 340 + 60 + 34 + 50 + 290 + 80, 900, 60)
    para(tf, p.get("sub", ""), _FS.get("body", 34), base="silver")
    # 页脚
    rect(slide, 130, 1006 - 32, 56, 3, fill="gold")
    tf = textbox(slide, 130 + 78, 1006 - 48, 700, 40)
    para(tf, p.get("foot", ""), _FS.get("cap", 22), base="silver")
    if p.get("corner"):
        tf = textbox(slide, 1920 - 130 - 300, 1006 - 48, 300, 40)
        para(tf, p["corner"], _FS.get("cap", 22), base="gold-soft", align=PP_ALIGN.RIGHT)

def r_section(slide, p):
    rect(slide, 0, 0, 1920, 1080, fill="bg-dark")
    ghost = p.get("ghost", "")
    if ghost:
        tf = textbox(slide, 1000, 60, 800, 800)
        para(tf, ghost, 400, base="ink", align=PP_ALIGN.RIGHT)
        # ghost：gold 混入 bg-dark（HTML 用低透明 gold）
        for para_ in tf.paragraphs:
            for r in para_.runs:
                r.font.color.rgb = blend(_TOKS["gold"], _TOKS["bg-dark"], 0.82)
    tf = textbox(slide, MX, 420, 900, 50)
    para(tf, p.get("eb", ""), _FS.get("cap", 22), base="gold", bold=True)
    rect(slide, MX, 490, 120, 6, fill="gold")
    tf = textbox(slide, MX, 530, 1050, 320)
    para(tf, p.get("title", ""), _FS.get("section-title", 118), bold=True,
         line_spacing=1.15)
    if p.get("sub"):
        sub = p["sub"] if isinstance(p["sub"], str) else "<br>".join(p["sub"])
        tf = textbox(slide, MX, 880, 900, 90)
        para(tf, sub, _FS.get("body", 34), base="silver")
    rect(slide, MX, 1006 - 32, 56, 3, fill="gold")
    tf = textbox(slide, MX + 78, 1006 - 48, 700, 40)
    para(tf, p.get("foot", ""), 21, base="silver")
    tf = textbox(slide, MX + CONTENT_W - 400, 64, 400, 40)
    para(tf, p.get("no", ""), _FS.get("brow", 22), base="silver", align=PP_ALIGN.RIGHT)

def _photo_left(slide, p):
    """左图（x=120,y=330,w=700,h=560）+ tag + cap，返回图片底部 y。"""
    pic_cover(slide, _img_path(p), 120, 330, 700, 560)
    if p.get("tag"):
        sp = rect(slide, 140, 350, 56 + 30 * len(re.sub(r"<[^>]+>", "", p["tag"])),
                  56, fill="bg-dark")
        tf = vmid(sp.text_frame)
        tf.word_wrap = True
        para(tf, p["tag"], 22)
    if p.get("cap"):
        tf = textbox(slide, 120, 900, 700, 40)
        para(tf, p["cap"], _FS.get("cap", 19), base="muted",
             align=PP_ALIGN.CENTER)

def r_photo_props(slide, p):
    page_head(slide, p)
    if _img_path(p):
        _photo_left(slide, p)
        x0, w0 = 900, 900
    else:
        # 无图时与 HTML 的 body.noimg 一致：文字区占满整宽
        x0, w0 = MX, CONTENT_W
    y = 330
    for r in p["rows"]:
        _, bw = badge(slide, x0, y, r["k"], r["b"])
        tf = textbox(slide, x0 + bw + 30, y - 8, w0 - bw - 30, 90)
        para(tf, r["n"], _FS.get("body-n", 29), bold=True)
        tf = textbox(slide, x0 + bw + 30, y + 62, w0 - bw - 30, 60)
        para(tf, r.get("d", ""), _FS.get("body", 22), base="muted")
        rect(slide, x0, y + 150, w0, 2, fill="line")
        y += 172
    if p.get("concl"):
        concl_bar(slide, x0, y + 10, w0, p["concl"])
    page_foot(slide, p)

def r_photo_chain(slide, p):
    page_head(slide, p)
    _photo_left(slide, p)
    x0 = 900
    y = 330
    steps = p["steps"]
    for i, s in enumerate(steps):
        sp = slide.shapes.add_shape(MSO_SHAPE.OVAL, px(x0), px(y), px(72), px(72))
        sp.fill.solid()
        sp.fill.fore_color.rgb = C("green")
        sp.line.fill.background()
        sp.shadow.inherit = False
        tf = vmid(sp.text_frame)
        tf.word_wrap = True
        para(tf, str(i + 1), _FS.get("body-n", 45), base="bg", bold=True, align=PP_ALIGN.CENTER)
        tf = textbox(slide, x0 + 100, y - 6, 800, 60)
        para(tf, s["t"], _FS.get("body", 34), bold=True)
        tf = textbox(slide, x0 + 100, y + 52, 800, 70)
        para(tf, s.get("d", ""), _FS.get("body", 34), base="muted")
        if i < len(steps) - 1:
            arrow_line(slide, x0 + 36, y + 80, x0 + 36, y + 150,
                       color="gold", w_pt=3, head=16)
        y += 168
    if p.get("warn"):
        concl_bar(slide, x0, y + 16, 900, p["warn"])
    page_foot(slide, p)

def r_table_compare(slide, p):
    page_head(slide, p)
    has_img = bool(p.get("img"))
    tw = 1040 if has_img else CONTENT_W
    cols, rows = p["cols"], p["rows"]
    nrow, ncol = len(rows) + 1, len(cols)
    y0 = 330
    gf = slide.shapes.add_table(nrow, ncol, px(MX), px(y0), px(tw), px(100))
    table = gf.table
    table.first_row = False
    table.horz_banding = False
    cw0 = 340
    cw = (tw - cw0) / (ncol - 1) if ncol > 1 else tw
    table.columns[0].width = px(cw0)
    for j in range(1, ncol):
        table.columns[j].width = px(cw)
    # 表头
    table.rows[0].height = px(88)
    for j, htxt in enumerate(cols):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C("green")
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        para(tf, htxt, _FS.get("body", 34), base="bg", bold=True,
             align=PP_ALIGN.CENTER if j else PP_ALIGN.LEFT)
    # 表体
    for i, r in enumerate(rows, start=1):
        table.rows[i].height = px(96)
        for j, txt in enumerate(r):
            cell = table.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C("bg")
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            base = "green" if j == 0 else "ink"
            para(tf, txt, _FS.get("body", 34), base=base, bold=(j == 0))
    total_h = 88 + 96 * len(rows)
    if has_img:
        pic_cover(slide, _img_path(p), MX + tw + 60, y0, 560, 460)
        if p.get("cap"):
            tf = textbox(slide, MX + tw + 60, y0 + 470, 560, 60)
            para(tf, p["cap"], _FS.get("cap", 22), base="muted", align=PP_ALIGN.CENTER)
    if p.get("concl"):
        concl_bar(slide, MX, y0 + total_h + 40, tw, p["concl"])
    page_foot(slide, p)

def r_flow_cycle(slide, p):
    page_head(slide, p)
    # 复用 svg.cycle 的几何：1680x600，中心(840,290)，rx=430，ry=190，r=86
    ox, oy = MX, 340
    cx, cy, rx, ry, nr = 840, 290, 430, 190, 86
    nodes = p["nodes"]
    n = len(nodes)
    pos = {}
    for i, name in enumerate(nodes):
        th = math.radians(-90 + i * 360 / n)
        pos[name] = (ox + cx + rx * math.cos(th), oy + cy + ry * math.sin(th))
    for e in p["edges"]:
        ax, ay = pos[e["from"]]
        bx, by = pos[e["to"]]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        ux, uy = dx / L, dy / L
        sx, sy = ax + ux * (nr + 8), ay + uy * (nr + 8)
        ex, ey = bx - ux * (nr + 8), by - uy * (nr + 8)
        arrow_line(slide, sx, sy, ex, ey, color="green", w_pt=3, head=20)
        # 标签：弧线中点外侧
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        vx, vy = mx - (ox + cx), my - (oy + cy)
        vl = math.hypot(vx, vy) or 1
        lx, ly = mx + vx / vl * 34, my + vy / vl * 34
        tf = textbox(slide, lx - 110, ly - 24, 220, 48)
        para(tf, e.get("label", ""), _FS.get("cap", 22), base="muted", align=PP_ALIGN.CENTER)
    for name, (x, y) in pos.items():
        sp = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                    px(x - nr), px(y - nr), px(nr * 2), px(nr * 2))
        sp.fill.solid()
        sp.fill.fore_color.rgb = C("card")
        sp.line.color.rgb = C("green")
        sp.line.width = Pt(3)
        sp.shadow.inherit = False
        # 文字用独立文本框（宽于圆，复用 HTML overflow:visible 的不换行效果）
        tf = textbox(slide, x - nr - 60, y - 40, (nr + 60) * 2, 80)
        para(tf, name, _FS.get("body", 34), base="green", bold=True, align=PP_ALIGN.CENTER)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    if p.get("concl"):
        concl_bar(slide, MX, 340 + 600 + 30, CONTENT_W, p["concl"])
    page_foot(slide, p)

def r_flow_branch(slide, p):
    page_head(slide, p)
    branches = p["branches"]
    n = len(branches)
    gap = 60
    bw = 520
    if bw * n + gap * (n - 1) > CONTENT_W:  # 与页面生成.py 同式自适应
        bw = (CONTENT_W - gap * (n - 1)) / n
    total = bw * n + gap * (n - 1)
    off = (CONTENT_W - total) / 2
    xs = [MX + off + i * (bw + gap) for i in range(n)]
    y0 = 340
    # root
    rsp = rect(slide, MX + (CONTENT_W - 520) / 2, y0, 520, 130, fill="green")
    tf = vmid(rsp.text_frame)
    tf.word_wrap = True
    para(tf, p["root"]["t"], _FS.get("body", 34), base="bg", bold=True, align=PP_ALIGN.CENTER)
    para(tf, p["root"].get("d", ""), _FS.get("cap", 22), base="bg", align=PP_ALIGN.CENTER,
         first=False)
    # 分叉线：root 底 → 横线 → 各卡顶箭头
    rcx = MX + CONTENT_W / 2
    y1, y2 = y0 + 130, y0 + 196
    rect(slide, rcx - 2, y1, 4, y2 - y1, fill="gold")
    rect(slide, xs[0] + bw / 2, y2 - 2, xs[-1] - xs[0], 4, fill="gold")
    card_top = y2 + 66
    for x in xs:
        arrow_line(slide, x + bw / 2, y2, x + bw / 2, card_top - 6,
                   color="gold", w_pt=3, head=18)
    # 卡片
    ch = 250
    for x, b in zip(xs, branches):
        csp = rect(slide, x, card_top, bw, ch, fill="card", line="line")
        tf = textbox(slide, x + 34, card_top + 28, bw - 68, 60)
        _, bwg = badge(slide, x + 34, card_top + 28, b["cond"], "gold")
        tf = textbox(slide, x + 34, card_top + 100, bw - 68, 80)
        para(tf, b["result"], _FS.get("body-n", 45), base="green", bold=True)
        tf = textbox(slide, x + 34, card_top + 170, bw - 68, 70)
        para(tf, b.get("d", ""), _FS.get("body", 34), base="muted")
    if p.get("concl"):
        concl_bar(slide, MX, card_top + ch + 40, CONTENT_W, p["concl"])
    page_foot(slide, p)

RENDER = {
    "cover": r_cover,
    "section": r_section,
    "photo_props": r_photo_props,
    "photo_chain": r_photo_chain,
    "table_compare": r_table_compare,
    "flow_cycle": r_flow_cycle,
    "flow_branch": r_flow_branch,
}

# ============================================================
# 主流程
# ============================================================
def build(proj, out_path):
    pages = json.load(io.open(os.path.join(proj, "页", "pages.json"),
                              encoding="utf-8"))
    prs = Presentation()
    prs.slide_width = Inches(13.3333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from pptx映射 import 映射表, 渲染声明式
    except ImportError as e:
        sys.stderr.write("WARN 声明式映射未加载：%s\n" % e)
        映射表, 渲染声明式 = {}, None
    for p in pages:
        映射 = 映射表.get(p["tpl"])
        fn = RENDER.get(p["tpl"])
        if not 映射 and not fn:
            die("E2 未实现的页型: %s（页 %s）" % (p["tpl"], p["id"]), code=FAIL)
        def _画(slide, 页):
            # 声明式优先，手写 fallback
            if 映射:
                渲染声明式(slide, 页, 映射)
            else:
                if 页["tpl"] not in ("cover", "section"):
                    rect(slide, 0, 0, 1920, 1080, fill="bg")
                fn(slide, 页)
            # 切换效果：pages.json "transition": "fade"
            tr = 页.get("transition")
            if tr and _有动画:
                try:
                    加切换(slide, tr)
                except Exception as e:
                    sys.stderr.write("WARN 切换失败 %s：%s\n" % (页["id"], e))
            # 进入动画：pages.json "enter": "fade" → 内容形状依次点击进入
            en = 页.get("enter")
            if en and _有动画:
                try:
                    内容形状 = [sh for sh in slide.shapes if not _是全页背景(slide, sh)]
                    加进入动画组(slide, 内容形状, en)
                except Exception as e:
                    sys.stderr.write("WARN 进入动画失败 %s：%s\n" % (页["id"], e))
        # build 分步构建：list of 字段补丁，每步多一张幻灯片（python-pptx 无动画，用构建页模拟）
        步骤s = p.get("build")
        if 步骤s:
            累 = dict(p)
            for i, 补丁 in enumerate(步骤s, 1):
                累.update(补丁)
                slide = prs.slides.add_slide(blank)
                _画(slide, 累)
                写备注(slide, 累)
                print("  + %s-构建%d (%s)" % (p["id"], i, p["tpl"]))
            continue
        slide = prs.slides.add_slide(blank)
        _画(slide, p)
        写备注(slide, p)
        print("  + %s (%s)" % (p["id"], p["tpl"]))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    prs.save(out_path)
    return out_path

def main():
    proj = project_dir()
    out = None
    args = sys.argv[1:]
    if "--out" in args:
        out = args[args.index("--out") + 1]
    if not out:
        name = os.path.basename(os.path.normpath(proj))
        out = os.path.join(proj, "导出", name + ".pptx")
    path = build(proj, out)
    print("PPTX 已生成: %s" % path)

if __name__ == "__main__":
    main()
