# 主题卡-luxury

- id: 主题卡-luxury
- 卡型: 主题卡
- 标题: 轻奢臻品 · 双模式冷奢
- 来源轨: 主题库 v4（2026-10-06，28 原型 deep_research encoding）
- 生产者: Muse
- 状态: 草案（2026-10-06）
- css路径: 库/theme-luxury.css、库/theme-luxury-light.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 双模式
- 行业: 奢侈品、珠宝、高端地产、私人银行、汽车旗舰
- 气质: 奢华、精致、稀缺、永恒
- 场景: 奢侈品发布、珠宝、高端地产、私人银行
- 关键词: 轻奢、香槟金、曜石黑、高端、稀缺、永恒

## 一句话

曜石黑/象牙白双模式 + 哑光香槟金唯一强调：冷奢距离感的高端模板。

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| --bg | #0E0E0C | 主底色，内容页背景 |
| --bg-dark | #080807 | 深底模式背景（封面/转场/全屏深色页） |
| --gold | #C9A063 | 唯一强调色：香槟金（哑光低饱和，深版 #C9A063 / 浅版 #A8843C） |
| --gold-soft | #5C4E28 | 强调浅底（色块、徽章、浅色强调底） |
| --ink | #F7F3EC | 主正文墨色 |
| --green | #C9A063 | 同金色系（禁用跳色） |
| --silver | #8A8578 | 次级文字与高光（深底眉题） |
| --muted | #A39E8F | 次要文字/注释（与背景对比度≥4.5:1） |
| --line | #2A2A28 | 细线（深版 #2A2A28 / 浅版 #E3DCCB，金线分隔） |
| --line-dark | #8A8578 | 深底分隔线 |
| --card | #171715 | 卡片底色 |
| --ox | #D99E06 | 警示/重点数字/热区点缀（慎用，禁用大面积） |
| --ink-dark | #F7F3EC | 深底正文墨色（反白） |

### 双模式

主卡 luxury 为深底曜石黑（--bg #0E0E0C）+ 香槟金 #C9A063，面向奢侈品发布、珠宝大屏、旗舰店大视觉；变体 luxury-light 为浅底象牙白（--bg #F7F3EC）+ 哑光金 #A8843C，面向高端地产手册、私人银行印刷品、日间提案。两版共用衬线字体与金细线语言。

- 深/浅 CSS：`库/theme-luxury.css`（深底）与 `库/theme-luxury-light.css`（浅底）
- 选用原则：大屏/发布/夜间场景用深底版；印刷/文档/日间投影用浅底版；同一套 deck 内不混用。

## 字体与字号

--font-display：衬线（Noto Serif CJK SC；沙箱可用）——标题庄重书卷感；--font-body：衬线（Noto Serif CJK SC）——正文与标题同族，论文/书卷气；字号沿用骨架 6 档（96/54/30/26/20/16）

- brow/页码/数字一律走 --font-latin（Georgia 栈，骨架约定）

## 间距

沿用骨架（--mx:120px 等）；字距宽松（标题 tracking 放大）；大量留白，产品大图+极少文字

## 页眉页脚系统

沿用骨架 brow/pageno/foot；深版 brow 走 --silver，浅版走 --muted；pageno 走 --font-latin，低调置于角落

## 结构件清单

badge/concl/numdot/hairline/photo/cap/tag 沿用骨架；hairline 金细线为标志性结构件；badge 慎用；photo 产品大图位（珠宝/腕表/汽车）；tag 极简

### 双模式 · 变体 luxury-light 13 令牌（色值照抄 theme-tokens.json）

| 令牌 | 色值 |
|---|---|
| --bg | #F7F3EC |
| --bg-dark | #1A1A1A |
| --gold | #A8843C |
| --gold-soft | #EAD9B8 |
| --ink | #1A1A1A |
| --green | #8A6D1F |
| --silver | #C5C9C6 |
| --muted | #6E685C |
| --line | #E3DCCB |
| --line-dark | #3A423F |
| --card | #FFFFFF |
| --ox | #B45309 |
| --ink-dark | #F7F3EC |

## 设计纪律

单强调色纪律（--gold 为全页唯一强调）、off-black 正文（禁用纯黑大面积）、--muted 与背景对比度≥4.5:1、香槟金系哑光低饱和（禁用高饱和金属金）；香槟金必须哑光低饱和，禁用高饱和金属金；冷奢，禁用年会式喜庆光效；字距宽松+大量留白；产品大图+极少文字；与年会金的区别是冷奢 vs 热闹，与地产的区别是距离感 vs 生活气息

依据：主题库 v4 deep_research（原型-28.md）

## css路径

`库/theme-luxury.css`、`库/theme-luxury-light.css`

## 下游

- 主题推荐.py（读匹配标签）
- 页面生成.py（PPT_THEME_CSS）
- 截图.py
