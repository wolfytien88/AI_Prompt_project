#!/usr/bin/env bash
# 講師課前驗證：Codex 外掛（不需要 OpenAI 金鑰；模型用 day4/codex_check/mock_codex.py 模擬）
# 1) Codex 直接讀 Claude 格式的市集  2) Codex 原生格式  3) 外掛 Hook：未信任時略過、略過信任後才擋
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; LAB="$(cd "$HERE/.." && pwd)"
MOCK="$(cd "$LAB/../codex_check" && pwd)/mock_codex.py"
BASE="${1:-$HOME/labI_codex_verify}"; PORT="${PORT:-8793}"
mkdir -p "$BASE"
prep_repo() {  # $1 = 目錄
  mkdir -p "$1"; ( cd "$1" && rm -rf remote.git repo && git init -q --bare remote.git && mkdir repo && cd repo && git init -q -b main \
    && echo a > a && git add a && git -c user.email=t@example.com -c user.name=t commit -qm init && git remote add origin ../remote.git )
}
run_case() {  # $1 = 名稱  $2 = 市集來源  其餘 = codex exec 參數
  local name=$1 src=$2; shift 2
  local W="$BASE/$name"; prep_repo "$W"
  export CODEX_HOME="$W/codex-home"; rm -rf "$CODEX_HOME"; mkdir -p "$CODEX_HOME"
  codex plugin marketplace add "$src" >/dev/null 2>&1
  codex plugin add acme-team-kit@acme-tools >/dev/null 2>&1
  cat >> "$CODEX_HOME/config.toml" <<CFG

[model_providers.mock]
name = "mock"
base_url = "http://127.0.0.1:$PORT/v1"
wire_api = "responses"
env_key = "MOCK_KEY"

[projects."$W/repo"]
trust_level = "trusted"
CFG
  sed -i '1i model = "mock-model"\nmodel_provider = "mock"\n' "$CODEX_HOME/config.toml"
  MOCK_CMDS='["git push origin main"]' MOCK_LOG="$W/req.jsonl" python3 "$MOCK" "$PORT" >/dev/null 2>&1 & local mp=$!
  sleep 1
  MOCK_KEY=x timeout 120 codex exec -s danger-full-access "$@" -C "$W/repo" "push" </dev/null > "$W/out.txt" 2>&1
  kill $mp 2>/dev/null; wait $mp 2>/dev/null
  local skill; skill=$(codex plugin list 2>/dev/null | grep -c 'installed, enabled')
  printf '%-28s 外掛已啟用=%s  遠端分支=[%s]  %s\n' "$name" "$skill" "$(git -C "$W/remote.git" branch | tr -d ' \n')" \
    "$(grep -o 'Command blocked by PreToolUse hook[^.]*' "$W/out.txt" | head -1)"
}
run_case claude-format-untrusted "$HERE/claude/acme-marketplace"
run_case claude-format-bypass    "$HERE/claude/acme-marketplace" --dangerously-bypass-hook-trust
run_case codex-native-bypass     "$HERE/codex/acme-marketplace"  --dangerously-bypass-hook-trust
echo "預期：untrusted 被推上去（遠端分支 main）；兩個 bypass 都被 Hook 擋下（遠端分支為空）"
