# -*- coding: utf-8 -*-
"""全页型展示册：18 种页型各一页，主题=智能电动汽车。"""
import io, json, os

PROJ = os.path.dirname(os.path.abspath(__file__))
FOOT = "未来出行实验室"

def base(pid, tpl, **kw):
    p = {"id": pid, "tpl": tpl, "foot": FOOT}
    p.update(kw)
    return p

P = []
# P1 cover
P.append(base("P1", "cover", eyebrow="SMART EV · 2026", title="未来出行",
              en="The Future of Mobility", sub="智能电动汽车年度技术发布",
              foot="未来出行实验室", corner="2026", bg="P1-bg.png"))
# P2 toc_grid
P.append(base("P2", "toc_grid", brow="目录", no="02", title="今天聊什么",
              sub="四个章节，一次讲透", en="AGENDA",
              cards=[
                  {"no": "01", "zh": "行业洞察", "desc": "销量、渗透率、格局", "img": "P2-img.png"},
                  {"no": "02", "zh": "核心技术", "desc": "电池、电机、电控", "img": "P2-img.png"},
                  {"no": "03", "zh": "产品矩阵", "desc": "三款车型全对比", "img": "P2-img.png"},
                  {"no": "04", "zh": "未来之路", "desc": "路线图与展望", "img": "P2-img.png"},
              ]))
# P3 section
P.append(base("P3", "section", brow="第一章", no="01", ghost="01",
              eb="CHAPTER ONE", title="行业洞察", sub="数据里的新大陆"))
# P4 chart（图表 PNG 后面生成）
P.append(base("P4", "chart", brow="数据", no="04", kick="销量趋势",
              title="五年销量翻了 12 倍",
              img="P4-chart.png",
              insight={"take": "2025 年突破 900 万辆，渗透率超 55%",
                       "bullets": ["2021→2025：75万 → 905万", "年复合增长率 86%"]}))
# P5 kpi_hero
P.append(base("P5", "kpi_hero", brow="关键指标", no="05", kick="一眼看懂",
              title="三个数字，看懂大局",
              kpis=[
                  {"v": "905万", "label": "2025 年销量", "hero": True},
                  {"v": "55%", "label": "市场渗透率"},
                  {"v": "680km", "label": "平均续航"},
              ],
              concl="结论：<b>电动化</b>已从可选项变为必答题"))
# P6 photo_props
P.append(base("P6", "photo_props", brow="旗舰", no="06", kick="产品特写",
              title="旗舰轿车，一眼心动",
              img="P6-img.png", tag="旗舰轿车", cap="实拍图",
              rows=[
                  {"b": "gold", "k": "续航", "n": "CLTC <em>1020km</em>", "d": "一次充电，北京到上海"},
                  {"b": "green", "k": "加速", "n": "零百 <em>3.1s</em>", "d": "双电机四驱，推背感拉满"},
                  {"b": "ox", "k": "智能", "n": "城市 <em>NOA</em> 全量推送", "d": "点到点领航辅助"},
              ],
              concl="一句话：<b>续航、性能、智能</b>三项全能"))
# P7 compare_bars
P.append(base("P7", "compare_bars", brow="对比", no="07", kick="横向 PK",
              title="它和燃油车，差在哪",
              a_name="电动车", b_name="燃油车",
              rows=[
                  {"label": "每公里成本", "a": 12, "b": 55},
                  {"label": "保养费用(年)", "a": 800, "b": 4500},
                  {"label": "百公里加速", "a": 4, "b": 9},
              ],
              concl="用车成本不到<b>三分之一</b>"))
# P8 table_compare
P.append(base("P8", "table_compare", brow="选购", no="08", kick="参数表",
              title="三款车型，怎么选",
              cols=["", "都市版", "长续航版", "性能版"],
              rows=[
                  ["续航", "620km", "1020km", "760km"],
                  ["零百加速", "6.8s", "5.9s", "3.1s"],
                  ["售价", "19.9万", "25.9万", "32.9万"],
              ],
              concl="长续航版<b>最均衡</b>，性能版为热爱买单"))
# P9 photo_chain
P.append(base("P9", "photo_chain", brow="技术", no="09", kick="拆解",
              title="一台电动车的四颗心脏",
              img="P9-img.png",
              steps=[
                  {"t": "电池", "d": "CTB 一体化车身"},
                  {"t": "电机", "d": "碳化硅高转速"},
                  {"t": "电控", "d": "全域 800V"},
                  {"t": "座舱", "d": "8295 座舱芯片"},
              ],
              warn="四颗心脏，一颗都不能少"))
# P10 timeline
P.append(base("P10", "timeline", brow="历史", no="10", kick="编年史",
              title="十年，三次跃迁",
              nodes=[
                  {"t": "2015", "h": "政策点火", "d": "补贴铺开，元年开启"},
                  {"t": "2020", "h": "爆款涌现", "d": "多款月销过万车型"},
                  {"t": "2023", "h": "油电同价", "d": "价格战，渗透率破 35%"},
                  {"t": "2026", "h": "智能决战", "d": "NOA 上车，体验为王"},
              ],
              concl="每一次跃迁，都由<b>技术</b>驱动"))
# P11 stepper
P.append(base("P11", "stepper", brow="指南", no="11", kick="四步走",
              title="第一次买电车，记住四步",
              steps=[
                  {"t": "定预算", "d": "20 万是甜点区"},
                  {"t": "看续航", "d": "按周里程 × 1.5 选"},
                  {"t": "试智能", "d": "NOA 一定要路上试"},
                  {"t": "算充电", "d": "家充桩省一半钱"},
              ],
              warn="试驾时把销售问住，你就入门了"))
# P12 flow_branch
P.append(base("P12", "flow_branch", brow="方案", no="12", kick="怎么充",
              title="充电焦虑？对症下药",
              root={"t": "你住哪", "d": "先看居住条件"},
              branches=[
                  {"cond": "有固定车位", "result": "装家充桩",
                   "d": "谷电 3 毛一公里，半天装好"},
                  {"cond": "没固定车位", "result": "超充 + 换电",
                   "d": "超充 30 分钟 80%，换电 3 分钟"},
              ],
              concl="结论：<b>有桩装桩</b>，没桩靠网"))
# P13 flow_cycle
P.append(base("P13", "flow_cycle", brow="循环", no="13", kick="电池一生",
              title="一块电池的循环之旅",
              nodes=["生产", "装车", "使用", "梯次利用", "回收再生"],
              edges=[
                  {"from": "生产", "to": "装车", "label": ""},
                  {"from": "装车", "to": "使用", "label": ""},
                  {"from": "使用", "to": "梯次利用", "label": "8年后"},
                  {"from": "梯次利用", "to": "回收再生", "label": ""},
                  {"from": "回收再生", "to": "生产", "label": "闭环"},
              ],
              concl="从摇篮到摇篮，<b>零废弃</b>"))
# P14 cards3
P.append(base("P14", "cards3", brow="优势", no="14", kick="为什么选它",
              title="三个理由，无法拒绝",
              cards=[
                  {"b": "gold", "k": "省", "n": "<em>省</em>钱", "d": "每公里 1 毛 2，保养砍半"},
                  {"b": "green", "k": "快", "n": "<em>快</em>感", "d": "电门一踩，推背即来"},
                  {"b": "ox", "k": "智", "n": "<em>智</em>能", "d": "常用常新，越开越聪明"},
              ],
              concl="省、快、智 —— <b>三位一体</b>"))
# P15 infographic
P.append(base("P15", "infographic", brow="图说", no="15", kick="一张图",
              title="电动车冷知识",
              items=[
                  {"v": "90%", "label": "能量效率", "d": "燃油车只有 30%"},
                  {"v": "3min", "label": "换电时间", "d": "比加油还快"},
                  {"v": "15年", "label": "电池寿命", "d": "日历寿命新纪录"},
              ],
              concl="数字不会说谎"))
# P16 equation_hero
P.append(base("P16", "equation_hero", brow="公式", no="16", kick="底层逻辑",
              title="续航焦虑终结公式",
              eq="真实续航 = 标称续航 × 0.8",
              cards=[
                  {"b": "gold", "k": "常识", "n": "标称续航要 <em>打八折</em>看", "d": "CLTC 工况偏理想，留余量"},
                  {"b": "green", "k": "杀器", "n": "充电 10 分钟补 <em>400km</em>", "d": "800V 高压平台，喝杯咖啡的功夫"},
              ],
              concl="记住公式，<b>告别焦虑</b>"))
# P17 number_hero
P.append(base("P17", "number_hero", brow="里程碑", no="17", kick="大数字",
              title="中国速度",
              v="905万", label="辆", d="2025 年新能源汽车年销量",
              ctx="连续 11 年全球第一", icon="增长"))
# P18 cover_split
P.append(base("P18", "cover_split", eyebrow="THANK YOU", title="谢谢观看",
              en="Drive the Future", sub="未来出行实验室 · 2026",
              foot="未来出行实验室", corner="2026", img="P18-img.png"))

out = os.path.join(PROJ, "页", "pages.json")
io.open(out, "w", encoding="utf-8").write(json.dumps(P, ensure_ascii=False, indent=1))
print("pages.json ok:", len(P), "页")
