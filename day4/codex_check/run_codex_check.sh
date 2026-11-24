#!/bin/bash
# 講師課前驗證：用假的 Responses API 讓 Codex 真的執行 Hook 與沙箱。
# 不需要 OpenAI 連線或 API Key；需要 codex CLI（npm install -g @openai/codex）與 python3、git。
#
# 案例：
#   A 沒有 Hook                         → 推送成功（對照組，證明測試有效）
#   B 專案層 Hook，專案未信任          → Hook 被靜默略過，推送成功（陷阱 1）
#   C 專案已信任，但 Hook 未經 /hooks 審查 → Hook 被靜默略過，推送成功（陷阱 1）
#   D 專案已信任＋Hook 已信任            → 推送被擋
#   E 使用者層 Hook（~/.codex/hooks.json）＋已信任 → 推送被擋
#   F 只靠 workspace-write，遠端在 /tmp   → 推送成功（陷阱 3：/tmp 預設可寫）
#   G 只靠 workspace-write，遠端在工作區外 → 推送被沙箱擋下
#
# 「Hook 已信任」在自動化時用 --dangerously-bypass-hook-trust 模擬；
# 學員在互動模式下應改用 CLI 的 /hooks 審查並信任。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
DAY4="$(cd "$HERE/.." && pwd)"
GUARD="$DAY4/guard.py"
WORK="$(mktemp -d /tmp/codex-hook-check.XXXXXX)"
OUTSIDE="$HOME/.codex-hook-check-remote.$$.git"   # 工作區與 /tmp 以外的位置
PORT="$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])')"
PASS=0; FAIL=0

command -v codex >/dev/null || { echo "找不到 codex，請先 npm install -g @openai/codex"; exit 1; }
echo "codex 版本：$(codex --version)"
echo "工作目錄：$WORK"

write_config() {  # $1 = CODEX_HOME
  mkdir -p "$1"
  cat > "$1/config.toml" <<EOF
model = "mock-model"
model_provider = "mock"

[model_providers.mock]
name = "mock"
base_url = "http://127.0.0.1:$PORT/v1"
wire_api = "responses"
env_key = "MOCK_KEY"
EOF
}

hooks_json() {  # $1 = guard.py 的路徑
  printf '{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"python3 %s","timeout":30}]}]}}\n' "$1"
}

# run_case 名稱 預期(blocked|pushed) Hook位置(none|project|user) 信任專案(yes|no) 遠端路徑 codex參數...
run_case() {
  local name=$1 expect=$2 hooks=$3 trust=$4 remote=$5; shift 5
  local dir="$WORK/$name"; mkdir -p "$dir"
  local home="$dir/codex_home" repo="$dir/repo" log="$dir/requests.jsonl"
  write_config "$home"
  rm -rf "$remote"; git init -q --bare "$remote"
  mkdir -p "$repo"
  (cd "$repo" && git init -q -b main && git config user.email t@example.com && git config user.name t \
     && echo hi > a.txt && git add -A && git commit -qm init && git remote add origin "$remote")
  if [ "$hooks" = project ]; then
    mkdir -p "$repo/.codex/hooks"; cp "$GUARD" "$repo/.codex/hooks/guard.py"
    hooks_json ".codex/hooks/guard.py" > "$repo/.codex/hooks.json"
  elif [ "$hooks" = user ]; then
    mkdir -p "$home/hooks"; cp "$GUARD" "$home/hooks/guard.py"
    hooks_json "$home/hooks/guard.py" > "$home/hooks.json"
  fi
  [ "$trust" = yes ] && printf '\n[projects."%s"]\ntrust_level = "trusted"\n' "$repo" >> "$home/config.toml"

  MOCK_CMDS='["git push origin main"]' MOCK_LOG="$log" python3 "$HERE/mock_codex.py" "$PORT" >/dev/null 2>&1 &
  local mp=$!; sleep 1
  CODEX_HOME="$home" MOCK_KEY=x timeout 90 codex exec -C "$repo" "$@" "請推送" < /dev/null > "$dir/codex_output.txt" 2>&1
  kill $mp 2>/dev/null; wait $mp 2>/dev/null

  local refs; refs=$(git --git-dir="$remote" show-ref 2>/dev/null | wc -l)
  local got=pushed; [ "$refs" -eq 0 ] && got=blocked
  local detail; detail=$(python3 - "$log" <<'PY'
import json, sys
outs = [o for l in open(sys.argv[1], encoding="utf-8") for o in json.loads(l)["function_call_outputs"]]
s = outs[-1] if outs else "(Codex 沒有回傳工具結果)"
for key in ("Command blocked", "unable to create", "Process exited"):
    i = s.find(key)
    if i >= 0:
        s = s[i:]
        break
print(s.replace("\n", " ")[:110])
PY
)
  if [ "$got" = "$expect" ]; then PASS=$((PASS+1)); r="PASS"; else FAIL=$((FAIL+1)); r="FAIL"; fi
  printf '[%s] %-34s 預期 %-7s 實際 %-7s 遠端 refs=%s\n      工具結果：%s\n' "$r" "$name" "$expect" "$got" "$refs" "$detail"
}

BYPASS=(--dangerously-bypass-approvals-and-sandbox)   # 關掉沙箱，只看 Hook 的效果
run_case A-no-hook                pushed  none    no  "$WORK/A.git" "${BYPASS[@]}"
run_case B-project-untrusted      pushed  project no  "$WORK/B.git" "${BYPASS[@]}"
run_case C-trusted-unreviewed     pushed  project yes "$WORK/C.git" "${BYPASS[@]}"
run_case D-trusted-reviewed       blocked project yes "$WORK/D.git" "${BYPASS[@]}" --dangerously-bypass-hook-trust
run_case E-user-level-hook        blocked user    no  "$WORK/E.git" "${BYPASS[@]}" --dangerously-bypass-hook-trust
run_case F-sandbox-remote-in-tmp  pushed  none    no  "$WORK/F.git" -s workspace-write
run_case G-sandbox-remote-outside blocked none    no  "$OUTSIDE"    -s workspace-write
rm -rf "$OUTSIDE"

echo "結果：$PASS 通過，$FAIL 失敗（詳細輸出在 $WORK/<案例>/codex_output.txt）"
[ "$FAIL" -eq 0 ]
