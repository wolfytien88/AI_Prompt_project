#!/bin/bash
# 用 Claude Code 的非互動模式分析 CI 記錄，輸出符合 triage_schema.json 的 JSON
# 用法：./triage_claude.sh logs/ci_01_assert.log > out/claude_01.json
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$1"
PROMPT="$(cat "$HERE/triage_prompt.md")

<ci_log>
$(cat "$LOG")
</ci_log>"
claude -p "$PROMPT" \
  --output-format json \
  --json-schema "$(cat "$HERE/triage_schema.json")" \
  --disallowedTools "Bash Edit Write WebFetch WebSearch" \
  --max-turns 3 \
  --max-budget-usd 0.50 \
  < /dev/null | jq '.structured_output'
