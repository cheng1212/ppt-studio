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
  页面生成.py    核心：pages.json（数据）+ 页型模板（18 种）→ HTML
                 主题 CSS 内联注入（PPT_THEME_CSS 可切换）、素材图 base64 内嵌
  回归.py        自动化回归：8 主题 × 18 页型全组合
                 （校验闸 → 页面生成 → 截图 PNG；另跑主题令牌闸）
  svg.py         SVG 图元工具库：fork（分支分叉线）/ cycle（环形节点+箭头），
                 颜色走主题 CSS 变量；flow_branch / flow_cycle 模板调用它
  img.py         图片处理固定工具：info / resize（cover/contain/stretch，语义对齐模板）
                 / crop-ratio（按比例中心裁剪）/ convert（格式转换，按后缀推断）
  截图.py        批量 HTML → PNG（1920×1080），整个目录一条命令
  内容生成.py    内容生成层：一句话 → 大纲 → briefs（约束）→ writer（窄接口）
                 → 收集（校验/图表/洞察/配图规划）→ pages.json → 校验闸。
                 无 writer 时停在 briefs 等人工填 filled/；生图不可用时出
                 "待生图"占位图并记配图规划.json，不冒充真实素材。
  控制台/
    server.py    图形化控制台后端（stdlib only）。--host/--token：手机/公网访问
                 时必须配 token，非回环无 token 拒绝启动。
    手机.sh      一键：server(0.0.0.0+token) + cloudflared 隧道，打印手机 URL。
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
0. 选型：按 规约/选型规约.json 的意图→候选映射列出候选页型；
        每个候选写一份草案数据跑 `python 程序/页面生成.py --预览 草案.json`
        渲染布局预览图，用户看图拍板（无预览不许拍板）；
        记录 _选型{意图/候选/选中/理由}，不留痕不许进写数据
1. 生图：python 程序/生图/gemini生图.py --prompt "…" --out <项目>/素材/x.png
        登记：库/素材/素材卡.jsonl 追加一行（文件/prompt/模型/尺寸）
2. 写数据：在 <项目>/页/pages.json 加一条（按页型卡数据字段表，只写字段不写样式）
3. 校验：python 程序/校验.py                 # 闸：tpl 闭集/必填/枚举/图片存在/选型一致性
4. 生成：python 程序/页面生成.py            # 数据 → HTML（零手写 HTML）
5. 出图：python 程序/截图.py "<项目>/页"     # 批量 PNG
6. 审美评审：python 程序/审美评审.py --项目 <项目> --主题 <主题>   # 备料→经 Playwright 送 Gemini/ChatGPT
   # 评审意见存 页/_评审/评审意见.md → --过闸：全覆盖+修改清单；模型只给意见，合格与否由用户判定（用户定案）
```

## 整体流程（定案：先整篇预览过审，再建导出）

```
S0. 需求：用户写 <项目>/需求.md → `流水线.py 需求` → 用户确认
S1. 大纲：写 大纲草案.json（页id/意图/标题）→ `流水线.py 大纲`（校验意图闭集）
        → 用户拍板 → `大纲确认` 落盘 大纲.json
逐页循环：
  S2. 布局：`流水线.py 布局`（候选→草案→预览图）→ 用户看图选 → `布局选 <tpl> --理由`
  S3. 做页：P2 数据写好放 页/待写/<页id>.json → `流水线.py 做页`
        （P1 门查素材 → 进 pages.json → 校验闸 → 生成 → 截图；闸 FAIL 自动回滚）
S4. 总览：`流水线.py 总览` → 用户整篇拍板 → `总览确认`
E1. 导出：从 pages.json 数据原生构建可编辑 PPTX（程序待建，不做 PNG 贴图）
```

一条命令走一步，状态落盘 `<项目>/流水线.json`，可续跑；拍板点全部显式停下等人。
`python 程序/流水线.py 状态` 随时看进度。

## 一句话 → 成品（内容生成层）

```
python 程序/内容生成.py 一句话 --输入 "双11大促战报" --项目 _草稿/双11
# 无 writer：生成 大纲.json + briefs/，按指引填 filled/ 后跑 收集
python 程序/内容生成.py 收集 --briefs <项目>/briefs --filled <项目>/filled \
    --项目 <项目> --主题 dianshang
# 有 writer（LLM/智能体，stdin brief → stdout 页数据 JSON）：
python 程序/内容生成.py 一句话 --输入 "…" --项目 <项目> \
    --writer-cmd "python my_writer.py" --writer-retries 2 --writer-timeout 120
```

- Writer 协议：stdin 收 brief JSON，stdout 只吐页数据 JSON（字段白名单约束，
  越界字段收集时拦截 FAIL）；stderr 日志；exit 非 0 按预算重试。
- 预算与降级：超预算的页记 `<项目>/内容生成_debt.json`（待手填），其余继续。
- chart 页：writer 只给 chart_spec，程序调 图表.py 生成 + 洞察.py 自动写洞察。
- 配图：prompt 走 生图/prompt规约.py（中国人/中国场景）；`--生图` 且后端可用
  时真实生成并登记素材卡，否则出中文"待生图"占位图 + 配图规划.json。

## 手机用控制台

```bash
bash 工作流/控制台/手机.sh --port 8901   # 打印形如 https://xxx.trycloudflare.com/?token=… 的 URL
```

- server.py `--host 0.0.0.0 --token <令牌>`（或环境变量 PPT_CONSOLE_TOKEN）；
  非回环监听无 token 时拒绝启动，不许把无鉴权服务暴露出去。
- 前端已做移动端适配（响应式布局、44px 触控目标），token 经 URL 参数透传给所有 API。
- 说明：cloudflared 隧道在受限网络（如 TLS 被拦截的沙箱）可能建连失败；
  此时手机最稳的路径是直接在对话里说一句话，由 Muse 跑内容生成层交回 PNG/PPTX。

PPTX 是唯一的客户交付物：PNG/HTML 只做预览与过程检查，不直接交付。

## 一句话模式（内容生成层，P0-1）

上面是手工流水线；一句话模式是它的自动化版本——输入一句话，直接出 pages.json：

```
python 程序/内容生成.py 大纲   --输入 "双11大促战报" --输出 /tmp/outline.json
python 程序/内容生成.py 填写单 --大纲 /tmp/outline.json --输出 /tmp/fill.json [--主题 dianshang]
# agent 按 fill.json 的填写说明逐页填 填/图表/配图（文案/数据/拍板标题），存 filled.json
python 程序/内容生成.py 组装   --填写 /tmp/filled.json --项目 示例-双11/双11战报 [--主题 dianshang]
python 程序/内容生成.py 配图   --填写 /tmp/fill.json   # 打印配图 prompt 清单
```

- 填写单：意图→选型规约自动选型（含 _选型留痕）→ 卡型规约出必填字段单 → prompt规约出配图 prompt
- 组装：chart 页 数据→洞察.py（断言标题+insight）→图表.py 渲染 PNG；缺图自动占位图过闸（交付前须换真实生图）；最后过 校验.py，FAIL 不许绕过
- 生图：`内容生成.py 生图 --填写 filled.json --项目 <项目> [--后端 千问|gemini] [--只 P1,P3] [--演练]`
  占位图→真实生图（素材/_步.json M1–M4）：prompt规约 --检查强制 → 后端生图 → 素材/ + 素材卡.jsonl 登记 → 配图.状态=已生图（写回 fill.json，可续跑）；生图后重跑 页面生成+截图
- 规约：规约/内容生成规约.json（选型规则/文案纪律/图表纪律/配图纪律/字段说明）
- 样张：工作流/示例-双11/双11战报（11 页，dianshang 主题，校验 PASS，HTML+PNG 已出）

新主题（定案 D1：改主题 = 换主题卡 + 换 CSS，不碰程序）：

```
1. python 程序/主题问卷.py --主题 <名> --答案 answers.json   # 6 问闭集收敛
2. 填主题卡 → 复制 库/主题/_骨架.css 为 库/theme-<名>.css，只填 :root 10 个令牌值
   （不许改规则；改规则=改骨架，会影响所有主题）
3. python 程序/校验.py --主题 <名>        # 令牌闸＋对比度闸（ink/bg≥4.5、gold/bg≥3.0）
4. python 程序/主题样张.py --主题 <名>    # T4：浅/深两张样张，用户看图拍板后主题卡转定稿
5. PPT_PROJECT=<项目> PPT_THEME_CSS=theme-<名>.css 跑上面 1–5 步
```

## 设计纪律（Library 层的规约，程序按此执行）

- 页面 = 数据 + 页型模板；页型卡数据字段节是页面数据规约的唯一来源
- 新增页型 = 先写页型卡，再写模板函数；卡与代码漂移即修卡
- 页型卡与模板代码的漂移由校验器 `--卡` 模式机检（K1–K6），
  `python 程序/校验.py --卡` 即跑；人工抽查（审计 S2 式）作为复核手段保留
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
