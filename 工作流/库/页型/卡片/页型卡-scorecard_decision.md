# 页型卡-scorecard_decision

- id: 页型卡-scorecard_decision
- 卡型: 页型卡
- 标题: 决策记分卡
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案
- 版式族: 对比

## 适用场景

多候选项的打分决策：供应商选型、方案评审、技术选型。
候选项行：名称＋评分条＋note；winner 高亮并给出胜出理由。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `scorecard_decision`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题（断言句，≤30 中文字） |
| cands | 是 | 数组，2–4 项；每项：name（选项名，必填）/ score（评分，必填）/ note（说明，选填） |
| winner | 是 | 胜出项＋理由（高亮条，如"胜出：A 方案——综合评分最高且交付周期最短"） |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- winner 必须在 cands 中出现（校验闸拦截），不许空降结论。
- score 必须可比：同一量纲同一尺度。
- 配色走主题令牌，不许在字段里写色值。

## 模板对应

程序/页面生成.py `t_scorecard_decision`；PPTX 声明式映射见 程序/pptx映射.py `映射表["scorecard_decision"]`
