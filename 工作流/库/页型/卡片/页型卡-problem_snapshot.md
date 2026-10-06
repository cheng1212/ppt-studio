# 页型卡-problem_snapshot

- id: 页型卡-problem_snapshot
- 卡型: 页型卡
- 标题: 现状快照分屏
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案
- 版式族: 图文

## 适用场景

问题现状的视觉化呈现：左右分屏，左为现状视觉（img 灰调处理），右为 3–4 条痛点纵向列表。
情绪必须与内容一致：问题页不许用"正能量"配色。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `problem_snapshot`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题（断言句，≤30 中文字） |
| img | 是 | 现状视觉 |
| cap | 否 | 图片说明 |
| mask | 否 | 图片遮罩 |
| pains | 是 | 数组，3–4 项字符串：痛点 |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- 情绪必须与内容一致：问题页不许"正能量"配色。
- 配色走主题令牌，不许在字段里写色值。

## 模板对应

程序/页面生成.py `t_problem_snapshot`；PPTX 声明式映射见 程序/pptx映射.py `映射表["problem_snapshot"]`
