# 页型卡-compare_proscons

- id: 页型卡-compare_proscons
- 卡型: 页型卡
- 标题: 优劣清单
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案
- 版式族: 对比

## 适用场景

单一主题的优劣盘点：pros 优点清单 vs cons 劣势清单，用于方案评估、去留决策前的事实铺垫。
双栏 ±/✓✗ 呈现；底部 verdict 给出推荐＋一句话理由。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `compare_proscons`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题（断言句，≤30 中文字） |
| topic | 是 | 对比主题（如"外包客服的可行性"） |
| pros | 是 | 数组，≤6 项字符串：优点清单 |
| cons | 是 | 数组，≤6 项字符串：劣势清单 |
| verdict | 是 | 推荐＋一句话理由（底部推荐区） |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- 只罗列不给 verdict 的禁入：优劣页必须落到推荐结论。
- 配色走主题令牌，不许在字段里写色值。

## 模板对应

程序/页面生成.py `t_compare_proscons`；PPTX 声明式映射见 程序/pptx映射.py `映射表["compare_proscons"]`
