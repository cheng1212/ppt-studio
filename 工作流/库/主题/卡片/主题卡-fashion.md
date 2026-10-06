# 主题卡-fashion

- id: 主题卡-fashion
- 卡型: 主题卡
- 标题: 时尚美妆 · Vogue式杂志妆感
- 来源轨: 主题库 v4（2026-10-06，28 原型 deep_research encoding）
- 生产者: Muse
- 状态: 草案（2026-10-06）
- css路径: 库/theme-fashion.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 浅底
- 行业: 时尚、美妆、零售
- 气质: 潮流、美学、态度、精致
- 场景: 时装周、美妆发布、买手店、穿搭分享
- 关键词: 时尚、美妆、Vogue、潮流、态度、精致

## 一句话

暖白底 + 品红唯一强调 + Vogue 式衬线大标题：有妆感的时尚模板。

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| --bg | #FDFBF7 | 主底色，内容页背景 |
| --bg-dark | #1C1A17 | 深底模式背景（封面/转场/全屏深色页） |
| --gold | #D63384 | 唯一强调色：品红（妆感，标题/高亮/唇色点缀） |
| --gold-soft | #F5C6DA | 品红浅底（标签底） |
| --ink | #1C1A17 | 主正文墨色 |
| --green | #A1245B | 辅助：深莓色（第二色） |
| --silver | #C5C9C6 | 次级文字与高光（深底眉题） |
| --muted | #6E675E | 次要文字/注释（与背景对比度≥4.5:1） |
| --line | #EFE7DA | 细线分隔线 |
| --line-dark | #3A423F | 深底分隔线 |
| --card | #FFFFFF | 卡片底色 |
| --ox | #C2410C | 警示/重点数字/热区点缀（慎用，禁用大面积） |
| --ink-dark | #FDFBF7 | 深底正文墨色（反白） |

## 字体与字号

--font-display：衬线（Noto Serif CJK SC）——大标题稳重优雅；--font-body：无衬线（Noto Sans CJK SC）——正文保证可读；字号沿用骨架 6 档（96/54/30/26/20/16）

- brow/页码/数字一律走 --font-latin（Georgia 栈，骨架约定）

## 间距

沿用骨架（--mx:120px 等）；杂志大片式：大图+大标题，留白果断；沿用骨架其余

## 页眉页脚系统

沿用骨架 brow/pageno/foot；浅底：brow 走 --muted（小字距宽松）；pageno 走 --font-latin；英文刊头可用衬线

## 结构件清单

badge/concl/numdot/hairline/photo/cap/tag 沿用骨架；photo 模特/大片图位（核心）；hairline 极细；badge 慎用；英文大标题 Playfair 风格（沙箱用 Noto Serif 替代）

## 设计纪律

单强调色纪律（--gold 为全页唯一强调）、off-black 正文（禁用纯黑大面积）、--muted 与背景对比度≥4.5:1、香槟金系哑光低饱和（禁用高饱和金属金）；Vogue 式衬线大标题+模特大图位；妆感（粉、红唇色）；年轻潮流，禁用商务蓝；与极简杂志的区别是更妆感，与轻奢的区别是年轻潮流 vs 永恒距离

依据：主题库 v4 deep_research（原型-28.md）

## css路径

`库/theme-fashion.css`

## 下游

- 主题推荐.py（读匹配标签）
- 页面生成.py（PPT_THEME_CSS）
- 截图.py
