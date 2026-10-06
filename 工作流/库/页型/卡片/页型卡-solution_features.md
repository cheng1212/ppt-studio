# 页型卡-solution_features

- id: 页型卡-solution_features
- 卡型: 页型卡
- 标题: 特性—价值行
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案（2026-10-06）
- 版式族: 观点

## 适用场景

特性列表页：纵向行列表，每行 icon 占位＋特性名加粗＋业务价值（so what）小字，
行间细分隔线。适合产品特性、功能清单页，强制每行回答"对用户有什么用"。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `solution_features`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题（断言句或特性集标题） |
| feats | 是 | 数组，3–5 项；每项：f（特性名，必填）/ v（业务价值 so what，必填） |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- 每行必须写出 so what：v 为必填（校验闸拦截）；只写特性不写价值的纯功能清单禁入。
- feats 必须为 3–5 项（校验闸拦截）；f 是"有什么"，v 是"对谁有什么用"，不许写反。
- 配色走主题令牌，不许在字段里写色值。

## 模板对应

程序/页面生成.py `t_solution_features`；PPTX 声明式映射见 程序/pptx映射.py `映射表["solution_features"]`
