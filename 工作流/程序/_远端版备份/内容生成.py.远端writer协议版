#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""内容生成.py —— 内容生成层（一句话 → 成品的数据引擎）。

定位：执行层。LLM/智能体是 Writer，经窄接口接入；程序负责：
  briefs 生成（约束）→ writer 调度（预算）→ 收集校验 →
  配图规划 → 图表生成 → 洞察 → 组装 pages.json → 校验闸。

Writer 协议（--writer-cmd）：
  stdin: brief JSON；stdout: 页数据 JSON（只含字段，不含 id/tpl/_选型）；
  stderr: 日志；exit 0 成功，非 0 失败（按预算重试）。

无 writer-cmd 时，一句话 流程在 briefs 后停下并打印填写指引
（由智能体按 briefs 填写 filled/ 后再跑 收集）。

预算与降级：--writer-retries（默认 2）、--writer-timeout（默认 120s）；
超预算的页记入 <项目>/内容生成_debt.json（待手填），其余页继续（pass-with-debt）。

配图：生图后端不可用时生成中文标注占位图（PIL，明确标"待生图"），
规划记入 <项目>/配图规划.json；传 --生图 且后端可用时走真实生成并登记素材卡。

子命令：
  briefs  --大纲 outline.json --输出 briefs_dir/
  收集    --briefs briefs_dir/ --filled filled_dir/ --项目 <项目> [--主题 <名>] [--生图]
  一句话  --输入 "..." --项目 <项目> [--主题 <名>] [--writer-cmd "..."]
          [--writer-retries N] [--writer-timeout S] [--生图]
"""
import argparse
import io
import json
import os
import re
import socket
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, USAGE, read_json, die, LIB_DIR, RULES_DIR, WORKFLOW
from 大纲模板 import 意图映射

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

_配图字段 = {
    "cover": [("bg", "封面背景")],
    "cover_split": [("img", "封面配图")],
    "photo_props": [("img", "左图")],
    "photo_chain": [("img", "左图")],
    "toc_grid": [("cards[].img", "目录卡片图")],
    "chart": [("img", "图表")],
}

_固定规则 = {
    "标题": "断言句（结论+原因）；≤30中文字；禁标签式结尾（介绍/概况/概述/总结/分析/情况/说明）",
    "标点": "中文段落用全角标点，。！？：；（）",
    "配色": "只写纯文本数据，不许写色值/样式/HTML 结构",
    "行内标签": "可用 <b>/<em>/<span class=\"q\">/<sub>/<sup>，其余 <>& 原样写（程序转义）",
}


def _解析字段表(path):
    fields = {}
    txt = io.open(path, encoding="utf-8").read()
    m = re.search(r"^##\s+[^\n]*数据字段表[^\n]*\n(.*?)(?=^##\s+|\Z)", txt, re.M | re.S)
    body = m.group(1) if m else ""
    for line in body.split("\n"):
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in s.strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = cells[0]
        if name in ("字段", "") or set(name) <= set("-"):
            continue
        req = cells[1] == "是"
        note = cells[2] if len(cells) > 2 else ""
        for sub in name.split("/"):
            sub = sub.strip()
            if sub:
                fields[sub] = {"必填": req, "说明": note}
    return fields


def _节(path, 关键词):
    txt = io.open(path, encoding="utf-8").read()
    secs = re.findall(r"^##\s+(.+?)\s*$", txt, re.M)
    name = next((s for s in secs if 关键词 in s), None)
    if not name:
        return ""
    m = re.search(r"^##\s+" + re.escape(name) + r"[^\n]*\n(.*?)(?=^##\s+|\Z)",
                  txt, re.M | re.S)
    return m.group(1).strip() if m else ""


def _选型计算(意图, tpl建议, sel_rules):
    意图2 = 意图映射.get(意图, 意图)
    mapping = sel_rules["映射"].get(意图2)
    if mapping is None:
        return None, "意图 %r 不在选型规约映射内" % 意图2
    tpls_all = [e["tpl"] if isinstance(e, dict) else e for e in mapping]
    选中 = next((t for t in tpl建议 if t in tpls_all), tpls_all[0])
    return ({"意图": 意图2, "候选": tpls_all, "选中": 选中,
             "理由": "内容生成自动选型（大纲模板 tpl 建议首选在候选内者）"},
            选中)


def _配图需求(tpl, 意图, 题材):
    needs = []
    for f, 用途 in _配图字段.get(tpl, []):
        场景 = _场景建议(题材, 意图)
        needs.append({"字段": f, "用途": 用途, "场景建议": 场景})
    return needs


def _场景建议(题材, 意图):
    m = {"化学": "实验室", "教育": "教室", "电商": "仓库",
         "商业": "办公室", "文化": "城市"}
    for k, v in m.items():
        if k in (题材 or ""):
            return v
    return "办公室"


def 生成briefs(大纲, rules, sel_rules):
    briefs = []
    for i, 页 in enumerate(大纲["页"]):
        选型, 选中 = _选型计算(页["意图"], 页.get("tpl建议", []), sel_rules)
        if 选型 is None:
            return None, 选中
        tpl = 选中
        card = os.path.join(LIB_DIR, "页型", "卡片", "页型卡-%s.md" % tpl)
        字段 = _解析字段表(card)
        tr = rules["页面条目"].get(tpl, {})
        机器字段 = {f for f, _ in _配图字段.get(tpl, [])}
        字段_out, 白名单 = {}, set()
        for name, info in 字段.items():
            if name in 机器字段:
                continue
            字段_out[name] = {"必填": info["必填"], "说明": info["说明"]}
            白名单.add(name)
        闭集 = {}
        if "b闭集" in tr:
            闭集["b"] = tr["b闭集"]
        闭集["bg纹理"] = ["dots", "grid", "diagonal", "mesh", "glow"]
        闭集["mask"] = ["circle", "rounded", "blob", "arch"]
        briefs.append({
            "页id": 页.get("页", "P%d" % (i + 1)),
            "意图": 页["意图"],
            "tpl": tpl,
            "_选型": 选型,
            "文案提示": 页.get("文案提示", ""),
            "字段": 字段_out,
            "字段白名单": sorted(白名单),
            "字段_由机器提供_writer不填": sorted(机器字段),
            "闭集": 闭集,
            "纪律": _节(card, "纪律").split("\n"),
            "规则": _固定规则,
            "图表": ({"说明": "本页是图表页。writer 在 filled 数据中提供 chart_spec，程序调 图表.py 生成图片",
                      "chart_spec": {"类型": "bar/line/pie/funnel/waterfall/scatter/bullet/radar",
                                    "数据": "bar/pie/funnel/waterfall/radar 用 {名: 值}；line 用 {x:[...], 系列:{名:[...]}}；bullet 用 {实际, 目标, 区间:[...]}；scatter 用 {x:[...], y:[...]}",
                                    "标题": "图表标题（可空）",
                                    "强调": "强调的数据名（可空）",
                                    "单位": "单位（可空）"}}
                     if tpl == "chart" else None),
            "配图": _配图需求(tpl, 页["意图"], (大纲.get("意图") or {}).get("题材")),
        })
    return briefs, None


def cmd_briefs(a):
    rules = read_json(os.path.join(RULES_DIR, "卡型规约.json"))
    sel_rules = read_json(os.path.join(RULES_DIR, "选型规约.json"))
    大纲 = read_json(a.大纲)
    briefs, err = 生成briefs(大纲, rules, sel_rules)
    if err:
        die(err, code=FAIL)
    os.makedirs(a.输出, exist_ok=True)
    for b in briefs:
        with io.open(os.path.join(a.输出, b["页id"] + ".json"),
                     "w", encoding="utf-8") as f:
            json.dump(b, f, ensure_ascii=False, indent=2)
    print("briefs → %s（%d 页）" % (a.输出, len(briefs)))
    return OK


def _run_writer(cmd, brief, timeout, retries):
    last_err = "未运行"
    for attempt in range(retries + 1):
        try:
            r = subprocess.run(
                cmd, shell=True, cwd=HERE, input=json.dumps(brief, ensure_ascii=False),
                capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            last_err = "writer 超时（%ss，第 %d 次）" % (timeout, attempt + 1)
            continue
        if r.returncode != 0:
            last_err = "writer exit=%d（第 %d 次）: %s" % (
                r.returncode, attempt + 1, (r.stderr or "")[-300:])
            continue
        try:
            data = json.loads(r.stdout)
        except Exception as e:
            last_err = "writer 输出非 JSON（第 %d 次）: %s" % (attempt + 1, e)
            continue
        if not isinstance(data, dict):
            last_err = "writer 输出非对象（第 %d 次）" % (attempt + 1)
            continue
        return data, None
    return None, last_err


def _生图后端():
    try:
        cfgp = os.path.join(os.path.expanduser("~"), ".zcode", "v2", "config.json")
        if os.path.isfile(cfgp):
            cfg = json.load(io.open(cfgp, encoding="utf-8"))

            def _find(o):
                if isinstance(o, dict):
                    if o.get("name") == "千问":
                        return True
                    return any(_find(v) for v in o.values())
                return False

            if _find(cfg):
                return "qwen", "千问 API（~/.zcode/v2/config.json）"
    except Exception:
        pass
    try:
        s = socket.create_connection(("127.0.0.1", 9222), timeout=2)
        s.close()
        return "gemini", "本机 Gemini 网页 CDP :9222"
    except OSError:
        pass
    return None, "无可用生图后端（缺 ~/.zcode/v2/config.json 千问 key，且 :9222 无 CDP）"


def _占位图(path, prompt, W=1280, H=720):
    from PIL import Image, ImageDraw, ImageFont
    import textwrap
    im = Image.new("RGB", (W, H), (232, 232, 228))
    d = ImageDraw.Draw(im)
    font = None
    for fp in ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",):
        try:
            font = ImageFont.truetype(fp, 44)
            break
        except OSError:
            pass
    if font is None:
        font = ImageFont.load_default()
    d.text((W // 2, H // 2 - 60), "待生图", font=font, fill=(120, 120, 115),
           anchor="mm")
    small = font.font_variant(size=26) if hasattr(font, "font_variant") else font
    for j, line in enumerate(textwrap.wrap(prompt, 24)[:3]):
        d.text((W // 2, H // 2 + 20 + j * 40), line, font=small,
               fill=(140, 140, 135), anchor="mm")
    d.rectangle([0, 0, W - 1, H - 1], outline=(180, 180, 175), width=4)
    im.save(path)


def _配图提示(用途, 场景建议, 题材):
    sys.path.insert(0, os.path.join(HERE, "生图"))
    import prompt规约 as pr
    base = "%s, %s" % (用途, 场景建议)
    prompt = pr.complete(base, has_people=False, scene=None)
    ok, missing = pr.check(prompt)
    return prompt, ok, missing


_图表函数 = {
    "bar": lambda g, d, t, e, u, o: g.bar(主题=t[0], 数据=d, 标题=t[1], 输出=o, 强调=e, 单位=u),
    "pie": lambda g, d, t, e, u, o: g.pie(主题=t[0], 数据=d, 标题=t[1], 输出=o, 单位=u),
    "funnel": lambda g, d, t, e, u, o: g.funnel(主题=t[0], 数据=d, 标题=t[1], 输出=o, 单位=u),
    "waterfall": lambda g, d, t, e, u, o: g.waterfall(主题=t[0], 数据=d, 标题=t[1], 输出=o, 单位=u),
    "radar": lambda g, d, t, e, u, o: g.radar(主题=t[0], 数据=d, 标题=t[1], 输出=o, 单位=u),
    "line": lambda g, d, t, e, u, o: g.line(主题=t[0], x=d["x"], 系列=d["系列"], 标题=t[1], 输出=o, 单位=u),
    "bullet": lambda g, d, t, e, u, o: g.bullet(主题=t[0], 实际=d["实际"], 目标=d["目标"], 区间=d["区间"], 标题=t[1], 输出=o, 单位=u),
    "scatter": lambda g, d, t, e, u, o: g.scatter(主题=t[0], x=d["x"], y=d["y"], 标题=t[1], 输出=o, 单位=u),
}


def _gen_chart(主题, spec, outpath):
    sys.path.insert(0, HERE)
    import 图表 as g
    类型 = spec.get("类型")
    fn = _图表函数.get(类型)
    if fn is None:
        return "未知图表类型 %r" % 类型
    try:
        fn(g, spec.get("数据"), (主题, spec.get("标题", "")),
           spec.get("强调"), spec.get("单位", ""), outpath)
    except Exception as e:
        return "图表生成异常: %s" % e
    if not os.path.isfile(outpath):
        return "图表未产出文件"
    return None


def _gen_insight(类型, 数据):
    if 类型 == "line" and isinstance(数据, dict) and "系列" in 数据:
        数据 = 数据["系列"]
    类型2 = 类型 if 类型 in ("bar", "line", "pie", "funnel", "waterfall") else "bar"
    r = subprocess.run([PY, os.path.join(HERE, "洞察.py"), 类型2,
                        json.dumps(数据, ensure_ascii=False)],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None, "洞察.py 失败: %s" % (r.stderr or "")[-200:]
    try:
        out = json.loads(r.stdout)
    except Exception as e:
        return None, "洞察输出非 JSON: %s" % e
    标题s = out.get("标题候选") or []
    if not 标题s:
        return None, "洞察无标题候选"
    return {"take": 标题s[0], "bullets": (out.get("支撑") or [])[:3]}, None


def _set_img(entry, 字段, fname):
    if 字段 == "cards[].img":
        for c in entry.get("cards", []):
            c.setdefault("img", fname)
    else:
        entry[字段] = fname


def cmd_收集(a):
    rules = read_json(os.path.join(RULES_DIR, "卡型规约.json"))
    proj = os.path.normpath(os.path.join(WORKFLOW, a.项目))
    页dir = os.path.join(proj, "页")
    素材dir = os.path.join(proj, "素材")
    os.makedirs(页dir, exist_ok=True)
    os.makedirs(素材dir, exist_ok=True)
    主题 = a.主题 or "sodium"

    briefs, filled = {}, {}
    for f in os.listdir(a.briefs):
        if f.endswith(".json"):
            b = read_json(os.path.join(a.briefs, f))
            briefs[b["页id"]] = b
    for f in os.listdir(a.filled):
        if f.endswith(".json"):
            d = read_json(os.path.join(a.filled, f))
            filled[os.path.splitext(f)[0]] = d

    errors, debt, pages = [], {"待手填": [], "说明": []}, []
    配图规划 = {}
    素材卡 = []

    for 页id in sorted(briefs):
        b = briefs[页id]
        d = filled.get(页id)
        if d is None:
            debt["待手填"].append(页id)
            debt["说明"].append("%s：filled 缺失" % 页id)
            continue
        白名单 = set(b["字段白名单"]) | {"chart_spec"}
        unknown = [k for k in d if k not in 白名单]
        if unknown:
            errors.append("%s 含 brief 未定义字段 %s（writer 越界）" % (页id, unknown))
            continue
        entry = {"id": 页id, "tpl": b["tpl"]}
        entry.update({k: v for k, v in d.items() if k != "chart_spec"})
        entry["_选型"] = b["_选型"]

        for 需 in b.get("配图") or []:
            字段, 用途 = 需["字段"], 需["用途"]
            if b["tpl"] == "chart":
                continue
            fname = "%s-%s.png" % (页id, "bg" if 字段 == "bg" else "img")
            fpath = os.path.join(素材dir, fname)
            prompt, ok, missing = _配图提示(用途, 需["场景建议"], None)
            real = None
            if a.生图:
                后端, _ = _生图后端()
                prog = {"qwen": "千问生图.py", "gemini": "gemini生图.py"}.get(后端)
                if prog:
                    r = subprocess.run(
                        [PY, os.path.join(HERE, "生图", prog),
                         "--prompt", prompt, "--out", fpath],
                        capture_output=True, text=True, timeout=300)
                    real = 后端 if r.returncode == 0 else None
            if real is None:
                _占位图(fpath, prompt)
            _set_img(entry, 字段, fname)
            配图规划[页id] = {"字段": 字段, "文件": fname, "用途": 用途,
                             "prompt": prompt,
                             "prompt_规约检查": "ok" if ok else missing,
                             "状态": "已生图(%s)" % real if real else "待生图（占位图）"}
            素材卡.append({"文件": fname, "prompt": prompt,
                           "模型": real or "占位图（待生图）",
                           "尺寸": "1280x720", "用于": "%s.%s" % (页id, 字段),
                           "来源轨": "内容生成"})

        if b["tpl"] == "chart":
            spec = d.get("chart_spec")
            if not isinstance(spec, dict):
                errors.append("%s chart 页缺 chart_spec" % 页id)
                continue
            fname = "%s-chart.png" % 页id
            fpath = os.path.join(素材dir, fname)
            err = _gen_chart(主题, spec, fpath)
            if err:
                errors.append("%s %s" % (页id, err))
                continue
            entry["img"] = fname
            素材卡.append({"文件": fname, "prompt": "图表：%s" % spec.get("标题", ""),
                           "模型": "程序/图表.py", "尺寸": "程序默认",
                           "用于": "%s.img" % 页id, "来源轨": "内容生成"})
            ins, ierr = _gen_insight(spec.get("类型", "bar"), spec.get("数据"))
            if ierr:
                debt["说明"].append("%s 洞察失败（%s），insight 留空" % (页id, ierr))
            else:
                entry["insight"] = ins

        pages.append(entry)

    with io.open(os.path.join(页dir, "pages.json"), "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    with io.open(os.path.join(proj, "配图规划.json"), "w", encoding="utf-8") as f:
        json.dump(配图规划, f, ensure_ascii=False, indent=2)
    if 素材卡:
        with io.open(os.path.join(素材dir, "素材卡.jsonl"), "a", encoding="utf-8") as f:
            for c in 素材卡:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
    with io.open(os.path.join(proj, "内容生成_debt.json"), "w", encoding="utf-8") as f:
        json.dump(debt, f, ensure_ascii=False, indent=2)

    if errors:
        print("收集 FAIL（%d 页未组装）" % len(errors))
        for e in errors:
            print("  -", e)
    env = dict(os.environ)
    env["PPT_PROJECT"] = a.项目
    r = subprocess.run([PY, os.path.join(HERE, "校验.py")], cwd=HERE, env=env,
                       capture_output=True, text=True)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    print(out[-1500:] if len(out) > 1500 else out)
    if r.returncode != 0 or errors:
        print("闸未过：修 filled/ 或 writer 输出后重跑 收集")
        return FAIL
    print("收集 OK：%d 页 → 校验 PASS；debt: %s" % (len(pages), debt))
    return OK


def cmd_一句话(a):
    proj = os.path.normpath(os.path.join(WORKFLOW, a.项目))
    os.makedirs(proj, exist_ok=True)
    r = subprocess.run([PY, os.path.join(HERE, "一句话.py"), "--输入", a.输入],
                       capture_output=True, text=True)
    if r.returncode != 0:
        die("一句话.py 失败: %s" % (r.stderr or "")[-300:], code=FAIL)
    try:
        大纲 = json.loads(r.stdout)
    except Exception as e:
        die("一句话.py 输出非 JSON: %s" % e, code=FAIL)
    with io.open(os.path.join(proj, "大纲.json"), "w", encoding="utf-8") as f:
        json.dump(大纲, f, ensure_ascii=False, indent=2)
    print("大纲：%d 页，模板=%s" % (大纲["页数"], 大纲["大纲模板"]), file=sys.stderr)
    主题 = a.主题 or (大纲["主题推荐"][0]["主题"] if 大纲["主题推荐"] else "sodium")
    print("主题：%s" % 主题, file=sys.stderr)

    briefs_dir = os.path.join(proj, "briefs")
    filled_dir = os.path.join(proj, "filled")
    os.makedirs(filled_dir, exist_ok=True)
    rc = cmd_briefs(argparse.Namespace(大纲=os.path.join(proj, "大纲.json"),
                                      输出=briefs_dir))
    if rc != OK:
        return rc

    if not a.writer_cmd:
        print("")
        print("writer 未配置：briefs 已生成在 %s" % briefs_dir)
        print("请按每份 brief 的【字段】填写同名 JSON 到 %s（只填字段，不填 id/tpl/_选型），" % filled_dir)
        print("然后跑：python 程序/内容生成.py 收集 --briefs %s --filled %s --项目 %s --主题 %s"
              % (briefs_dir, filled_dir, a.项目, 主题))
        print("（在 Muse 对话里，我就是 writer：把 briefs 发我，我填好交回。）")
        return OK
    debt = []
    for fn in sorted(os.listdir(briefs_dir)):
        if not fn.endswith(".json"):
            continue
        brief = read_json(os.path.join(briefs_dir, fn))
        data, err = _run_writer(a.writer_cmd, brief, a.writer_timeout,
                                a.writer_retries)
        outp = os.path.join(filled_dir, fn)
        if err:
            debt.append({"页id": brief["页id"], "原因": err})
            print("writer 失败 %s：%s" % (brief["页id"], err), file=sys.stderr)
            continue
        with io.open(outp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    if debt:
        with io.open(os.path.join(proj, "内容生成_debt.json"), "w", encoding="utf-8") as f:
            json.dump({"writer失败": debt}, f, ensure_ascii=False, indent=2)

    rc = cmd_收集(argparse.Namespace(briefs=briefs_dir, filled=filled_dir,
                                    项目=a.项目, 主题=主题, 生图=a.生图))
    if rc != OK:
        return rc

    env = dict(os.environ)
    env["PPT_PROJECT"] = a.项目
    env["PPT_THEME_CSS"] = "theme-%s.css" % 主题
    for prog, pargs in (("页面生成.py", []), ("截图.py", [os.path.join(proj, "页")])):
        r = subprocess.run([PY, os.path.join(HERE, prog)] + pargs, cwd=HERE,
                           env=env, capture_output=True, text=True)
        if r.returncode != 0:
            die("%s 失败: %s" % (prog, ((r.stdout or "") + (r.stderr or ""))[-500:]),
                code=FAIL)
    print("")
    print("一句话 → 成品预览完成：%s/页/*.png（%d 页）" % (proj, 大纲["页数"]))
    print("下一步：看 PNG 总览，拍板后跑 `python 程序/流水线.py 导出`"
          "（需先走 S4 总览确认）或直接 `PPT_PROJECT=%s python 程序/pptx导出.py`" % a.项目)
    if debt:
        print("debt：%d 页 writer 超预算，见 %s/内容生成_debt.json（待手填）"
              % (len(debt), proj))
    return OK


CMDS = {"briefs": cmd_briefs, "收集": cmd_收集, "一句话": cmd_一句话}


def main():
    ap = argparse.ArgumentParser(prog="内容生成.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("briefs")
    b.add_argument("--大纲", required=True)
    b.add_argument("--输出", required=True)
    c = sub.add_parser("收集")
    c.add_argument("--briefs", required=True)
    c.add_argument("--filled", required=True)
    c.add_argument("--项目", required=True)
    c.add_argument("--主题", default=None)
    c.add_argument("--生图", action="store_true")
    o = sub.add_parser("一句话")
    o.add_argument("--输入", required=True)
    o.add_argument("--项目", required=True)
    o.add_argument("--主题", default=None)
    o.add_argument("--writer-cmd", default=None)
    o.add_argument("--writer-retries", type=int, default=2)
    o.add_argument("--writer-timeout", type=int, default=120)
    o.add_argument("--生图", action="store_true")
    a = ap.parse_args()
    sys.exit(CMDS[a.cmd](a))


if __name__ == "__main__":
    main()
