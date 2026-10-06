# 内容页 32 新页型入库计划（2026-10-06）

> 来源：展示形式研究报告 `~/workspace/research_notes/ppt-content-display-patterns-20261006-0710/report.md`
> （注意：该 report.md 文件尾部截断，止于 12-1 中段；13–17 与 A–E 以 researcher handoff 摘要为准，已足够指导入库）
> 用户指令：不预览，直接入库 32 个新页型（草案），后面用到时再调。
> 目标：tpl 总数 68 → 100。

## 设计哲学（必须遵守）

- 程序＋卡库＋规约三层；改 schema 即改程序行为。
- 能固定的都固定：字段走闭集/必填清单；配色走主题令牌，**不许在模板里硬编码色值**。
- 校验闸必经：`校验.py --卡` K1–K7 全过。草案卡 WARN 可接受，FAIL 必须修。
- 新卡状态一律**草案**（逐张评审后再定稿）。
- 每张卡必须有 `- 版式族` 字段（K7）。
- 标准页铬：brow/no/kick 页眉 + foot 底部右注；bg 纹理选填（dots/grid/diagonal/mesh/glow 闭集）。

## 现有成员（去重依据，勿重复入库）

- 观点：cards3, equation_hero, infographic
- 对比：compare_bars（两组数据条形）, table_compare（对比表，覆盖三线表）
- 流程：flow_branch, flow_cycle（覆盖循环）, stepper（横向步骤条 2–4 步，覆盖 5-1）, timeline（横向里程碑轴）
- 图文：photo_chain, photo_props
- 数据：17 个已完备（全幅巨型数字→number_hero；KPI 卡片簇→kpi_hero；仪表盘→chart_dashboard）

## 合并/跳过清单（入库时不再立项，原因备查）

- 三线表对比 → table_compare 已覆盖
- 横向步骤条 → stepper 已覆盖；循环 → flow_cycle 已覆盖；横向里程碑 → timeline 已覆盖
- 命名框架页（12-1）是元规则（"一页一命名框架＋副标题说明读法"），不是版式，不单独立型
- 快照盒（9-1）并入 case_psr 卡说明（顶部可选五字段速览盒）
- 数据化痛点（7-2）暂不单独立型（可用 kpi_hero＋因果链表达）
- 叙事型时间线（6-4，直线/曲线/阶梯轴线形态）是 timeline 的形态变体，暂不单独立型
- 概念图解（11-3）暂不单独立型（可用 framework_hub / infographic）
- 致谢＋联系（14-4）与引导式问答（16-2）合并为 closing_qa
- 议程/过渡（17）是结构族事项，不占用内容族

## 32 新页型规格

字段记法：必填[] / 选填[] / 嵌套：`父>子（必填/选填）`。未注明的通用字段：brow/no/kick（页眉左/页码/眉题）必填，
foot（底部右注）必填，bg（背景纹理闭集）选填。有图页型另加 img（必填注明）/cap/mask 选填。

### 观点族（19）

1. **statement_assertion** 行动标题页
   - 必填：title（断言句）, sub（口径/范围/读法）, points（2–4 项）, foot
   - 嵌套：points>t（分论点，必填）, points>d（论据，选填）
   - 版式：标题大字断言；副标题小字灰；points 纵向列表，分论点加粗、论据缩进小字
   - 纪律：title 必须是完整结论句，不许话题式标题

2. **statement_dotdash** 点线式
   - 必填：title（结论句）, items（2–4 项）, foot
   - 嵌套：items>b（分论点，必填）, items>ds（论据数组，选填）
   - 版式：bullet 实心圆点＋分论点；dash 短横＋论据缩进；单个 bullet 下 ds ≤ 4

3. **statement_golden** 金句独白
   - 必填：phrase（4–7 词核心主张）, foot
   - 选填：sub（一句语境）
   - 版式：phrase 居中或左下超大字；大量留白；一页只放这一句

4. **quote_full** 全幅引言
   - 必填：quote, author（作者＋身份）, foot
   - 选填：source（出处）, bgimg（全幅图）
   - 版式：巨大引号装饰＋引文大字居中＋细线分隔作者行；bgimg 时文字区加半透明框压住

5. **quote_card** 卡片式引用
   - 必填：quote（≤30 词）, by（署名）, src（来源行：谁/何时/何处）, foot
   - 选填：point（关联论点）
   - 版式：中央卡片：引号＋引文＋署名＋来源行；point 为顶部关联论点小字
   - 纪律：一页只放一条引用

6. **definition_dict** 词典条目式
   - 必填：term（术语）, def（一句话定义）, foot
   - 选填：en（英文原词）, note（边界说明：包含/不包含什么）
   - 版式：term 左上巨大加粗；规则线/冒号分隔；def 干净小字；一页只定义一个词

7. **definition_terms** 术语卡片
   - 必填：title, terms（2–4 项）, foot
   - 嵌套：terms>t（术语，必填）, terms>d（一句话定义，必填）
   - 版式：横向 2–4 卡：术语加粗＋一句话定义；统一句式

8. **problem_pain** 痛点图标阵列
   - 必填：title（可用反问/断言）, pains（3–4 项）, foot
   - 嵌套：pains>k（痛点论断，必填）, pains>q（量化补充，必填）
   - 版式：3–4 横向卡：icon 占位＋痛点论断加粗＋q 量化小字
   - 纪律：痛点必须定量；须与后页方案对应

9. **solution_pillars** 方案支柱总览
   - 必填：title（价值主张断言）, pillars（2–4 项）, foot
   - 嵌套：pillars>k（支柱名，必填）, pillars>d（一行说明，必填）
   - 版式：title 断言式；2–4 横向 icon 卡
   - 纪律：支柱名不许内部黑话；支柱间 MECE

10. **solution_features** 特性—价值行
    - 必填：title, feats（3–5 项）, foot
    - 嵌套：feats>f（特性名，必填）, feats>v（业务价值 so what，必填）
    - 版式：纵向行列表：icon 占位＋特性名加粗＋价值小字；行间细分隔线

11. **solution_how** 原理解剖
    - 必填：title, steps（3 项：输入→机制→输出）, foot
    - 嵌套：steps>t（环节名，必填）, steps>d（说明，必填）, steps>hot（被改变环节 true/false，选填）
    - 版式：横向 3 框箭头连接；hot 环节强调色＋"改变点"标注

12. **checklist_tasks** 任务清单
    - 必填：title, tasks（3–7 项）, foot
    - 嵌套：tasks>t（事项，必填）, tasks>owner（责任人，必填）, tasks>due（时间，必填）
    - 版式：纵向清单行：复选框＋事项＋责任人＋时间右对齐
    - 纪律：无责任人/时间的伪清单禁入

13. **scorecard_status** 状态记分卡
    - 必填：title, items（3–7 项）, foot
    - 嵌套：items>k（条目，必填）, items>status（状态文本，必填）, items>prog（进度 0–100 数字，选填）
    - 选填：legend（阈值图例）
    - 版式：行列表：条目＋状态徽（色块）＋进度条；legend 图例行

14. **cta_single** 单一行动
    - 必填：action（一个行动句）, who（责任人）, when（截止时间）, foot
    - 选填：ask（需要的决策/资源）
    - 版式：action 超大字居中；who/when/ask 三行小字
    - 纪律：只给 ONE action；结尾页不引入新论点/数据

15. **cta_next** 下一步清单
    - 必填：title, steps（≤3 项）, contact（联系方式）, foot
    - 嵌套：steps>t（行动，动词开头，必填）, steps>owner（必填）, steps>due（必填）
    - 版式：编号清单 ≤3 条；contact 底部联系方式条

16. **scr_brief** SCR 一页纸
    - 必填：title, s（背景 2–3 行）, c（冲突/变化 2–3 行）, r（结论与建议 2–3 行）, foot
    - 版式：三段纵向：S/C/R 标签＋正文；R 段强调
    - 纪律：只写 Situation 不写 Complication 的无张力摘要禁入

17. **framework_hub** 枢纽辐射
    - 必填：title, hub（中心名）, spokes（4–6 项）, foot
    - 嵌套：spokes>t（节点名，必填）, spokes>d（说明，选填）
    - 版式：中心圆＋辐射节点环绕/阵列；连线

18. **framework_sipoc** SIPOC
    - 必填：title, suppliers[], inputs[], process[], outputs[], customers[]（字符串数组，各 2–6 项）, foot
    - 版式：横向五列：列头＋条目纵向

19. **closing_qa** 致谢＋问答
    - 必填：thanks（致谢标题）, contact（联系方式）, foot
    - 选填：seeds（2–3 个种子问题数组）, takeaway（一句话核心回顾）
    - 版式：thanks 大字；contact 醒目；seeds 小字列表；takeaway 金句条；Q&A 留屏供拍照

### 对比族（5）

20. **compare_vs** 镜像双栏 VS
    - 必填：title, a_title, b_title, a_points[]（2–5 字符串）, b_points[]（2–5 字符串）, foot
    - 选填：verdict（结论倾向）
    - 版式：左右镜像两栏；中央 VS＋竖分隔线；要点逐条平行对位；verdict 底部条
    - 纪律：两侧条目必须对位回答同一问题；信息量对称

21. **compare_beforeafter** 前后对比
    - 必填：title, before, after, delta（底部量化结论）, foot
    - 嵌套：before>t（旧状态标题，必填）, before>points（数组，必填）；after 同构
    - 版式：左右分屏；before 灰调弱化；after 品牌色；中央箭头/分隔线；delta 底部通栏

22. **compare_proscons** 优劣清单
    - 必填：title, topic（对比主题）, pros[]（≤6 字符串）, cons[]（≤6 字符串）, verdict（推荐＋一句话理由）, foot
    - 版式：双栏 ±/✓✗；verdict 底部推荐区
    - 纪律：只罗列不给 verdict 的禁入

23. **matrix_2x2** 2×2 矩阵
    - 必填：title, x_axis（轴名＋方向）, y_axis（轴名＋方向）, quads（4 项）, foot
    - 嵌套：quads>n（象限名，必填）, quads>d（说明/默认动作，选填）, quads>items（落位条目数组，选填）
    - 版式：2×2 网格；轴标签；象限名＋条目
    - 纪律：轴无标签/象限无命名的装饰九宫格禁入

24. **scorecard_decision** 决策记分卡
    - 必填：title, cands（2–4 项）, winner（胜出项＋理由）, foot
    - 嵌套：cands>name（选项名，必填）, cands>score（评分，必填）, cands>note（说明，选填）
    - 版式：候选项行：名称＋评分条＋note；winner 高亮＋理由条

### 流程族（4）

25. **flow_chevron** 箭形管道
    - 必填：title, steps（3–5 项）, foot
    - 嵌套：steps>t（阶段名，必填）, steps>d（描述，选填）
    - 版式：横向首尾咬合箭形段；每段一色、标题白字；段内浅色描述只留关键词

26. **flow_swimlane** 泳道图
    - 必填：title, lanes（2–4 条）, foot
    - 嵌套：lanes>role（角色/部门，必填）, lanes>steps（步骤字符串数组，必填）
    - 选填：note
    - 版式：横向泳道；步骤盒按泳道落位；交接处跨道箭头
    - 纪律：活动不许悬浮在泳道之外、归属不明

27. **timeline_vertical** 纵向时间线
    - 必填：title, nodes（4–8 项）, foot
    - 嵌套：nodes>t（时间，必填）, nodes>h（标题，必填）, nodes>d（说明，选填）
    - 版式：左侧细 rail＋dot；日期小字弱化＋标题加粗＋说明；纵向堆叠

28. **roadmap_swimlane** 泳道式路线图
    - 必填：title, quarters[]（时间列名）, lanes（1–4 条）, foot
    - 嵌套：lanes>name（workstream 名，必填）, lanes>bars（数组，必填）
    - 嵌套：bars>t（任务名，必填）, bars>q0（起始列索引，必填）, bars>q1（结束列索引，必填）,
      bars>confirmed（true/false，选填，默认 true）
    - 选填：now（NOW 标记列索引）, milestones[]（里程碑：{q（列索引）, t（名）}）
    - 版式：列＝季度、行＝lane；任务圆角条按 q0–q1 跨列；NOW 竖线；proposed 用虚线/浅色
    - 纪律：backlog 不许全画上；讲解顺序：时间轴→lane 含义→任务条

### 图文族（4）

29. **case_psr** PSR 三段面板
    - 必填：title, img（案例主图）, problem（量化痛点）, solution（方案）, results（2 项）, foot
    - 嵌套：results>k（指标，必填）, results>before（必填）, results>after（必填）
    - 选填：cap, mask, timebox（时间框）, quote（客户证言一句）
    - 版式：上方主图；Problem 灰调 muted→Solution 品牌 accent-soft→Results KPI before→after 大字
    - 纪律：Results 必须量化（before/after＋时间框）；Challenge 与 Results 指标口径一致
    - 卡说明：顶部可选快照盒（Company/Industry/Challenge/Result/Product 五行速览）

30. **case_arc** 转变弧
    - 必填：title, stages（4–5 项）, foot
    - 嵌套：stages>k（阶段名，必填）, stages>d（说明，必填）
    - 选填：img, cap, mask
    - 版式：横向弧线/阶梯：旧世界→转折点→方法→新世界→下一步；转折点高亮
    - 纪律：Turning Point 不可缺（不许 Before 直跳 After）

31. **testimonial** 证言式
    - 必填：quote, name（姓名/职位/公司）, photo（肖像图）, result（一个结果数字＋说明）, foot
    - 选填：cap, mask
    - 版式：左肖像（圆形/圆角）；右大引号＋引文＋署名＋结果数字；一次只放一条证言
    - 纪律：匿名证言（"某头部客户"）禁入

32. **problem_snapshot** 现状快照分屏
    - 必填：title, img（现状视觉）, pains[]（3–4 痛点字符串）, foot
    - 选填：cap, mask
    - 版式：左右分屏：img 灰调处理；右 pains 纵向列表
    - 纪律：情绪必须与内容一致（问题页不许"正能量"配色）

## 七处入库（按顺序执行）

1. **读**：规约/卡型规约.json（页面条目/tpl闭集/条目 schema 格式）、规约/选型规约.json（映射结构）、
   规约/版式族.json、库/页型/卡片/页型卡-compare_bars.md（卡格式范例）、
   程序/页面生成.py（读 2–3 个 t_ 函数＋TEMPLATES 注册方式＋组件 helper：text/rect/line/img 等）、
   程序/pptx映射.py（读 2–3 条映射格式）。
2. **32 张页型卡**：`库/页型/卡片/页型卡-<tpl>.md`，状态=草案，必须含 `- 版式族` 字段、适用场景、
   数据字段表（字段/必填/说明）、纪律、模板对应节（程序/页面生成.py `t_<tpl>`；PPTX 映射表["<tpl>"]）。
3. **卡型规约.json**：`页面条目/tpl闭集` += 32 个新名；每个新条目写 schema：
   `{"必填":[...],"选填":[...],"xxx必填":[...],"说明":"..."}`（格式照抄 compare_bars 条目）。
4. **选型规约.json**：`映射` 下各意图追加新 tpl 条目（{"tpl","何时用","关系"}，关系照既有写法）。
5. **版式族.json**：四族成员 += 新名；**增补各族选型口诀**（一句话写清新成员何时用）。
6. **程序/页面生成.py**：32 个 `t_<tpl>(d, ctx)` 函数＋TEMPLATES 注册。组件走既有 helper；
   页眉 brow/no/kick＋foot 标准铬；有图页型 img 走既有图片组件（含 mask/cap）；chevron/泳道/矩阵等几何走 svg.py 既有图元或简单 rect/line 装配。
7. **程序/pptx映射.py**：32 条声明式映射（格式照抄既有条目；表格类用既有表格/文本行降级写法，参考 chart_table 的 `｜` 连接降级）。
8. **校验**：跑 `校验.py --卡`，修到 K1–K7 全过（草案卡 WARN 可接受，FAIL 必修；特别注意 K4 模板 AST 读取 vs 卡表、
   K7 族成员 vs tpl闭集）。
9. **汇报**：改动文件清单、校验结果（PASS 行原样贴）、tpl 总数 68→100 确认。

## 不做的事

- 不生成预览 PNG（用户明确不预览）
- 不导出 PPTX 验证（拍板前不做）
- 不 commit、不 push（未经用户明确允许）
