#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""意图识别.py —— 一句话 → {维度: 取值} 的窄接口。

LLM 模式：shell 调 LLM（stdin JSON，stdout JSON），与内容生成._run_writer
同模式（timeout/retries）；输出必须命中闭集，闭集从 主题推荐.py 的
意图词典/深浅意图 程序化抽取（不许手抄枚举，漂移即错）。
越界/非 JSON → 记错重试，耗尽则回退关键词。
无 llm_cmd 配置 → 直接复用 主题推荐.抽取意图（确定性回退，本沙箱走这条）。

用法：
    python 程序/意图识别.py --输入 "双11大促战报"
    python 程序/意图识别.py --输入 "双11大促战报" --llm-cmd "my-llm --stdin-json"
    python 程序/意图识别.py --自检
环境变量：PPT_LLM_CMD（与 writer 同模式的 shell 命令，从 stdin 读 JSON）
"""
import io
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# prompt 模板：只许输出 JSON，只许闭集取值，禁用解释文字
PROMPT = (
    "你是意图分类器。输入是一句话需求和候选维度（维度→允许取值列表）。"
    "只输出一个 JSON 对象：键为维度名，值为该维度的一个允许取值；"
    "拿不准的维度直接省略，不许编造取值。"
    "不许输出解释、前言、markdown 围栏，只输出纯 JSON。"
)


def _闭集():
    """闭集从主题推荐.py 程序化抽取（不许手抄）。"""
    from 主题推荐 import 意图词典, 深浅意图
    闭集 = {}
    for 维, 组s in 意图词典.items():
        闭集[维] = sorted({取值 for _, 取值 in 组s})
    闭集["深浅"] = sorted(深浅意图.keys())
    闭集["深浅否定"] = sorted(深浅意图.keys())
    return 闭集


def _调llm(cmd, 一句话, timeout, retries):
    闭集 = _闭集()
    stdin = json.dumps({"指令": PROMPT, "一句话": 一句话,
                        "候选维度": 闭集}, ensure_ascii=False)
    last_err = "未运行"
    for attempt in range(retries + 1):
        try:
            r = subprocess.run(cmd, shell=True, input=stdin,
                               capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            last_err = "LLM 超时（%ss，第 %d 次）" % (timeout, attempt + 1)
            continue
        if r.returncode != 0:
            last_err = "LLM exit=%d（第 %d 次）: %s" % (
                r.returncode, attempt + 1, (r.stderr or "")[-200:])
            continue
        try:
            data = json.loads(r.stdout)
        except Exception as e:
            last_err = "LLM 输出非 JSON（第 %d 次）: %s" % (attempt + 1, e)
            continue
        if not isinstance(data, dict):
            last_err = "LLM 输出非对象（第 %d 次）" % (attempt + 1)
            continue
        越界 = [(k, v) for k, v in data.items()
                if k not in 闭集 or v not in 闭集[k]]
        if 越界:
            last_err = "LLM 输出越界（第 %d 次）: %s" % (attempt + 1, 越界[:3])
            continue
        return data, None
    return None, last_err


def 识别(一句话, llm_cmd=None, timeout=30, retries=1):
    """返回 {维度: 取值}。有 llm_cmd 则走 LLM（闭集校验），否则/失败回退关键词。"""
    cmd = llm_cmd or os.environ.get("PPT_LLM_CMD")
    if cmd:
        data, err = _调llm(cmd, 一句话, timeout, retries)
        if data is not None:
            return data
        print("意图识别 LLM 失败（%s），回退关键词路径" % err, file=sys.stderr)
    from 主题推荐 import 抽取意图
    return 抽取意图(一句话)


def _自检():
    from 主题推荐 import 意图词典, 抽取意图
    # 1. 闭集程序化抽取一致性
    闭集 = _闭集()
    assert set(闭集) >= set(意图词典) | {"深浅", "深浅否定"}, "闭集维度缺失"
    assert "电商" in 闭集["题材"], "闭集取值缺失"
    print("自检1 OK：闭集 %d 维，程序化抽取自主题推荐.py" % len(闭集))
    # 2. stub LLM 越界输出被拦截 → 回退关键词
    越界cmd = "echo '{\"题材\":\"不存在的题材\",\"气质\":\"科技\"}'"
    r = 识别("双11大促战报", llm_cmd=越界cmd, retries=0)
    assert r == 抽取意图("双11大促战报"), "越界未被拦截：%s" % r
    print("自检2 OK：stub 越界输出被拦截，回退关键词一致")
    # 3. stub LLM 合法输出通过
    合法cmd = "printf '{\"题材\":\"融资\",\"气质\":\"科技\"}'"
    r = 识别("AI 芯片发布会", llm_cmd=合法cmd, retries=0)
    assert r == {"题材": "融资", "气质": "科技"}, "合法输出未通过：%s" % r
    print("自检3 OK：stub 合法输出通过闭集校验")
    # 4. stub 非 JSON → 回退
    坏cmd = "echo '不是json'"
    r = 识别("双11大促战报", llm_cmd=坏cmd, retries=0)
    assert r == 抽取意图("双11大促战报"), "非 JSON 未回退"
    print("自检4 OK：stub 非 JSON 回退关键词")
    # 5. 无配置回退（确保环境变量未干扰）
    旧 = os.environ.pop("PPT_LLM_CMD", None)
    try:
        r = 识别("双11大促战报")
        assert r == 抽取意图("双11大促战报"), "无配置回退不一致"
    finally:
        if 旧 is not None:
            os.environ["PPT_LLM_CMD"] = 旧
    print("自检5 OK：无 llm_cmd 回退关键词路径")
    print("意图识别 --自检 全过")
    return 0


def main():
    import argparse
    ap = argparse.ArgumentParser(prog="意图识别.py")
    ap.add_argument("--输入", default=None)
    ap.add_argument("--llm-cmd", default=None)
    ap.add_argument("--自检", action="store_true")
    a = ap.parse_args()
    if a.自检:
        sys.exit(_自检())
    if not a.输入:
        print("需 --输入 或 --自检", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(识别(a.输入, llm_cmd=a.llm_cmd), ensure_ascii=False))


if __name__ == "__main__":
    main()
