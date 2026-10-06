# 页型卡-case_psr

- id: 页型卡-case_psr
- 卡型: 页型卡
- 标题: PSR 三段面板
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案
- 版式族: 图文

## 适用场景

客户案例一页纸：Problem（量化痛点）→ Solution（方案）→ Results（KPI before→after）。
上方主图；Problem 灰调 muted、Solution 品牌 accent-soft、Results 大字 KPI。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `case_psr`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题（断言句，≤30 中文字） |
| img | 是 | 案例主图 |
| cap | 否 | 图片说明 |
| mask | 否 | 图片遮罩 |
| problem | 是 | 量化痛点 |
| solution | 是 | 方案 |
| results | 是 | 数组，2 项；每项：k（指标，必填）/ before（必填）/ after（必填） |
| timebox | 否 | 时间框（如"3 个月内"） |
| quote | 否 | 客户证言一句 |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- Results 必须量化（before/after＋时间框）；Challenge 与 Results 指标口径一致。
- 配色走主题令牌，不许在字段里写色值。

## 卡说明

- 顶部可选快照盒（Company/Industry/Challenge/Result/Product 五行速览）。快照盒（报告 9-1）不单独立型，并入本卡。

## 模板对应

程序/页面生成.py `t_case_psr`；PPTX 声明式映射见 程序/pptx映射.py `映射表["case_psr"]`
