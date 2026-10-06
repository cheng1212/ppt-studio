# 页型卡-kpi_hero

- id: 页型卡-kpi_hero
- 卡型: 页型卡
- 标题: KPI英雄页（巨型数字 + 上下文）
- 来源轨: 专家报告 encoding（Few/Knaflic）
- 生产者: chengge
- 状态: 定稿

## 适用场景

讲"关键数字"：1 个数字→居中英雄（118px）；2-4 个→等分网格（64px），标出 1 个主角。
数字无比较=噪音：每个数字必须配上下文（环比/同比/目标）。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `kpi_hero`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 断言式标题（结论句） |
| kpis | 是 | 数组 1-4 个：{v（数字）, label（指标名）, ctx（上下文如"▲32% YoY"）, hero（bool，主角）} |
| concl | 选填 | 金边结论条 |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- kpis 1-4 个，超了拆页
- 数字用等宽 lining figures（模板已焊死 tabular-nums）
- 主角卡 accent 顶边 + 数字走强调色；其余卡数字走墨色
- ctx 必须有比较（YoY/目标/环比），无比较的数字不上页
- 每页只标 1 个主角（全标=无主角）

## 模板对应

程序/页面生成.py `t_kpi_hero`
