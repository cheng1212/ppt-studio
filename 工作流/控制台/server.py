#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""控制台 server.py —— PPT Studio 图形化控制台后端。

stdlib only，无第三方依赖。

API:
    POST /api/一句话        {"输入": "..."} → {意图, 主题推荐, 大纲}
    GET  /api/主题样张?名=dianshang → PNG（浅/深拼一张）
    POST /api/渲染页        {"主题": "dianshang", "pages": [...]} → {ok, 页数}
    GET  /api/缩略图?i=0    → 第 i 页 PNG
    POST /api/导出          {"主题": ..., "pages": [...], "transition": "fade"} → PPTX 文件下载
    GET  /api/图标列表      → [图标名...]
    GET  /api/页型列表      → {tpl: 说明}

启动：
    python 工作流/控制台/server.py --port 8901
    浏览器打开 http://localhost:8901/
"""
import base64
import io
import json
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
WORKFLOW = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(WORKFLOW, "程序"))

REPO_TMP = "/tmp/ppt-console"
os.makedirs(REPO_TMP, exist_ok=True)


def _json(handler, obj, code=200):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _read_json(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        qs = urllib.parse.parse_qs(parsed.query)

        # 静态文件
        if path == "/" or path == "/index.html":
            return self._static("index.html", "text/html; charset=utf-8")
        if path.startswith("/static/"):
            name = path[len("/static/"):]
            ctype = {"html": "text/html", "js": "text/javascript",
                     "css": "text/css", "png": "image/png"}.get(
                         name.rsplit(".", 1)[-1], "application/octet-stream")
            return self._static(name, ctype)

        if path == "/api/图标列表":
            from 图标 import 列表
            return _json(self, 列表())
        if path == "/api/页型列表":
            d = json.load(io.open(os.path.join(WORKFLOW, "库", "页型", "清单.json"),
                                  encoding="utf-8"))
            return _json(self, d.get("卡", []))
        if path == "/api/主题样张":
            return self._theme_preview(qs.get("名", ["dianshang"])[0])
        if path == "/api/缩略图":
            return self._thumb(int(qs.get("i", ["0"])[0]))
        if path == "/api/下载":
            return self._download()
        self.send_error(404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        if path == "/api/一句话":
            return self._one_sentence()
        if path == "/api/渲染页":
            return self._render()
        if path == "/api/导出":
            return self._export()
        self.send_error(404)

    # ---------- handlers ----------
    def _static(self, name, ctype):
        p = os.path.join(HERE, "static", name)
        if not os.path.isfile(p):
            self.send_error(404)
            return
        data = open(p, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _one_sentence(self):
        from 一句话 import 生成大纲
        body = self._read_json()
        try:
            out = 生成大纲(body.get("输入", ""))
        except Exception as e:
            return _json(self, {"error": str(e)}, 500)
        # 主题推荐加样张 URL
        for t in out["主题推荐"]:
            t["样张"] = "/api/主题样张?名=%s" % t["主题"]
        return _json(self, out)

    def _theme_preview(self, name):
        # 用主题样张.py 生成浅/深/封面三张（输出到库/主题/_样张），拼浅+封面返回
        import subprocess
        sample = os.path.join(WORKFLOW, "库", "主题", "_样张",
                              "theme-%s-浅.png" % name)
        cover = os.path.join(WORKFLOW, "库", "主题", "_样张",
                             "theme-%s-封面.png" % name)
        if not (os.path.isfile(sample) and os.path.isfile(cover)):
            r = subprocess.run(
                [sys.executable, os.path.join(WORKFLOW, "程序", "主题样张.py"),
                 "--主题", name],
                capture_output=True, text=True, cwd=WORKFLOW)
            if r.returncode != 0:
                return _json(self, {"error": r.stderr[-300:]}, 500)
        try:
            from PIL import Image
            a, b = Image.open(cover), Image.open(sample)
            w = min(a.width, b.width)
            h = int(w * a.height / a.width)
            canvas = Image.new("RGB", (w * 2 + 8, h), "#111")
            canvas.paste(a.resize((w, h)), (0, 0))
            canvas.paste(b.resize((w, h)), (w + 8, 0))
            buf = io.BytesIO()
            canvas.save(buf, "PNG")
            data = buf.getvalue()
        except ImportError:
            data = open(cover, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _render(self):
        """渲染 pages → HTML + PNG，存 REPO_TMP/preview/"""
        import subprocess
        body = self._read_json()
        theme, pages = body.get("主题", "dianshang"), body.get("pages", [])
        prev = os.path.join(REPO_TMP, "preview")
        os.makedirs(prev, exist_ok=True)
        # 清空旧的
        for f in os.listdir(prev):
            os.remove(os.path.join(prev, f))
        draft = os.path.join(REPO_TMP, "draft.json")
        io.open(draft, "w", encoding="utf-8").write(
            json.dumps(pages, ensure_ascii=False))
        env = dict(os.environ, PPT_THEME_CSS="theme-%s.css" % theme,
                   PPT_PROJECT="__console__")
        # 页面生成需要项目目录结构；用 --预览 模式输出到 prev
        r = subprocess.run(
            [sys.executable, os.path.join(WORKFLOW, "程序", "页面生成.py"),
             "--预览", draft, prev],
            capture_output=True, text=True, cwd=WORKFLOW, env=env)
        if r.returncode != 0:
            return _json(self, {"error": r.stderr[-500:]}, 500)
        # 截图
        r = subprocess.run(
            [sys.executable, os.path.join(WORKFLOW, "程序", "截图.py"), prev],
            capture_output=True, text=True, cwd=WORKFLOW)
        if r.returncode != 0:
            return _json(self, {"error": "截图失败:" + r.stderr[-300:]}, 500)
        n = len([f for f in os.listdir(prev) if f.endswith(".png")])
        return _json(self, {"ok": True, "页数": n})

    def _thumb(self, i):
        prev = os.path.join(REPO_TMP, "preview")
        files = sorted(f for f in os.listdir(prev) if f.endswith(".png"))
        if i < 0 or i >= len(files):
            self.send_error(404)
            return
        data = open(os.path.join(prev, files[i]), "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _export(self):
        import subprocess
        body = self._read_json()
        theme, pages = body.get("主题", "dianshang"), body.get("pages", [])
        proj = os.path.join(REPO_TMP, "exportproj", "页")
        os.makedirs(proj, exist_ok=True)
        io.open(os.path.join(proj, "pages.json"), "w", encoding="utf-8").write(
            json.dumps(pages, ensure_ascii=False))
        out = os.path.join(REPO_TMP, "export.pptx")
        env = dict(os.environ, PPT_THEME_CSS="theme-%s.css" % theme,
                   PPT_PROJECT=os.path.join(REPO_TMP, "exportproj"))
        r = subprocess.run(
            [sys.executable, os.path.join(WORKFLOW, "程序", "pptx导出.py"), out],
            capture_output=True, text=True, cwd=WORKFLOW, env=env)
        if r.returncode != 0:
            return _json(self, {"error": r.stderr[-500:]}, 500)
        # 找到实际输出（按项目名命名）
        cands = [os.path.join(REPO_TMP, f) for f in os.listdir(REPO_TMP)
                 if f.endswith(".pptx")]
        src = max(cands, key=os.path.getmtime)
        data = open(src, "rb").read()
        # 记下来给 /api/下载
        open(os.path.join(REPO_TMP, "last_export"), "w").write(src)
        self.send_response(200)
        self.send_header("Content-Type",
                         "application/vnd.openxmlformats-officedocument."
                         "presentationml.presentation")
        self.send_header("Content-Disposition",
                         'attachment; filename="ppt-studio.pptx"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _download(self):
        p = os.path.join(REPO_TMP, "last_export")
        if not os.path.isfile(p):
            self.send_error(404)
            return
        src = open(p).read().strip()
        data = open(src, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type",
                         "application/vnd.openxmlformats-officedocument."
                         "presentationml.presentation")
        self.send_header("Content-Disposition",
                         'attachment; filename="ppt-studio.pptx"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8901)
    a = ap.parse_args()
    srv = HTTPServer(("127.0.0.1", a.port), Handler)
    print("PPT Studio 控制台 → http://localhost:%d/" % a.port)
    srv.serve_forever()


if __name__ == "__main__":
    main()
