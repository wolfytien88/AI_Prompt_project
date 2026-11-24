---
name: changelog
description: 依 git 紀錄替指定版本寫更新紀錄，寫入 CHANGELOG.md。只在使用者明確輸入 $changelog 時使用。
---
# 更新紀錄產生器

使用者會在 `$changelog` 後面寫新版本號，可能再加發布日期（沒給就用今天，格式 YYYY-MM-DD）。

1. 執行 `bash .agents/skills/changelog/scripts/commits_since_tag.sh`，取得最新標籤與之後的 commit。
2. 依 commit 前綴分組：feat →「新功能」、fix →「修正」、docs 與 test →「文件與測試」。沒有內容的組別不要寫。
3. 每項一行，改寫成使用者看得懂的句子，不要照抄 commit 前綴。
4. 把新段落插在 CHANGELOG.md 的「# 更新紀錄」標題下方、上一個版本之前，標題格式：`## <版本號>（<日期>）`。
5. 不要建立 commit 或標籤。完成後回報新增了幾項。
