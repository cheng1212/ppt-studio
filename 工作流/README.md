# 工作流 · 创作工具核心（Python 程序 + Library）

> **这就是本仓库的核心**：Python 程序与 Library（知识/主题资产）共同构成的工作流。
> 二者不可分——程序按 Library 的规约执行，Library 靠程序落地成页面。

## 组成

```
程序/
  页面生成.py     核心：pages.json（数据）+ 页型模板（5 种）→ HTML
                  布局模板 = 库内页型卡的程序化（cover/toc_grid/section/photo_props/photo_chain）
                  主题 CSS 内联注入、素材图 base64 内嵌（file:// 中文路径跨源规避）
  截图.py         批量 HTML → PNG（1920×1080），整个目录一条命令
  gemini生图.py   Playwright 驱动本机 Gemini 网页（CDP 9222），canvas 通道取原图
  千问生图.py     dashscope API 同步生图（key 从本机 ZCode 配置读取，仓库无密钥）

库/
  theme-sodium.css  主题唯一真源：配色令牌/页眉系统/结构件（色块标签/金边结论条/编号圆/
                    因果箭头/发丝线）——改一处，全套页面生效
```

## 工作流（新增一页的完整路径）
```
1. 生图：python 程序/gemini生图.py --prompt "…" --out 示例-…/素材/x.png
2. 写数据：在 示例-*/页/pages.json 加一条（页型/标题/要点/图/页码）
3. 生成：python 程序/页面生成.py            # 数据 → HTML（零手写 HTML）
4. 出图：python 程序/截图.py "示例-*/页"     # 批量 PNG
```

## 设计纪律（Library 层的规约，程序按此执行）
- 页面 = 数据 + 页型模板；改主题 = 只改 theme-sodium.css
- 知识页禁止裸列表：色块标签/金边结论条/编号圆/因果箭头/发丝线五式点缀，
  每件须答得出「去掉它损失什么信息」
- 实物特写图 contain 完整显示（裁切斩断主体=事故）；场景图才 cover
- 配色 ≤ 主色 1 + 强调色 1 + 中性；多色卡底 = AI 味
```
