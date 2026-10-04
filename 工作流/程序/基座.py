#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""基座 —— 程序层共享执行层（ppt-studio 工作流）

「共同父类」的实质：每个程序都要干的那部分——stdout 编码、退出码、
路径定位、JSON 读写。一处定义，全部程序共用。

分层（import 只许向下，不许逆向）：
  基座（本文件，程序/）
    ↑            ↑
  校验/问卷等     页面生成 / 截图 / 生图
"""
import io, json, os, sys

# ---- stdout 编码（import 即生效，幂等） ----
if hasattr(sys.stdout, "buffer") and not getattr(sys, "_ppt_stdout_wrapped", False):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys._ppt_stdout_wrapped = True

# ---- 路径 ----
HERE = os.path.dirname(os.path.abspath(__file__))   # 程序/
WORKFLOW = os.path.dirname(HERE)                    # 工作流/
REPO = os.path.dirname(WORKFLOW)                    # 仓库根
LIB_DIR = os.path.join(WORKFLOW, "库")
RULES_DIR = os.path.join(WORKFLOW, "规约")

# ---- 退出码 ----
OK, FAIL, USAGE, ERR = 0, 1, 2, 3


def read_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def die(msg, code=ERR):
    print("ERR:", msg, file=sys.stderr)
    sys.exit(code)


def project_dir():
    """当前项目目录（环境变量 PPT_PROJECT，相对 工作流/）"""
    return os.path.normpath(os.path.join(
        WORKFLOW, os.environ.get("PPT_PROJECT", "示例-化学钠/化学-钠及其化合物")))


def theme_css_path():
    """主题 CSS 路径（环境变量 PPT_THEME_CSS，相对 库/；默认 theme-sodium.css）"""
    return os.path.normpath(os.path.join(
        LIB_DIR, os.environ.get("PPT_THEME_CSS", "theme-sodium.css")))
