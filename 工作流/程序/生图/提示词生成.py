#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生图提示词生成 —— 配图 prompt 走提问哲学。

管线：归约（页面信息→固定JSON）→ 提示词（固定模板，喂大模型）
      → 校验（prompt规约.check/禁令/语言）→ prompt 进生图管线
大模型调用由 agent/控制台完成，本程序不碰 LLM API。

用法:
  python 提示词生成.py 归约 --标题 "氧化还原反应" --摘要 "电子转移是本质" \
      --意图 封面 --行业 教育 --场景 教室 --情绪 清新,启发 --输出 /tmp/img-brief.json
  python 提示词生成.py 提示词 --归约 /tmp/img-brief.json
  python 提示词生成.py 校验 --prompt /tmp/prompt.json
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from 基座 import read_json, die
from prompt规约 import check as 规约检查


def 归约(标题, 摘要, 意图, 行业, 场景, 情绪, 配图字段="img"):
    return {
        "页面标题": 标题,
        "页文案摘要": 摘要,
        "意图": 意图,
        "行业": 行业,
        "场景": 场景,
        "主题情绪": 情绪,
        "配图字段": 配图字段,
    }


PROMPT_TPL = (
    "你是商业摄影指导兼AI生图提示词专家。需求（JSON）：\n{brief}\n\n"
    "第一步：用一句话说出这张图的情绪与视觉焦点。\n"
    "第二步：写英文prompt，输出JSON：{{\"prompt\": str, \"构图推理\": str}}。\n"
    "prompt要求：commercial photography打底；写清镜头/光线/构图；"
    "中国场景（教室→modern Chinese classroom；直播间→Chinese livestream studio；"
    "仓库→Chinese e-commerce warehouse；办公室→modern Chinese office；"
    "街道→Chinese city street；家庭→modern Chinese home interior）；"
    "有人物→East Asian面孔。\n\n"
    "硬约束：必须含'no text, no numbers, no logos, no watermark'；"
    "有人物必须含Chinese people或East Asian；场景词必须出自上述闭集；"
    "真人摄影感，不许水彩抽象（除非意图要求）。\n"
    "只输出JSON，不要markdown、不要解释。"
)


def 校验(obj):
    errs = []
    p = obj["prompt"] if isinstance(obj, dict) else obj
    if not isinstance(p, str) or not p.strip():
        return ["prompt为空"]
    ok, 缺项 = 规约检查(p)
    for m in 缺项:
        errs.append("prompt规约缺项：%s" % m)
    low = p.lower()
    for w in ["no text", "no numbers", "no logos"]:
        if w not in low:
            errs.append("禁令缺失：%s" % w)
    n = len(p.split())
    if not (30 <= n <= 120):
        errs.append("prompt长度%d词，须30–120词" % n)
    return errs


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("归约")
    p.add_argument("--标题", required=True)
    p.add_argument("--摘要", required=True)
    p.add_argument("--意图", required=True)
    p.add_argument("--行业", required=True)
    p.add_argument("--场景", required=True)
    p.add_argument("--情绪", required=True, help="逗号分隔")
    p.add_argument("--配图字段", default="img")
    p.add_argument("--输出", required=True)
    p = sub.add_parser("提示词")
    p.add_argument("--归约", required=True)
    p = sub.add_parser("校验")
    p.add_argument("--prompt", required=True,
                   help="JSON文件（含prompt字段）或直接prompt文本文件")
    a = ap.parse_args()
    if a.cmd == "归约":
        b = 归约(a.标题, a.摘要, a.意图, a.行业, a.场景,
                 [e.strip() for e in a.情绪.split(",")], a.配图字段)
        json.dump(b, open(a.输出, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("归约 → %s" % a.输出)
    elif a.cmd == "提示词":
        b = read_json(a.归约)
        print(PROMPT_TPL.format(brief=json.dumps(b, ensure_ascii=False, indent=2)))
    elif a.cmd == "校验":
        raw = open(a.prompt, encoding="utf-8").read()
        try:
            obj = json.loads(raw)
        except Exception:
            obj = {"prompt": raw}
        errs = 校验(obj)
        if errs:
            print("FAIL 校验不通过（%d项）：" % len(errs))
            for e in errs:
                print(" - " + e)
            sys.exit(1)
        print("校验 PASS：prompt可用（规约/禁令/语言）")
    else:
        die("用法见文件头注释")


if __name__ == "__main__":
    main()
