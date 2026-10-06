# 主题卡-premium

- id: 主题卡-premium
- 卡型: 主题卡
- 标题: 高端大气 · 暗黑奢华模板
- 来源轨: chengge 2026-10-05 授权「高端大气」
- 生产者: Muse（自主执行）
- 状态: 旧版（已被 v4 主题库取代，仅供老项目）
- css路径: 库/theme-premium.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 深底
- 行业: 商务、金融、地产、奢侈品、发布会
- 气质: 高端、大气、奢华、正式、震撼
- 场景: 发布会、大屏、提案、年会
- 关键词: 高端、大气、黑金、奢华、发布会

## 一句话

深黑底 + 香槟金唯一强调，大字号、大留白、大图片；发布会级的高端大气模板。

## 设计说明

- --gold 取香槟金 #D4AF37，慎用 green（已映射为同金色，避免跳色）
- 建议 bg 用 glow（角落光晕）或 mesh
- 封面宜用 cover 大图 + 金线，内页宜少字

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| `--bg` | #0C0C0E | 页面底色 |
| `--bg-dark` | #000000 | 深底（封面/章节页） |
| `--gold` | #D4AF37 | 唯一强调色（眉题/徽章/装饰条） |
| `--gold-soft` | #E8C874 | 次级强调（渐变光效/柔和填充） |
| `--ink` | #F5F2EA | 正文墨色 |
| `--green` | #D4AF37 | 标题/标签/章名 |
| `--silver` | #8A8578 | 深底辅助字 |
| `--muted` | #7D796F | 浅底弱化字 |
| `--line` | #2A2A2E | 发丝线 |
| `--line-dark` | #3A352A | 深底发丝线 |
| `--card` | #141416 | 卡片底 |
| `--ox` | #B8860B | 语义橙（徽章/大文本/装饰） |
| `--ink-dark` | #F5F2EA | 深底正文字 |

## 字体与字号

- 沿用骨架：body 走 `var(--font-body)`，h1 走 `var(--font-display)`，brow/pageno/数字走 `var(--font-latin)`（Georgia 栈）
- 字号 6 档：`--fs-hero`/`--fs-page-title`/`--fs-section-title`/`--fs-body-n`/`--fs-body`/`--fs-desc`/`--fs-cap`/`--fs-kick`，标题:正文≈2:1

## 间距

- 沿用骨架：`--mx:120px` 页边距，`--head-top:126px` 页头起始，`--space-1/2/3` 三档间距

## 页眉页脚系统

- 沿用骨架：`.brow` 左上眉题＋`.pageno` 右上页码，`.foot-line` 发丝线＋`.foot` 右下注脚；深底自动切 `--silver`/`--line-dark`

## 结构件清单

- 沿用骨架：`.badge`（ink/green/gold/ox 四色）、`.concl` 结论条、`.numdot` 数字圆点、`.hairline`、`.photo` 图框、`.cap` 图注、`.tag` 图上标签、`.ghost` 章节大数字、背景纹理（dots/grid/diagonal/mesh/glow）

## 设计纪律

- 本卡为旧版（已被 v4 主题库取代，仅供老项目）：不再新增页型适配，配色/字号冻结
- 规则以骨架为准，不许在主题 CSS 里写 bespoke 规则（已由主题同步.py 对齐）

## css路径

- `库/theme-premium.css`

## 下游

- `程序/主题推荐.py`（匹配标签消费）、`程序/页面生成.py`（`PPT_THEME_CSS` 环境变量切换）、`程序/截图.py`（主题样张渲染）
