# -*- coding: utf-8 -*-
"""img.py — 素材图片处理固定工具（Pillow 打底）。

定位：PPT 制作中反复出现的图片处理需求，固定成确定性函数，
不许自由发挥。所有几何语义与页面模板的 CSS 行为对齐：
  cover   = 等比缩放填满目标尺寸后中心裁剪（对应 .photo 的 cover）
  contain = 等比完整显示，底色填充（对应 .photo.contain）

函数：
  info(src) -> dict                      # 尺寸/格式/字节数
  resize(src, dst, w, h, mode, bg)       # 缩放
  crop_ratio(src, dst, ratio)            # 按比例中心裁剪，如 "16:9" / "1:1"
  convert(src, dst, fmt, quality)        # 格式转换

CLI：
  python img.py info 素材/x.png
  python img.py resize in.png out.png 1920 1080 --mode cover
  python img.py resize in.png out.png 800 600 --mode contain --bg "#252C2B"
  python img.py crop-ratio in.png out.png 16:9
  python img.py convert in.png out.jpg --quality 90
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image


def info(src):
    """返回图片基本信息。"""
    with Image.open(src) as im:
        return {
            "file": src,
            "w": im.width,
            "h": im.height,
            "fmt": im.format,
            "mode": im.mode,
            "bytes": os.path.getsize(src),
        }


def _parse_bg(s):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def resize(src, dst, w, h, mode="cover", bg="#F5F3ED"):
    """缩放到 w×h。

    mode=cover   等比放大填满后中心裁剪（可能裁掉边缘，不丢主体需先构图）
    mode=contain  等比完整显示，bg 底色填充
    mode=stretch  直接拉伸到 w×h（会变形，仅兼容用）
    """
    if mode not in ("cover", "contain", "stretch"):
        raise ValueError("mode 须为 cover/contain/stretch")
    w, h = int(w), int(h)
    with Image.open(src) as im:
        im = im.convert("RGBA")
        if mode == "stretch":
            out = im.resize((w, h), Image.LANCZOS)
        else:
            sw, sh = im.width, im.height
            if mode == "cover":
                scale = max(w / sw, h / sh)
            else:  # contain
                scale = min(w / sw, h / sh)
            nw, nh = round(sw * scale), round(sh * scale)
            im = im.resize((nw, nh), Image.LANCZOS)
            if mode == "cover":
                x, y = (nw - w) // 2, (nh - h) // 2
                out = im.crop((x, y, x + w, y + h))
            else:
                out = Image.new("RGBA", (w, h), _parse_bg(bg) + (255,))
                out.alpha_composite(im, ((w - nw) // 2, (h - nh) // 2))
        out = out.convert("RGB")
        out.save(dst)
    return {"dst": dst, "w": w, "h": h, "mode": mode}


def crop_ratio(src, dst, ratio="16:9"):
    """按比例中心裁剪，不缩放（只裁剪）。ratio 如 "16:9" / "1:1" / "4:3"。"""
    rw, rh = (float(x) for x in ratio.split(":"))
    target = rw / rh
    with Image.open(src) as im:
        sw, sh = im.width, im.height
        cur = sw / sh
        if cur > target:  # 太宽，裁左右
            nw, nh = round(sh * target), sh
        else:             # 太高，裁上下
            nw, nh = sw, round(sw / target)
        x, y = (sw - nw) // 2, (sh - nh) // 2
        out = im.crop((x, y, x + nw, y + nh))
        out.save(dst)
    return {"dst": dst, "w": nw, "h": nh, "ratio": ratio}


def convert(src, dst, fmt=None, quality=92):
    """格式转换。fmt 不传则按 dst 后缀推断；转 JPEG 时自动白底合成（丢 alpha）。"""
    if not fmt:
        ext = os.path.splitext(dst)[1].lower()
        fmt = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG",
               "webp": "WEBP", "bmp": "BMP"}.get(ext.lstrip("."), "PNG")
    fmt = fmt.upper()
    with Image.open(src) as im:
        if fmt in ("JPEG", "JPG"):
            if im.mode in ("RGBA", "LA"):
                bg = Image.new("RGB", im.size, (255, 255, 255))
                bg.paste(im, mask=im.split()[-1])
                im = bg
            else:
                im = im.convert("RGB")
            im.save(dst, "JPEG", quality=int(quality))
        else:
            im.save(dst, fmt)
    return {"dst": dst, "fmt": fmt}


def main():
    ap = argparse.ArgumentParser(prog="img.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("info")
    p.add_argument("src")

    p = sub.add_parser("resize")
    p.add_argument("src")
    p.add_argument("dst")
    p.add_argument("w")
    p.add_argument("h")
    p.add_argument("--mode", default="cover")
    p.add_argument("--bg", default="#F5F3ED")

    p = sub.add_parser("crop-ratio")
    p.add_argument("src")
    p.add_argument("dst")
    p.add_argument("ratio", default="16:9")

    p = sub.add_parser("convert")
    p.add_argument("src")
    p.add_argument("dst")
    p.add_argument("--fmt", default=None,
                   help="不传则按 dst 后缀推断（.jpg→JPEG/.png→PNG/.webp→WEBP）")
    p.add_argument("--quality", default=92)

    a = ap.parse_args()
    if a.cmd == "info":
        print(json.dumps(info(a.src), ensure_ascii=False))
    elif a.cmd == "resize":
        print(json.dumps(resize(a.src, a.dst, a.w, a.h, a.mode, a.bg),
                         ensure_ascii=False))
    elif a.cmd == "crop-ratio":
        print(json.dumps(crop_ratio(a.src, a.dst, a.ratio), ensure_ascii=False))
    elif a.cmd == "convert":
        print(json.dumps(convert(a.src, a.dst, a.fmt, a.quality),
                         ensure_ascii=False))


if __name__ == "__main__":
    main()
