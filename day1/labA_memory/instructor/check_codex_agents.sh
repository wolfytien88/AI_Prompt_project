#!/bin/bash
# 講師課前驗證：不需要 OpenAI 金鑰。用模擬的 Responses API 讓真的 Codex 組出指令鏈，
# 再從送出的請求檢查哪些 AGENTS.md 被載入。需要 codex、python3、git。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; LAB="$(cd "$HERE/.." && pwd)"; MOCK="$(cd "$LAB/../../mock" && pwd)/mock_responses.py"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/labA-codex.XXXXXX")"; cd "$WORK"
PORT="$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])')"
bash "$LAB/make_repo.sh" repo >/dev/null
cp -r "$HERE/ref/." repo/; rm -f repo/CLAUDE.md repo/CLAUDE.local.md repo/services/billing/CLAUDE.md
export CODEX_HOME="$WORK/home"; mkdir -p "$CODEX_HOME"
cat > "$CODEX_HOME/config.toml" <<TOML
model = "mock-model"
model_provider = "mock"
[model_providers.mock]
name = "mock"
base_url = "http://127.0.0.1:$PORT/v1"
wire_api = "responses"
env_key = "MOCK_KEY"
[projects."$WORK/repo"]
trust_level = "trusted"
TOML
echo "# 全域：所有專案回覆都要簡短" > "$CODEX_HOME/AGENTS.md"
python3 "$MOCK" "$PORT" >/dev/null 2>&1 & MPID=$!; sleep 1
PASS=0; FAIL=0
check() { # 說明 資料夾 必須出現... -- 不可出現...
  local desc=$1 dir=$2; shift 2
  MOCK_KEY=x timeout 60 codex exec --cd "repo/$dir" "List the instruction sources you loaded." </dev/null >/dev/null 2>&1
  local ok=1 mode=need
  for k in "$@"; do
    [ "$k" = "--" ] && { mode=deny; continue; }
    if grep -q -- "$k" full_req.json; then [ $mode = deny ] && ok=0; else [ $mode = need ] && ok=0; fi
  done
  if [ $ok = 1 ]; then echo "PASS  $desc"; PASS=$((PASS+1)); else echo "FAIL  $desc"; FAIL=$((FAIL+1)); fi
}
check "billing：全域＋根目錄＋override，不含同層 AGENTS.md 與 API 規則" services/billing "全域：所有專案" "order-portal 專案指令" "結帳凍結" -- "# 帳務服務規則" "訂單 API 規則"
check "src/api：全域＋根目錄＋API 規則，不含帳務規則" src/api "全域：所有專案" "order-portal 專案指令" "訂單 API 規則" -- "結帳凍結"
sed -i 's/65536/200/' repo/.codex/config.toml
check "project_doc_max_bytes=200：根目錄被截斷，override 被擠掉" services/billing "order-portal 專案指令" -- "結帳凍結"
kill $MPID 2>/dev/null
echo "通過 $PASS／失敗 $FAIL（工作目錄 $WORK）"
