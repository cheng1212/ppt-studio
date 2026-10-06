# -*- coding: utf-8 -*-
"""目录11预览：11 种新目录版式各一张（D1=toc_list … D11=toc_minimal），主题 redox。"""
import io, json, os

PROJ = os.path.dirname(os.path.abspath(__file__))
FOOT = "未来出行实验室"

CH = [
    {"no": "01", "zh": "行业洞察", "desc": "新能源渗透率突破 50%，拐点已至", "icon": "全球"},
    {"no": "02", "zh": "核心技术", "desc": "三电系统与智能驾驶双线突破", "icon": "芯片"},
    {"no": "03", "zh": "产品矩阵", "desc": "轿车 / SUV / MPV 全价格带覆盖", "icon": "奖杯"},
    {"no": "04", "zh": "品牌故事", "desc": "从造车新势力到全球化品牌", "icon": "星"},
    {"no": "05", "zh": "服务生态", "desc": "补能网络与用户运营双轮驱动", "icon": "用户"},
    {"no": "06", "zh": "未来之路", "desc": "2027 年技术路线图前瞻", "icon": "灯泡"},
]

def base(pid, tpl, idx, items, **kw):
    p = {"id": pid, "tpl": tpl, "brow": "FUTURE MOBILITY",
         "no": "%02d / 11" % idx,
         "title": "目录", "sub": "智能电动汽车年度技术发布 · 议程",
         "en": "CONTENTS", "foot": FOOT, "items": items}
    p.update(kw)
    return p

P = []
P.append(base("D1", "toc_list", 1, CH[:5]))                                   # 数字列表式
P.append(base("D2", "toc_bignum", 2, CH[:4]))                                 # 大字数字式
P.append(base("D3", "toc_split", 3, CH[:4]))                                  # 左右分栏式
P.append(base("D4", "toc_tb", 4, CH[:4]))                                    # 上下分割式
P.append(base("D5", "toc_tabs", 5,                         # 横向条带式（无描述）
              [{"no": c["no"], "zh": c["zh"]} for c in CH[:4]]))
P.append(base("D6", "toc_icon", 6, CH[:4]))                                   # 图标式
P.append(base("D7", "toc_image", 7, CH[:4], img="P1-bg.png"))                 # 图片驱动式
P.append(base("D8", "toc_roadmap", 8, CH[:5], current=2))                     # 路线图/进度式
P.append(base("D9", "toc_magazine", 9, CH[:5]))                               # 杂志索引式
P.append(base("D10", "toc_curve", 10, CH[:6]))                                # 曲线路径式
P.append(base("D11", "toc_minimal", 11,                        # 极简文字式
              [{"no": c["no"], "zh": c["zh"]} for c in CH[:4]]))

out = os.path.join(PROJ, "页", "pages.json")
io.open(out, "w", encoding="utf-8").write(json.dumps(P, ensure_ascii=False, indent=1))
print("pages.json ok:", len(P), "页")
