#!/bin/bash
# 用 Codex 的非互動模式分析 CI 記錄，輸出符合 triage_schema.json 的 JSON
# 用法：./triage_codex.sh logs/ci_01_assert.log > out/codex_01.json
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$1"
OUT="$(mktemp)"
PROMPT="$(cat "$HERE/triage_prompt.md")

<ci_log>
$(cat "$LOG")
</ci_log>"
codex exec "$PROMPT" \
  --sandbox read-only \
  --skip-git-repo-check \
  --ephemeral \
  --output-schema "$HERE/triage_schema.json" \
  -o "$OUT" \
  < /dev/null > /dev/null
cat "$OUT"; rm -f "$OUT"
