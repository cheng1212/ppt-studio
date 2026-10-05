#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一句话.py —— 一句话 → 大纲 → 页规格。

一句话模式的"脑子"：
    输入：一句话（如"双11大促战报"）
    输出：大纲.json = {意图, 主题推荐, 每页{意图, tpl建议, 文案提示}}

流程：
    1. 抽取意图（复用 主题推荐.py 的 抽取意图）
    2. 主题推荐 top3（复用）
    3. 按 内容类型 取大纲模板（程序/大纲模板.py）
    4. 意图映射到选型规约闭集
    5. 输出 JSON，agent 按文案提示填真实文案/数据 → pages.json

用法：
    python 程序/一句话.py --输入 "双11大促战报" --输出 /tmp/outline.json
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 主题推荐 import 抽取意图, 推荐
from 大纲模板 import 取模板, 意图映射


def 生成大纲(一句话):
    意图 = 抽取意图(一句话)
    候选, 命中, _ = 推荐(一句话, top=3)
    内容类型 = 意图.get("内容类型", "数据报告")
    # 内容类型 → 模板名
    模板名 = {"数据报告": "数据报告", "课件": "课件",
            "方案": "方案", "总结": "总结"}.get(内容类型, "数据报告")
    页s = []
    for i, p in enumerate(取模板(模板名), 1):
        页s.append({
            "页": "P%d" % i,
            "意图": 意图映射.get(p["意图"], p["意图"]),
            "tpl建议": p["tpl建议"],
            "文案提示": p["文案提示"],
        })
    return {
        "输入": 一句话,
        "意图": 意图,
        "主题推荐": [{"主题": t["name"], "状态": t["状态"], "理由": r}
                   for _, t, r in 候选],
        "命中": 命中,
        "大纲模板": 模板名,
        "页数": len(页s),
        "页": 页s,
        "下一步": "agent 按每页'文案提示'填真实文案/数据，写 pages.json，走 校验→生成→截图",
    }


def main():
    import argparse
    ap = argparse.ArgumentParser(prog="一句话.py")
    ap.add_argument("--输入", required=True, help="一句话需求")
    ap.add_argument("--输出", default=None, help="大纲 JSON 输出路径")
    a = ap.parse_args()
    out = 生成大纲(a.输入)
    txt = json.dumps(out, ensure_ascii=False, indent=2)
    if a.输出:
        io.open(a.输出, "w", encoding="utf-8").write(txt)
        print("大纲 → %s（%d页，模板=%s）" % (a.输出, out["页数"], out["大纲模板"]),
              file=sys.stderr)
    else:
        print(txt)  # stdout 只走纯 JSON，摘要走 stderr
    # 打印意图和主题推荐摘要（stderr，不污染 stdout 的 JSON）
    print("意图：%s" % "、".join("%s=%s" % kv for kv in out["意图"].items()),
          file=sys.stderr)
    print("主题：%s" % " / ".join(t["主题"] for t in out["主题推荐"]),
          file=sys.stderr)


if __name__ == "__main__":
    main()
