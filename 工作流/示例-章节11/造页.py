# -*- coding: utf-8 -*-
"""章节11预览：11 种新章节页版式各一张（S1=section_image … S11=section_bridge），主题 redox。"""
import io, json, os

PROJ = os.path.dirname(os.path.abspath(__file__))
FOOT = "未来出行实验室"

CHS = [
    {"no": "01", "zh": "行业洞察"},
    {"no": "02", "zh": "核心技术"},
    {"no": "03", "zh": "产品矩阵"},
    {"no": "04", "zh": "服务生态"},
    {"no": "05", "zh": "未来之路"},
]

def base(pid, tpl, idx, **kw):
    p = {"id": pid, "tpl": tpl, "brow": "FUTURE MOBILITY",
         "no": "%02d / 11" % idx,
         "kick": "CHAPTER 01", "title": "行业洞察",
         "sub": "新能源渗透率突破 50%，拐点已至",
         "en": "INDUSTRY INSIGHT", "foot": FOOT}
    p.update(kw)
    return p

P = []
P.append(base("S1", "section_image", 1, img="P1-bg.png"))          # 全出血图片式
P.append(base("S2", "section_split", 2, img="P2-img.png"))        # 左右分栏式
P.append(base("S3", "section_minimal", 3))                        # 极简留白式
P.append(base("S4", "section_accent", 4, num="01"))               # 深色强调条式
P.append(base("S5", "section_band", 5, img="P6-img.png"))         # 图片横带式
P.append(base("S6", "section_statement", 6,                        # 金句落锤式
              title="新能源渗透率突破50%",
              sub="2026 年，中国新能源汽车迎来历史性拐点"))
P.append(base("S7", "section_progress", 7,                         # 进度指示式
              current=1, items=CHS))
P.append(base("S8", "section_duo", 8, num="01"))                  # 撞色块式
P.append(base("S9", "section_reuse", 9,                            # 目录复用高亮式
              title="目录", en="CONTENTS", current=1, items=CHS))
P.append(base("S10", "section_icon", 10, icon="全球"))             # 图标印章式
P.append(base("S11", "section_bridge", 11,                         # 引导过渡式
              sub="接下来，我们将深入拆解市场的结构性变化"))

out = os.path.join(PROJ, "页", "pages.json")
io.open(out, "w", encoding="utf-8").write(json.dumps(P, ensure_ascii=False, indent=1))
print("pages.json ok:", len(P), "页")
