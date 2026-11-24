---
name: weekly-report
description: 把最近一週的 git 紀錄整理成中文週報。使用者要「週報」或「本週進度」時使用。
---
# 週報產生
1. 執行 `git log --since="7 days ago" --oneline`
2. 依「新功能 / 修正 / 文件」分類，每類最多 5 點
3. 寫入 `reports/weekly-YYYY-MM-DD.md`
