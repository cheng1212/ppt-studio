# 页型卡-closing_cta

- id: 页型卡-closing_cta
- 卡型: 页型卡
- 标题: 行动收尾·决策型（McKinsey 四组件）
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案（2026-10-06）
- 版式族: 观点

## 适用场景

需要当场拍板的汇报结尾：decision 一句话决策主张＋points 3 点摘要＋ask 明确诉求
（要什么决策/资源）＋bliss（yes 之后的世界，一句话）。
与 cta_single 的区别：cta_single 是执行型（who/when 落到人头），本页是决策型
（decision/consequence 对齐决策权）。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `closing_cta`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| decision | 是 | 一句话决策主张（断言句，大字） |
| points | 是 | 数组，3 项摘要（字符串） |
| ask | 是 | 明确诉求：要什么决策/资源（强调框） |
| bliss | 选填 | yes 之后的世界，一句话（new bliss，不是第二个 CTA） |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- 只许一个 ask；ask 必须与在场人的决策权对齐（行动与决策权错位禁入）。
- bliss 是行动完成后的世界，不许写成第二个 CTA。
- 结尾页不引入新论点/新数据。

## 模板对应

程序/页面生成.py `t_closing_cta`；PPTX 声明式映射见 程序/pptx映射.py `映射表["closing_cta"]`
