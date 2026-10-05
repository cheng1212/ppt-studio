#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""图片处理.py —— 配图的"调进去"而不是"贴上去"。

三件事：
1. 调色（--调色 <主题>）：按主题色温给图套一层淡淡的主题色，
   深色主题压暗暖化、浅色主题提亮冷化，让图和版式像一家人。
   强度默认 12%，可用 --强度 调（0-40）。
2. 智能裁剪（--裁剪 16:9）：按视觉显著性找焦点（边缘密度+中心权重），
   裁出目标比例，尽量不切掉主体。比无脑居中裁强。
3. 压缩（--压缩）：最长边压到 1920，JPEG q=82，给 PPTX 减肥。
   18 页 42MB 的病根就是原图直塞。

用法：
    python 程序/图片处理.py --调色 dianshang --输入 a.png --输出 b.png
    python 程序/图片处理.py --裁剪 16:9 --输入 a.png --输出 b.png
    python 程序/图片处理.py --压缩 --输入 a.png --输出 b.jpg
    三个开关可组合，一次跑完：调色→裁剪→压缩。
"""
import io
import os
import re
import sys

USAGE = 2
LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "库")


def die(msg, code=1):
    sys.stderr.write("FAIL: %s\n" % msg)
    sys.exit(code)


def _pil():
    try:
        from PIL import Image, ImageFilter, ImageStat
    except ImportError:
        die("缺 PIL：pip install pillow")
    return Image, ImageFilter, ImageStat


def 主题令牌(主题):
    css = io.open(os.path.join(LIB_DIR, "theme-%s.css" % 主题), encoding="utf-8").read()
    t = dict(re.findall(r"--([\w-]+)\s*:\s*#([0-9a-fA-F]{6})", css))
    bg = t.get("bg", "FFFFFF")
    lum = sum(int(bg[i:i+2], 16) for i in (0, 2, 4)) / 3
    return {"bg": "#" + bg, "gold": "#" + t.get("gold", "E69F00"),
            "ink": "#" + t.get("ink", "000000"), "深色": lum < 128}


def 调色(img, 主题, 强度=12):
    """主题色调统一。深色主题：叠加暖色+轻微压暗；浅色主题：叠加冷白+轻微提亮。"""
    Image, _, _ = _pil()
    tok = 主题令牌(主题)
    base = img.convert("RGB")
    w, h = base.size
    if tok["深色"]:
        # 深炭底：叠一层暖金，压一点暗部
        tint = Image.new("RGB", (w, h), tok["gold"])
        out = Image.blend(base, tint, 强度 / 100.0 * 0.6)
        # 暗部轻微下压
        lut = [max(0, int(v * 0.96)) for v in range(256)] * 3
        out = out.point(lut)
    else:
        # 浅底：叠一层纸白，提一点亮
        tint = Image.new("RGB", (w, h), "#FFFFFF")
        out = Image.blend(base, tint, 强度 / 100.0 * 0.5)
    return out


def 显著图(img):
    """简易显著性：边缘密度 + 中心高斯权重。返回灰度图，亮=显著。"""
    Image, ImageFilter, ImageStat = _pil()
    g = img.convert("L").filter(ImageFilter.FIND_EDGES)
    g = g.filter(ImageFilter.GaussianBlur(25))
    w, h = g.size
    # 中心权重
    import math
    px = g.load()
    cx, cy = w / 2, h / 2
    sigma = min(w, h) / 2.5
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            d2 = ((x - cx) ** 2 + (y - cy) ** 2) / (2 * sigma * sigma)
            wt = math.exp(-d2)
            for dy in range(4):
                for dx in range(4):
                    xx, yy = x + dx, y + dy
                    if xx < w and yy < h:
                        px[xx, yy] = int(px[xx, yy] * (0.35 + 0.65 * wt))
    return g


def 智能裁剪(img, 比例="16:9", 网格=40):
    """按显著性找最佳裁剪框。比例如 16:9。"""
    Image, _, ImageStat = _pil()
    a, b = [int(x) for x in 比例.split(":")]
    target = a / b
    w, h = img.size
    cur = w / h
    sal = 显著图(img)
    spx = sal.load()
    best, best_box = -1, None
    if cur > target:
        # 太宽：定高，滑窗找左右
        ch, cw = h, int(h * target)
        for lx in range(0, w - cw + 1, max(1, (w - cw) // 网格)):
            box = (lx, 0, lx + cw, ch)
            s = ImageStat.Stat(sal.crop(box)).mean[0]
            if s > best:
                best, best_box = s, box
    else:
        # 太高：定宽，滑窗找上下
        cw, ch = w, int(w / target)
        for ty in range(0, h - ch + 1, max(1, (h - ch) // 网格)):
            box = (0, ty, cw, ty + ch)
            s = ImageStat.Stat(sal.crop(box)).mean[0]
            if s > best:
                best, best_box = s, box
    return img.crop(best_box)


def 压缩(img, 最长边=1920, 质量=82):
    """给 PPTX 减肥：缩到最长边 1920。返回 (img, 建议格式)。"""
    w, h = img.size
    m = max(w, h)
    if m > 最长边:
        r = 最长边 / m
        img = img.resize((int(w * r), int(h * r)), resample=2)
    return img


def main():
    import argparse
    ap = argparse.ArgumentParser(prog="图片处理.py")
    ap.add_argument("--输入", required=True)
    ap.add_argument("--输出", required=True)
    ap.add_argument("--调色", default=None, help="主题名，如 dianshang")
    ap.add_argument("--强度", type=int, default=12, help="调色强度 0-40")
    ap.add_argument("--裁剪", default=None, help="目标比例，如 16:9")
    ap.add_argument("--压缩", action="store_true")
    a = ap.parse_args()
    Image, _, _ = _pil()
    if not os.path.exists(a.输入):
        die("输入不存在：%s" % a.输入, code=USAGE)
    img = Image.open(a.输入)
    log = []
    if a.调色:
        img = 调色(img, a.调色, a.强度)
        log.append("调色(%s,%d%%)" % (a.调色, a.强度))
    if a.裁剪:
        img = 智能裁剪(img, a.裁剪)
        log.append("裁剪(%s)" % a.裁剪)
    if a.压缩:
        img = 压缩(img)
        log.append("压缩(≤1920)")
    out = a.输出
    if out.lower().endswith(".jpg") or out.lower().endswith(".jpeg"):
        img.convert("RGB").save(out, quality=82, optimize=True)
    else:
        img.save(out, optimize=True)
    kb = os.path.getsize(out) // 1024
    print("OK → %s（%s，%dKB）" % (out, "、".join(log) or "无处理", kb))


if __name__ == "__main__":
    main()
