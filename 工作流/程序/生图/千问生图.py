# -*- coding: utf-8 -*-
"""千问 dashscope 文生图（异步任务轮询）。用法: python 千问生图.py --prompt "..." --out out.png"""
import argparse, base64, json, os, sys, time, urllib.request

# 跨平台 key 查找：环境变量 ZCODE_CONFIG > ~/.zcode/v2/config.json > 旧 Windows 路径
def _load_zcode_config():
    import io
    cands = []
    if os.environ.get("ZCODE_CONFIG"):
        cands.append(os.environ["ZCODE_CONFIG"])
    cands.append(os.path.join(os.path.expanduser("~"), ".zcode", "v2", "config.json"))
    cands.append(r"C:\Users\chengge\.zcode\v2\config.json")  # 旧 Windows 路径兜底
    for p in cands:
        if p and os.path.isfile(p):
            return json.load(io.open(p, encoding="utf-8"))
    raise SystemExit("ERR: 找不到 ZCode 配置（已尝试: %s）。可设环境变量 ZCODE_CONFIG 指定路径。"
                     % "；".join(cands))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="qwen-image-3.0")
    ap.add_argument("--size", default="1664*928")
    a = ap.parse_args()
    key = _load_zcode_config()
    # 从 provider 段取 key
    def find_key(o):
        if isinstance(o, dict):
            if o.get("name") == "千问":
                return o["options"]["apiKey"]
            for v in o.values():
                r = find_key(v)
                if r: return r
        return None
    apikey = find_key(key)
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    body = json.dumps({"model": a.model, "input": {"messages": [
        {"role": "user", "content": [{"text": a.prompt}]}]},
        "parameters": {"size": a.size, "n": 1}}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": "Bearer " + apikey, "Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=300).read())
    out = resp["output"]
    # 同步返回: choices[0].message.content[0].image 或 output.results
    img_url = None
    try:
        img_url = out["choices"][0]["message"]["content"][0]["image"]
    except Exception:
        try: img_url = out["results"][0]["url"]
        except Exception: pass
    if not img_url:
        print("FAIL", json.dumps(resp, ensure_ascii=False)[:400]); raise SystemExit(1)
    raw = urllib.request.urlopen(urllib.request.Request(img_url, headers={
        "Authorization": "Bearer " + apikey}), timeout=120).read()
    open(a.out, "wb").write(raw)
    print("OK", a.out, len(raw), "bytes")

if __name__ == "__main__":
    main()
