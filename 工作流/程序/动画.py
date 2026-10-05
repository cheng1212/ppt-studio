#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""动画.py —— PPTX 切换 + 进入动画（OOXML 注入）。

python-pptx 原生不支持动画，这里直接写 timing/transition XML。

切换（整页）：
    加切换(slide, "fade")      # 淡入
    加切换(slide, "push", 方向="left")
    可选：fade/push/wipe/split/blinds/dissolve/cover/uncover

进入动画（按形状）：
    加进入动画(slide, shape, "fade")       # 点击后淡入
    可选：appear/fade/fly/zoom

用法（pptx导出.py）：
    pages.json 里 "transition": "fade" → 整页切换

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


def 加进入动画(slide, shape, 效果="fade"):
    """给形状加进入动画（点击触发）。"""
    if 效果 not in 进入表:
        raise ValueError("未知进入动画：%s" % 效果)
    spid = _shape_spid(shape)
    preset = 进入表[效果]
    xml = (
        '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmrPar">'
        '<p:childTnLst><p:seq concurrent="1" nextAc="seek">'
        '<p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
        '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond evt="onClick" delay="indefinite">'
        '<p:tgtEl><p:spTgt spid="%s"/></p:tgtEl></p:cond></p:stCondLst>'
        '<p:childTnLst><p:par><p:cTn id="4" fill="hold">'
        '<p:childTnLst><p:animEffect transition="in" filter="sld">'
        '<p:cBhvr><p:cTn id="6" dur="500" fill="hold">'
        '<p:tgtEl><p:spTgt spid="%s"/></p:tgtEl>'
        '</p:cTn><p:tgtEl><p:spTgt spid="%s"/></p:tgtEl></p:cBhvr>'
        '</p:animEffect></p:childTnLst></p:cTn></p:par>'
        '</p:childTnLst></p:cTn></p:par>'
        '</p:childTnLst></p:cTn></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'
        % (spid, spid, spid))
    timing = _parse(xml)
    sld = slide._element
    csld = sld.find(qn("p:cSld"))
    csd = csld.getparent()
    old = csd.find(qn("p:timing"))
    if old is not None:
        csd.remove(old)
    csld.addnext(timing)
    return slide


if __name__ == "__main__":
    from pptx import Presentation
    from pptx.util import Inches
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    for i in range(2):
        sl = prs.slides.add_slide(prs.slide_layouts[6])
        txBox = sl.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1))
        txBox.text_frame.text = "测试页 %d" % (i + 1)
        加切换(sl, "fade")
        if i == 0:
            加进入动画(sl, txBox, "fade")
    prs.save("/tmp/anim-test.pptx")
    print("自测 → /tmp/anim-test.pptx")
    # 验证
    prs2 = Presentation("/tmp/anim-test.pptx")
    xml = prs2.slides[0]._element.xml
    assert "p:transition" in xml and "p:timing" in xml and "animEffect" in xml
    print("XML 验证通过")
