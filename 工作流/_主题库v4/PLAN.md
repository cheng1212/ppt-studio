# 主题库 v4 建库计划（2026-10-06）

> 来源：
> - 28 原型规格：`~/workspace/research_notes/ppt-theme-library-research-20261006-0820/report.md` §②（A1–F7，含配色 hex/字体性格/气质/场景/差异化要点）
> - 高级感规则：`~/workspace/research_notes/ppt-premium-color-typography-20261006-0812/report.md`（60-30-10/单强调色/off-black/字阶≥2x/行高1.6–1.8/左对齐）
> 用户指令：建非常全面的主题库；28 原型为依据；hex 以原型值为准（"约定"值可微调，"来源"值不许改）。
> 目标：28 个主题（33 个 CSS 文件，5 个双模式变体），全部 K5 通过。

## 设计决策（已定，不许违背）

1. **Token 名是机器 API，不许改名**：13 个配色令牌（--bg/--bg-dark/--gold/--gold-soft/--ink/--green/
   --silver/--muted/--line/--line-dark/--card/--ox/--ink-dark）＋字号/行高/字距/间距令牌，
   名字一个不许动（107 个模板在用）。其中 --gold 语义＝"唯一强调色"（不一定是金色），
   在设计规约里注明。
2. **只加字体令牌**（additive）：--font-sans/--font-serif/--font-latin/--font-round 四个字栈定义，
   --font-body/--font-display 两个角色令牌（默认＝sans 栈）。骨架里硬编码的 font-family
   规则改走 var(--font-body)/var(--font-display)/var(--font-latin)，默认值与现状视觉一致
   （老 8 套主题视觉不变）。
3. **沙箱可用字体**（fc-list 实测）：Noto Sans CJK SC（R/B）、Noto Serif CJK SC（R/B）。
   字栈必须把这两个放在靠前可命中位置；站酷快乐体/猫啃网糖圆体等写进 --font-round 供用户机器，
   沙箱回退到 Noto Sans CJK SC。
   - --font-sans: "Noto Sans CJK SC","PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC","Source Han Sans SC",system-ui,sans-serif
   - --font-serif: "Noto Serif CJK SC","Songti SC","SimSun","Noto Serif SC",Georgia,serif
   - --font-latin: Georgia,"Times New Roman","DejaVu Serif",serif
   - --font-round: "站酷快乐体","猫啃网糖圆体","Noto Sans CJK SC",sans-serif
4. **高级感纪律**（逐套自查）：单强调色（--gold 只做强调，不做正文）；深底不用纯 #000
   （用 #0B0E17/#0E0E0C 这类 off-black，C3 launch 也不许纯黑，用 #0A0A0B）；浅底 --ink
   用 #1A1A1A–#23272F 不用纯黑；--muted 与底色对比度 ≥4.5:1；香槟金用哑光低饱和
   （#B08A46/#C9A063 系，不许高饱和亮金）。
5. **旧 8 套**（chemlab/deepsea/dianshang/ocean/premium/redox/sodium/wanyue）：CSS 文件保留不动
   （老示例项目在引用）；主题卡状态改为"旧版（已被 v4 主题库取代，仅供老项目）"。
   回归.py 若硬编码 8 主题列表，更新为新主题抽查集（读文件后定，不许大改逻辑）。

## 28 主题 × slug（CSS 文件名 theme-<slug>.css；★＝双模式变体）

- A 政企党建：dangjian（白底红金）、dangjian-dark ★（深红底）、gov-blue、career、gala、resume
- B 商务金融：finance-navy、consulting、pitch、pitch-dark ★、marketing、annual
- C 科技：tech、darktech、launch
- D 医疗教育学术：healthcare、education、academic、kids
- E 文化美学：guochao（黛蓝深主）、guochao-light ★（宣纸浅）、ink、editorial、luxury（曜石黑主）、luxury-light ★（象牙白）
- F 行业垂直：realestate、automotive、food、fashion、sports（深主）、sports-light ★、wedding、共 33 个 CSS，28 张卡（变体共用一张卡，卡里注明双模式）。

## 字体角色分配（--font-display/--font-body）

- serif display：dangjian(+dark)、academic、guochao(+light)、ink（body 也 serif）、luxury(+light)、realestate、fashion、wedding
- round display：education、kids、food（body 均为 sans）
- 其余：display/body 均为 sans；--font-latin 统一用于 brow/pageno/数字（Georgia 栈）

## 七处落地（按顺序）

1. **读**：`库/主题/_骨架.css`（token 结构＋硬编码 font-family 位置）、`程序/主题同步.py`
   （同步机制＋主题列表来源）、`校验.py` K5（主题卡自检要哪些节）、`规约/清单.json`
   （结构）、一张现有主题卡（格式范例）、`程序/回归.py`（主题列表是否硬编码）。
2. **骨架升级**：_骨架.css 加 6 个字体令牌（4 栈＋2 角色，默认值＝现状视觉）；
   硬编码 font-family 的规则改走 var()。跑 `主题同步.py` 全量同步老 8 套
   （视觉不变），`--check` 通过。
3. **33 个 CSS**：以骨架为底，按原型 hex 填 :root 13 色令牌＋字体角色令牌。
   每个文件必须 13 色令牌齐全（缺一不可，否则 var() 悬空）。
   配色取值：report §② 各原型 --bg/--ink/--accent/--muted/--line：
   --gold＝accent，--green＝原型次要语义色（无则与 accent 同系深一档），
   --gold-soft＝accent 浅一档，--silver/--muted/--line 按原型，--card＝bg 抬升一档，
   --bg-dark＝bg 压暗（深主题）或沿用，--ox 保留语义橙（警告/强调点缀）。
4. **28 张主题卡**：`库/主题/卡片/主题卡-<slug>.md`（变体不单独立卡），状态＝草案，
   必须含：id/卡型/标题/来源轨/生产者/状态/css路径/匹配标签（深浅/行业/气质/场景/关键词，
   供主题推荐.py 消费）/一句话/设计说明/结构件清单/设计纪律/下游（K5 要求的节一个不少，
   先读 K5 代码确认）。
5. **旧 8 卡**：状态改为旧版（只改状态行，不动其他）。
6. **清单.json**：按其结构加入 28 新主题（读文件后按格式加）。
7. **校验**：`校验.py --卡` K1–K7 全过（新卡草案 WARN 可接受，FAIL 必修）；
   另抽查：3 个新主题 × 3 个模板（cover/kpi_hero/chart 任选）内存渲染冒烟通过，
   确认无 var() 悬空（可简单 grep 渲染后 HTML 无 "var(--" 残留）。
8. **汇报**：文件清单、校验 PASS 原样行、主题数 8→36（28 新＋8 旧）。

## 差异化自查（入库前逐套过）

report §③ 硬规则：任意两主题至少 2 轴不同（6 轴：色相×明暗×字体性格×装饰纹理×
版式密度×影像语言）；同色相家族强制分化（如 finance-navy vs consulting vs gov-blue
必须在明暗/装饰/字体上拉开）。自查不过的不许入库，降级为变体或砍掉。

## 不做的事

- 不改 13 个配色令牌的名字；不动 107 个模板的 token 引用。
- 不删旧 8 套 CSS 文件；不改老示例项目。
- 不生成 33 套 × 107 页型的全量预览（只做抽查冒烟）。
- 不 commit、不 push。
