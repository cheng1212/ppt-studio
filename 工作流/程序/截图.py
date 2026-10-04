# -*- coding: utf-8 -*-
"""批量截图：HTML → PNG(1920x1080)。
用法:
  python 截图.py <dir>              # 目录下所有 .html → 同名 .png
  python 截图.py a.html [b.html …]  # 指定文件
"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, USAGE, ERR
from playwright.sync_api import sync_playwright


def main():
    targets = []
    for a in sys.argv[1:]:
        if os.path.isdir(a):
            targets += sorted(glob.glob(os.path.join(a, "*.html")))
        else:
            targets.append(a)
    if not targets:
        print("用法: python 截图.py <dir|file.html> …", file=sys.stderr)
        sys.exit(USAGE)

    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        for html in targets:
            pg.goto("file:///" + os.path.abspath(html).replace("\\", "/"))
            pg.wait_for_timeout(2200)
            out = html[:-5] + ".png" if html.endswith(".html") else html + ".png"
            pg.screenshot(path=out)
            print("OK", os.path.basename(out))
        b.close()


if __name__ == "__main__":
    main()
