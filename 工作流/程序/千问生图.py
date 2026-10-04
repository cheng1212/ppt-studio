# -*- coding: utf-8 -*-
"""千问 dashscope 文生图（异步任务轮询）。用法: python qwen_gen.py --prompt "..." --out out.png"""
import argparse, base64, json, time, urllib.request

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="qwen-image-3.0")
    ap.add_argument("--size", default="1664*928")
    a = ap.parse_args()
    key = json.load(open(r"C:\Users\chengge\.zcode\v2\config.json", encoding="utf-8"))
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
