# 主题卡-sports

- id: 主题卡-sports
- 卡型: 主题卡
- 标题: 体育竞技 · 双模式荧光动能
- 来源轨: 主题库 v4（2026-10-06，28 原型 deep_research encoding）
- 生产者: Muse
- 状态: 草案（2026-10-06）
- css路径: 库/theme-sports.css、库/theme-sports-light.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 双模式
- 行业: 体育、健身、电竞
- 气质: 激情、拼搏、力量、速度
- 场景: 赛事报道、健身品牌、体育营销、校园运动会
- 关键词: 体育、竞技、荧光、动感、力量、拼搏

## 一句话

纯黑/纯白双模式 + 荧光黄唯一强调：全库动感最强的竞技模板。

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| --bg | #0A0A0B | 主底色，内容页背景 |
| --bg-dark | #060607 | 深底模式背景（封面/转场/全屏深色页） |
| --gold | #D8FF3E | 唯一强调色：荧光黄（深版 #D8FF3E / 浅版活力绿 #65A30D，速度/力量高亮） |
| --gold-soft | #3D4A0A | 强调浅底（色块、徽章、浅色强调底） |
| --ink | #FFFFFF | 深底正文纯白 / 浅底正文墨黑 |
| --green | #E4FF70 | 辅助强调/次要数据系列 |
| --silver | #9AA0AA | 次级文字与高光（深底眉题） |
| --muted | #9AA0AA | 次要文字/注释（与背景对比度≥4.5:1） |
| --line | #26262A | 细线分隔线 |
| --line-dark | #9AA0AA | 深底分隔线 |
| --card | #141416 | 卡片底色 |
| --ox | #FF4D00 | 热区点缀：深版用橙红 #FF4D00（慎用） |
| --ink-dark | #FFFFFF | 深底正文墨色（反白） |

### 双模式

主卡 sports 为深底纯黑（--bg #0A0A0B）+ 荧光黄 #D8FF3E，面向赛事报道、电竞大屏、夜间发布，动感最强；变体 sports-light 为浅底纯白（--bg #FFFFFF）+ 活力绿 #65A30D，面向校园运动会、健身品牌印刷、日间文档。两版共用超粗无衬线与斜切版式语言。

- 深/浅 CSS：`库/theme-sports.css`（深底）与 `库/theme-sports-light.css`（浅底）
- 选用原则：大屏/发布/夜间场景用深底版；印刷/文档/日间投影用浅底版；同一套 deck 内不混用。

## 字体与字号

--font-display：无衬线（Noto Sans CJK SC）——现代高效；--font-body：无衬线（Noto Sans CJK SC）——全篇统一；字号沿用骨架 6 档（96/54/30/26/20/16）

- brow/页码/数字一律走 --font-latin（Georgia 栈，骨架约定）

## 间距

沿用骨架（--mx:120px 等）；动态斜切版式允许打破常规边距，但正文区仍守骨架；大字压迫感优先

## 页眉页脚系统

沿用骨架 brow/pageno/foot；深版 brow 走 --silver，浅版走 --muted；pageno 走 --font-latin，可放大做比分感

## 结构件清单

badge/concl/numdot/hairline/photo/cap/tag 沿用骨架；photo 运动员剪影/赛场大图位；numdot 超粗；hairline 斜切线；badge 荧光底黑字高对比

### 双模式 · 变体 sports-light 13 令牌（色值照抄 theme-tokens.json）

| 令牌 | 色值 |
|---|---|
| --bg | #FFFFFF |
| --bg-dark | #111111 |
| --gold | #65A30D |
| --gold-soft | #E3F2B8 |
| --ink | #111111 |
| --green | #4D7C0F |
| --silver | #C5C9C6 |
| --muted | #5A6478 |
| --line | #E5E7EB |
| --line-dark | #3A423F |
| --card | #FFFFFF |
| --ox | #EA580C |
| --ink-dark | #FFFFFF |

## 设计纪律

单强调色纪律（--gold 为全页唯一强调）、off-black 正文（禁用纯黑大面积）、--muted 与背景对比度≥4.5:1、香槟金系哑光低饱和（禁用高饱和金属金）；超粗无衬线+斜体，大字压迫感；动态斜切版式；荧光色只作强调，禁用大面积铺底（伤眼）；与汽车主题的区别是人体动能 vs 机械速度

依据：主题库 v4 deep_research（原型-28.md）

## css路径

`库/theme-sports.css`、`库/theme-sports-light.css`

## 下游

- 主题推荐.py（读匹配标签）
- 页面生成.py（PPT_THEME_CSS）
- 截图.py
