#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主题同步 —— 主题 CSS = 骨架规则 + 本主题 :root token 值。

骨架改了规则后跑本程序，所有主题一键同步，不再漂移。
用法: python 程序/主题同步.py [--主题 <名>] [--check]
  --check 只检查是否同步，不写文件（给校验器用）
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 基座 import OK, FAIL, LIB_DIR, die

骨架 = os.path.join(LIB_DIR, "主题", "_骨架.css")
TOKEN_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;]+);")


def 读tokens(css_path):
    txt = io.open(css_path, encoding="utf-8").read()
    m = re.search(r":root\s*\{(.*?)\}", txt, re.S)
    return dict(TOKEN_RE.findall(m.group(1))) if m else {}


def 同步一(name):
    path = os.path.join(LIB_DIR, "theme-%s.css" % name)
    skel = io.open(骨架, encoding="utf-8").read()
    old_tokens = 读tokens(path)
    # 骨架 :root 里每个 token，用主题的旧值替换（主题缺的 token 用骨架默认）
    def sub(m):
        tok = m.group(1)
        val = old_tokens.get(tok, m.group(2)).strip()
        return "%s:%s;" % (tok, val)
    新root = re.sub(r"(--[\w-]+)\s*:\s*([^;]+);",
                   lambda m: m.group(0),  # 先占位
                   re.search(r":root\s*\{(.*?)\}", skel, re.S).group(0))
    # 对骨架 :root 逐 token 替换
    def rep_root(skel_txt):
        def one(mm):
            tok = mm.group(1)
            val = old_tokens.get(tok)
            if val is None:
                return mm.group(0)
            return "%s:%s;" % (tok, val.strip())
        return re.sub(r"(--[\w-]+)\s*:\s*([^;]+);", one,
                      skel_txt, count=0)
    # 只替换 :root 块内的
    m = re.search(r"(:root\s*\{)(.*?)(\})", skel, re.S)
    new_css = skel[:m.start()] + m.group(1) + rep_root(m.group(2)) + m.group(3) + skel[m.end():]
    # 头部注释加同步标记
    new_css = new_css.replace(" * 主题骨架 —— 全套主题 CSS 的唯一结构源",
                              " * 主题骨架 —— 全套主题 CSS 的唯一结构源\n * （本文件由 程序/主题同步.py 从骨架生成，只改 :root 值）", 1)
    cur = io.open(path, encoding="utf-8").read()
    return new_css, cur != new_css


def main():
    import argparse
    ap = argparse.ArgumentParser(prog="主题同步.py")
    ap.add_argument("--主题", default=None, help="只同步一个（默认全部）")
    ap.add_argument("--check", action="store_true", help="只检查，不写")
    a = ap.parse_args()
    names = [a.主题] if a.主题 else [
        f[len("theme-"):-len(".css")]
        for f in sorted(os.listdir(LIB_DIR))
        if f.startswith("theme-") and f.endswith(".css")]
    脏 = []
    for n in names:
        new_css, changed = 同步一(n)
        if changed:
            脏.append(n)
            if not a.check:
                io.open(os.path.join(LIB_DIR, "theme-%s.css" % n),
                        "w", encoding="utf-8").write(new_css)
                print("已同步 theme-%s.css" % n)
    if a.check:
        if 脏:
            print("以下主题与骨架不同步: %s" % "、".join(脏))
            sys.exit(FAIL)
        print("全主题与骨架同步 OK")
    sys.exit(OK)


if __name__ == "__main__":
    main()
