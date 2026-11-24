#!/usr/bin/env bash
# 啟動待辦清單 App 的開發伺服器。重複執行也安全：已在執行時直接結束。
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-5173}"
URL="http://localhost:${PORT}"
mkdir -p data logs

if python3 tools/smoke_test.py "$URL" >/dev/null 2>&1; then
  echo "伺服器已在執行：$URL"
  exit 0
fi

PORT="$PORT" nohup python3 -m src.ui.server >logs/server.log 2>&1 &
echo $! > logs/server.pid

for _ in $(seq 1 20); do
  if python3 tools/smoke_test.py "$URL" >/dev/null 2>&1; then
    echo "伺服器已啟動：$URL（PID $(cat logs/server.pid)，日誌 logs/server.log）"
    exit 0
  fi
  sleep 0.5
done

echo "啟動失敗，請查看 logs/server.log" >&2
exit 1
