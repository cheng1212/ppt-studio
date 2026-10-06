#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""洞察生成 —— 图表数据的洞察走提问哲学（LLM路径）。

管线：归约（kind+数据→固定JSON）→ 提示词（固定模板，喂大模型）
      → 校验（形状/数字出处/标题/条数）→ 输出与 洞察.py 同形，可直接替换
大模型调用由 agent/控制台完成，本程序不碰 LLM API。
洞察.py（规则版）保留作离线兜底。

用法:
  python 洞察生成.py 归约 --kind bar --数据 '{"A":12,"B":12}' --标题 "得失电子守恒" --输出 /tmp/ins-brief.json
  python 洞察生成.py 提示词 --归约 /tmp/ins-brief.json
  python 洞察生成.py 校验 --归约 /tmp/ins-brief.json --洞察 /tmp/ins.json
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import read_json, die


def 中文数(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def 归约(kind, 数据, 标题, 受众="公众"):
    return {"kind": kind, "数据": 数据, "页面标题": 标题, "受众": 受众}


PROMPT_TPL = (
    "你是数据分析师，擅长把数字讲成人话。需求（JSON）：\n{brief}\n\n"
    "第一步：用一句话说出这组数据呈现的核心特征或矛盾。\n"
    "第二步：生成2个标题候选+3条支撑，输出JSON："
    "{{\"标题候选\": [], \"支撑\": [], \"数据事实\": {{}}, \"洞察推理\": str}}。\n"
    "标题候选=断言句≤30字；支撑每条≤40字、口语化、面向受众。\n\n"
    "硬约束：每条支撑/标题中出现的每个数字，必须在'数据'或'数据事实'中找到出处，"
    "找不到=编造；不许编造数据没有的结论；不许'共N类、总计X'式正确的废话。\n"
    "只输出JSON，不要markdown、不要解释。"
)

数字 = re.compile(r"\d+(?:\.\d+)?%?")


def norm(n):
    """数值归一化：1.10==1.1，40%==40"""
    n = n.rstrip("%")
    if "." in n:
        n = n.rstrip("0").rstrip(".")
    return n


def 数字集合(obj):
    return {norm(n) for n in 数字.findall(json.dumps(obj, ensure_ascii=False))}


def 校验(brief, ins):
    errs = []
    for k in ["标题候选", "支撑", "数据事实"]:
        if k not in ins:
            errs.append("缺字段 %s（须与洞察.py同形）" % k)
    if errs:
        return errs
    if len(ins["标题候选"]) != 2:
        errs.append("标题候选须=2条，实%d条" % len(ins["标题候选"]))
    if len(ins["支撑"]) != 3:
        errs.append("支撑须=3条，实%d条" % len(ins["支撑"]))
    for t in ins["标题候选"]:
        if 中文数(t) > 30:
            errs.append("标题候选中文%d字>30：%r" % (中文数(t), t[:12]))
    允许 = 数字集合(brief["数据"]) | 数字集合(ins["数据事实"])
    for sec in ["标题候选", "支撑"]:
        for s in ins[sec]:
            for n in 数字.findall(s):
                if norm(n) not in 允许:
                    errs.append("%s中数字%s无出处，判编造：%r" % (sec, n, s[:24]))
    return errs


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("归约")
    p.add_argument("--kind", required=True)
    p.add_argument("--数据", required=True)
    p.add_argument("--标题", required=True)
    p.add_argument("--受众", default="公众")
    p.add_argument("--输出", required=True)
    p = sub.add_parser("提示词")
    p.add_argument("--归约", required=True)
    p = sub.add_parser("校验")
    p.add_argument("--归约", required=True)
    p.add_argument("--洞察", required=True)
    a = ap.parse_args()
    if a.cmd == "归约":
        b = 归约(a.kind, json.loads(a.数据), a.标题, a.受众)
        json.dump(b, open(a.输出, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("归约 → %s（kind=%s）" % (a.输出, a.kind))
    elif a.cmd == "提示词":
        b = read_json(a.归约)
        print(PROMPT_TPL.format(brief=json.dumps(b, ensure_ascii=False, indent=2)))
    elif a.cmd == "校验":
        errs = 校验(read_json(a.归约), read_json(a.洞察))
        if errs:
            print("FAIL 校验不通过（%d项）：" % len(errs))
            for e in errs:
                print(" - " + e)
            sys.exit(1)
        print("校验 PASS：洞察可用（形状/数字出处/标题/条数）")
    else:
        die("用法见文件头注释")


if __name__ == "__main__":
    main()
