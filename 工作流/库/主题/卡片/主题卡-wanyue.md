# 主题卡-wanyue

- id: 主题卡-wanyue
- 卡型: 主题卡
- 标题: 婉约 · 简洁东方美学模板
- 来源轨: chengge 2026-10-05 授权「简洁婉约」
- 生产者: Muse（自主执行）
- 状态: 旧版（已被 v4 主题库取代，仅供老项目）
- css路径: 库/theme-wanyue.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 浅底
- 行业: 文化、教育、文创、国风
- 气质: 婉约、简洁、东方、留白、优雅
- 场景: 课件、文化分享、读书会
- 关键词: 简洁、婉约、国风、宣纸、黛青、留白

## 一句话

宣纸白底 + 黛青唯一强调 + 朱砂点缀，大留白、细线条；东方文人审美的简洁婉约模板。

## 设计说明

- --gold 取黛青 #3D5A5A（克制、文气），--ox 取朱砂 #C73E3A（印章式点缀，慎用）
- 留白即装饰：建议 bg 用 dots（淡）或不用背景纹理
- 标题宜短，忌 dense 信息页

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| `--bg` | #F8F6F1 | 页面底色 |
| `--bg-dark` | #2B2F2E | 深底（封面/章节页） |
| `--gold` | #3D5A5A | 唯一强调色（眉题/徽章/装饰条） |
| `--gold-soft` | #8AA8A5 | 次级强调（渐变光效/柔和填充） |
| `--ink` | #1F2423 | 正文墨色 |
| `--green` | #2B3A3A | 标题/标签/章名 |
| `--silver` | #A8B5B2 | 深底辅助字 |
| `--muted` | #6C736F | 浅底弱化字 |
| `--line` | #E2DDD2 | 发丝线 |
| `--line-dark` | #3A4442 | 深底发丝线 |
| `--card` | #FFFFFF | 卡片底 |
| `--ox` | #C73E3A | 语义橙（徽章/大文本/装饰） |
| `--ink-dark` | #F8F6F1 | 深底正文字 |

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

- `库/theme-wanyue.css`

## 下游

- `程序/主题推荐.py`（匹配标签消费）、`程序/页面生成.py`（`PPT_THEME_CSS` 环境变量切换）、`程序/截图.py`（主题样张渲染）
