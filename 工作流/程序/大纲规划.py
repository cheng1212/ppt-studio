#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""大纲规划 —— 大纲页意图走提问哲学（LLM动态规划路径）。

管线：归约（沿用主题生成归约格式）→ 提示词（固定模板，喂大模型）
      → 校验（闭集/结构/节奏）→ 输出大纲JSON（与 一句话.py 同形）
大模型调用由 agent/控制台完成，本程序不碰 LLM API。
一句话.py（规则模板版）保留作离线兜底。

用法:
  python 大纲规划.py 归约 --输入 "社区团购运营方案" --输出 /tmp/ol-brief.json
  python 大纲规划.py 提示词 --归约 /tmp/ol-brief.json
  python 大纲规划.py 校验 --大纲 /tmp/outline.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import read_json, die
from 主题生成 import 归约 as 主题归约


def 意图闭集():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "规约", "选型规约.json")
    return read_json(p)["意图闭集"]


意图列表 = ",".join([
    "封面", "章节", "特征", "关键指标", "趋势", "对比", "数据对比", "构成",
    "增减构成", "流程", "方法", "因果", "相关性", "亮点", "目标达成", "目录",
    "历程", "漏斗", "循环", "分支", "性质"])


PROMPT_TPL = (
    "你是资深课程设计师/咨询顾问。用户需求（JSON）：\n{brief}\n\n"
    "第一步：用一句话说出听众画像与他们听完要带走什么。\n"
    "第二步：生成N页大纲，每页输出JSON对象："
    "{{\"页码\": str, \"意图\": str, \"一句话内容\": str, \"为什么需要这一页\": str}}。\n\n"
    "硬约束：意图必须出自闭集[{intents}]；6–12页；P1=封面；至少1个章节页；"
    "最后一页=小结/行动/致谢类；不许连续3页同一意图。\n"
    "只输出JSON数组，不要markdown、不要解释。"
)

小结类 = {"特征", "关键指标", "目标达成"}


def 校验(outline):
    errs = []
    if not isinstance(outline, list) or not (6 <= len(outline) <= 12):
        return ["须是6–12页的JSON数组"]
    闭集 = set(意图闭集())
    for i, p in enumerate(outline):
        for k in ["页码", "意图", "一句话内容", "为什么需要这一页"]:
            if k not in p or not p[k]:
                errs.append("第%d页缺字段%s" % (i + 1, k))
        if p.get("意图") not in 闭集:
            errs.append("第%d页意图%r不在闭集中" % (i + 1, p.get("意图")))
    if outline[0].get("意图") != "封面":
        errs.append("P1意图须=封面")
    if not any(p.get("意图") == "章节" for p in outline):
        errs.append("至少需要1个章节页")
    if outline[-1].get("意图") not in 小结类:
        errs.append("尾页意图须为小结类%r" % 小结类)
    for i in range(len(outline) - 2):
        its = [outline[i + k].get("意图") for k in range(3)]
        if its[0] == its[1] == its[2]:
            errs.append("第%d–%d页连续3页同一意图%r" % (i + 1, i + 3, its[0]))
    return errs


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("归约")
    p.add_argument("--输入", required=True)
    p.add_argument("--输出", required=True)
    p = sub.add_parser("提示词")
    p.add_argument("--归约", required=True)
    p = sub.add_parser("校验")
    p.add_argument("--大纲", required=True)
    a = ap.parse_args()
    if a.cmd == "归约":
        b = 主题归约(a.输入)
        json.dump(b, open(a.输出, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("归约 → %s（行业=%s）" % (a.输出, b["行业"]))
    elif a.cmd == "提示词":
        b = read_json(a.归约)
        print(PROMPT_TPL.format(brief=json.dumps(b, ensure_ascii=False, indent=2),
                                intents=意图列表))
    elif a.cmd == "校验":
        errs = 校验(read_json(a.大纲))
        if errs:
            print("FAIL 校验不通过（%d项）：" % len(errs))
            for e in errs:
                print(" - " + e)
            sys.exit(1)
        print("校验 PASS：大纲可用（闭集/结构/节奏）")
    else:
        die("用法见文件头注释")


if __name__ == "__main__":
    main()
