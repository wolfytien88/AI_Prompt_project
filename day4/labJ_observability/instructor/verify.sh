#!/usr/bin/env bash
# 講師課前驗證：實作 J（Claude Code 部分需要模型額度；Codex 部分用模擬模型）
set -uo pipefail
LAB="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-$HOME/labJ_verify}"; PORT="${PORT:-8796}"
mkdir -p "$BASE/repo" "$BASE/codex-home"; cd "$BASE/repo"; [ -d .git ] || { git init -q; printf '# demo\n' > README.md; printf 'print("hi")\n' > a.py; }
echo "== 1. 範例資料"
bash "$LAB/claude/statusline.sh" < "$LAB/samples/claude_status_input.json"
python3 "$LAB/claude/statusline.py" < "$LAB/samples/claude_status_input.json"
CODEX_NOTIFY_LOG="$BASE/direct.jsonl" python3 "$LAB/codex/notify.py" "$(cat "$LAB/samples/codex_notify_event.json")"
python3 "$LAB/cost_log.py" "$LAB"/samples/claude_p_output.json "$LAB"/samples/codex_exec_output.jsonl --codex-model demo
echo "== 2. 預算上限（真實模型）"
claude -p "讀 a.py，再寫一份 50 行的說明文件 NOTES.md" --max-budget-usd 0.01 --allowedTools "Read,Write" \
  --output-format json </dev/null 2>/dev/null | jq -c '{subtype, is_error, total_cost_usd}'
echo "== 3. Codex notify 與 --json（模擬模型）"
cat > "$BASE/codex-home/config.toml" <<CFG
model = "mock-model"
model_provider = "mock"
notify = ["python3", "$LAB/codex/notify.py"]

[model_providers.mock]
name = "mock"
base_url = "http://127.0.0.1:$PORT/v1"
wire_api = "responses"
env_key = "MOCK_KEY"

[tui]
notifications = ["agent-turn-complete", "approval-requested"]
notification_method = "auto"
CFG
MOCK_CMDS='["ls"]' MOCK_LOG="$BASE/req.jsonl" python3 "$LAB/instructor/mock_codex_usage.py" "$PORT" >/dev/null 2>&1 & mp=$!
sleep 1
CODEX_NOTIFY_LOG="$BASE/turns.jsonl" CODEX_HOME="$BASE/codex-home" MOCK_KEY=x codex exec --json "list files" </dev/null > "$BASE/codex.jsonl" 2>/dev/null
kill $mp 2>/dev/null
grep '"turn.completed"' "$BASE/codex.jsonl" | jq -c '.usage'
echo "notify 紀錄筆數：$(wc -l < "$BASE/turns.jsonl")"
echo "== 4. run_both.sh（Claude 真實、Codex 模擬）"
MOCK_CMDS='["ls"]' MOCK_LOG="$BASE/req2.jsonl" python3 "$LAB/instructor/mock_codex_usage.py" "$PORT" >/dev/null 2>&1 & mp=$!
sleep 1
CODEX_NOTIFY_LOG="$BASE/turns.jsonl" CODEX_HOME="$BASE/codex-home" MOCK_KEY=x CODEX_MODEL=mock-model BUDGET=0.30 \
  bash "$LAB/run_both.sh" "用一句話說明 README.md 的內容" "$BASE/repo" 2>/dev/null | tail -3
kill $mp 2>/dev/null
