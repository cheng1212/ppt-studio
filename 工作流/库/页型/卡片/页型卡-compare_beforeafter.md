# 页型卡-compare_beforeafter

- id: 页型卡-compare_beforeafter
- 卡型: 页型卡
- 标题: 前后对比
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案
- 版式族: 对比

## 适用场景

改进前 vs 改进后的分屏展示：改造、上线、优化项目的成果呈现页。
before 灰调弱化、after 品牌色强调，中央箭头/分隔线；底部 delta 通栏给出量化结论。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `compare_beforeafter`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题（断言句，≤30 中文字） |
| before | 是 | 对象；t（旧状态标题，必填）/ points（旧状态要点数组，必填） |
| after | 是 | 对象；与 before 同构：t（新状态标题，必填）/ points（新状态要点数组，必填） |
| delta | 是 | 底部量化结论（沉底通栏，如"效率提升 40%"） |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- before 与 after 必须同构（t＋points 结构一致），要点逐条对位。
- delta 必须量化，不许空泛表述（如"大幅提升"）。
- 配色走主题令牌，不许在字段里写色值。

## 模板对应

程序/页面生成.py `t_compare_beforeafter`；PPTX 声明式映射见 程序/pptx映射.py `映射表["compare_beforeafter"]`
