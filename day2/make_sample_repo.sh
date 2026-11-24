#!/usr/bin/env bash
# 建立給 weekly-report Skill 練習用的範例 Repo：近 7 天內 8 筆不同類型的 commit，
# 並把 SKILL.md 放到 Claude Code 與 Codex 各自讀取的位置。
# 用法：bash make_sample_repo.sh [目標資料夾，預設 ./weekly-demo]
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-./weekly-demo}"

if [ -e "$TARGET" ]; then
  echo "錯誤：$TARGET 已存在，請換一個資料夾名稱或先自行移除" >&2
  exit 1
fi

mkdir -p "$TARGET"
cd "$TARGET"
git init -q -b main
git config user.name "課程範例"
git config user.email "demo@example.com"

commit() {   # commit <幾天前> <訊息> <檔名>
  local days="$1" msg="$2" file="$3"
  mkdir -p "$(dirname "$file")"
  echo "$msg" >> "$file"
  git add -A
  local when
  when="$(date -d "-${days} days" '+%Y-%m-%dT%H:%M:%S' 2>/dev/null || date -v-"${days}"d '+%Y-%m-%dT%H:%M:%S')"
  GIT_AUTHOR_DATE="$when" GIT_COMMITTER_DATE="$when" git commit -qm "$msg"
}

commit 6 "feat: 新增會員登入頁" src/login.py
commit 5 "fix: 修正購物車金額未乘數量" src/cart.py
commit 5 "docs: 更新 README 安裝步驟" README.md
commit 4 "feat: 訂單列表支援匯出 CSV" src/orders.py
commit 3 "fix: 滿額免運邊界條件錯誤" src/cart.py
commit 2 "feat: 新增商品搜尋關鍵字建議" src/search.py
commit 1 "docs: 補上 API 錯誤碼說明" docs/api.md
commit 0 "fix: 登入失敗訊息顯示亂碼" src/login.py

mkdir -p .claude/skills/weekly-report .agents/skills/weekly-report
cp "$HERE/skills/weekly-report/SKILL.md" .claude/skills/weekly-report/SKILL.md
cp "$HERE/skills/weekly-report/SKILL.md" .agents/skills/weekly-report/SKILL.md

echo "已建立 $(pwd)"
echo "commit 數：$(git rev-list --count HEAD)"
echo "Skill 位置：.claude/skills/weekly-report/  與  .agents/skills/weekly-report/"
