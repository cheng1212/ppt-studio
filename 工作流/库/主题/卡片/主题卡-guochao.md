# 主题卡-guochao

- id: 主题卡-guochao
- 卡型: 主题卡
- 标题: 国潮新中式 · 双模式东方潮流
- 来源轨: 主题库 v4（2026-10-06，28 原型 deep_research encoding）
- 生产者: Muse
- 状态: 草案（2026-10-06）
- css路径: 库/theme-guochao.css、库/theme-guochao-light.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 双模式
- 行业: 国货品牌、文创、零售营销、旅游
- 气质: 东方、自信、潮流、文化
- 场景: 国货品牌、文创、传统节日营销、青年文化
- 关键词: 国潮、新中式、朱砂、黛蓝、潮流、东方

## 一句话

黛蓝深底/宣纸浅底双模式 + 朱砂唯一强调：高饱和东方潮流模板。

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| --bg | #1F2A44 | 主底色，内容页背景 |
| --bg-dark | #141B2E | 深底模式背景（封面/转场/全屏深色页） |
| --gold | #E34234 | 唯一强调色：朱砂红（印章/标题/高亮，深浅两版通用） |
| --gold-soft | #7A2A22 | 强调浅底（色块、徽章、浅色强调底） |
| --ink | #F5F0E6 | 主正文墨色 |
| --green | #C9A063 | 辅助：鎏金（描边/点缀，深版更亮） |
| --silver | #C9BFA8 | 深底次级文字/浅底描边 |
| --muted | #C9BFA8 | 次要文字/注释（与背景对比度≥4.5:1） |
| --line | #3A4A68 | 细线分隔线 |
| --line-dark | #C9BFA8 | 深底分隔线 |
| --card | #28334F | 卡片底色 |
| --ox | #F59E0B | 警示/重点数字/热区点缀（慎用，禁用大面积） |
| --ink-dark | #F5F0E6 | 深底正文墨色（反白） |

### 双模式

主卡 guochao 为深底黛蓝（--bg #1F2A44）+ 朱砂 #E34234，面向青年潮流、国货发布、大屏场景，鎏金点缀更亮；变体 guochao-light 为浅底宣纸（--bg #F5F0E6）+ 朱砂 #C63A2B，面向传统节日营销、文创印刷、白底文档场景。两版共用朱砂唯一强调与衬线字体，纹样语言一致。

- 深/浅 CSS：`库/theme-guochao.css`（深底）与 `库/theme-guochao-light.css`（浅底）
- 选用原则：大屏/发布/夜间场景用深底版；印刷/文档/日间投影用浅底版；同一套 deck 内不混用。

## 字体与字号

--font-display：衬线（Noto Serif CJK SC；沙箱可用）——标题庄重书卷感；--font-body：衬线（Noto Serif CJK SC）——正文与标题同族，论文/书卷气；字号沿用骨架 6 档（96/54/30/26/20/16）

- brow/页码/数字一律走 --font-latin（Georgia 栈，骨架约定）

## 间距

沿用骨架（--mx:120px 等）；竖排标题页左右留白加大，营造中式气韵；沿用骨架其余

## 页眉页脚系统

沿用骨架 brow/pageno/foot；深版 brow 走 --silver，浅版 brow 走 --gold；pageno 走 --font-latin；foot 可配印章式小标

## 结构件清单

badge/concl/numdot/hairline/photo/cap/tag 沿用骨架；badge 做印章风（朱砂底反白）；hairline 可用回纹式双线；photo 配国风摄影/纹样位；竖排标题为本主题特色结构件

### 双模式 · 变体 guochao-light 13 令牌（色值照抄 theme-tokens.json）

| 令牌 | 色值 |
|---|---|
| --bg | #F5F0E6 |
| --bg-dark | #1A1A1A |
| --gold | #C63A2B |
| --gold-soft | #F0C4BC |
| --ink | #1A1A1A |
| --green | #8A6D1F |
| --silver | #C5C9C6 |
| --muted | #6B6257 |
| --line | #D8CFC0 |
| --line-dark | #3A423F |
| --card | #FFFFFF |
| --ox | #C2410C |
| --ink-dark | #F5F0E6 |

## 设计纪律

单强调色纪律（--gold 为全页唯一强调）、off-black 正文（禁用纯黑大面积）、--muted 与背景对比度≥4.5:1、香槟金系哑光低饱和（禁用高饱和金属金）；高饱和对比色是标志；装饰用回纹/祥云/团扇等传统纹样，禁用纯几何科技感线条；标题可用书法体/思源宋体 Heavy；与水墨主题的区别是潮（高饱和）vs 雅（留白淡雅）

依据：主题库 v4 deep_research（原型-28.md）

## css路径

`库/theme-guochao.css`、`库/theme-guochao-light.css`

## 下游

- 主题推荐.py（读匹配标签）
- 页面生成.py（PPT_THEME_CSS）
- 截图.py
