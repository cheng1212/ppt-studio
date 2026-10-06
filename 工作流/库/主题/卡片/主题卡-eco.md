# 主题卡-eco

- id: 主题卡-eco
- 卡型: 主题卡
- 标题: 环保自然 · 有机清新
- 来源轨: 主题库 v4（2026-10-06，28 原型 deep_research encoding）
- 生产者: Muse
- 状态: 草案（2026-10-06）
- css路径: 库/theme-eco.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 浅底
- 行业: 环保、ESG、农业、能源
- 气质: 自然、可持续、清新、责任
- 场景: ESG、环保公益、农业、双碳报告
- 关键词: 环保、自然、ESG、双碳、绿色、可持续

## 一句话

新芽白底 + 青绿唯一强调：有机呼吸感的环保模板。

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| --bg | #F7FAF7 | 主底色，内容页背景 |
| --bg-dark | #1E2E22 | 深底模式背景（封面/转场/全屏深色页） |
| --gold | #0E9E6E | 唯一强调色：青绿（自然/生长，标题/图表主色） |
| --gold-soft | #BDEBD9 | 强调浅底（色块、徽章、浅色强调底） |
| --ink | #1E2E22 | 主正文墨色 |
| --green | #146B4A | 辅助：墨绿（第二数据色） |
| --silver | #C5C9C6 | 次级文字与高光（深底眉题） |
| --muted | #5A6E60 | 次要文字/注释（与背景对比度≥4.5:1） |
| --line | #DDE9DD | 细线分隔线 |
| --line-dark | #3A423F | 深底分隔线 |
| --card | #FFFFFF | 卡片底色 |
| --ox | #D97706 | 警示（慎用） |
| --ink-dark | #F7FAF7 | 深底正文墨色（反白） |

## 字体与字号

--font-display：无衬线（Noto Sans CJK SC）——现代高效；--font-body：无衬线（Noto Sans CJK SC）——全篇统一；字号沿用骨架 6 档（96/54/30/26/20/16）

- brow/页码/数字一律走 --font-latin（Georgia 栈，骨架约定）

## 间距

沿用骨架（--mx:120px 等）；沿用骨架；圆润亲和，卡片圆角可稍大

## 页眉页脚系统

沿用骨架 brow/pageno/foot；浅底：brow 走 --green；pageno 走 --font-latin；foot 走 --muted

## 结构件清单

badge/concl/numdot/hairline/photo/cap/tag 沿用骨架；photo 自然/田野摄影位；hairline 细线；badge 叶形感（圆角大）；tag 可用 --green 点缀

## 设计纪律

单强调色纪律（--gold 为全页唯一强调）、off-black 正文（禁用纯黑大面积）、--muted 与背景对比度≥4.5:1、香槟金系哑光低饱和（禁用高饱和金属金）；有机自然，禁用医疗无菌感冷蓝；叶脉/地形/手绘自然纹理点缀；圆润亲和无衬线；与医疗绿的区别是有机 vs 无菌

依据：主题库 v4 deep_research（原型-28.md）

## css路径

`库/theme-eco.css`

## 下游

- 主题推荐.py（读匹配标签）
- 页面生成.py（PPT_THEME_CSS）
- 截图.py
