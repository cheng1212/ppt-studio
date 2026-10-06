#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回归 —— 自动化回归测试（18 页型 × 8 主题）。

为每个页型按 规约/卡型规约.json 自动构造最小合法数据（含 _选型 留痕），
每个主题 × 全页型跑：校验.py（闸 PASS）→ 页面生成.py（HTML 产出）
→ 截图.py（PNG 产出）；另对每个主题跑令牌闸（校验.py --主题）。

数据生成器只读规约：改 schema 即改回归覆盖，不改代码。

用法:
  python 回归.py                    # 全量：8 主题 × 18 页型
  python 回归.py --主题 sodium       # 只跑一个主题
  python 回归.py --页型 cover        # 只跑一个页型
退出码: 0 全过；1 有失败；2 参数错
"""
import argparse
import io
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, USAGE, read_json, LIB_DIR, RULES_DIR, WORKFLOW

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
REG_DIR = os.path.join(WORKFLOW, "_回归", "回归测试")

# ---------- 最小合法数据生成（规约驱动） ----------

_TEXT = {
    "brow": "REGRESSION", "no": "01 / 18", "kick": "回归测试",
    "title": "回归测试断言标题", "eyebrow": "REGRESSION", "en": "Regression",
    "sub": "回归测试副标题", "foot": "回归测试页脚", "corner": "R",
    "cap": "回归测试图注", "tag": "回归角标", "ghost": "R", "eb": "R1",
    "warn": "回归测试提示", "concl": "<b>回归</b>测试结论条",
    "label": "回归标签", "k": "回归", "n": "<em>回归</em>要点",
    "d": "回归测试说明文字", "t": "回归阶段", "h": "回归里程碑",
    "v": "99%", "ctx": "回归上下文", "cond": "回归条件",
    "result": "回归结果", "eq": "回归方程式", "a_name": "回归A组",
    "b_name": "回归B组", "icon": "星", "take": "回归测试得出确定性结论",
    "zh": "回归卡片", "desc": "回归卡片说明",
}

# 嵌套数组元素个数（落在各页型校验区间内）
_COUNTS = {("toc_grid", "cards"): 4, ("flow_branch", "branches"): 2}


def _值(f, tpl=None, parent=None):
    if f in ("a", "b") and not (f == "b" and tpl in
                                ("photo_props", "cards3", "equation_hero")):
        return 100 if f == "a" else 60
    if f == "img":
        return "占位.png"
    if f == "b":
        return "ink"
    if f == "hero":
        return True
    if f == "contain":
        return False
    return _TEXT.get(f, "回归")


def _数组项(tpl, parent, tr, idx):
    item = {}
    for f in tr.get(parent + "必填", []):
        if f in ("from", "to"):
            continue  # flow_cycle edges 特殊处理
        item[f] = _值(f, tpl, parent)
    for f in tr.get(parent + "选填", []):
        if f in ("icon", "d", "ctx", "contain"):
            item[f] = _值(f, tpl, parent)
        elif f == "hero" and idx == 0:
            item[f] = True  # kpi_hero：只标 1 个主角
    return item


def _条目(tpl, tr, 选型):
    p = {"id": "R-%s" % tpl, "tpl": tpl}
    for f in tr.get("必填", []):
        if f in ("id", "tpl"):
            continue
        if f == "bg" or f == "img":
            p[f] = "占位.png"
        elif f == "root":
            p[f] = {"t": "回归起点", "d": "回归测试说明文字"}
        elif f == "insight":
            p[f] = {"take": "回归测试得出确定性结论",
                    "bullets": ["回归要点一", "回归要点二"]}
        elif f in ("items", "rows", "cards", "steps", "nodes", "edges",
                   "branches", "cols", "kpis"):
            n = _COUNTS.get((tpl, f), 3 if f in ("cards", "steps", "nodes") else 2)
            if f == "cols":
                p[f] = ["回归列一", "回归列二"]
            elif f == "rows" and tpl == "table_compare":
                p[f] = [["回归甲", "回归乙"], ["回归丙", "回归丁"]]
            elif f == "nodes" and tpl == "flow_cycle":
                p[f] = ["N1", "N2", "N3"][:n]
            else:
                p[f] = [_数组项(tpl, f, tr, i) for i in range(n)]
            if f == "edges":
                nodes = p.get("nodes", ["N1", "N2", "N3"])
                p[f] = [{"from": nodes[i % len(nodes)],
                         "to": nodes[(i + 1) % len(nodes)],
                         "label": "回归"} for i in range(3)]
        else:
            p[f] = _值(f)
    p["_选型"] = 选型
    return p


def _选型_for(tpl, sel):
    for intent, mapping in sel["映射"].items():
        tpls = [e["tpl"] if isinstance(e, dict) else e for e in mapping]
        if tpl in tpls:
            return {"意图": intent, "候选": list(tpls),
                    "选中": tpl, "理由": "回归测试自动构造"}
    return None


def _准备项目(tpls, rules, sel):
    """建临时项目：页/pages.json + 素材/占位.png。"""
    for d in ("页", "素材"):
        os.makedirs(os.path.join(REG_DIR, d), exist_ok=True)
    png = os.path.join(REG_DIR, "素材", "占位.png")
    if not os.path.isfile(png):
        from PIL import Image
        Image.new("RGB", (32, 32), (200, 200, 200)).save(png)
    entry_rules = rules["页面条目"]
    pages = []
    for tpl in tpls:
        sel_one = _选型_for(tpl, sel)
        if sel_one is None:
            return None, "页型 %r 在选型规约意图映射中找不到" % tpl
        pages.append(_条目(tpl, entry_rules[tpl], sel_one))
    with io.open(os.path.join(REG_DIR, "页", "pages.json"),
                 "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    return pages, None


def _run(args, env):
    r = subprocess.run([PY] + args, cwd=HERE, env=env,
                       capture_output=True, text=True)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def _主题列表():
    names = []
    for f in sorted(os.listdir(LIB_DIR)):
        if f.startswith("theme-") and f.endswith(".css"):
            names.append(f[len("theme-"):-len(".css")])
    return names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--主题", default=None)
    ap.add_argument("--页型", default=None)
    a = ap.parse_args()

    rules = read_json(os.path.join(RULES_DIR, "卡型规约.json"))
    sel = read_json(os.path.join(RULES_DIR, "选型规约.json"))
    tpls = list(rules["页面条目"]["tpl闭集"])
    if a.页型:
        if a.页型 not in tpls:
            print("ERR: 未知页型 %r" % a.页型, file=sys.stderr)
            return USAGE
        tpls = [a.页型]
    themes = _主题列表()
    if a.主题:
        if a.主题 not in themes:
            print("ERR: 未知主题 %r" % a.主题, file=sys.stderr)
            return USAGE
        themes = [a.主题]

    pages, err = _准备项目(tpls, rules, sel)
    if err:
        print("ERR:", err, file=sys.stderr)
        return FAIL

    fails, total = [], 0
    for th in themes:
        env = dict(os.environ)
        env["PPT_PROJECT"] = os.path.relpath(REG_DIR, WORKFLOW)
        env["PPT_THEME_CSS"] = "theme-%s.css" % th

        # 1) 闸
        total += 1
        code, out = _run([os.path.join(HERE, "校验.py")], env)
        if code != 0:
            fails.append("[%s] 校验 FAIL:\n%s" % (th, out[-600:]))
            continue
        # 2) 生成
        total += 1
        code, out = _run([os.path.join(HERE, "页面生成.py")], env)
        bad = []
        for p in pages:
            hp = os.path.join(REG_DIR, "页", p["id"] + ".html")
            if not os.path.isfile(hp) or os.path.getsize(hp) == 0:
                bad.append(p["id"])
            elif "<html" not in io.open(hp, encoding="utf-8").read(2000):
                bad.append(p["id"] + "(无html)")
        if code != 0 or bad:
            fails.append("[%s] 生成 FAIL(rc=%d 缺:%s):\n%s"
                         % (th, code, bad, out[-600:]))
            continue
        # 3) 主题令牌闸
        total += 1
        code, out = _run([os.path.join(HERE, "校验.py", ), "--主题", th], env)
        if code != 0:
            fails.append("[%s] 主题闸 FAIL:\n%s" % (th, out[-600:]))
            continue
        print("PASS 主题 %s：%d 页型校验+生成全过" % (th, len(pages)))

        # 4) 截图（HTML → PNG 冒烟）
        total += 1
        页dir = os.path.join(REG_DIR, "页")
        code, out = _run([os.path.join(HERE, "截图.py"), 页dir], env)
        pngs = [f for f in os.listdir(页dir) if f.endswith(".png")]
        if code != 0 or len(pngs) < len(pages):
            fails.append("[%s] 截图 FAIL(rc=%d png=%d/%d):\n%s"
                         % (th, code, len(pngs), len(pages), out[-600:]))
            continue

    print("---- 回归：%d 项检查，%d 失败 ----" % (total, len(fails)))
    for f in fails:
        print(f)
    return FAIL if fails else OK


if __name__ == "__main__":
    sys.exit(main())
