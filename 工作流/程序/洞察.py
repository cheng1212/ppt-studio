#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""洞察.py —— 从图表数据里算出结论，起草断言式标题。

定位：Knaflic 的核心技能是"看一眼数据说出故事"。图表工厂只负责画，
讲故事还是人的活。这个程序把"算"的那部分自动化：极值、占比、差距、
趋势、拐点、最大流失环节，输出 2-3 个断言标题候选 + 支撑 bullets。

用法：
    python 程序/洞察.py bar '{"华东":128,"华南":96,"华北":84}'
    python 程序/洞察.py line '{"今年":[20,35,48,72,110]}'
    python 程序/洞察.py pie '{"服饰":42,"美妆":28,"3C":18}'
    python 程序/洞察.py funnel '{"曝光":1000,"点击":320,"加购":128,"支付":52}'
    python 程序/洞察.py waterfall '{"新增":45,"流失":-20,"复购":30}'

输出 JSON：{"标题候选": [...], "支撑": [...], "数据事实": {...}}
注意：候选是草稿，人要拍板。断言标题≤30字由校验.py复核。
"""
import io
import json
import sys

USAGE = 2


def die(msg, code=1):
    sys.stderr.write("FAIL: %s\n" % msg)
    sys.exit(code)


def _pct(a, b):
    return round(a / b * 100) if b else 0


def 分析_bar(数据):
    """分类对比：找老大、断层、集中度。"""
    if not 数据:
        die("bar：数据为空")
    items = sorted(数据.items(), key=lambda kv: kv[1], reverse=True)
    total = sum(数据.values())
    top, tv = items[0]
    share = _pct(tv, total)
    事实 = {"第一": top, "第一值": tv, "第一占比%": share, "类别数": len(items)}
    标题, 支撑 = [], []
    if len(items) >= 2:
        second, sv = items[1]
        gap = _pct(tv - sv, sv) if sv else 0
        事实["第二"] = second
        事实["领先第二%"] = gap
        if gap >= 30:
            标题.append("%s断层领先，超第二名%d%%" % (top, gap))
            支撑.append("%s %s，%s %s，差距拉开%d%%" % (top, tv, second, sv, gap))
        elif share >= 40:
            标题.append("%s一家独大，占%s%%" % (top, share))
        else:
            标题.append("%s领先，%s紧随其后" % (top, second))
            支撑.append("前两名合计占%s%%" % _pct(tv + sv, total))
    else:
        标题.append("%s：%s" % (top, tv))
    支撑.append("共%d类，总计%s" % (len(items), total))
    return {"标题候选": 标题[:3], "支撑": 支撑, "数据事实": 事实}


def 分析_line(系列):
    """趋势：方向、加速、反超。系列：dict{名: [y...]}，只看第一系列。"""
    if not 系列:
        die("line：系列为空")
    name = next(iter(系列))
    ys = list(系列[name])
    if len(ys) < 3:
        die("line：至少3个点才谈趋势")
    事实 = {"系列": name, "起点": ys[0], "终点": ys[-1]}
    增 = (ys[-1] - ys[0]) / ys[0] * 100 if ys[0] else 0
    事实["整体涨幅%"] = round(增)
    # 后半段 vs 前半段斜率
    mid = len(ys) // 2
    前 = (ys[mid] - ys[0]) / max(mid, 1)
    后 = (ys[-1] - ys[mid]) / max(len(ys) - 1 - mid, 1)
    事实["加速"] = 后 > 前 * 1.2
    标题 = []
    if 增 >= 50 and 后 > 前 * 1.2:
        标题.append("%s加速上扬，涨幅超%d%%" % (name, round(增)))
    elif 增 >= 20:
        标题.append("%s持续走高，累计涨%d%%" % (name, round(增)))
    elif 增 <= -20:
        标题.append("%s明显回落，下滑%d%%" % (name, round(-增)))
    else:
        标题.append("%s整体平稳，波动不大" % name)
    # 拐点
    拐点 = [i for i in range(1, len(ys) - 1)
          if (ys[i] - ys[i - 1]) * (ys[i + 1] - ys[i]) < 0]
    支撑 = ["起点%s → 终点%s" % (ys[0], ys[-1])]
    if 拐点:
        支撑.append("第%d个点出现转向" % (拐点[0] + 1))
        事实["拐点位置"] = 拐点[0] + 1
    return {"标题候选": 标题[:3], "支撑": 支撑, "数据事实": 事实}


def 分析_pie(数据):
    """构成：集中度、头部效应。"""
    if not 数据:
        die("pie：数据为空")
    items = sorted(数据.items(), key=lambda kv: kv[1], reverse=True)
    total = sum(数据.values())
    top, tv = items[0]
    share = _pct(tv, total)
    top2 = _pct(tv + items[1][1], total) if len(items) > 1 else share
    事实 = {"第一": top, "第一占比%": share, "前二合计%": top2, "类别数": len(items)}
    标题 = []
    if share >= 50:
        标题.append("%s占半壁江山，达%d%%" % (top, share))
    elif top2 >= 70:
        标题.append("头部两强合计占%d%%，集中度高" % top2)
    else:
        标题.append("%s份额最高（%d%%），格局分散" % (top, share))
    支撑 = ["%s %d%%" % (k, _pct(v, total)) for k, v in items[:3]]
    return {"标题候选": 标题[:3], "支撑": 支撑, "数据事实": 事实}


def 分析_funnel(数据):
    """漏斗：找流失最大的环节。"""
    labels = list(数据.keys())
    vals = list(数据.values())
    if len(labels) < 2:
        die("funnel：至少2个阶段")
    流失 = []
    for i in range(1, len(labels)):
        if vals[i - 1]:
            流失.append((labels[i - 1] + "→" + labels[i],
                       round((1 - vals[i] / vals[i - 1]) * 100)))
    最惨 = max(流失, key=lambda x: x[1])
    总转化 = _pct(vals[-1], vals[0])
    事实 = {"阶段数": len(labels), "总转化率%": 总转化,
          "最大流失环节": 最惨[0], "最大流失%": 最惨[1]}
    标题 = ["%s环节流失最严重，达%d%%" % (最惨[0], 最惨[1])]
    if 总转化 < 10:
        标题.append("全链路仅转化%d%%，漏斗漏得厉害" % 总转化)
    支撑 = ["%s：流失%d%%" % (k, v) for k, v in 流失]
    支撑.append("首→末总转化 %d%%" % 总转化)
    return {"标题候选": 标题[:3], "支撑": 支撑, "数据事实": 事实}


def 分析_waterfall(数据):
    """瀑布：找最大正/负贡献。数据 dict{标签:增减}（不含总计）或 list。"""
    items = list(数据.items()) if isinstance(数据, dict) else list(数据)
    # 去掉名为总计/期末的最后一项
    if items and items[-1][0] in ("总计", "期末", "total"):
        items = items[:-1]
    if not items:
        die("waterfall：数据为空")
    正 = max(items, key=lambda kv: kv[1])
    负 = min(items, key=lambda kv: kv[1])
    净 = sum(v for _, v in items)
    事实 = {"最大正贡献": 正[0], "最大正值": 正[1],
          "最大负贡献": 负[0], "最大负值": 负[1], "净增减": 净}
    标题 = []
    if 正[1] > 0:
        标题.append("%s是增长主引擎，贡献+%s" % (正[0], 正[1]))
    if 负[1] < 0:
        标题.append("%s拖后腿，-%s要止血" % (负[0], abs(负[1])))
    支撑 = ["%s：%+d" % (k, v) for k, v in items]
    return {"标题候选": 标题[:3], "支撑": 支撑, "数据事实": 事实}


分析器 = {
    "bar": 分析_bar, "line": 分析_line, "pie": 分析_pie,
    "funnel": 分析_funnel, "waterfall": 分析_waterfall,
}


def main():
    if len(sys.argv) < 3:
        die("用法: python 程序/洞察.py <bar|line|pie|funnel|waterfall> '<JSON数据>'", code=USAGE)
    kind, raw = sys.argv[1], sys.argv[2]
    if kind not in 分析器:
        die("未知类型 %r，可选：%s" % (kind, sorted(分析器)), code=USAGE)
    try:
        数据 = json.loads(raw)
    except ValueError as e:
        die("JSON 解析失败：%s" % e, code=USAGE)
    out = 分析器[kind](数据)
    io.open("/dev/stdout", "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
