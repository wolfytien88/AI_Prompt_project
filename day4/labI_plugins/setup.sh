#!/usr/bin/env bash
# 建立實作 I 的練習 repo（含本機遠端與一筆尚未提交的變更）：bash setup.sh [目錄]（預設 ~/labI）
set -euo pipefail
BASE="${1:-$HOME/labI}"
mkdir -p "$BASE" && cd "$BASE"
[ -d remote.git ] || git init -q --bare remote.git
[ -d repo ] || {
  mkdir repo && cd repo
  git init -q -b main
  printf 'def price(x):\n    return x\n' > shop.py
  git add -A && git -c user.email=t@example.com -c user.name=t commit -qm init
  git remote add origin ../remote.git
  printf 'def price(x, discount=0):\n    return x * (1 - discount)\n' > shop.py
  printf 'API_KEY = "sk-live-fake-123"\nimport os\ndef run(name):\n    os.system("ls " + name)\n' > util.py
}
echo "練習 repo：$BASE/repo"
