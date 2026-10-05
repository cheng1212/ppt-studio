#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主题问卷 —— 按规约收敛主题答案，生成主题卡骨架。

定主题只问固定的 6 个问题（规约/主题问卷规约.json），答案只许从枚举里选，
闭集外即拒——不让大模型自由发挥主题。

用法:
  python 主题问卷.py --主题 <主题名> --答案 answers.json   # 非交互
  python 主题问卷.py --主题 <主题名>                        # 逐题交互
answers.json 格式: {"Q1": "暖白", "Q2": "焰金", ..., "Q6": ["色块标签","金边结论条"]}
产出: 库/主题/卡片/主题卡-<主题名>.md（状态=草案）
"""
import argparse, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, USAGE, ERR, read_json, die, LIB_DIR


def load_rules():
    return read_json(os.path.join(os.path.dirname(LIB_DIR), "规约", "主题问卷规约.json"))


def check_answer(q, ans):
    enum = q["枚举"]
    if q.get("多选"):
        if not isinstance(ans, list) or not ans:
            return "Q%s 须是非空数组" % q["id"]
        bad = [a for a in ans if a not in enum]
        if bad:
            return "%s 含非法选项 %s，合法取值为 %s" % (q["id"], bad, enum)
    else:
        if ans not in enum:
            return "%s 答案 %r 非法，合法取值为 %s" % (q["id"], ans, enum)
    return None


def ask_interactive(q):
    enum = q["枚举"]
    print("\n[%s] %s" % (q["id"], q["问题"]))
    print("  说明: %s" % q["说明"])
    for i, e in enumerate(enum, 1):
        print("  %d. %s" % (i, e))
    dflt = q.get("默认值")
    dflt_txt = ("（默认: %s，直接回车）" % ("/".join(dflt) if isinstance(dflt, list) else dflt)) if dflt else ""
    while True:
        raw = input("  请选择%s: " % dflt_txt).strip()
        if not raw and dflt:
            return dflt
        if q.get("多选"):
            picks = [p.strip() for p in raw.replace("，", ",").split(",") if p.strip()]
            ans = [enum[int(p) - 1] for p in picks if p.isdigit() and 1 <= int(p) <= len(enum)] or picks
        else:
            ans = enum[int(raw) - 1] if raw.isdigit() and 1 <= int(raw) <= len(enum) else raw
        err = check_answer(q, ans)
        if err:
            print("  !!", err)
            continue
        return ans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--主题", required=True, help="主题名（如 ocean）")
    ap.add_argument("--答案", default=None, help="答案 JSON 路径（非交互模式）")
    a = ap.parse_args()

    rules = load_rules()
    answers = {}
    if a.答案:
        given = read_json(a.答案)
        for q in rules["问题"]:
            if q["id"] not in given:
                die("答案缺 Q%s（%s）" % (q["id"], q["问题"]), code=USAGE)
            err = check_answer(q, given[q["id"]])
            if err:
                die(err, code=FAIL)
            answers[q["id"]] = given[q["id"]]
        if "主色" not in given or not given["主色"]:
            die("答案缺 主色（T0 设计简报拍板的主色 hex，如 161A21）", code=USAGE)
        answers["主色"] = given["主色"].strip().lstrip("#").upper()
    else:
        for q in rules["问题"]:
            answers[q["id"]] = ask_interactive(q)
        answers["主色"] = input("  主色 hex（T0 简报拍板，如 161A21）: ").strip().lstrip("#").upper()
        if len(answers["主色"]) != 6:
            die("主色 hex 非法", code=USAGE)

    # v2：调色板生成器按 60-30-10 出完整 12 令牌，不再手填
    from 配色 import full_scheme
    scheme = full_scheme(answers["主色"])
    print("调色板方案（60-30-10）：")
    for tok in ["--bg", "--bg-dark", "--gold", "--gold-soft", "--ink", "--green",
                "--silver", "--muted", "--line", "--card", "--ox", "--ink-dark"]:
        print("  %s #%s" % (tok, scheme[tok]))
    print("确认无误回车继续，人要微调请现在改 answers.json 重跑（微调须记录偏离）")
    if not a.答案:
        input()

    name = a.主题
    out = os.path.join(LIB_DIR, "主题", "卡片", "主题卡-%s.md" % name)
    if os.path.exists(out):
        die("主题卡已存在: %s（不覆盖）" % out, code=FAIL)

    lines = [
        "# 主题卡-%s" % name, "",
        "- id: 主题卡-%s" % name,
        "- 卡型: 主题卡",
        "- 标题: （待填）",
        "- 来源轨: 用户输入",
        "- 生产者: （待填）",
        "- 状态: 草案",
        "- css路径: 库/theme-%s.css" % name, "",
        "## 一句话", "", "（待填）", "",
        "## 问卷答案（本卡拍板依据）", "",
    ]
    for q in rules["问题"]:
        ans = answers[q["id"]]
        lines.append("- %s %s: %s" % (q["id"], q["问题"], "/".join(ans) if isinstance(ans, list) else ans))
    用途 = {"--bg": "知识页底（60% 主色）", "--bg-dark": "深页底（封面/章节页）",
            "--gold": "唯一核心强调（10%，只落焦点）", "--gold-soft": "次级强调",
            "--ink": "主墨色（正文，≥7.0）", "--green": "标题/标签（30% 副色）",
            "--silver": "深底辅助字", "--muted": "弱化字（≥4.5）",
            "--line": "发丝线", "--card": "卡底",
            "--ox": "语义警示/热销（≥3.0）",
            "--ink-dark": "深底正文字（≥4.5）"}
    tok_rows = ["| %s | #%s | %s |" % (t, scheme[t], 用途[t])
               for t in ["--bg", "--bg-dark", "--gold", "--gold-soft", "--ink",
                         "--green", "--silver", "--muted", "--line", "--card",
                         "--ox", "--ink-dark"]]
    lines += ["",
              "## 配色令牌表（令牌/色值/用途；60-30-10 由配色.py 生成）", "",
              "| 令牌 | 色值 | 用途 |",
              "|---|---|---|"] + tok_rows + [
              "", "## 间距", "",
              "- 页边距（--mx）: （待填，如 120px）",
              "- 页头起始（--head-top）: （待填，如 126px）",
              "", "## 页眉页脚系统", "", "（待填）",
              "", "## 结构件清单", "",
              "本主题选用: %s" % "、".join(answers["Q6"]),
              "", "## 设计纪律", "",
              "1. 知识页禁止裸列表；2. 实物特写图 contain；3. 配色 ≤ 主色1 + 强调色1 + 中性",
              "", "## css路径", "",
              "库/theme-%s.css（待手写；校验器按规约主题令牌逐个核对存在）" % name,
              "", "## 下游", "", "（待填）", ""]
    io.open(out, "w", encoding="utf-8").write("\n".join(lines))
    print("OK 已生成主题卡骨架:", out)
    # T3：由骨架 + 方案直接生成 CSS，不手写
    skel = io.open(os.path.join(LIB_DIR, "主题", "_骨架.css"), encoding="utf-8").read()
    import re as _re
    # 取骨架 :root 当前 12 个 token 的旧值，逐个替换为方案值
    for tok, new_hex in scheme.items():
        skel, n = _re.subn(r"(%s\s*:\s*)#[0-9a-fA-F]{6}" % tok.replace("-", r"\-"),
                           r"\g<1>#%s" % new_hex, skel, count=1)
        if n == 0:
            die("骨架缺令牌 %s" % tok, code=FAIL)
    css_out = os.path.join(LIB_DIR, "theme-%s.css" % name)
    if os.path.exists(css_out):
        die("主题 CSS 已存在: %s（不覆盖）" % css_out, code=FAIL)
    io.open(css_out, "w", encoding="utf-8").write(skel)
    print("OK 已生成主题 CSS:", css_out)
    print("下一步: 补主题卡文字部分 → python 程序/校验.py --主题 %s → python 程序/主题样张.py --主题 %s" % (name, name))


if __name__ == "__main__":
    main()
