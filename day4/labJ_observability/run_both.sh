#!/usr/bin/env bash
# 用同一個任務分別跑 Claude Code 與 Codex，留下 JSON 紀錄後彙整成 costs.csv
# 用法：bash run_both.sh "<任務>" [專案目錄，預設目前目錄]
# 環境變數：CODEX_MODEL（寫進 CSV 的模型名稱）、BUDGET（Claude Code 的 --max-budget-usd，預設 0.50）
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TASK="${1:?請給任務文字}"; PROJ="${2:-$PWD}"
LOG="$PROJ/logs"; mkdir -p "$LOG"; TS=$(date +%Y%m%d-%H%M%S)
cd "$PROJ"
echo "== Claude Code"
claude -p "$TASK" --output-format json --max-budget-usd "${BUDGET:-0.50}" \
  --allowedTools "Read,Grep,Glob" </dev/null > "$LOG/claude-$TS.json"
echo "== Codex"
codex exec --json "$TASK" </dev/null > "$LOG/codex-$TS.jsonl"
echo "== 彙整"
python3 "$HERE/cost_log.py" "$LOG"/claude-*.json "$LOG"/codex-*.jsonl \
  --codex-model "${CODEX_MODEL:-default}" -o "$PROJ/costs.csv"
column -s, -t < "$PROJ/costs.csv" 2>/dev/null || cat "$PROJ/costs.csv"
