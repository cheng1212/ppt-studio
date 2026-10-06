# 页型卡-equation_hero

- id: 页型卡-equation_hero
- 卡型: 页型卡
- 标题: 方程式 hero（中央大方程式 + 三横卡 + 结论条沉底）
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 定稿（2026-10-05）
- 版式族: 观点

## 适用场景

性质页有核心方程式/公式时：方程式超大字居中为视觉中心，下方三横卡（定义/实例/注意），结论条沉底。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `equation_hero`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题（可用 `<span class="q">` 标绿半句） |
| eq | 是 | 方程式 HTML，可用 `<sub>`/`<sup>` 写上下标 |
| eqlabel | 否 | 方程式下标注（如"合成氨"） |
| cards | 是 | 数组，固定 3 项；每项：b（左边色：闭集 ink/green/gold/ox）/ k（标签词）/ n（要点，可用 `<em>` 标绿）/ d（说明） |
| concl | 是 | 结论条（沉底通栏，可用 `<b>` 标金） |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- cards 必须为 3 项（校验闸拦截）。
- eq 是本页视觉中心，字号 104px，不要写长串文字。

## 模板对应

程序/页面生成.py `t_equation_hero`；PPTX 声明式映射见 程序/pptx映射.py `映射表["equation_hero"]`
