# -*- coding: utf-8 -*-
# 生图 prompt 规约 —— M1 定 prompt / M2 生成前强制执行。
#
# 【中国人默认·2026-10-05 chengge 定】
# chengge 的场景在中国（课堂/电商/商业），生图默认按中国写：
# - 有人物 → 东亚面孔中国人
# - 场景 → 中国（教室/办公室/街道/家庭/城市，按题材选）
#
# 用法：
#   python prompt规约.py --检查 "prompt 原文"
#   python prompt规约.py --补全 "prompt 原文" [--有人物] [--场景 办公室]
import argparse
import sys

REN_SUFFIX = "Chinese people, East Asian features"
SCENE_SUFFIX = {
    "教室": "modern Chinese classroom",
    "办公室": "modern Chinese office",
    "街道": "Chinese city street",
    "家庭": "modern Chinese home interior",
    "城市": "Chinese city",
    "仓库": "Chinese e-commerce warehouse",
    "直播间": "Chinese livestream studio",
}

PEOPLE_WORDS = ["people", "person", "man", "woman", "girl", "boy", "host",
                "team", "teacher", "student", "worker", "crowd", "family",
                "shoppers", "audience"]


def check(prompt):
    # 返回 (ok, 缺项列表)
    missing = []
    p = prompt.lower()
    has_people = any(w in p for w in PEOPLE_WORDS)
    if has_people and "chinese" not in p and "east asian" not in p and "asian" not in p:
        missing.append("PEOPLE_WITHOUT_CN")
    return (not missing, missing)


def complete(prompt, has_people=False, scene=None):
    # 缺啥补啥，返回补全后的 prompt
    p = prompt.rstrip().rstrip(",").rstrip(".")
    low = prompt.lower()
    if has_people and "chinese" not in low and "east asian" not in low and "asian" not in low:
        p += ", " + REN_SUFFIX
    if scene and scene in SCENE_SUFFIX and "china" not in low and "chinese" not in low:
        p += ", " + SCENE_SUFFIX[scene]
    return p


CN_MSG = {
    "PEOPLE_WITHOUT_CN": "有人物但未声明 Chinese/East Asian（默认须为中国人）",
}




# 【写实默认·2026-10-05】去 AI 味：用摄影语言代替品质堆砌词。
# 五层（aiartrevolution 实测）：光源/镜头/皮肤/场景/瞬间。
# 禁止词：8K/masterpiece/ultra-detailed/HDR/flawless/perfect/beautiful（直接要出磨皮塑料感）。
# Gemini 无负面 prompt 字段，一律正面描述（写"visible pores"不写"no smooth skin"）。
REALISM_SUFFIX = (
    "shot on 50mm lens at f/2.8, natural light falloff, "
    "natural skin texture with visible pores, subtle film grain, "
    "candid unposed moment, imperfect lived-in scene details"
)


def add_realism(prompt):
    """拼写实后缀（已含则不重复）。"""
    if "50mm lens" in prompt or "film grain" in prompt:
        return prompt
    return prompt.rstrip().rstrip(",").rstrip(".") + ", " + REALISM_SUFFIX


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--检查", default=None, help="check a prompt")
    ap.add_argument("--补全", default=None, help="complete a prompt")
    ap.add_argument("--有人物", action="store_true")
    ap.add_argument("--场景", default=None, choices=list(SCENE_SUFFIX.keys()))
    ap.add_argument("--写实", action="store_true", help="拼写实后缀（去 AI 味）")
    a = ap.parse_args()
    chk = getattr(a, "检查")
    cpl = getattr(a, "补全")
    if chk:
        ok, missing = check(chk)
        if ok:
            print("OK")
        else:
            print("FAIL:")
            for x in missing:
                print("  - " + CN_MSG.get(x, x))
            sys.exit(1)
    elif cpl:
        out = complete(cpl, has_people=a.有人物, scene=a.场景)
        print(add_realism(out) if a.写实 else out)
    else:
        ap.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()