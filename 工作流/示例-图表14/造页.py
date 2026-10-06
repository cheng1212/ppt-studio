# -*- coding: utf-8 -*-
"""图表14预览：14 种新图表页版式各一张（G1=chart_rail … G14=chart_stacked），主题 redox。"""
import io, json, os

PROJ = os.path.dirname(os.path.abspath(__file__))
FOOT = "未来出行实验室"
SRC = "来源：乘联会；口径：批发销量"

def base(pid, tpl, idx, **kw):
    p = {"id": pid, "tpl": tpl, "brow": "FUTURE MOBILITY",
         "no": "%02d / 14" % idx, "foot": FOOT}
    p.update(kw)
    return p

P = []
P.append(base("G1", "chart_rail", 1, kick="SALES / 销量",
    title="华东大区贡献 38% 销量，是第一增长引擎",
    img="g1.png", cap=SRC,
    rail={"label": "核心发现", "hero": "50.2%",
          "body": "新能源渗透率首次突破 50%，电动化拐点已至，直营渠道成为增长主引擎。"}))
P.append(base("G2", "chart_multiples", 2, kick="TREND / 趋势",
    title="四个大区同步上行，华东增速领跑",
    img="g2.png", cap=SRC))
P.append(base("G3", "chart_waterfall", 3, kick="PROFIT / 利润",
    title="规模效应消化价格战，单车利润回升 12%",
    img="g3.png", cap="来源：公司财报；口径：单车毛利，亿元"))
P.append(base("G4", "chart_combo", 4, kick="SALES / 销量",
    title="销量与渗透率双升，电动化不可逆",
    img="g4.png", cap=SRC))
P.append(base("G5", "chart_table", 5, kick="SALES / 销量",
    title="Q3 销量环比 +18%，全年目标完成 82%",
    img="g5.png", cap=SRC,
    headers=["季度", "销量（万辆）", "环比", "目标完成率"],
    rows=[["Q1", "28", "—", "23%"], ["Q2", "36", "+29%", "53%"],
          ["Q3", "42", "+17%", "82%"], ["Q4E", "48", "+14%", "100%"]]))
P.append(base("G6", "chart_annotated", 6, kick="GROWTH / 增长",
    title="年销量突破 120 万辆，八年 CAGR 达 34%",
    img="g6.png", cap=SRC))
P.append(base("G7", "chart_dashboard", 7, kick="Q3 / 三季度",
    title="Q3 经营全面超预期，四个核心指标全线飘红",
    img="g7.png", cap=SRC,
    kpis=[{"名": "销量", "值": "42万", "变化": "+18.2%"},
          {"名": "渗透率", "值": "55%", "变化": "+6.0pp"},
          {"名": "市占率", "值": "18%", "变化": "+2.1pp"},
          {"名": "NPS", "值": "62", "变化": "+4"}]))
P.append(base("G8", "chart_dumbbell", 8, kick="RESIDUAL / 保值率",
    title="新款三年保值率高出 12 个百分点，SUV 提升最显著",
    img="g8.png", cap="来源：中国汽车流通协会；口径：三年保值率"))
P.append(base("G9", "chart_ranked", 9, kick="BRAND / 品牌",
    title="TOP3 品牌占据 61% 市场份额",
    img="g9.png", cap=SRC))
P.append(base("G10", "chart_map", 10, kick="REGION / 区域",
    title="华东、华南渗透率突破 60%，区域分化加剧",
    cap=SRC, metric="各省新能源渗透率（%）"))
P.append(base("G11", "chart_dualpanel", 11, kick="MIX / 结构",
    title="纯电占比 58%，成为绝对主力",
    img_abs="g11a.png", img_share="g11b.png", cap=SRC))
P.append(base("G12", "chart_bullet", 12, kick="KPI / 目标",
    title="4 项核心 KPI 全部达成年度目标",
    img="g12.png", cap="来源：公司经营分析会"))
P.append(base("G13", "chart_pareto", 13, kick="QUALITY / 质量",
    title="前 3 项客诉占总量 85%，先啃续航与充电",
    img="g13.png", cap="来源：客服中心；口径：2026Q3 客诉工单"))
P.append(base("G14", "chart_stacked", 14, kick="MIX / 结构",
    title="纯电份额逐季提升，燃油份额跌破 30%",
    img="g14.png", cap=SRC))

out = os.path.join(PROJ, "页", "pages.json")
io.open(out, "w", encoding="utf-8").write(json.dumps(P, ensure_ascii=False, indent=1))
print("pages.json ok:", len(P), "页")
