#!/usr/bin/env bash
# 不經過模型，直接把 probes.txt 的每個指令丟進 Codex 沙箱執行
# 用法：CODEX_HOME=~/labH/codex-home bash codex_probes.sh ~/labH/proj [權限設定檔名稱，預設 lab]
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PROJ="${1:?請給練習專案路徑}"; PROFILE="${2:-lab}"
grep -v '^#' "$HERE/probes.txt" | while IFS='|' read -r id desc cmd; do
  out=$(cd "$PROJ" && timeout 40 codex sandbox -C "$PROJ" -P "$PROFILE" -- bash -c "$cmd" 2>&1 </dev/null \
        | grep -vE '^\s+[0-9]+: <unknown>|Stack backtrace|PATH aliases' | head -2 | tr '\n' ' ')
  printf '%s｜%s｜%s\n' "$id" "$desc" "$out"
done
