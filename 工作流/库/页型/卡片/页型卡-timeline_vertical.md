# 页型卡-timeline_vertical

- id: 页型卡-timeline_vertical
- 卡型: 页型卡
- 标题: 纵向时间线
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案
- 版式族: 流程

## 适用场景

纵向叙事的时间序列：4–8 个时间节点，如公司大事记、项目里程碑回顾、版本演进。
左侧细 rail＋dot 贯穿；日期小字弱化、标题加粗、说明小字；纵向堆叠。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `timeline_vertical`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题（断言句，≤30 中文字） |
| nodes | 是 | 数组，4–8 项；每项：t（时间，必填）/ h（标题，必填）/ d（说明，选填） |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- nodes 必须为 4–8 项（校验闸拦截）；t/h 必填，时间模糊的节点不许上轴。
- 配色走主题令牌，不许在字段里写色值。

## 模板对应

程序/页面生成.py `t_timeline_vertical`；PPTX 声明式映射见 程序/pptx映射.py `映射表["timeline_vertical"]`
