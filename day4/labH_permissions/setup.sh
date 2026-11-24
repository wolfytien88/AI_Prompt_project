#!/usr/bin/env bash
# 建立實作 H 的練習專案：bash setup.sh [目錄]（預設 ~/labH）
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE="${1:-$HOME/labH}"
mkdir -p "$BASE/proj/sub" "$BASE/codex-home"
cd "$BASE/proj"
[ -d .git ] || git init -q -b main
echo "PAYMENT_API_KEY=sk-fake-labH-0000" > .env          # 假金鑰
echo "DB_PASSWORD=fake-password" > sub/app.env
echo "# 練習專案" > README.md
mkdir -p .claude && cp "$HERE/claude/settings.json" .claude/settings.json
cp "$HERE/codex/config.toml" "$BASE/codex-home/config.toml"
echo "練習專案：$BASE/proj"
echo "Codex 設定：$BASE/codex-home/config.toml（用 export CODEX_HOME=$BASE/codex-home 隔離）"
