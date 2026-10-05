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
  ④ photo_props rows[].b 在闭集（ink/green/gold/ox）；
     table_compare 列数/行数范围 + 行列对齐；
     flow_branch root/branches 结构 + 2–4 分支；
     flow_cycle nodes 3–6 + edges from/to 命中 nodes
  ⑤ 引用的图片文件在 <项目>/素材/ 存在
  ⑥ --主题：主题卡存在；主题令牌逐个在 CSS 存在（定案 D1）；
     对比度闸：--ink/--bg ≥ 4.5、--gold/--bg ≥ 3.0、--ox/--bg ≥ 3.0、--ink-dark/--bg-dark ≥ 4.5（阈值见卡型规约·主题令牌）
  ⑦ _选型一致性（选型规约 v2）：_选型必填；意图在闭集内；
     有 关系 时：关系在闭集内，候选=映射[意图]按关系过滤；
     无 关系 的旧记录按 v1 grandfather（候选=映射[意图]全量）；
     选中=tpl 且在候选中；理由非空
  ⑧ 版式节奏（WARN 不阻断）：连续 3 页同一版式则提示
退出码: 0=PASS；1=FAIL；2=参数错；3=异常
"""
import argparse, io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, USAGE, ERR, read_json, die, project_dir, LIB_DIR, RULES_DIR, WORKFLOW


def _lum(hex6):
    c = [int(hex6[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    """WCAG 对比度（a/b 为 #rrggbb）。"""
    l1, l2 = sorted([_lum(a), _lum(b)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--主题", default=None, help="主题名（校验主题卡与 CSS 令牌）")
    a = ap.parse_args()

    rules = read_json(os.path.join(RULES_DIR, "卡型规约.json"))
    entry_rules = rules["页面条目"]
    tpl_set = set(entry_rules["tpl闭集"])
    errors = []
    warns = []
    tpl_seq = []  # ⑧ 节奏检查用

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
        if tpl == "cards3":
            cards = p.get("cards", [])
            if len(cards) != 3:
                errors.append("%s cards3 须为 3 项，实为 %d" % (tag, len(cards)))
            b_set = set(tr["b闭集"])
            for j, c in enumerate(cards):
                for f in tr["cards必填"]:
                    if f not in c:
                        errors.append("%s cards[%d] 缺 %r" % (tag, j, f))
                if c.get("b") not in b_set:
                    errors.append("%s cards[%d].b=%r 非法，闭集为 %s" % (tag, j, c.get("b"), sorted(b_set)))
        if tpl == "stepper":
            steps = p.get("steps", [])
            if not (2 <= len(steps) <= 4):
                errors.append("%s stepper 须为 2–4 步，实为 %d" % (tag, len(steps)))
            for j, s in enumerate(steps):
                for f in tr["steps必填"]:
                    if f not in s:
                        errors.append("%s steps[%d] 缺 %r" % (tag, j, f))
        if tpl == "equation_hero":
            cards = p.get("cards", [])
            if len(cards) != 3:
                errors.append("%s equation_hero cards 须为 3 项，实为 %d" % (tag, len(cards)))
            b_set = set(tr["b闭集"])
            for j, c in enumerate(cards):
                for f in tr["cards必填"]:
                    if f not in c:
                        errors.append("%s cards[%d] 缺 %r" % (tag, j, f))
                if c.get("b") not in b_set:
                    errors.append("%s cards[%d].b=%r 非法，闭集为 %s" % (tag, j, c.get("b"), sorted(b_set)))
        if tpl == "table_compare":
            cols = p.get("cols", [])
            if not isinstance(cols, list) or not (2 <= len(cols) <= 6):
                errors.append("%s cols 须为 2–6 列的字符串数组" % tag)
            rows = p.get("rows", [])
            if not isinstance(rows, list) or not (2 <= len(rows) <= 8):
                errors.append("%s rows 须为 2–8 行" % tag)
            for j, r in enumerate(rows if isinstance(rows, list) else []):
                if not isinstance(r, list) or len(r) != len(cols):
                    errors.append("%s rows[%d] 列数须等于 cols 长度(%d)"
                                  % (tag, j, len(cols)))
        if tpl == "flow_branch":
            root = p.get("root", {})
            for f in tr.get("root必填", []):
                if f not in root:
                    errors.append("%s root 缺 %r" % (tag, f))
            brs = p.get("branches", [])
            if not isinstance(brs, list) or not (2 <= len(brs) <= 4):
                errors.append("%s branches 须为 2–4 项" % tag)
            for j, b in enumerate(brs if isinstance(brs, list) else []):
                for f in tr.get("branches必填", []):
                    if f not in b:
                        errors.append("%s branches[%d] 缺 %r" % (tag, j, f))
        if tpl == "flow_cycle":
            nodes = p.get("nodes", [])
            if not isinstance(nodes, list) or not (3 <= len(nodes) <= 6):
                errors.append("%s nodes 须为 3–6 项" % tag)
            for j, e in enumerate(p.get("edges", [])):
                for f in tr.get("edges必填", []):
                    if f not in e:
                        errors.append("%s edges[%d] 缺 %r" % (tag, j, f))
                if e.get("from") not in nodes or e.get("to") not in nodes:
                    errors.append("%s edges[%d] from/to 须命中 nodes" % (tag, j))
        if tpl == "timeline":
            nodes = p.get("nodes", [])
            if not isinstance(nodes, list) or not (3 <= len(nodes) <= 6):
                errors.append("%s nodes 须为 3–6 项" % tag)
            for j, n in enumerate(nodes if isinstance(nodes, list) else []):
                for f in ("t", "h", "d"):
                    if f not in n:
                        errors.append("%s nodes[%d] 缺 %r" % (tag, j, f))
        if tpl == "chart":
            # 图表由 程序/图表.py 生成，本处只查数据纪律
            if not p.get("img"):
                errors.append("%s chart 缺 img（图表 PNG，程序/图表.py 生成）" % tag)
            ins = p.get("insight")
            if ins is not None:
                if not isinstance(ins, dict) or not ins.get("take"):
                    errors.append("%s insight 须为 {take, bullets}，take 必填" % tag)
                elif len(ins.get("bullets", [])) > 3:
                    errors.append("%s insight.bullets ≤3 条" % tag)
        if tpl == "kpi_hero":
            kpis = p.get("kpis", [])
            if not isinstance(kpis, list) or not (1 <= len(kpis) <= 4):
                errors.append("%s kpis 须为 1–4 项，实为 %s" % (tag, len(kpis) if isinstance(kpis, list) else "?"))
            else:
                for j, k in enumerate(kpis):
                    for f in ("v", "label"):
                        if f not in k:
                            errors.append("%s kpis[%d] 缺 %r" % (tag, j, f))
                    if not k.get("ctx"):
                        warns.append("%s kpis[%d] 无 ctx 上下文（数字无比较=噪音）" % (tag, j))
                heroes = [k for k in kpis if k.get("hero")]
                if len(kpis) > 1 and len(heroes) != 1:
                    warns.append("%s 多卡 KPI 应标出 1 个主角，实为 %d 个" % (tag, len(heroes)))
        # ---- ⑨ 断言标题（专家报告 Topic 3.8）：正文页标题必须是结论句 ----
        if tpl not in ("cover", "section", "toc_grid"):
            title = re.sub(r"<[^>]+>", "", p.get("title", ""))
            中文数 = sum(1 for c in title if "\u4e00" <= c <= "\u9fff")
            if 中文数 > 30:
                errors.append("%s 标题中文 %d 字>30（断言标题≤30字/≤2行）" % (tag, 中文数))
            # 标签式标题黑名单：纯名词、无动词无判断
            标签词 = ("介绍", "概况", "概述", "总结", "分析", "情况", "说明")
            if any(title.strip().endswith(w) for w in 标签词) and len(title.strip()) <= 10:
                warns.append("%s 标题疑似标签式（%r），请改断言句：结论+原因" % (tag, title.strip()))
        # ---- ⑩ CJK 标点（专家报告 Topic 3.7）：中文段落禁半角标点 ----
        for f in ("title", "concl", "foot"):
            txt = re.sub(r"<[^>]+>", "", p.get(f, "") or "")
            if re.search(r"[\u4e00-\u9fff][,.!?;:()]", txt) or re.search(r"[,.!?;:()][\u4e00-\u9fff]", txt):
                warns.append("%s.%s 含半角标点紧贴中文（请用全角，。！？：；（））" % (tag, f))
                break
        # ---- ⑦ 选型一致性（选型规约 v2）：_选型必填；意图在闭集内；
        # 有 关系 时：关系须在闭集内，候选=映射[意图]按关系过滤；
        # 无 关系 的旧记录按 v1 规则 grandfather（候选=映射[意图]全量）
        # 选中必须等于 tpl 且在候选中；理由非空
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
                rel = sel.get("关系")
                mapping = sel_rules["映射"][intent]
                is_v2 = (isinstance(mapping, list) and mapping
                         and isinstance(mapping[0], dict))
                if rel:
                    if rel not in sel_rules.get("关系闭集", []):
                        errors.append("%s _选型.关系=%r 非法，闭集为 %s"
                                      % (tag, rel, sel_rules["关系闭集"]))
                    elif not is_v2:
                        errors.append("%s 选型规约映射[%s] 非 v2 格式" % (tag, intent))
                    else:
                        want = [e["tpl"] for e in mapping if rel in e.get("关系", [])]
                        got = sel.get("候选")
                        if not isinstance(got, list):
                            errors.append("%s _选型.候选须为数组" % tag)
                        elif set(got) - set(want):
                            errors.append("%s _选型.候选=%r 含非法候选 %r（映射[%s]按关系=%r 过滤=%r）"
                                          % (tag, got, sorted(set(got) - set(want)), intent, rel, want))
                        elif set(got) != set(want):
                            # 子集容忍：记录时映射还没这么多候选（库升级导致），WARN 不阻断
                            warns.append("%s _选型.候选=%r 是当前映射的子集（库升级新增候选），建议新项目重选"
                                         % (tag, got))
                else:
                    want = ([e["tpl"] for e in mapping] if is_v2 else list(mapping))
                    got = sel.get("候选")
                    if not isinstance(got, list):
                        errors.append("%s _选型.候选须为数组" % tag)
                    elif set(got) - set(want):
                        errors.append("%s _选型.候选=%r 含非法候选 %r（映射[%s]=%r）"
                                      % (tag, got, sorted(set(got) - set(want)), intent, want))
                    elif set(got) != set(want):
                        warns.append("%s _选型.候选=%r 是当前映射的子集（库升级新增候选），建议新项目重选"
                                     % (tag, got))
            if sel.get("选中") != tpl:
                errors.append("%s _选型.选中=%r 必须等于 tpl=%r"
                              % (tag, sel.get("选中"), tpl))
            elif sel.get("选中") not in (sel.get("候选") or []):
                errors.append("%s _选型.选中=%r 不在候选中" % (tag, sel.get("选中")))
            if not (isinstance(sel.get("理由"), str) and sel.get("理由").strip()):
                errors.append("%s _选型.理由为空" % tag)
        tpl_seq.append(tpl)

    # ---- ⑧ 版式节奏（专家报告 Topic 5.5）：连续 2 页同一版式 → WARN（不阻断，仅提示）
    for i in range(len(tpl_seq) - 1):
        if tpl_seq[i] == tpl_seq[i+1]:
            warns.append("第 %d–%d 页连续使用 %s：专家规则要求连续不超过 2 页同一版式，建议调整节奏"
                         % (i + 1, i + 2, tpl_seq[i]))

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
            # 对比度闸：按卡型规约·主题令牌.对比度 阈值机检 WCAG 对比度
            vars_ = dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})", body))
            for pair, need in rules["主题令牌"].get("对比度", {}).items():
                fg_tok, bg_tok = ("--" + x for x in pair.split("/"))
                if fg_tok in vars_ and bg_tok in vars_:
                    r = contrast(vars_[fg_tok], vars_[bg_tok])
                    print("  对比度 %s = %.2f（要求 ≥ %.1f）" % (pair, r, need))
                    if r < need:
                        errors.append(
                            "主题对比度不达标: %s=%s 在 %s=%s 上为 %.2f，"
                            "要求 ≥ %.1f" % (fg_tok, vars_[fg_tok],
                                           bg_tok, vars_[bg_tok], r, need))
            # 字号阶梯闸：按设计规约·字号.机检（2026-10-05 网页调研 encoding）
            fs = {}
            for m in re.finditer(r"(--fs-[\w-]+)\s*:\s*([0-9]+)px", body):
                fs[m.group(1)] = int(m.group(2))
            if fs:
                distinct = sorted(set(fs.values()))
                print("  字号档: %s" % " / ".join(
                    "%s=%dpx" % kv for kv in sorted(fs.items())))
                if len(distinct) > 5:
                    errors.append("字号档数 %d 超过 5（含 display 装饰档），见设计规约·字号" % len(distinct))
                t, b = fs.get("--fs-page-title"), fs.get("--fs-body")
                if t and b:
                    ratio = t / b
                    if not 1.8 <= ratio <= 2.5:
                        errors.append(
                            "字号 title/body = %.2f，不在 [1.8, 2.5]（设计规约·字号.比例关系）" % ratio)
                if b and b < 32:
                    errors.append(
                        "正文字号 %dpx < 32px（投影 24pt 下限，设计规约·字号.机检）" % b)

    # 模板硬编码字号闸：页面生成.py 里不许出现 font-size:<数字>px，
    # 一律走 var(--fs-*)（2026-10-05 收敛 12 模板 41 处硬编码；相对单位 em 允许）
    pg = os.path.join(WORKFLOW, "程序", "页面生成.py")
    if os.path.isfile(pg):
        bad = []
        for i, line in enumerate(io.open(pg, encoding="utf-8"), 1):
            for m in re.finditer(r"font-size:\s*([\d.]+)px", line):
                if "var(--fs" not in line:
                    bad.append("行%d %spx" % (i, m.group(1)))
        if bad:
            errors.append("页面生成.py 仍有硬编码字号（须用 var(--fs-*)）: %s" %
                          "、".join(bad[:8]) + (" 等%d处" % (len(bad) - 8) if len(bad) > 8 else ""))
    # pptx导出.py：para() 的字号参数不许写裸数字，一律 _FS.get()（ghost 400 装饰字除外）
    px = os.path.join(WORKFLOW, "程序", "pptx导出.py")
    if os.path.isfile(px):
        bad = ["行%d" % (i + 1) for i, line in
               enumerate(io.open(px, encoding="utf-8"), 1)
               if re.search(r"para\([^)]*,\s*\d+\s*,", line)
               and "ghost, 400" not in line]
        if bad:
            errors.append("pptx导出.py 仍有硬编码 para 字号（须用 _FS.get()）: %s" % "、".join(bad[:8]))
    # svg.py：SVG 文字字号只许用 4 档值（22/34/45/64/118）
    sg = os.path.join(WORKFLOW, "程序", "svg.py")
    if os.path.isfile(sg):
        bad = []
        for i, line in enumerate(io.open(sg, encoding="utf-8"), 1):
            for m in re.finditer(r"font_size=(\d+)", line):
                if int(m.group(1)) not in (22, 34, 45, 64, 118):
                    bad.append("行%d font_size=%s" % (i, m.group(1)))
        if bad:
            errors.append("svg.py 的 SVG 文字字号不在 4 档内: %s" % "、".join(bad[:8]))
    # 主题同步闸：主题 CSS 必须 = 骨架规则 + :root 值，漂移就 FAIL（跑 程序/主题同步.py 修）
    import subprocess as _sp
    _r = _sp.run([sys.executable, os.path.join(WORKFLOW, "程序", "主题同步.py"), "--check"],
                 capture_output=True, text=True)
    if _r.returncode != 0:
        errors.append("主题与骨架不同步（%s），跑 `python 程序/主题同步.py` 修" %
                      _r.stdout.strip().split("\n")[-1][:80])

    if errors:
        print("FAIL 共 %d 项:" % len(errors))
        for e in errors:
            print("  -", e)
        sys.exit(FAIL)
    for w in warns:
        print("WARN:", w)
    print("PASS pages.json %d 条全过%s" % (len(pages), "；主题 %s 令牌齐" % a.主题 if a.主题 else ""))


if __name__ == "__main__":
    main()
