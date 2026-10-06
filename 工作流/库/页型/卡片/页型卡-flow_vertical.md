# 页型卡-flow_vertical

- id: 页型卡-flow_vertical
- 卡型: 页型卡
- 标题: 纵向步骤（每步可展开）
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案（2026-10-06）
- 版式族: 流程

## 适用场景

步骤需要展开说明的流程：左侧 rail＋编号节点纵向堆叠，
每步＝步骤名＋展开说明。区别于 stepper（横向 2–4 步、说明短）、
timeline_vertical（时间驱动、有时间标签；本页步骤驱动、无时间）。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `flow_vertical`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题 |
| steps | 是 | 数组，3–6 项；每项：t（步骤名）/ d（展开说明） |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- steps 必须为 3–6 项；每步说明一句话，不许展开成段落。
- 无时间语义的步骤不许硬套 timeline_vertical。

## 模板对应

程序/页面生成.py `t_flow_vertical`；PPTX 声明式映射见 程序/pptx映射.py `映射表["flow_vertical"]`
