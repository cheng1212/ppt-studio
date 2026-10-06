#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回归.py —— 18 页型 × 8 主题自动化回归。

每个主题：组装 18 页 fixtures → 校验.py → 页面生成.py → pptx导出.py →
重开 PPTX 数页数。任一步非零退出或页数不对即 FAIL。

用法：
    python 工作流/程序/回归.py [--主题 dianshang] [--只 cover,chart]
    不带参数 = 全量 18×8。
"""
import io
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORKFLOW = os.path.dirname(HERE)
REPO = os.path.dirname(WORKFLOW)
TMP = "/tmp/ppt-regress"

THEMES = ["sodium", "deepsea", "dianshang", "ocean", "premium", "wanyue",
          "redox", "chemlab"]


意图表 = {"cover": "封面", "toc_grid": "目录", "section": "章节",
         "photo_props": "性质", "photo_chain": "因果", "table_compare": "对比",
         "flow_branch": "分支", "flow_cycle": "循环", "timeline": "历程",
         "cards3": "特征", "stepper": "方法", "equation_hero": "构成",
         "chart": "趋势", "kpi_hero": "关键指标", "cover_split": "封面",
         "infographic": "亮点", "compare_bars": "数据对比",
         "number_hero": "目标达成"}


def _base(i, tpl):
    return {"id": "P%02d" % i, "tpl": tpl, "brow": "回归", "no": "%02d" % i,
            "kick": "TEST", "title": "回归测试·%s" % tpl, "foot": "回归测试",
            "_选型": {"意图": 意图表.get(tpl, "特征"), "候选": [tpl],
                    "选中": tpl, "理由": "回归夹具直写"}}


def fixtures():
    F = []
    i = 0

    def add(tpl, **kw):
        p = _base(len(F) + 1, tpl)
        p.update(kw)
        F.append(p)

    add("cover", bg="bg.png", eyebrow="REGRESS 2026", en="REGRESSION TEST",
        sub="回归测试封面")
    add("toc_grid", sub="目录副标题", en="CONTENTS",
        cards=[{"no": "01", "zh": "第一章", "desc": "说明一", "img": "bg.png"},
               {"no": "02", "zh": "第二章", "desc": "说明二", "img": "bg.png"},
               {"no": "03", "zh": "第三章", "desc": "说明三", "img": "bg.png"},
               {"no": "04", "zh": "第四章", "desc": "说明四", "img": "bg.png"}])
    add("section", ghost="01", eb="PART ONE", sub=["第一部分", "说明行"])
    add("photo_props", img="bg.png", concl="结论条",
        rows=[{"b": "gold", "k": "要点", "n": "名称一", "d": "说明一"},
              {"b": "green", "k": "要点", "n": "名称二", "d": "说明二"}])
    add("photo_chain", img="bg.png", warn="提示框",
        steps=[{"t": "第一步", "d": "说明一"}, {"t": "第二步", "d": "说明二"}])
    add("table_compare", concl="结论",
        cols=["维度", "A", "B"],
        rows=[["价格", "高", "低"], ["速度", "快", "慢"]])
    add("flow_branch", concl="结论",
        root={"t": "起点", "d": "说明"},
        branches=[{"cond": "条件一", "result": "结果一", "d": "说明"},
                  {"cond": "条件二", "result": "结果二", "d": "说明"}])
    add("flow_cycle", concl="结论",
        nodes=["甲", "乙", "丙"],
        edges=[{"from": "甲", "to": "乙", "label": "推"},
               {"from": "乙", "to": "丙", "label": "动"},
               {"from": "丙", "to": "甲", "label": "环"}])
    add("timeline", concl="结论",
        nodes=[{"t": "2024", "h": "事件一", "d": "说明"},
               {"t": "2025", "h": "事件二", "d": "说明"},
               {"t": "2026", "h": "事件三", "d": "说明"}])
    add("cards3", concl="结论",
        cards=[{"b": "gold", "k": "一", "n": "卡片一", "d": "说明"},
               {"b": "green", "k": "二", "n": "卡片二", "d": "说明"},
               {"b": "ink", "k": "三", "n": "卡片三", "d": "说明"}])
    add("stepper", warn="提示",
        steps=[{"t": "第一步", "d": "说明一"}, {"t": "第二步", "d": "说明二"},
               {"t": "第三步", "d": "说明三"}])
    add("equation_hero", eq="E = mc²", concl="结论",
        cards=[{"b": "gold", "k": "项一", "n": "名称一", "d": "说明"},
               {"b": "green", "k": "项二", "n": "名称二", "d": "说明"},
               {"b": "ink", "k": "项三", "n": "名称三", "d": "说明"}])
    add("chart", img="chart.png")
    add("kpi_hero",
        kpis=[{"v": "3.6亿", "label": "GMV", "ctx": "▲32%"},
              {"v": "120万", "label": "订单", "ctx": "▲18%"},
              {"v": "98%", "label": "好评率", "ctx": "▲2pt"}])
    add("cover_split", img="bg.png", eyebrow="REGRESS", en="SPLIT COVER",
        sub="副标题")
    add("infographic",
        items=[{"icon": "奖杯", "v": "80万", "label": "销量", "d": "说明一"},
               {"icon": "用户", "v": "500万", "label": "在线", "d": "说明二"},
               {"icon": "增长", "v": "Top1", "label": "排名", "d": "说明三"}])
    add("compare_bars", a_name="本期", b_name="上期",
        rows=[{"label": "美妆", "a": 120, "b": 80},
              {"label": "服饰", "a": 90, "b": 95},
              {"label": "食品", "a": 60, "b": 40}])
    add("number_hero", v="3.6亿", label="全年 GMV", icon="增长",
        d="补充说明", ctx="▲32% 同比")
    return F


def _png(path, color):
    from PIL import Image
    Image.new("RGB", (320, 180), color).save(path)


def run(cmd, env, cwd=WORKFLOW):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env,
                       timeout=300)
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode, out[-400:]


def regress_theme(theme, only):
    proj = os.path.join(TMP, "proj-%s" % theme)
    if os.path.isdir(proj):
        shutil.rmtree(proj)
    os.makedirs(os.path.join(proj, "页"))
    素材 = os.path.join(proj, "素材")
    os.makedirs(素材)
    _png(os.path.join(素材, "bg.png"), (40, 60, 90))
    _png(os.path.join(素材, "chart.png"), (60, 90, 40))
    pages = [p for p in fixtures()
             if not only or p["tpl"] in only]
    io.open(os.path.join(proj, "页", "pages.json"), "w",
            encoding="utf-8").write(json.dumps(pages, ensure_ascii=False))
    env = dict(os.environ, PPT_PROJECT=proj,
               PPT_THEME_CSS="theme-%s.css" % theme)
    fails = []

    code, err = run([sys.executable, os.path.join(HERE, "校验.py")], env)
    if code != 0:
        fails.append("校验 FAIL: %s" % err)
    code, err = run([sys.executable, os.path.join(HERE, "页面生成.py")], env)
    if code != 0:
        fails.append("页面生成 FAIL: %s" % err)
    else:
        htmls = [f for f in os.listdir(os.path.join(proj, "页"))
                 if f.endswith(".html")]
        if len(htmls) != len(pages):
            fails.append("HTML 数量 %d != %d" % (len(htmls), len(pages)))
    out = os.path.join(proj, "导出.pptx")
    code, err = run([sys.executable, os.path.join(HERE, "pptx导出.py"),
                     "--out", out], env)
    if code != 0:
        fails.append("PPTX导出 FAIL: %s" % err)
    elif os.path.isfile(out):
        try:
            from pptx import Presentation
            n = len(Presentation(out).slides)
            if n != len(pages):
                fails.append("PPTX 页数 %d != %d" % (n, len(pages)))
        except Exception as e:
            fails.append("PPTX 重开失败: %s" % e)
    else:
        fails.append("PPTX 文件未生成")
    return fails


def main():
    ap = __import__("argparse").ArgumentParser()
    ap.add_argument("--主题", default=None)
    ap.add_argument("--只", default=None, help="只跑指定页型，如 cover,chart")
    a = ap.parse_args()
    themes = [a.主题] if a.主题 else THEMES
    only = set(a.只.split(",")) if a.只 else None
    if os.path.isdir(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    total_fail = 0
    for th in themes:
        fails = regress_theme(th, only)
        if fails:
            total_fail += 1
            print("FAIL [%s]" % th)
            for f in fails:
                print("   -", f)
        else:
            n = len(fixtures() if not only else [1])
            print("PASS [%s]" % th)
    print("回归完成：%d/%d 主题通过" % (len(themes) - total_fail, len(themes)))
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
