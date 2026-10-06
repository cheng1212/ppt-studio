# 页型卡-roadmap_swimlane

- id: 页型卡-roadmap_swimlane
- 卡型: 页型卡
- 标题: 泳道式路线图
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案
- 版式族: 流程

## 适用场景

多 workstream 的季度级规划：列＝季度、行＝lane；任务圆角条按 q0–q1 跨列；
NOW 竖线标出当前时间；proposed（未确认）任务用虚线/浅色区分。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `roadmap_swimlane`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题（断言句，≤30 中文字） |
| quarters | 是 | 数组：时间列名（如 ["Q1","Q2","Q3","Q4"]） |
| lanes | 是 | 数组，1–4 条；每条：name（workstream 名，必填）/ bars（任务条数组，必填）；bars 每项：t（任务名，必填）/ q0（起始列索引，必填）/ q1（结束列索引，必填）/ confirmed（true/false，选填，默认 true） |
| now | 否 | NOW 标记列索引 |
| milestones | 否 | 数组：里程碑 {q（列索引）, t（名）} |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- backlog 不许全画上：路线图只画已排期的任务。
- 讲解顺序：时间轴→lane 含义→任务条。
- bars>q0/q1 索引必须落在 quarters 范围内（校验闸拦截）。
- 配色走主题令牌，不许在字段里写色值。

## 模板对应

程序/页面生成.py `t_roadmap_swimlane`；PPTX 声明式映射见 程序/pptx映射.py `映射表["roadmap_swimlane"]`
