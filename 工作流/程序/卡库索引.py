#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""卡库索引.py —— 技能供给层的"拿"。

程序启动时扫描卡库建内存索引。不手写技能注册表：索引从卡片字段长出来，
改卡即改行为（新增一张卡，Agent 自动就会用）。

扫描源：
- 库/页型/卡片/页型卡-*.md：front matter `- 版式族:` / `- 标题:`、`## 适用场景`、`## 纪律`
- 库/主题/卡片/主题卡-*.md：`## 匹配标签`、`## 一句话`、`## 设计纪律`、
  `## css路径`、`## 配色令牌表`（--gold 行的用途＝强调色语义）
- 规约/版式族.json：族 → {何时用， 成员， 选型口诀}
- 规约/选型规约.json：映射（只做交叉校验，WARN 不自动改规约）

对外 API：load_index()、知识包_页型(tpl)、知识包_主题(theme)、意图查页型(意图)
用法：python 程序/卡库索引.py --自检
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import LIB_DIR, RULES_DIR, WORKFLOW

页型卡dir = os.path.join(LIB_DIR, "页型", "卡片")
主题卡dir = os.path.join(LIB_DIR, "主题", "卡片")

_INDEX = None


def _读节(path, 节名前缀):
    """取 `## <节名前缀>...` 到下一个 `## ` 之间的正文（去空行）。"""
    txt = io.open(path, encoding="utf-8").read()
    lines = txt.split("\n")
    抓 = False
    out = []
    for ln in lines:
        if ln.startswith("## "):
            if 抓:
                break
            if ln[3:].strip().startswith(节名前缀):
                抓 = True
            continue
        if 抓 and ln.strip():
            out.append(ln.strip())
    return "\n".join(out)


def _读front(path):
    """front matter：第一个 `## ` 之前的 `- k: v` 行。"""
    txt = io.open(path, encoding="utf-8").read()
    d = {}
    for ln in txt.split("\n"):
        if ln.startswith("## "):
            break
        m = re.match(r"-\s*([^:：]+)\s*[:：]\s*(.*)", ln)
        if m:
            d[m.group(1).strip()] = m.group(2).strip()
    return d


def _bullets(节文本):
    # 兼容 `- ` 与 `1.`/`1)`/`1、` 两种列表写法（2026-10-06：旧主题卡曾用编号列表导致抽空）
    items = []
    for ln in 节文本.split("\n"):
        s = ln.strip()
        m = re.match(r"^(?:-\s*|\d+[.)、]\s*)(.+)$", s)
        if m:
            items.append(m.group(1).strip())
    return items


def _扫页型卡():
    页型 = {}
    for f in sorted(os.listdir(页型卡dir)):
        if not (f.startswith("页型卡-") and f.endswith(".md")):
            continue
        tpl = f[len("页型卡-"):-len(".md")]
        path = os.path.join(页型卡dir, f)
        front = _读front(path)
        纪律 = _bullets(_读节(path, "纪律"))
        页型[tpl] = {
            "标题": front.get("标题", ""),
            "状态": front.get("状态", ""),
            "版式族": front.get("版式族", ""),
            "适用场景": _读节(path, "适用场景"),
            "纪律": 纪律,
        }
    return 页型


def _扫主题卡():
    主题 = {}
    for f in sorted(os.listdir(主题卡dir)):
        if not (f.startswith("主题卡-") and f.endswith(".md")):
            continue
        name = f[len("主题卡-"):-len(".md")]
        path = os.path.join(主题卡dir, f)
        front = _读front(path)
        标签 = {}
        for b in _bullets(_读节(path, "匹配标签")):
            m = re.match(r"([^:：]+)\s*[:：]\s*(.*)", b)
            if m:
                标签[m.group(1).strip()] = [v.strip() for v in
                                          re.split(r"[、，,]", m.group(2)) if v.strip()]
        # 配色令牌表：取 --gold 行的用途（唯一强调色语义）
        accent语义 = ""
        for ln in _读节(path, "配色令牌表").split("\n"):
            cells = [c.strip().strip("`") for c in ln.strip().strip("|").split("|")]
            if len(cells) >= 3 and cells[0] == "--gold":
                accent语义 = cells[2]
                break
        css路径s = re.findall(r"`([^`]*theme-[^`]*\.css)`", _读节(path, "css路径"))
        主题[name] = {
            "状态": front.get("状态", ""),
            "一句话": _读节(path, "一句话"),
            "匹配标签": 标签,
            "设计纪律": _bullets(_读节(path, "设计纪律")),
            "css路径": css路径s,
            "accent语义": accent语义 or "唯一强调色（只做大文本与装饰，不做正文）",
        }
    return 主题


def load_index():
    """建（或取缓存）内存索引。"""
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    页型 = _扫页型卡()
    主题 = _扫主题卡()
    族 = json.load(io.open(os.path.join(RULES_DIR, "版式族.json"),
                           encoding="utf-8"))["族"]
    选型 = json.load(io.open(os.path.join(RULES_DIR, "选型规约.json"),
                             encoding="utf-8"))
    映射 = 选型.get("映射", {})
    族查页型 = {z: list(info.get("成员", [])) for z, info in 族.items()}
    意图查 = {意: [e["tpl"] for e in es] for 意, es in 映射.items()}
    # tpl → 族（K7 保证单归属，取首个命中）
    tpl族 = {}
    for z, tpls in 族查页型.items():
        for t in tpls:
            tpl族.setdefault(t, z)
    _INDEX = {
        "页型": 页型, "主题": 主题, "族": 族,
        "族查页型": 族查页型, "意图查页型": 意图查, "tpl族": tpl族,
        "选型映射": 映射,
    }
    return _INDEX


def 知识包_页型(tpl):
    """本页 writer 需要的页型知识摘要（不贴整卡）。无此 tpl 返回 None。"""
    idx = load_index()
    p = idx["页型"].get(tpl)
    if not p:
        return None
    族 = idx["tpl族"].get(tpl) or p.get("版式族") or ""
    族信息 = idx["族"].get(族, {})
    return {
        "tpl": tpl,
        "标题": p["标题"],
        "版式族": 族,
        "适用场景": p["适用场景"][:200],
        "纪律": p["纪律"][:4],
        "族口诀": 族信息.get("选型口诀", ""),
    }


def _主题卡名(theme):
    """变体（如 dangjian-dark）回查主卡：看哪张卡的 css路径 覆盖该主题文件。"""
    idx = load_index()
    if theme in idx["主题"]:
        return theme
    目标 = "theme-%s.css" % theme
    for name, t in idx["主题"].items():
        if any(os.path.basename(p) == 目标 for p in t["css路径"]):
            return name
    return None


def 知识包_主题(theme):
    """本页 writer 需要的主题知识摘要（不贴整卡）。无此主题返回 None。"""
    idx = load_index()
    name = _主题卡名(theme)
    if not name:
        return None
    t = idx["主题"][name]
    return {
        "主题": theme,
        "主题卡": name,
        "一句话": t["一句话"][:200],
        "设计纪律": t["设计纪律"][:5],
        "配色语义": t["accent语义"],
    }


def 意图查页型(意图):
    """选型规约 映射[意图] → [tpl]（程序化，不手抄）。"""
    return list(load_index()["意图查页型"].get(意图, []))


def 自检():
    idx = load_index()
    print("索引：页型 %d / 主题 %d / 族 %d" %
          (len(idx["页型"]), len(idx["主题"]), len(idx["族"])))
    warns = []
    映射tpl = set()
    for 意, tpls in idx["意图查页型"].items():
        映射tpl.update(tpls)
    for tpl in sorted(idx["页型"]):
        if tpl not in 映射tpl:
            warns.append("页型卡 %s 未被选型规约映射覆盖" % tpl)
    for tpl in sorted(映射tpl):
        if tpl not in idx["页型"]:
            warns.append("选型规约映射引用 %s，但无对应页型卡" % tpl)
    for z, tpls in idx["族查页型"].items():
        for tpl in tpls:
            if tpl not in idx["页型"]:
                warns.append("版式族 %s 成员 %s 无对应页型卡" % (z, tpl))
    for name, t in sorted(idx["主题"].items()):
        for p in t["css路径"]:
            full = os.path.normpath(os.path.join(WORKFLOW, p))
            if not os.path.isfile(full):
                warns.append("主题卡 %s 的 css路径 %s 文件缺失" % (name, p))
    if warns:
        print("交叉校验 WARN（%d）：" % len(warns))
        for w in warns:
            print("  WARN: %s" % w)
    else:
        print("交叉校验：无 WARN")
    return 0 if True else 1


if __name__ == "__main__":
    sys.exit(自检() if "--自检" in sys.argv else (print(__doc__) or 0))
