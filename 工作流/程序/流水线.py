#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""流水线 —— 全流程编排（需求→大纲→逐页→总览→导出）。

把 _步.json 的 S0/S1/P0–P4/E1 串成可执行的流水线。
拍板点全部显式停下等人，不自动往下走；状态落盘 <项目>/流水线.json，可续跑。

用法（在 工作流/程序/ 下运行；项目由 PPT_PROJECT 环境变量指定）:
  python 流水线.py 状态                     # 当前阶段与进度
  python 流水线.py 需求                      # S0：打印 <项目>/需求.md，待用户确认
  python 流水线.py 需求确认                  # S0 拍板 → S1
  python 流水线.py 大纲                      # S1：读 大纲草案.json，校验意图闭集，打印
  python 流水线.py 大纲确认                  # S1 拍板 → 落盘 大纲.json → S2
  python 流水线.py 布局                      # S2：当前页候选→草案→预览图，待用户选
  python 流水线.py 布局选 <tpl> --理由 "…"   # S2 拍板 → S3
  python 流水线.py 做页                      # S3：读 页/待写/<页id>.json → 校验 → 生成 → 截图
  python 流水线.py 总览                      # S4：汇总全部 PNG，待用户拍板
  python 流水线.py 总览确认                  # S4 拍板 → S5
  python 流水线.py 导出                      # S5：导出程序待建，占位
"""
import argparse
import io
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, USAGE, ERR, read_json, die, project_dir, RULES_DIR

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


# ---------- 状态 ----------

def state_path(proj):
    return os.path.join(proj, "流水线.json")


def load_state(proj):
    p = state_path(proj)
    if os.path.isfile(p):
        return read_json(p)
    return {"阶段": "S0", "需求确认": False, "大纲": [], "当前页": 0,
            "待选": None, "选型": {}, "日志": []}


def save_state(proj, st):
    with io.open(state_path(proj), "w", encoding="utf-8") as f:
        import json
        json.dump(st, f, ensure_ascii=False, indent=2)


def log(st, msg):
    st["日志"].append(msg)
    print(msg)


def run_prog(args, proj):
    """跑工作流内其他程序，返回 (exitcode, 输出)。"""
    env = dict(os.environ)
    env["PPT_PROJECT"] = os.path.basename(proj)
    # PPT_PROJECT 是相对 工作流/ 的路径，取相对部分
    rel = os.path.relpath(proj, os.path.dirname(HERE))
    env["PPT_PROJECT"] = rel
    r = subprocess.run([PY] + args, cwd=HERE, env=env,
                       capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode, out.strip()


# ---------- 草案骨架（仅布局预览用占位文案，不参与校验） ----------

def first_img(proj):
    d = os.path.join(proj, "素材")
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                return f
    return "占位.png"


def placeholder(field, tpl, ctx):
    img = ctx["img"]
    if field == "id":
        return "草案-%s-%s" % (ctx["页id"], tpl)
    if field == "brow":
        return "xx"
    if field == "no":
        return "%02d / %02d" % (ctx["序号"], ctx["总页数"])
    if field == "kick":
        return "LAYOUT DRAFT"
    if field == "title":
        return "%s<span class=\"q\">（只看布局）</span>" % ctx["标题"]
    if field == "eyebrow":
        return "草案"
    if field == "en":
        return "Layout Draft"
    if field == "sub":
        return "占位副标题（只看布局，不管文案）"
    if field == "foot":
        return "占位页脚"
    if field in ("bg", "img"):
        return img
    if field == "tag":
        return "<b>草案</b>角标"
    if field == "cap":
        return "占位图注"
    if field == "concl":
        return "占位结论条"
    if field == "warn":
        return "<b>占位提示：</b>只看布局"
    if field == "ghost":
        return "草案"
    if field == "eb":
        return "DRAFT"
    if field == "rows" and tpl == "photo_props":
        return [
            {"b": "green", "k": "标签一", "n": "<em>要点一</em>", "d": "占位说明"},
            {"b": "gold", "k": "标签二", "n": "要点二", "d": "占位说明"},
            {"b": "ink", "k": "标签三", "n": "要点三", "d": "占位说明"},
        ]
    if field == "rows" and tpl == "table_compare":
        return [["占位", "占位", "占位"], ["占位", "占位", "占位"]]
    if field == "cols":
        return ["列一", "列二", "列三"]
    if field == "steps":
        return [{"t": "步骤一", "d": "占位说明"},
                {"t": "步骤二", "d": "占位说明"},
                {"t": "步骤三", "d": "占位说明"}]
    if field == "root":
        return {"t": "起点", "d": "占位说明"}
    if field == "branches":
        return [{"cond": "条件A", "result": "结果A", "d": "占位"},
                {"cond": "条件B", "result": "结果B", "d": "占位"}]
    if field == "nodes":
        return ["节点一", "节点二", "节点三"]
    if field == "edges":
        return [{"from": "节点一", "to": "节点二", "label": "转化"},
                {"from": "节点二", "to": "节点三", "label": "转化"},
                {"from": "节点三", "to": "节点一", "label": "转化"}]
    if field == "cards":
        return [{"no": "01", "zh": "卡片一", "desc": "占位说明", "img": img},
                {"no": "02", "zh": "卡片二", "desc": "占位说明", "img": img},
                {"no": "03", "zh": "卡片三", "desc": "占位说明", "img": img},
                {"no": "04", "zh": "卡片四", "desc": "占位说明", "img": img}]
    return "占位"


def build_draft(tpl, required_fields, ctx):
    d = {"id": placeholder("id", tpl, ctx), "tpl": tpl}
    for f in required_fields:
        if f in ("id", "tpl"):
            continue
        d[f] = placeholder(f, tpl, ctx)
    return d


# ---------- 图片引用检查 ----------

IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif")


def find_imgs(obj, acc):
    if isinstance(obj, str) and obj.lower().endswith(IMG_EXTS):
        acc.add(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            find_imgs(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            find_imgs(v, acc)


# ---------- 各阶段 ----------

def cmd_状态(proj, st, a):
    print("项目:", proj)
    print("阶段:", st["阶段"])
    if st["大纲"]:
        total = len(st["大纲"])
        print("大纲: %d 页，当前第 %d 页" % (total, min(st["当前页"] + 1, total)))
        for i, g in enumerate(st["大纲"]):
            mark = "✓" if i < st["当前页"] else ("→" if i == st["当前页"] else "·")
            print("  %s %s 意图=%s 标题=%s" % (mark, g["页id"], g["意图"], g["标题"]))
    if st["待选"]:
        t = st["待选"]
        print("待选布局: %s 候选=%s" % (t["页id"], t["候选"]))
    return OK


def cmd_需求(proj, st, a):
    p = os.path.join(proj, "需求.md")
    if not os.path.isfile(p):
        die("S0：找不到 %s，请先写需求" % p, code=USAGE)
    print(open(p, encoding="utf-8").read())
    print("\n---- S0 需求确认：看完没问题跑 `python 流水线.py 需求确认` ----")
    st["阶段"] = "S0"
    save_state(proj, st)
    return OK


def cmd_需求确认(proj, st, a):
    st["需求确认"] = True
    st["阶段"] = "S1"
    log(st, "S0 拍板：需求已定 → S1 定大纲")
    save_state(proj, st)
    return OK


def cmd_大纲(proj, st, a):
    if not st["需求确认"]:
        die("S1：需求未定，先跑 `需求` → `需求确认`", code=USAGE)
    p = os.path.join(proj, "大纲草案.json")
    if not os.path.isfile(p):
        die("S1：找不到 %s，请先写大纲草案" % p, code=USAGE)
    drafts = read_json(p)
    sel = read_json(os.path.join(RULES_DIR, "选型规约.json"))
    意图集 = set(sel["映射"].keys())
    for i, g in enumerate(drafts):
        for f in ("页id", "意图", "标题"):
            if f not in g:
                die("S1：大纲草案条目#%d 缺 %r" % (i, f), code=FAIL)
        if g["意图"] not in 意图集:
            die("S1：条目#%d 意图 %r 不在选型规约意图闭集内，合法为: %s"
                % (i, g["意图"], sorted(意图集)), code=FAIL)
    st["大纲草案"] = drafts
    st["阶段"] = "S1"
    save_state(proj, st)
    print("大纲草案（%d 页），意图全部在闭集内：" % len(drafts))
    for i, g in enumerate(drafts):
        候选 = sel["映射"][g["意图"]]
        print("  %02d. %s 意图=%s 标题=%s 候选=%s"
              % (i + 1, g["页id"], g["意图"], g["标题"], 候选))
    print("\n---- S1 大纲拍板：没问题跑 `python 流水线.py 大纲确认` ----")
    return OK


def cmd_大纲确认(proj, st, a):
    if "大纲草案" not in st:
        die("S1：先跑 `大纲`", code=USAGE)
    st["大纲"] = st.pop("大纲草案")
    with io.open(os.path.join(proj, "大纲.json"), "w", encoding="utf-8") as f:
        import json
        json.dump(st["大纲"], f, ensure_ascii=False, indent=2)
    st["当前页"] = 0
    st["阶段"] = "S2"
    log(st, "S1 拍板：大纲已定（%d 页）→ S2 逐页布局" % len(st["大纲"]))
    save_state(proj, st)
    return OK


def cmd_布局(proj, st, a):
    if st["阶段"] not in ("S2", "S3"):
        die("先完成 S1 大纲拍板", code=USAGE)
    if st["当前页"] >= len(st["大纲"]):
        die("大纲已走完，跑 `总览`", code=USAGE)
    g = st["大纲"][st["当前页"]]
    sel = read_json(os.path.join(RULES_DIR, "选型规约.json"))
    候选 = sel["映射"][g["意图"]]
    rules = read_json(os.path.join(RULES_DIR, "卡型规约.json"))["页面条目"]
    ctx = {"页id": g["页id"], "标题": g["标题"],
           "序号": st["当前页"] + 1, "总页数": len(st["大纲"]),
           "img": first_img(proj)}
    drafts = [build_draft(t, rules[t]["必填"], ctx) for t in 候选]
    prev_dir = os.path.join(proj, "页", "_预览")
    os.makedirs(prev_dir, exist_ok=True)
    draft_path = os.path.join(prev_dir, "草案-%s.json" % g["页id"])
    with io.open(draft_path, "w", encoding="utf-8") as f:
        import json
        json.dump(drafts, f, ensure_ascii=False, indent=2)
    code, out = run_prog([os.path.join(HERE, "页面生成.py"), "--预览", draft_path,
                          prev_dir], proj)
    if code != 0:
        die("布局预览渲染失败:\n%s" % out, code=FAIL)
    pngs = {}
    for d in drafts:
        html = os.path.join(prev_dir, d["id"] + ".html")
        code, out = run_prog([os.path.join(HERE, "截图.py"), html], proj)
        if code != 0:
            die("布局预览截图失败:\n%s" % out, code=FAIL)
        pngs[d["tpl"]] = html[:-5] + ".png"
    st["待选"] = {"页id": g["页id"], "意图": g["意图"], "候选": 候选, "预览": pngs}
    st["阶段"] = "S2"
    save_state(proj, st)
    print("页 %s（意图=%s）布局候选预览：" % (g["页id"], g["意图"]))
    for t in 候选:
        print("  [%s] %s" % (t, pngs[t]))
    print("\n---- S2 布局拍板：选定后跑 "
          "`python 流水线.py 布局选 <tpl> --理由 \"…\"` ----")
    return OK


def cmd_布局选(proj, st, a):
    t = st.get("待选")
    if not t:
        die("S2：先跑 `布局`", code=USAGE)
    if a.tpl not in t["候选"]:
        die("S2：tpl=%r 不在候选 %s 内" % (a.tpl, t["候选"]), code=USAGE)
    if not a.理由:
        die("S2：--理由 必填（留痕）", code=USAGE)
    st["选型"][t["页id"]] = {"意图": t["意图"], "候选": t["候选"],
                           "选中": a.tpl, "理由": a.理由}
    st["待选"] = None
    st["阶段"] = "S3"
    log(st, "S2 拍板：%s 选 %s（%s）→ S3 做页" % (t["页id"], a.tpl, a.理由))
    save_state(proj, st)
    return OK


def cmd_做页(proj, st, a):
    if st["阶段"] != "S3":
        die("S3：先完成 S2 布局拍板", code=USAGE)
    g = st["大纲"][st["当前页"]]
    页id = g["页id"]
    if 页id not in st["选型"]:
        die("S3：%s 未选型，先跑 `布局` → `布局选`" % 页id, code=USAGE)
    data_path = os.path.join(proj, "页", "待写", 页id + ".json")
    if not os.path.isfile(data_path):
        die("S3：找不到 %s（P2 数据由人写好放这里）" % data_path, code=USAGE)
    entry = read_json(data_path)
    entry["_选型"] = st["选型"][页id]
    # P1 门：图片引用必须在 素材/ 存在，否则停下走生图
    acc = set()
    find_imgs(entry, acc)
    missing = [f for f in acc
               if not os.path.isfile(os.path.join(proj, "素材", f))]
    if missing:
        die("S3 P1 门：素材缺失 %s，先走 M1–M3 生图登记再跑 `做页`"
            % missing, code=FAIL)
    # P2→闸→P3→P4
    pages_path = os.path.join(proj, "页", "pages.json")
    pages = read_json(pages_path) if os.path.isfile(pages_path) else []
    pages = [p for p in pages if p.get("id") != 页id]
    pages.append(entry)
    with io.open(pages_path, "w", encoding="utf-8") as f:
        import json
        json.dump(pages, f, ensure_ascii=False, indent=2)
    code, out = run_prog([os.path.join(HERE, "校验.py")], proj)
    if code != 0:
        pages = [p for p in pages if p.get("id") != 页id]
        with io.open(pages_path, "w", encoding="utf-8") as f:
            import json
            json.dump(pages, f, ensure_ascii=False, indent=2)
        die("闸 FAIL，已回滚:\n%s" % out, code=FAIL)
    code, out = run_prog([os.path.join(HERE, "页面生成.py"), 页id], proj)
    if code != 0:
        die("P3 生成失败:\n%s" % out, code=FAIL)
    html = os.path.join(proj, "页", 页id + ".html")
    code, out = run_prog([os.path.join(HERE, "截图.py"), html], proj)
    if code != 0:
        die("P4 截图失败:\n%s" % out, code=FAIL)
    st["当前页"] += 1
    if st["当前页"] >= len(st["大纲"]):
        st["阶段"] = "S4"
        log(st, "S3：%s 完成（P1–P4 全过）→ 全部 %d 页做完 → S4 总览"
            % (页id, len(st["大纲"])))
    else:
        st["阶段"] = "S2"
        log(st, "S3：%s 完成 → 下一页 %s（S2 布局）"
            % (页id, st["大纲"][st["当前页"]]["页id"]))
    save_state(proj, st)
    return OK


def cmd_总览(proj, st, a):
    if st["阶段"] != "S4":
        die("S4：逐页未做完", code=USAGE)
    import glob
    pngs = sorted(glob.glob(os.path.join(proj, "页", "*.png")))
    print("整篇 %d 页 PNG：" % len(pngs))
    for p in pngs:
        print("  " + os.path.relpath(p, proj))
    print("\n---- S4 整篇拍板：没问题跑 `python 流水线.py 总览确认` ----")
    save_state(proj, st)
    return OK


def cmd_总览确认(proj, st, a):
    st["阶段"] = "S5"
    log(st, "S4 拍板：整篇通过 → S5 导出")
    save_state(proj, st)
    return OK


def cmd_导出(proj, st, a):
    if st["阶段"] != "S5":
        die("S5：先完成 S4 整篇拍板", code=USAGE)
    print("E1 导出程序待建：从 <项目>/页/pages.json 原生构建可编辑 PPTX"
          "（不做 PNG 贴图）。整篇已过审，可以开始写导出程序。")
    st["阶段"] = "DONE"
    save_state(proj, st)
    return OK


CMDS = {
    "状态": cmd_状态, "需求": cmd_需求, "需求确认": cmd_需求确认,
    "大纲": cmd_大纲, "大纲确认": cmd_大纲确认,
    "布局": cmd_布局, "布局选": cmd_布局选, "做页": cmd_做页,
    "总览": cmd_总览, "总览确认": cmd_总览确认, "导出": cmd_导出,
}


def main():
    ap = argparse.ArgumentParser(prog="流水线.py")
    ap.add_argument("cmd", choices=sorted(CMDS.keys()))
    ap.add_argument("tpl", nargs="?", default=None)
    ap.add_argument("--理由", default=None)
    a = ap.parse_args()
    proj = project_dir()
    st = load_state(proj)
    code = CMDS[a.cmd](proj, st, a)
    sys.exit(code)


if __name__ == "__main__":
    main()
