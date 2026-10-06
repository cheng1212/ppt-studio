# 页型卡-solution_pillars

- id: 页型卡-solution_pillars
- 卡型: 页型卡
- 标题: 方案支柱总览
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案（2026-10-06）
- 版式族: 观点

## 适用场景

方案总览页：title 为价值主张断言，下方 2–4 个支柱横向 icon 卡（支柱名＋
一行说明）。适合方案章的第一节，后续每页展开一个支柱。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `solution_pillars`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 价值主张断言（断言句） |
| pillars | 是 | 数组，2–4 项；每项：k（支柱名，必填）/ d（一行说明，必填） |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- 支柱名不许内部黑话：必须是大白话、可被外部人理解的命名。
- 支柱间 MECE：不重叠、不遗漏，合计覆盖 title 的价值主张。
- pillars 必须为 2–4 项（校验闸拦截）。
- 配色走主题令牌，不许在字段里写色值。

## 模板对应

程序/页面生成.py `t_solution_pillars`；PPTX 声明式映射见 程序/pptx映射.py `映射表["solution_pillars"]`
