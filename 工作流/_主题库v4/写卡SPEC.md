# 主题库 v4 写卡 SPEC（子代理执行用）

## 输入文件（必读）
- `~/workspace/ppt-studio/工作流/_主题库v4/原型-28.md`：28 原型（气质/场景/差异化要点/依据）
- `~/workspace/ppt-studio/工作流/_主题库v4/theme-tokens.json`：33 主题的 13 色令牌 hex（键：bg/bg-dark→--bg-dark/gold→--gold/gsoft→--gold-soft/ink/green/silver/muted/line/lined→--line-dark/card/ox/inkd→--ink-dark）
- 范例卡：`~/workspace/ppt-studio/工作流/库/主题/卡片/主题卡-premium.md`（只参考头格式，不抄节——新卡节要全）

## 输出
`~/workspace/ppt-studio/工作流/库/主题/卡片/主题卡-<slug>.md`，28 张（变体不单独立卡）。

## 卡片格式（K5 机检，一个不少，否则 WARN/FAIL）

文件头（`- ` 前缀行）：
```
- id: 主题卡-<slug>
- 卡型: 主题卡
- 标题: <中文名> · <一句话气质>
- 来源轨: 主题库 v4（2026-10-06，28 原型 deep_research encoding）
- 生产者: Muse
- 状态: 草案（2026-10-06）
- css路径: 库/theme-<slug>.css
```
变体卡（如 dangjian 覆盖 dangjian-dark）：标题注明"双模式"，css路径写两个，用 `、` 分隔。

正文节（标题必须包含以下字符串，K5 用子串匹配）：
1. `## 匹配标签（主题推荐.py 消费）`：深浅（深底/浅底/双模式）/行业/气质/场景/关键词（各 3–6 个，来自原型）
2. `## 一句话`：定位句
3. `## 配色令牌表（令牌/色值/用途）`：13 行表格（令牌/色值/用途），色值照抄 theme-tokens.json；用途列写该令牌在本主题的语义（如 --gold＝唯一强调色：党建红）
4. `## 字体与字号`：display/body 字体角色（serif/sans/round，见下表）＋字号沿用骨架 6 档
5. `## 间距`：沿用骨架（--mx:120px 等），有主题特殊要求则注明
6. `## 页眉页脚系统`：沿用骨架 brow/pageno/foot，本主题的适配说明（如深底主题 brow 走 --silver）
7. `## 结构件清单`：badge/concl/numdot/hairline/photo/cap/tag 沿用骨架，本主题适配说明
8. `## 设计纪律`：高级感纪律（单强调色/off-black/muted≥4.5/香槟金哑光）＋本主题特有纪律（来自原型"差异化要点"，如党建禁用几何装饰、医疗禁用高饱和）
9. `## css路径`：`库/theme-<slug>.css`（变体卡列两个）
10. `## 下游`：主题推荐.py / 页面生成.py（PPT_THEME_CSS）/ 截图.py

## 字体角色分配表（--font-display/--font-body）
- serif display（h1 衬线）：dangjian(+dark)、academic、guochao(+light)、ink（body 也是 serif）、luxury(+light)、realestate、fashion、wedding
- round display：education、kids、food（body 均为 sans）
- 其余：display/body 均为 sans
- 所有主题：brow/pageno/数字走 --font-latin（Georgia 栈）

## 变体卡（5 张）
dangjian（覆盖 dangjian-dark）、pitch（覆盖 pitch-dark）、guochao（覆盖 guochao-light）、luxury（覆盖 luxury-light）、sports（覆盖 sports-light）：
卡内单列"双模式"小节，说明深/浅两个 CSS 的配色差异与选用场景。

## 禁止事项
- 不许改 13 个配色令牌的名字；色值照抄 theme-tokens.json，一个字符不许动
- 不许编造原型没有的气质/场景；依据写"主题库 v4 deep_research"
- 不许碰 CSS 文件、规约、程序
