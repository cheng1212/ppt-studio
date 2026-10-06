#!/usr/bin/env bash
# 手机.sh —— 一键让控制台手机可用：server(0.0.0.0+token) + cloudflared 隧道。
# 用法：bash 工作流/控制台/手机.sh [--port 8901]
# 令牌：环境变量 PPT_CONSOLE_TOKEN，未设则随机生成并打印。Ctrl-C 退出并清理。
set -e
cd "$(dirname "$0")/.."

PORT=8901
if [ "${1:-}" = "--port" ]; then PORT="${2:-8901}"; fi

if [ -z "${PPT_CONSOLE_TOKEN:-}" ]; then
  export PPT_CONSOLE_TOKEN=$(python3 -c "import secrets;print(secrets.token_urlsafe(16))")
fi
echo "令牌：$PPT_CONSOLE_TOKEN"

command -v cloudflared >/dev/null || { echo "缺 cloudflared，先装"; exit 1; }

python3 控制台/server.py --host 0.0.0.0 --port "$PORT" &
SRV=$!
cloudflared tunnel --url "http://127.0.0.1:$PORT" > /tmp/ppt-tunnel.log 2>&1 &
TUN=$!
trap "kill $SRV $TUN 2>/dev/null" EXIT

echo "隧道启动中…（约 10 秒）"
for i in $(seq 1 30); do
  URL=$(grep -oE "https://[a-zA-Z0-9.-]+\.trycloudflare\.com" /tmp/ppt-tunnel.log 2>/dev/null | head -1)
  if [ -n "$URL" ]; then
    echo ""
    echo "手机打开：$URL/?token=$PPT_CONSOLE_TOKEN"
    echo ""
    break
  fi
  sleep 1
done
wait $TUN
