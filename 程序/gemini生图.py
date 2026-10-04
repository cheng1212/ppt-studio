# -*- coding: utf-8 -*-
"""gemini-web 生图修正版: 捕获任何 googleusercontent 图片响应(不限 gg-dl)。
用法: python gemini_capture.py --prompt "..." --out out.png [--timeout 180]
"""
import argparse, time, sys
from playwright.sync_api import sync_playwright

MIN_BYTES = 51200  # 50KB 以上才算候选原图

def log(m): print("[capture %s] %s" % (time.strftime("%H:%M:%S"), m), flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cdp", default="http://127.0.0.1:9222")
    ap.add_argument("--timeout", type=int, default=180)
    args = ap.parse_args()

    hits = []  # (url, content-type)
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(args.cdp)
        pg = None
        for ctx in b.contexts:
            for x in ctx.pages:
                if "gemini.google.com" in x.url:
                    pg = x; break
            if pg: break
        if pg is None:
            pg = b.contexts[0].new_page()
            pg.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=40000)
            pg.wait_for_timeout(6000)
        log("页面: " + pg.url[:80])

        def on_response(resp):
            try:
                u = resp.url
                ct = (resp.headers or {}).get("content-type", "")
                if resp.status == 200 and "image/" in ct and "svg" not in ct and \
                   ("googleusercontent" in u or "gstatic" in u or "ggpht" in u):
                    hits.append(u)
            except Exception:
                pass
        pg.on("response", on_response)

        inp = pg.locator("rich-textarea textarea, div.ql-editor[contenteditable='true'], textarea").first
        inp.wait_for(state="visible", timeout=20000)
        try: inp.fill("")
        except Exception: pass
        inp.click()
        pg.wait_for_timeout(300)
        inp.type(args.prompt, delay=10)
        pg.wait_for_timeout(400)
        pg.keyboard.press("Enter")
        log("已提交, 等待图片响应...")

        deadline = time.time() + args.timeout
        while time.time() < deadline:
            # 从大到小尝试下载捕获到的原图 URL
            for u in list(hits):
                try:
                    r = pg.request.get(u, timeout=20000)
                    if r.status != 200: continue
                    body = r.body()
                    if len(body) < MIN_BYTES: continue
                    # 放大尺寸参数再试一次 (googleusercontent =sNNN / =wNNN-hNNN)
                    big = u
                    if "=s" in u or "=w" in u:
                        base = u.split("=", 1)[0]
                        big = base + "=s4096-rw" if "=s" in u else base.split("=")[0] + "=w4096-h2304-rw"
                        try:
                            r2 = pg.request.get(big, timeout=25000)
                            if r2.status == 200 and len(r2.body()) > len(body):
                                body = r2.body(); u = big
                        except Exception:
                            pass
                    with open(args.out, "wb") as f:
                        f.write(body)
                    log("已保存 %s (%d bytes) %s..." % (args.out, len(body), u[:90]))
                    print("OK", args.out)
                    return 0
                except Exception as e:
                    log("下载失败 %s: %s" % (u[:70], e))
                    hits.remove(u)
            pg.wait_for_timeout(3000)
        raise RuntimeError("timeout")

sys.exit(main())
