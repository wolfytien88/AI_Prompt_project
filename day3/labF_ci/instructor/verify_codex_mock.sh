#!/bin/bash
# 講師課前驗證：不需要 OpenAI 金鑰，用假的 Responses API 確認 triage_codex.sh 的流程
#  1. codex exec 有把 triage_schema.json 以 strict JSON Schema 送出（記錄在 req.jsonl 的 text.format）
#  2. -o 指定的檔案只含最後一則訊息，stdout 可直接接 jq
# 模型回覆是假的（固定回傳 MOCK_TEXT），不代表 GPT 的實際判斷。
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d "$HOME/.labF-check.XXXXXX")"    # CODEX_HOME 不要放在 /tmp 底下
PORT="$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])')"
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
MOCK_TEXT='{"status":"fail","failed_tests":["tests/test_invoice.py::test_vat_rounding_half_up"],"root_cause":"模擬回覆","category":"code_bug","suggested_owner":"backend","next_step":"模擬回覆"}' \
MOCK_LOG="$WORK/req.jsonl" python3 "$HERE/mock/mock_schema_api.py" "$PORT" &
PID=$!; trap 'kill $PID 2>/dev/null; rm -rf "$WORK"' EXIT
sleep 1
cd "$WORK"
CODEX_HOME="$WORK/codex_home" MOCK_KEY=x "$HERE/triage_codex.sh" "$HERE/logs/ci_01_assert.log" 2>/dev/null > out.json
echo "== -o 輸出（應為一個 JSON 物件）"; jq . out.json
echo "== Codex 送出的 text.format（應為 json_schema、strict=true）"
jq -c '.text.format | {type, strict, name, required: .schema.required}' req.jsonl | head -1
jq -e '.status' out.json >/dev/null && echo "結果：通過"
