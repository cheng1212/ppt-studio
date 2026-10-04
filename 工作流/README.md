# 工作流 · 创作工具核心（程序 + Library + 规约）

> **这就是本仓库的核心**：Python 程序、Library（知识卡库）与规约（JSON schema）
> 共同构成的工作流。三者不可分——程序按 Library 与规约执行，
> Library 靠程序落地成页面，规约是"卡长什么样/数据长什么样"的数据定义。
> `示例-化学钠/` 是用这套工具产出的第一套完整课件：《钠及其化合物》。

## 组成

```
程序/
  基座.py        共享执行层：stdout 编码 / 路径 / 退出码 / JSON 读写（一处定义，全部共用）
  校验.py        数据闸：pages.json 按页型卡 schema 校验 + 主题令牌检查（P2→P3 必经）
  主题问卷.py    定主题：按主题问卷规约收敛 6 问答案 → 生成主题卡骨架
  页面生成.py    核心：pages.json（数据）+ 页型模板（5 种）→ HTML
                 主题 CSS 内联注入（PPT_THEME_CSS 可切换）、素材图 base64 内嵌
  截图.py        批量 HTML → PNG（1920×1080），整个目录一条命令
  生图/
    gemini生图.py  Playwright 驱动本机 Gemini 网页（CDP 9222），canvas 通道取原图
    千问生图.py    dashscope API 同步生图（key 跨平台查找，仓库无密钥）

库/            卡库：知识卡（主题卡 / 页型卡 / 素材台账）+ _步.json（步的机器可读定义）
  主题/_步.json        定主题步：问卷 6 问 → 主题卡 → CSS → 令牌闸
  主题/卡片/主题卡-sodium.md
  页型/_步.json        页面生产步：生图 → 写数据 → 校验闸 → 生成 → 出图
  页型/卡片/页型卡-{cover,toc_grid,section,photo_props,photo_chain}.md
  素材/_步.json        生图步：prompt 留痕 → 生成 → 登记素材卡
  素材/素材卡.jsonl    素材台账（一行一卡：文件/prompt/模型/尺寸）
  theme-sodium.css  主题执行形态：配色令牌/页眉系统/结构件

规约/          数据定义：改 schema 即改程序行为，不改代码
  卡型规约.json      主题卡/页型卡/素材卡 schema + 页面条目（按 tpl）schema + 主题令牌清单
  主题问卷规约.json  定主题固定 6 问 + 枚举闭集
```

## 工作流（新增一页的完整路径）

```
1. 生图：python 程序/生图/gemini生图.py --prompt "…" --out <项目>/素材/x.png
        登记：库/素材/素材卡.jsonl 追加一行（文件/prompt/模型/尺寸）
2. 写数据：在 <项目>/页/pages.json 加一条（按页型卡数据字段表，只写字段不写样式）
3. 校验：python 程序/校验.py                 # 闸：tpl 闭集/必填/枚举/图片存在
4. 生成：python 程序/页面生成.py            # 数据 → HTML（零手写 HTML）
5. 出图：python 程序/截图.py "<项目>/页"     # 批量 PNG
```

新主题（定案 D1：改主题 = 换主题卡 + 换 CSS，不碰程序）：

```
1. python 程序/主题问卷.py --主题 <名> --答案 answers.json   # 6 问闭集收敛
2. 填主题卡 → 手写 库/theme-<名>.css
3. python 程序/校验.py --主题 <名>        # 令牌闸
4. PPT_PROJECT=<项目> PPT_THEME_CSS=theme-<名>.css 跑上面 1–5 步
```

## 设计纪律（Library 层的规约，程序按此执行）

- 页面 = 数据 + 页型模板；页型卡数据字段节是页面数据规约的唯一来源
- 新增页型 = 先写页型卡，再写模板函数；卡与代码漂移即修卡
- 知识页禁止裸列表：色块标签/金边结论条/编号圆/因果箭头/发丝线五式点缀，
  每件须答得出「去掉它损失什么信息」
- 实物特写图 contain 完整显示（裁切斩断主体=事故）；场景图才 cover
- 配色 ≤ 主色 1 + 强调色 1 + 中性；多色卡底 = AI 味
- 拍板一律枚举闭集，程序做闭集校验；prompt 原文留痕，禁转述

## 环境

```
pip install -r requirements.txt
python -m playwright install chromium   # 截图用
```
