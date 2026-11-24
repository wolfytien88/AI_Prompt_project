#!/bin/bash
# 講師課前驗證（可自動化的部分）
#  1. Claude Code：--permission-mode plan 只產生計畫，不修改專案檔案（需要 ANTHROPIC_API_KEY 或已登入）
#  2. Codex：exec --worktree 在獨立的 worktree 執行，原本的工作目錄不受影響（用假伺服器，不需金鑰）
# 互動操作（Shift+Tab、Ctrl+G、Esc Esc、/rewind、/fork、/side）無法自動化，請課前手動走一次 labE.md。
set -uo pipefail
LAB="$(cd "$(dirname "$0")/.." && pwd)"
STARTER="$LAB/../starter"
MOCK="$LAB/../labG_sdk/mock/mock_codex_agent.py"
WORK="$(mktemp -d "$HOME/.labE-check.XXXXXX")"
PID=""; trap 'kill $PID 2>/dev/null; cd /; git -C "$WORK/proj" worktree prune 2>/dev/null; rm -rf "$WORK"' EXIT
cp -r "$STARTER" "$WORK/proj"
cd "$WORK/proj" && git init -q && git add -A && git -c user.email=t@example.com -c user.name=t commit -qm init

echo "== 1. Claude Code plan mode"
if command -v claude >/dev/null; then
  claude -p "$(cat "$LAB/feature_request.md") 先規劃，不要修改檔案。" \
    --permission-mode plan --output-format json < /dev/null > "$WORK/plan.json"
  jq -r '"subtype=\(.subtype) turns=\(.num_turns) cost=$\(.total_cost_usd)"' "$WORK/plan.json"
  if [ -z "$(git status --short)" ]; then echo "通過：專案檔案沒有變動"; else echo "失敗：有檔案被修改"; git status --short; fi
else
  echo "略過：找不到 claude"
fi

echo "== 2. Codex exec --worktree"
PORT="$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])')"
mkdir -p "$WORK/codex_home"
printf 'model = "mock-model"\nmodel_provider = "mock"\n[model_providers.mock]\nname = "mock"\nbase_url = "http://127.0.0.1:%s/v1"\nwire_api = "responses"\nenv_key = "MOCK_KEY"\n' "$PORT" > "$WORK/codex_home/config.toml"
MOCK_CMDS='["pwd", "echo changed >> README.md"]' MOCK_LOG="$WORK/req.jsonl" python3 "$MOCK" "$PORT" & PID=$!
sleep 1
CODEX_HOME="$WORK/codex_home" MOCK_KEY=x codex exec --worktree -s workspace-write "test" < /dev/null > "$WORK/codex.log" 2>&1
grep -m1 "worktrees" "$WORK/codex.log" | sed 's/^/  執行位置：/'
if [ -z "$(git status --short)" ]; then echo "通過：原工作目錄沒有變動"; else echo "失敗：原工作目錄被修改"; fi
git worktree list
