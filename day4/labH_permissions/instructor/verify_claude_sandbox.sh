#!/usr/bin/env bash
# 講師課前驗證：用 claude -p 跑 P1–P7（Linux 需要 bubblewrap 與 socat；macOS 用內建 Seatbelt）
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-$HOME/labH}"
bash "$HERE/setup.sh" "$BASE" >/dev/null
cd "$BASE/proj"
claude -p "$(cat "$HERE/claude_probe_prompt.txt")" --output-format json </dev/null > "$BASE/claude_probe.json"
python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['result']);print('cost',d.get('total_cost_usd'))" "$BASE/claude_probe.json"
