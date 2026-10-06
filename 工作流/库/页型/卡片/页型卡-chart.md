# 页型卡-chart

- id: 页型卡-chart
- 卡型: 页型卡
- 标题: 图表页（断言标题 + 图表 + 右侧解读栏）
- 来源轨: 专家报告 encoding（Tufte/Few/Knaflic）
- 生产者: chengge
- 状态: 定稿
- 版式族: 数据

## 适用场景

讲"数据故事"：图表由 程序/图表.py 生成（declutter 焊死），本页只做版式。
标题必须是断言句（结论），不是标签（"华东GMV断层领先"而非"GMV分析"）。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `chart`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 断言式标题（结论句，中文≤30字） |
| img | 是 | 图表 PNG（程序/图表.py 生成，data URI 或素材路径） |
| cap | 选填 | 图注：数据来源 + 时间范围 |
| insight | 选填 | 右侧解读：{take（一句话结论）, bullets（2-3条）} |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |
| mask | 否 | 图片蒙版：circle/rounded/blob/arch（闭集，仅有图页型） |

## 纪律

- 标题断言式：ghost-deck 测试（只读标题能讲通故事）
- 图表选型走 程序/图表.py：bar=分类对比/pie≤5片/line仅时间序列
- 有 insight 时图左 1080 + 右 480 解读栏；无 insight 图占全宽
- 图注必须有数据来源（无来源的图表不可信）
- 一页只讲一个数据故事，不堆两张图

## 模板对应

程序/页面生成.py `t_chart`，图表由 程序/图表.py 生成
