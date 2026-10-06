#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""动画.py —— PPTX 切换 + 进入动画（OOXML 注入）。

python-pptx 原生不支持动画，这里直接写 timing/transition XML。

切换（整页）：
    加切换(slide, "fade")      # 淡入
    加切换(slide, "push", 方向="left")
    可选：fade/push/wipe/split/blinds/dissolve/cover/uncover

进入动画（按形状，可同页多次调用，依次追加进同一 mainSeq）：
    加进入动画(slide, shape, "fade")       # 点击后淡入
    加进入动画组(slide, [s1, s2, s3], "fly")  # 一组形状依次点击进入
    可选：appear/fade/fly/zoom

用法（pptx导出.py）：
    pages.json 里 "transition": "fade" → 整页切换
    pages.json 里 "enter": "fade" → 内容形状（除全页背景图）依次点击进入

注意：LibreOffice 预览可能不渲染动画，PowerPoint/WPS 正常。
"""
from pptx.oxml.ns import qn

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"

切换表 = {
    "fade": "fade", "push": "push", "wipe": "wipe", "split": "split",
    "blinds": "blinds", "dissolve": "dissolve", "cover": "cover",
    "uncover": "uncover",
}

进入表 = {
    "appear": "1",    # 出现
    "fade": "10",     # 淡入
    "fly": "2",       # 飞入
    "zoom": "13",     # 缩放
}


def _parse(tag_xml):
    """解析单个 p: 元素（自动包命名空间）。"""
    from pptx.oxml import parse_xml
    wrapped = '<p:root xmlns:p="%s">%s</p:root>' % (P_NS, tag_xml)
    return parse_xml(wrapped)[0]


def 加切换(slide, 效果="fade", 速度="med", 方向=None):
    """整页切换效果。速度：slow/med/fast。"""
    if 效果 not in 切换表:
        raise ValueError("未知切换：%s" % 效果)
    sld = slide._element
    csld = sld.find(qn("p:cSld"))
    csd = csld.getparent()
    old = csd.find(qn("p:transition"))
    if old is not None:
        csd.remove(old)
    inner = ""
    if 效果 == "fade":
        inner = '<p:fade thruBlk="1"/>'
    elif 效果 in ("push", "wipe", "cover", "uncover"):
        orient = {"left": "horz", "up": "vert"}.get(方向, "horz")
        inner = '<p:%s orient="%s"/>' % (效果, orient)
    else:
        inner = '<p:%s/>' % 效果
    trans = _parse('<p:transition spd="%s">%s</p:transition>' % (速度, inner))
    csld.addnext(trans)
    return slide


def _shape_spid(shape):
    cNvPr = shape._element.find(".//" + qn("p:cNvPr"))
    return cNvPr.get("id") if cNvPr is not None else "2"


def _seq_child_list(slide):
    """取本页 mainSeq 的 childTnLst；没有则创建整棵 timing 树。"""
    sld = slide._element
    csld = sld.find(qn("p:cSld"))
    csd = csld.getparent()
    timing = csd.find(qn("p:timing"))
    if timing is None:
        timing = _parse(
            '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmrPar">'
            '<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
            '<p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
            '</p:childTnLst></p:cTn></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
        csld.addnext(timing)
    return timing.find(".//" + qn("p:seq") + "/" + qn("p:cTn") + "/" + qn("p:childTnLst"))


def _next_ids(slide, n):
    """在 timing 树内分配 n 个未使用的 id。"""
    sld = slide._element
    used = set()
    for el in sld.iter():
        i = el.get("id")
        if i is not None and i.isdigit():
            used.add(int(i))
    start = (max(used) if used else 0) + 1
    return list(range(start, start + n))


def 加进入动画(slide, shape, 效果="fade"):
    """给形状加进入动画（点击触发）。同页可调多次，依次追加进同一 mainSeq。"""
    if 效果 not in 进入表:
        raise ValueError("未知进入动画：%s" % 效果)
    spid = _shape_spid(shape)
    preset = 进入表[效果]
    child_list = _seq_child_list(slide)
    nid, nid2, nid3 = _next_ids(slide, 3)
    par = _parse(
        '<p:par><p:cTn id="%d" fill="hold">'
        '<p:stCondLst><p:cond evt="onClick" delay="indefinite">'
        '<p:tgtEl><p:spTgt spid="%s"/></p:tgtEl></p:cond></p:stCondLst>'
        '<p:childTnLst><p:par><p:cTn id="%d" fill="hold">'
        '<p:childTnLst><p:animEffect transition="in" filter="sld" presetID="%s" presetClass="entr">'
        '<p:cBhvr><p:cTn id="%d" dur="500" fill="hold">'
        '<p:tgtEl><p:spTgt spid="%s"/></p:tgtEl>'
        '</p:cTn><p:tgtEl><p:spTgt spid="%s"/></p:tgtEl></p:cBhvr>'
        '</p:animEffect></p:childTnLst></p:cTn></p:par>'
        '</p:childTnLst></p:cTn></p:par>' % (nid, spid, nid2, preset, nid3, spid, spid))
    child_list.append(par)
    return slide


def 加进入动画组(slide, shapes, 效果="fade"):
    """给一组形状按顺序加进入动画（依次点击进入）。空组直接跳过。"""
    shapes = list(shapes)
    if not shapes:
        return slide
    for sh in shapes:
        加进入动画(slide, sh, 效果)
    return slide


if __name__ == "__main__":
    from pptx import Presentation
    from pptx.util import Inches
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    for i in range(2):
        sl = prs.slides.add_slide(prs.slide_layouts[6])
        boxes = []
        for j in range(3):
            txBox = sl.shapes.add_textbox(Inches(1), Inches(1 + j * 1.2), Inches(4), Inches(1))
            txBox.text_frame.text = "测试页 %d-%d" % (i + 1, j + 1)
            boxes.append(txBox)
        加切换(sl, "fade")
        加进入动画组(sl, boxes, "fade")  # 同页多形状依次追加
    prs.save("/tmp/anim-test.pptx")
    print("自测 → /tmp/anim-test.pptx")
    # 验证
    prs2 = Presentation("/tmp/anim-test.pptx")
    xml = prs2.slides[0]._element.xml
    assert "p:transition" in xml and "p:timing" in xml and "animEffect" in xml
    assert xml.count("<p:par>") >= 4, "同页多形状应追加多个 par"
    assert 'presetID="10"' in xml, "fade 应带 presetID"
    print("XML 验证通过")
