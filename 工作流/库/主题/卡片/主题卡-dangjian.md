# 主题卡-dangjian

- id: 主题卡-dangjian
- 卡型: 主题卡
- 标题: 红金党建 · 庄重热烈（双模式）
- 来源轨: 主题库 v4（2026-10-06，28 原型 deep_research encoding）
- 生产者: Muse
- 状态: 草案（2026-10-06）
- css路径: 库/theme-dangjian.css、库/theme-dangjian-dark.css

## 匹配标签（主题推荐.py 消费）

- 深浅: 双模式
- 行业: 党政机关、事业单位、国企、高校
- 气质: 庄重、热烈、仪式感、信仰
- 场景: 党建学习、党课、建党节/国庆主题活动、政府汇报
- 关键词: 党建、中国红、描金、仪式感、党课

## 一句话

白底中国红或深红底鎏金的红金党建主题，配五星/华表/祥云/红旗符号系统，庄重热烈的仪式感。

## 配色令牌表（令牌/色值/用途）

| 令牌 | 色值 | 用途 |
|---|---|---|
| --bg | #FFFFFF | 页面底色（双模式） |
| --bg-dark | #7A0E1E | 深底模式底色 / 深色区块底 |
| --gold | #DE1C31 | 唯一强调色：中国红 #DE1C31 |
| --gold-soft | #F0B9C0 | 强调色浅色衍生：底纹/浅底高光区块 |
| --ink | #1A1A1A | 正文墨色 |
| --green | #8A6D1F | 深金 #8A6D1F：党建语境下替代绿色，避免跳色 |
| --silver | #C5C9C6 | 浅底装饰灰；深底反白辅助文字（brow/页码） |
| --muted | #595959 | 次要文字（对比度≥4.5:1） |
| --line | #E8DCC3 | 浅底分隔线/细线装饰 |
| --line-dark | #3A423F | 深底分隔线 |
| --card | #FFFFFF | 卡片底色 |
| --ox | #C2410C | 辅助语义橙：图表次要系列/警示点缀，慎用 |
| --ink-dark | #FFFFFF | 深底正文墨色（反白） |

## 字体与字号

- display serif（思源宋体 Heavy/大标宋类，庄重衬线）/ body sans（思源黑体/微软雅黑）；英文 Times New Roman
- 字号沿用骨架 6 档（96/54/30/26/20/16）
- brow/pageno/数字走 --font-latin（Georgia 栈）

## 间距

- 沿用骨架（--mx:120px 等）；封面宜加大上下留白以承载仪式感

## 页眉页脚系统

- 沿用骨架 brow/pageno/foot；深底模式 brow/页码走 --silver 反白；brow 建议配五星或党徽线稿小标

## 结构件清单

- badge/concl/numdot/hairline/photo/cap/tag 沿用骨架；badge 宜用金色描边徽章样式承载"先锋""模范"等称号；hairline 宜用 --line 金色细线

## 设计纪律

- 单强调色（浅底=中国红，深底=鎏金）；off-black 正文；muted≥4.5:1；香槟金哑光低饱和。本主题特有纪律：**禁用几何装饰**——装饰语言必须为党建矢量元素（五星/华表/祥云/红旗），不许用通用几何图形；标题宜金色描边或红色底反白；绿色系慎用（已映射为深金）。

## 双模式（深/浅）

- 浅底 `库/theme-dangjian.css`：白底 #FFFFFF＋中国红 #DE1C31 唯一强调，配描金 #C9A063，适用于日常党课、党建学习、文档型政府汇报。深底 `库/theme-dangjian-dark.css`：深红底 #8E1626＋鎏金 #E8C874 强调，适用于建党节/国庆主题活动、大屏氛围场；深底下 brow/页码走 --silver 反白，线条走 --line-dark，标题宜金色大字。选用原则：要"庄重可读"选浅底，要"热烈氛围"选深底。


深底变体 `dangjian-dark` 13 令牌（色值照抄 theme-tokens.json）：

| 令牌 | 色值 |
|---|---|
| --bg | #8E1626 |
| --bg-dark | #6E1019 |
| --gold | #E8C874 |
| --gold-soft | #7A5C1E |
| --ink | #FFFFFF |
| --green | #E8C874 |
| --silver | #D8CFC0 |
| --muted | #E8DCC3 |
| --line | #5C1A24 |
| --line-dark | #E8DCC3 |
| --card | #9E1B30 |
| --ox | #F59E0B |
| --ink-dark | #FFFFFF |

## css路径

- `库/theme-dangjian.css`
- `库/theme-dangjian-dark.css`

## 下游

- 主题推荐.py（匹配标签消费）
- 页面生成.py（PPT_THEME_CSS）
- 截图.py

> 依据：主题库 v4 deep_research（2026-10-06）；色值照抄 theme-tokens.json，未改动。
