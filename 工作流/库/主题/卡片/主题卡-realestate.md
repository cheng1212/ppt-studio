# 主题卡-realestate

- id: 主题卡-realestate
- 卡型: 主题卡
- 标题: 地产家居 · 厚重大地品质感
- 来源轨: 主题库 v4（2026-10-06，28 原型 deep_research encoding）
- 生产者: Muse
- 状态: 草案（2026-10-06）
- css路径: 库/theme-realestate.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 浅底
- 行业: 地产、家居、物业、城市更新
- 气质: 品质、安居、人文、厚重
- 场景: 楼盘发布、家装、物业、城市更新
- 关键词: 地产、家居、楼盘、品质、安居、人文

## 一句话

米白底 + 棕褐唯一强调 + 衬线标题：有人文温度的品质地产模板。

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| --bg | #FAF8F5 | 主底色，内容页背景 |
| --bg-dark | #2D2A26 | 深底模式背景（封面/转场/全屏深色页） |
| --gold | #5D4037 | 唯一强调色：棕褐（大地色，标题/线框/高亮） |
| --gold-soft | #D5C4B8 | 强调浅底（色块、徽章、浅色强调底） |
| --ink | #2D2A26 | 主正文墨色 |
| --green | #1F6B4A | 辅助：墨绿（第二色、生态/配套语义） |
| --silver | #C5C9C6 | 次级文字与高光（深底眉题） |
| --muted | #6E675E | 次要文字/注释（与背景对比度≥4.5:1） |
| --line | #E8E0D5 | 暖灰分隔线 |
| --line-dark | #3A423F | 深底分隔线 |
| --card | #FFFFFF | 卡片底色 |
| --ox | #C2410C | 警示/重点数字/热区点缀（慎用，禁用大面积） |
| --ink-dark | #FAF8F5 | 深底正文墨色（反白） |

## 字体与字号

--font-display：衬线（Noto Serif CJK SC）——大标题稳重优雅；--font-body：无衬线（Noto Sans CJK SC）——正文保证可读；字号沿用骨架 6 档（96/54/30/26/20/16）

- brow/页码/数字一律走 --font-latin（Georgia 栈，骨架约定）

## 间距

沿用骨架（--mx:120px 等）；沿用骨架；鸟瞰图/户型图页可放宽图片区

## 页眉页脚系统

沿用骨架 brow/pageno/foot；浅底：brow 走 --gold（衬线感）；pageno 走 --font-latin；foot 走 --muted

## 结构件清单

badge/concl/numdot/hairline/photo/cap/tag 沿用骨架；hairline 暖灰细线；photo 建筑线稿/鸟瞰图/样板间大图位；badge 慎用；cap 配图注走 --muted

## 设计纪律

单强调色纪律（--gold 为全页唯一强调）、off-black 正文（禁用纯黑大面积）、--muted 与背景对比度≥4.5:1、香槟金系哑光低饱和（禁用高饱和金属金）；大地色系为主；建筑线稿/鸟瞰图位是标志；生活气息，禁用疏离冷奢；与轻奢的区别是生活气息 vs 距离感

依据：主题库 v4 deep_research（原型-28.md）

## css路径

`库/theme-realestate.css`

## 下游

- 主题推荐.py（读匹配标签）
- 页面生成.py（PPT_THEME_CSS）
- 截图.py
