#!/bin/bash
# 講師課前驗證：不需要 OpenAI 金鑰，用假的 Responses API 跑 fix_agent_codex.mjs
#  - 模型回覆是假的：假伺服器依序要求 Codex 執行 MOCK_CMDS（跑測試 → 套用修正 → 再跑測試）
#  - Codex 執行指令、workspace-write 沙箱、SDK 事件串流、resumeThread 與 outputSchema 都是真的
# 需要：node 18+、python3；會在暫存資料夾安裝 @openai/codex-sdk
set -euo pipefail
LAB="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d "$HOME/.labG-check.XXXXXX")"
PORT="$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])')"
PID=""
trap 'kill $PID 2>/dev/null; rm -rf "$WORK"' EXIT
cp -r "$LAB/buggy_invoice" "$WORK/proj"
cp "$LAB/fix_agent_codex.mjs" "$WORK/"
(cd "$WORK" && echo '{"name":"labg-check","private":true}' > package.json && npm i @openai/codex-sdk >/dev/null 2>&1)
mkdir -p "$WORK/codex_home"
cat > "$WORK/codex_home/config.toml" <<TOML
model = "mock-model"
model_provider = "mock"
[model_providers.mock]
name = "mock"
base_url = "http://127.0.0.1:$PORT/v1"
wire_api = "responses"
env_key = "MOCK_KEY"
TOML
FIX="cp '$LAB/instructor/buggy_invoice_solution/calc.py' invoice/calc.py"
export MOCK_CMDS="[\"python3 -m unittest discover -s tests 2>&1 | tail -1\", \"$FIX\", \"python3 -m unittest discover -s tests 2>&1 | tail -1\"]"
export MOCK_JSON='{"tests_passed":true,"bugs":[{"function":"vat_amount","cause":"模擬回覆","fix":"模擬回覆"}]}'
export MOCK_LOG="$WORK/req.jsonl"
python3 "$LAB/mock/mock_codex_agent.py" "$PORT" & PID=$!
sleep 1
export CODEX_HOME="$WORK/codex_home" MOCK_KEY=x
cd "$WORK"
echo "== 第一次：runStreamed"
node fix_agent_codex.mjs proj | tee run1.log
TID=$(grep -o -- '--resume [0-9a-f-]*' run1.log | awk '{print $2}')
echo "== 第二次：resumeThread + outputSchema（thread $TID）"
node fix_agent_codex.mjs proj --resume "$TID"
echo "== 專案測試結果"
(cd proj && python3 -m unittest discover -s tests 2>&1 | tail -1)
echo "== 假伺服器收到的請求（第二次應帶 json_schema，且輸入包含第一次的歷史）"
cat req.jsonl
