# -*- coding: utf-8 -*-
"""封面16预览：16 种封面版式各一张（C1=cover … C16=cover_brush），主题 redox。"""
import io, json, os

PROJ = os.path.dirname(os.path.abspath(__file__))
FOOT = "未来出行实验室"

def base(pid, tpl, **kw):
    p = {"id": pid, "tpl": tpl, "foot": FOOT}
    p.update(kw)
    return p

P = []
# C1 cover（满版图压字）
P.append(base("C1", "cover", eyebrow="SMART EV · 2026", title="未来出行",
              en="The Future of Mobility", sub="智能电动汽车年度技术发布",
              corner="2026", bg="P1-bg.png"))
# C2 cover_split（左右分栏）
P.append(base("C2", "cover_split", eyebrow="THANK YOU", title="谢谢观看",
              en="Drive the Future", sub="未来出行实验室 · 2026",
              corner="2026", img="P18-img.png"))
# C3 cover_typo（大字报式纯文字）
P.append(base("C3", "cover_typo", eyebrow="SMART EV · 2026",
              title="电动车的<b>时代</b>",
              en="The EV Era", sub="智能电动汽车年度技术发布", corner="2026"))
# C4 cover_minimal（留白主导极简）
P.append(base("C4", "cover_minimal", eyebrow="FUTURE MOBILITY",
              title="少即是多", sub="未来出行实验室 · 2026 年度发布",
              corner="2026"))
# C5 cover_block（图片独立色块·拱形）
P.append(base("C5", "cover_block", eyebrow="FLAGSHIP", title="旗舰轿车",
              en="Flagship Sedan", sub="一眼心动，一见倾心", corner="2026",
              img="P6-img.png", shape="arch"))
# C6 cover_duo（双色拼接）
P.append(base("C6", "cover_duo", eyebrow="SMART EV · 2026", title="双色之美",
              en="Duo Tone", sub="品牌色 × 影像，一眼即品牌", corner="2026",
              img="P1-bg.png"))
# C7 cover_diagonal（斜切对角）
P.append(base("C7", "cover_diagonal", eyebrow="SPEED · 2026", title="速度与未来",
              en="Speed & Future", sub="为快而生，向未来而行", corner="2026",
              img="P1-bg.png"))
# C8 cover_brand（品牌色底+图形）
P.append(base("C8", "cover_brand", eyebrow="FUTURE MOBILITY LAB",
              title="未来出行实验室", en="Future Mobility Lab",
              sub="智能电动汽车年度技术发布", corner="2026"))
# C9 cover_magazine（杂志编辑风）
P.append(base("C9", "cover_magazine", eyebrow="VOL.2026",
              title="未来出行", sub="智能电动汽车年度特刊",
              kickers=[{"t": "年度旗舰 · 1020km 超长续航"},
                       {"t": "城市 NOA · 全量推送"},
                       {"t": "800V 高压 · 充电 10 分钟补 400km"}],
              corner="NO.2026", img="P18-img.png"))
# C10 cover_lux（暗黑奢华）
P.append(base("C10", "cover_lux", eyebrow="PRIVATE PREVIEW",
              title="曜夜旗舰", en="Noir Flagship",
              sub="仅以此夜，敬未来", corner="2026"))
# C11 cover_collage（多图拼贴）
P.append(base("C11", "cover_collage", eyebrow="SMART EV · 2026",
              title="多面未来", sub="城市 / 充电 / 座舱 / 远方",
              corner="2026",
              imgs=[{"src": "P1-bg.png"}, {"src": "P18-img.png"},
                    {"src": "P2-img.png"}, {"src": "P6-img.png"}]))
# C12 cover_crop（超大裁切）
P.append(base("C12", "cover_crop", eyebrow="DETAIL", title="细节之美",
              en="Beauty in Detail", sub="把每一处线条，都做到极致",
              corner="2026", img="P6-img.png"))
# C13 cover_anchor（单锚点）
P.append(base("C13", "cover_anchor", eyebrow="SMART EV", num="2026",
              title="未来出行元年", sub="这一年，电动化成为必答题",
              corner="2026"))
# C14 cover_fusion（图字融合/双重曝光）
P.append(base("C14", "cover_fusion", eyebrow="SMART EV · 2026",
              title="人 · 车 · 城市", sub="当科技融入生活",
              corner="2026", img="P1-bg.png", img2="P9-img.png"))
# C15 cover_band（半出血图片带）
P.append(base("C15", "cover_band", eyebrow="SMART EV · 2026",
              title="年度技术发布", en="Annual Tech Release",
              sub="电池 / 智能 / 补能，三大技术一次讲透", corner="2026",
              img="P2-img.png"))
# C16 cover_brush（笔刷书法）
P.append(base("C16", "cover_brush", eyebrow="甲辰年 · 未来出行",
              title="未来出行", en="FUTURE MOBILITY",
              sub="智能电动汽车年度技术发布", seal="未来", corner="2026"))

out = os.path.join(PROJ, "页", "pages.json")
io.open(out, "w", encoding="utf-8").write(json.dumps(P, ensure_ascii=False, indent=1))
print("pages.json ok:", len(P), "页")
