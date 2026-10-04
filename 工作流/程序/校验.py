#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 —— 数据闸（v2 模式的「闸」）。

P2（写数据）→ P3（生成）之间必须过本闸：任一不过即 FAIL，
不许带着坏数据进生成。

用法:
  python 校验.py                    # 校验当前项目 pages.json
  python 校验.py --主题 <主题名>    # 追加校验主题卡 + 主题 CSS 令牌

校验项:
  ① 条目通用必填（id/tpl）齐
  ② tpl 在闭集内（未知页型即拒）
  ③ 该 tpl 的必填字段齐（按 卡型规约·页面条目）
  ④ photo_props rows[].b 在闭集（ink/green/gold）
  ⑤ 引用的图片文件在 <项目>/素材/ 存在
  ⑥ --主题：主题卡存在；主题令牌逐个在 CSS 存在（定案 D1）
  ⑦ _选型一致性（选型规约）：_选型必填；意图在闭集内；候选=映射[意图]；
     选中=tpl 且在候选中；理由非空
退出码: 0=PASS；1=FAIL；2=参数错；3=异常
"""
import argparse, io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, USAGE, ERR, read_json, die, project_dir, LIB_DIR, RULES_DIR, WORKFLOW


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--主题", default=None, help="主题名（校验主题卡与 CSS 令牌）")
    a = ap.parse_args()

    rules = read_json(os.path.join(RULES_DIR, "卡型规约.json"))
    entry_rules = rules["页面条目"]
    tpl_set = set(entry_rules["tpl闭集"])
    errors = []

    # ---- ①–⑤ pages.json ----
    proj = project_dir()
    pages_path = os.path.join(proj, "页", "pages.json")
    if not os.path.isfile(pages_path):
        die("找不到 %s" % pages_path, code=USAGE)
    pages = read_json(pages_path)
    seen_ids = set()
    for i, p in enumerate(pages):
        tag = "条目#%d(%s)" % (i, p.get("id", "?"))
        for f in entry_rules["通用必填"]:
            if f not in p:
                errors.append("%s 缺通用必填字段 %r" % (tag, f))
        if p.get("id") in seen_ids:
            errors.append("%s id 重复" % tag)
        seen_ids.add(p.get("id"))
        tpl = p.get("tpl")
        if tpl not in tpl_set:
            errors.append("%s tpl=%r 非法，闭集为 %s" % (tag, tpl, sorted(tpl_set)))
            continue
        tr = entry_rules[tpl]
        for f in tr["必填"]:
            if f not in p:
                errors.append("%s 缺必填字段 %r（tpl=%s）" % (tag, f, tpl))
        # 图片存在性
        for imgkey in ("bg", "img"):
            if p.get(imgkey):
                ip = os.path.join(proj, "素材", p[imgkey])
                if not os.path.isfile(ip):
                    errors.append("%s 图片不存在: 素材/%s" % (tag, p[imgkey]))
        if tpl == "toc_grid":
            for j, c in enumerate(p.get("cards", [])):
                for f in tr["cards必填"]:
                    if f not in c:
                        errors.append("%s cards[%d] 缺 %r" % (tag, j, f))
                if c.get("img") and not os.path.isfile(os.path.join(proj, "素材", c["img"])):
                    errors.append("%s cards[%d] 图片不存在: 素材/%s" % (tag, j, c["img"]))
        if tpl == "photo_props":
            b_set = set(tr["b闭集"])
            for j, r in enumerate(p.get("rows", [])):
                for f in tr["rows必填"]:
                    if f not in r:
                        errors.append("%s rows[%d] 缺 %r" % (tag, j, f))
                if r.get("b") not in b_set:
                    errors.append("%s rows[%d].b=%r 非法，闭集为 %s" % (tag, j, r.get("b"), sorted(b_set)))
        if tpl == "photo_chain":
            for j, s in enumerate(p.get("steps", [])):
                for f in tr["steps必填"]:
                    if f not in s:
                        errors.append("%s steps[%d] 缺 %r" % (tag, j, f))
        # ---- ⑦ 选型一致性（选型规约）：_选型必填；意图在闭集内；
        # 候选必须严格等于映射[意图]；选中必须等于 tpl 且在候选中；理由非空
        sel = p.get("_选型")
        if not isinstance(sel, dict):
            errors.append("%s 缺 _选型记录（P0 选型未留痕）" % tag)
        else:
            sel_rules = read_json(os.path.join(RULES_DIR, "选型规约.json"))
            intent = sel.get("意图")
            if intent not in sel_rules["意图闭集"]:
                errors.append("%s _选型.意图=%r 非法，闭集为 %s"
                              % (tag, intent, sel_rules["意图闭集"]))
            else:
                want = sel_rules["映射"][intent]
                got = sel.get("候选")
                if not isinstance(got, list) or sorted(got) != sorted(want):
                    errors.append("%s _选型.候选=%r 与选型规约映射[%s]=%r 不一致"
                                  % (tag, got, intent, want))
            if sel.get("选中") != tpl:
                errors.append("%s _选型.选中=%r 必须等于 tpl=%r"
                              % (tag, sel.get("选中"), tpl))
            elif sel.get("选中") not in (sel.get("候选") or []):
                errors.append("%s _选型.选中=%r 不在候选中" % (tag, sel.get("选中")))
            if not (isinstance(sel.get("理由"), str) and sel.get("理由").strip()):
                errors.append("%s _选型.理由为空" % tag)

    # ---- ⑥ 主题 ----
    if a.主题:
        card = os.path.join(LIB_DIR, "主题", "卡片", "主题卡-%s.md" % a.主题)
        if not os.path.isfile(card):
            errors.append("主题卡不存在: %s" % card)
        css = None
        if os.path.isfile(card):
            for line in io.open(card, encoding="utf-8"):
                if line.startswith("- css路径:"):
                    css = line.split(":", 1)[1].strip().replace("库/", "", 1)
        css_path = os.path.join(LIB_DIR, css) if css else None
        if not css_path or not os.path.isfile(css_path):
            errors.append("主题 CSS 不存在: %s" % (css_path or css))
        else:
            body = io.open(css_path, encoding="utf-8").read()
            for tok in rules["主题令牌"]["令牌"]:
                if tok not in body:
                    errors.append("主题 CSS 缺令牌 %s（定案 D1）" % tok)

    if errors:
        print("FAIL 共 %d 项:" % len(errors))
        for e in errors:
            print("  -", e)
        sys.exit(FAIL)
    print("PASS pages.json %d 条全过%s" % (len(pages), "；主题 %s 令牌齐" % a.主题 if a.主题 else ""))


if __name__ == "__main__":
    main()
