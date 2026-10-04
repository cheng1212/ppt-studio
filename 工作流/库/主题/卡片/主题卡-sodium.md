# 主题卡-sodium

- id: 主题卡-sodium
- 卡型: 主题卡
- 标题: SODIUM · 活性之源（高中化学《钠及其化合物》主题）
- 来源轨: 库内装配
- 生产者: chengge
- 状态: 定稿
- css路径: 库/theme-sodium.css

## 一句话

矿物暖白知识页 + 金属炭黑深页，焰色金黄为唯一核心强调——"实验室里的贵金属"气质。

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| --bg | #F5F3ED | 矿物暖白：知识页底 |
| --bg-dark | #252C2B | 金属炭黑：封面/章节页底 |
| --gold | #E9AE38 | 焰色金黄：唯一核心强调 |
| --gold-soft | #D8B85B | 过氧化物淡金：次级强调 |
| --ink | #252C2B | 主墨色（同炭黑） |
| --green | #526D61 | 矿物墨绿：标题/标签/章名 |
| --silver | #C5C9C6 | 金属银灰：深底辅助字 |
| --muted | #8A938F | 浅底弱化字 |
| --line | #DDD8CC | 发丝线 |
| --card | #FFFFFF | 卡底 |

## 字体与字号

- 中文：Microsoft YaHei / PingFang SC；英文眉题/数字：Georgia serif
- 字号阶（16:9 @1920）：页标题 62px / 章节标题 118px / 正文 29px / 说明 22px / 描述 19px
- 眉题类全大写 + 宽字距（.26em–.42em），深页眉题银灰弱化

## 间距

- 页边距 --mx: 120px
- 页头起始 --head-top: 126px

## 页眉页脚系统

- 页眉：左 brow（英文章名）+ 右 pageno（页码），top 60px
- 页脚：发丝线（bottom 50px）+ 右注 foot / 左注 foot-left（bottom 64px）
- 封面/章节页用 footline2 变体（金线 + 银灰字）

## 结构件清单

色块标签（badge：ink/green/gold 三色）/ 金边结论条（concl）/ 编号圆（numdot）/
因果箭头（photo_chain 的 ↓）/ 发丝线（hairline）/ 图注（cap）/ 图角标（tag）/
章节 ghost 大数字 / 金分割线（gold-rule）

## 设计纪律

1. 知识页禁止裸列表：五式点缀件每件须答得出「去掉它损失什么信息」
2. 实物特写图 contain 完整显示（裁切斩断主体 = 事故）；场景图才 cover
3. 配色 ≤ 主色 1 + 强调色 1 + 中性；多色卡底 = AI 味
4. 页面 = 数据 + 页型模板；改主题 = 只改本卡 + CSS

## css路径

库/theme-sodium.css（本卡令牌表的执行形态；校验器按规约主题令牌逐个核对存在）

## 下游

示例-化学钠/化学-钠及其化合物（pages.json 全部条目）
