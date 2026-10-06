# 主题卡-consulting

- id: 主题卡-consulting
- 卡型: 主题卡
- 标题: 咨询智库 · 理性洞察
- 来源轨: 主题库 v4（2026-10-06，28 原型 deep_research encoding）
- 生产者: Muse
- 状态: 草案（2026-10-06）
- css路径: 库/theme-consulting.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 浅底
- 行业: 战略咨询、行业研究、智库
- 气质: 理性、逻辑、洞察、精英
- 场景: 战略咨询报告、行业研究、MBB 风格汇报
- 关键词: 咨询、麦肯锡、MECE、矩阵、洞察

## 一句话

浅灰底+睿蓝的咨询主题，标志性"标题下藏青 2px 线+右上角 logo 位"，大量 2×2 矩阵与瀑布图，比金融更浅更"论文感"。

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| --bg | #F5F7FA | 页面底色（浅底） |
| --bg-dark | #2D3748 | 深底模式底色 / 深色区块底 |
| --gold | #2B6CB0 | 唯一强调色：睿蓝 #2B6CB0 |
| --gold-soft | #BFD7EE | 强调色浅色衍生：底纹/浅底高光区块 |
| --ink | #2D3748 | 正文墨色 |
| --green | #2B6CB0 | 睿蓝同系 #2B6CB0：图表次要系列走同色系深浅，避免跳色 |
| --silver | #C5C9C6 | 浅底装饰灰；深底反白辅助文字（brow/页码） |
| --muted | #5A6B85 | 次要文字（对比度≥4.5:1） |
| --line | #CBD5E0 | 浅底分隔线/细线装饰 |
| --line-dark | #3A423F | 深底分隔线 |
| --card | #FFFFFF | 卡片底色 |
| --ox | #C2410C | 辅助语义橙：图表次要系列/警示点缀，慎用 |
| --ink-dark | #F5F3ED | 深底正文墨色（反白） |

## 字体与字号

- display/body 均为 sans；框架感强，标题栏式排版
- 字号沿用骨架 6 档（96/54/30/26/20/16）
- brow/pageno/数字走 --font-latin（Georgia 栈）

## 间距

- 沿用骨架（--mx:120px 等）；网格对齐严格，宜用 2×2 矩阵式分区

## 页眉页脚系统

- 沿用骨架 brow/pageno/foot；**标题下藏青 2px 线 + 右上角 logo 位**为本主题标志（BP skill 规范）

## 结构件清单

- badge/concl/numdot/hairline/photo/cap/tag 沿用骨架；concl 宜做"结论先行"的 action title 条；瀑布图/矩阵组件优先

## 设计纪律

- 单强调色（睿蓝）；off-black 正文；muted≥4.5:1。本主题特有纪律：**结论先行、MECE**——每页标题必须是结论句；装饰≈0，全靠框架与对齐；与学术的区别是"商业感"vs"书卷气"，图表宜商业配色而非论文灰。

## css路径

- `库/theme-consulting.css`

## 下游

- 主题推荐.py（匹配标签消费）
- 页面生成.py（PPT_THEME_CSS）
- 截图.py

> 依据：主题库 v4 deep_research（2026-10-06）；色值照抄 theme-tokens.json，未改动。
