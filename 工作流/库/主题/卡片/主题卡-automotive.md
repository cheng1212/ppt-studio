# 主题卡-automotive

- id: 主题卡-automotive
- 卡型: 主题卡
- 标题: 汽车出行 · 暗夜速度红
- 来源轨: 主题库 v4（2026-10-06，28 原型 deep_research encoding）
- 生产者: Muse
- 状态: 草案（2026-10-06）
- css路径: 库/theme-automotive.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 深底
- 行业: 汽车、出行、4S店
- 气质: 速度、力量、机械、未来
- 场景: 新车发布、4S店营销、出行行业报告
- 关键词: 汽车、速度、赛车红、机械、发布、出行

## 一句话

深灰底 + 赛车红唯一强调：速度感拉满的汽车发布模板。

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| --bg | #0D1117 | 主底色，内容页背景 |
| --bg-dark | #080A0E | 深底模式背景（封面/转场/全屏深色页） |
| --gold | #E10600 | 唯一强调色：赛车红（车型高亮/标题/速度线） |
| --gold-soft | #5C0F0A | 强调浅底（色块、徽章、浅色强调底） |
| --ink | #EDEFF2 | 深底正文（浅灰白） |
| --green | #FF6B5E | 辅助：浅红（第二色） |
| --silver | #9AA0AA | 次级文字与高光（深底眉题） |
| --muted | #9AA0AA | 次要文字/注释（与背景对比度≥4.5:1） |
| --line | #2A2F3A | 细线分隔线 |
| --line-dark | #9AA0AA | 深底分隔线 |
| --card | #151A24 | 卡片底色 |
| --ox | #F59E0B | 热区点缀（慎用） |
| --ink-dark | #EDEFF2 | 深底正文墨色（反白） |

## 字体与字号

--font-display：无衬线（Noto Sans CJK SC）——现代高效；--font-body：无衬线（Noto Sans CJK SC）——全篇统一；字号沿用骨架 6 档（96/54/30/26/20/16）

- brow/页码/数字一律走 --font-latin（Georgia 栈，骨架约定）

## 间距

沿用骨架（--mx:120px 等）；沿用骨架；参数表页可加密行距，信息密度优先

## 页眉页脚系统

沿用骨架 brow/pageno/foot；深底：brow 走 --silver；pageno 走 --font-latin；foot 走 --muted

## 结构件清单

badge/concl/numdot/hairline/photo/cap/tag 沿用骨架；photo 车型大图位（核心）；参数表为特色结构件；hairline 金属灰细线；badge 可用 --gold 实心

## 设计纪律

单强调色纪律（--gold 为全页唯一强调）、off-black 正文（禁用纯黑大面积）、--muted 与背景对比度≥4.5:1、香槟金系哑光低饱和（禁用高饱和金属金）；速度线/金属质感是标志；斜体速度感标题可用；参数表组件必备；禁用圆角卖萌元素；与产品发布会的区别是行业专属符号 vs 通用舞台

依据：主题库 v4 deep_research（原型-28.md）

## css路径

`库/theme-automotive.css`

## 下游

- 主题推荐.py（读匹配标签）
- 页面生成.py（PPT_THEME_CSS）
- 截图.py
