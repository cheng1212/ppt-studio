#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文案生成 —— 填写单每页的文案走提问哲学。

管线：归约（填写单页条目→固定JSON）→ 提示词（固定模板，喂大模型）
      → 校验（必填/标题/结构/数字防编造）→ 填 回填进填写单
大模型调用由 agent/控制台完成，本程序不碰 LLM API。

用法:
  python 文案生成.py 归约 --填写单 /tmp/fill.json --页 P4 --输出 /tmp/copy-brief.json
  python 文案生成.py 提示词 --归约 /tmp/copy-brief.json
  python 文案生成.py 校验 --归约 /tmp/copy-brief.json --文案 /tmp/copy.json
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import read_json, die

# 与 校验.py ⑨ 同源，并加严：LLM 路径下"题"结尾亦判标签式
标签词 = ("介绍", "概况", "概述", "总结", "分析", "情况", "说明", "题")


def 中文数(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def 页面条目():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "规约", "卡型规约.json")
    return read_json(p)["页面条目"]


def 归约(fill_path, 页码, 受众="公众", 行业="通用"):
    d = read_json(fill_path)
    pages = d["页"] if isinstance(d, dict) else d
    pg = next(p for p in pages if p["页"] == 页码)
    数字上下文 = ""
    g = pg.get("图表") or {}
    if g.get("数据"):
        数字上下文 = json.dumps(g["数据"], ensure_ascii=False)
    return {
        "页码": 页码,
        "意图": pg.get("意图", ""),
        "tpl": pg["tpl"],
        "字段说明": pg.get("字段说明", {}),
        "文案提示": pg.get("文案提示", ""),
        "受众": 受众,
        "行业": 行业,
        "数字上下文": 数字上下文,
    }


PROMPT_TPL = (
    "你是资深PPT文案策划，擅长断言式标题。需求（JSON）：\n{brief}\n\n"
    "第一步：用一句话说出这一页要让观众带走的核心信息。\n"
    "第二步：按字段说明逐字段写文案，输出JSON：{{\"填\": {{字段: 文案}}, \"页推理\": str}}。\n"
    "字段约束：title=断言句（结论+原因，≤30汉字，禁以介绍/概况/概述/总结/分析/情况/说明结尾）；"
    "cards/rows按项写，每项一句话。\n\n"
    "硬约束：标题必须是结论句，不许标签式；"
    "文案中的数字不许编造（数字上下文非空时，每个数字必须在其中出现）；面向受众的口语。\n"
    "只输出JSON，不要markdown、不要解释。"
)


def 校验(brief, copy):
    errs = []
    if not isinstance(copy, dict) or "填" not in copy:
        return ["须是{填:{...},页推理:str}形状"]
    填 = copy["填"]
    try:
        必填 = 页面条目()[brief["tpl"]]["必填"]
    except KeyError:
        return ["未知tpl %s" % brief["tpl"]]
    for f in 必填:
        if f == "img" and brief["tpl"] == "chart":
            continue  # 图表页 img 由组装时 图表.py 自动渲染，文案不填
        if f not in 填 or not 填[f]:
            errs.append("缺必填字段 %s" % f)
    t = 填.get("title", "")
    if t:
        if 中文数(t) > 30:
            errs.append("title中文%d字>30" % 中文数(t))
        if any(t.strip().endswith(w) for w in 标签词) and len(t.strip()) <= 10:
            errs.append("title疑似标签式：%r" % t.strip())
    ctx = brief.get("数字上下文", "")
    if ctx:
        允许 = set(re.findall(r"\d+(?:\.\d+)?", ctx))
        # 只查文案内容字段：编号类（no/brow/kick/foot/eb/ghost）天生带数字，不查；
        # 题1/第2类序号不查（lookbehind 排除）
        查字段 = [f for f in 填 if f not in
                  ("no", "brow", "kick", "foot", "eb", "ghost")]
        for f in 查字段:
            txt = json.dumps(填[f], ensure_ascii=False)
            for m in re.finditer(r"\d+(?:\.\d+)?", txt):
                if m.start() > 0 and txt[m.start() - 1] in "题第":
                    continue
                if m.group() not in 允许:
                    errs.append("字段%s数字%s不在数字上下文中，判编造" % (f, m.group()))
    return errs


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("归约")
    p.add_argument("--填写单", required=True)
    p.add_argument("--页", required=True)
    p.add_argument("--受众", default="公众")
    p.add_argument("--行业", default="通用")
    p.add_argument("--输出", required=True)
    p = sub.add_parser("提示词")
    p.add_argument("--归约", required=True)
    p = sub.add_parser("校验")
    p.add_argument("--归约", required=True)
    p.add_argument("--文案", required=True)
    a = ap.parse_args()
    if a.cmd == "归约":
        b = 归约(a.填写单, a.页, a.受众, a.行业)
        json.dump(b, open(a.输出, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("归约 → %s（%s/%s）" % (a.输出, a.页, b["tpl"]))
    elif a.cmd == "提示词":
        b = read_json(a.归约)
        print(PROMPT_TPL.format(brief=json.dumps(b, ensure_ascii=False, indent=2)))
    elif a.cmd == "校验":
        errs = 校验(read_json(a.归约), read_json(a.文案))
        if errs:
            print("FAIL 校验不通过（%d项）：" % len(errs))
            for e in errs:
                print(" - " + e)
            sys.exit(1)
        print("校验 PASS：文案可用（必填/标题/结构/数字防编造）")
    else:
        die("用法见文件头注释")


if __name__ == "__main__":
    main()
