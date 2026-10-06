# 主题卡-pitch

- id: 主题卡-pitch
- 卡型: 主题卡
- 标题: 创业路演 · 锐气增长（双模式）
- 来源轨: 主题库 v4（2026-10-06，28 原型 deep_research encoding）
- 生产者: Muse
- 状态: 草案（2026-10-06）
- css路径: 库/theme-pitch.css、库/theme-pitch-dark.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 双模式
- 行业: 创业公司、投资机构、创业大赛
- 气质: 锐气、增长、颠覆、自信
- 场景: 融资路演、创业大赛、商业计划书
- 关键词: 路演、融资、BP、增长、颠覆

## 一句话

活力橙强调的创业路演主题，强对比色+大字+产品截图位，节奏快（问题→方案→数据→团队），"热"而非"稳"。

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| --bg | #FFFFFF | 页面底色（双模式） |
| --bg-dark | #111827 | 深底模式底色 / 深色区块底 |
| --gold | #E8490F | 唯一强调色：活力橙 #E8490F |
| --gold-soft | #FCCFB8 | 强调色浅色衍生：底纹/浅底高光区块 |
| --ink | #111827 | 正文墨色 |
| --green | #C2410C | 深橙 #C2410C：图表次要系列/渐变深端，避免跳色 |
| --silver | #C5C9C6 | 浅底装饰灰；深底反白辅助文字（brow/页码） |
| --muted | #5B6478 | 次要文字（对比度≥4.5:1） |
| --line | #E5E7EB | 浅底分隔线/细线装饰 |
| --line-dark | #3A423F | 深底分隔线 |
| --card | #FFFFFF | 卡片底色 |
| --ox | #EA580C | 辅助语义橙：图表次要系列/警示点缀，慎用 |
| --ink-dark | #FFFFFF | 深底正文墨色（反白） |

## 字体与字号

- display/body 均为 sans；大标题 ExtraBold，英文 Montserrat/Poppins
- 字号沿用骨架 6 档（96/54/30/26/20/16）
- brow/pageno/数字走 --font-latin（Georgia 栈）

## 间距

- 沿用骨架（--mx:120px 等）；一页一句话，字号宜拉满，留白服务于"锐"

## 页眉页脚系统

- 沿用骨架 brow/pageno/foot；深底模式 brow/页码走 --silver 反白

## 结构件清单

- badge/concl/numdot/hairline/photo/cap/tag 沿用骨架；产品截图位为核心组件；numdot 宜用橙色大数字

## 设计纪律

- 单强调色（活力橙）；off-black 正文；muted≥4.5:1。本主题特有纪律：与金融/咨询的区别是"热"而非"稳"——强对比、大字、快节奏；忌公文式长文本；数据页宜"一页一个核心数字"。

## 双模式（深/浅）

- 浅底 `库/theme-pitch.css`：白底 #FFFFFF＋活力橙 #E8490F，适用于商业计划书文档、邮件发送、打印场景。深底 `库/theme-pitch-dark.css`：近黑底 #141419＋霓虹橙 #F54E00，适用于路演现场大屏演示，舞台感更强；深底下 brow/页码走 --silver 反白，线条走 --line-dark。选用原则：要"可阅读可打印"选浅底，要"现场气场"选深底。


深底变体 `pitch-dark` 13 令牌（色值照抄 theme-tokens.json）：

| 令牌 | 色值 |
|---|---|
| --bg | #141419 |
| --bg-dark | #0C0C0F |
| --gold | #F54E00 |
| --gold-soft | #7A2E0A |
| --ink | #F5F5F7 |
| --green | #FB923C |
| --silver | #C5C9C6 |
| --muted | #A8AEBB |
| --line | #2A2D3A |
| --line-dark | #A8AEBB |
| --card | #1D1D24 |
| --ox | #FB923C |
| --ink-dark | #F5F5F7 |

## css路径

- `库/theme-pitch.css`
- `库/theme-pitch-dark.css`

## 下游

- 主题推荐.py（匹配标签消费）
- 页面生成.py（PPT_THEME_CSS）
- 截图.py

> 依据：主题库 v4 deep_research（2026-10-06）；色值照抄 theme-tokens.json，未改动。
