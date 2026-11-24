---
description: 依 git 紀錄替指定版本寫更新紀錄，寫入 CHANGELOG.md。
argument-hint: <版本號> [發布日期]
disable-model-invocation: true
allowed-tools:
  - Read
  - Edit(CHANGELOG.md)
---
## 最新的版本標籤
!`git describe --tags --abbrev=0`

## 最近的 commit（標籤以 tag: 標示）
!`git log --oneline --decorate -20`

## 指示
新版本號：$0
發布日期：$1（空白就用今天的日期，格式 YYYY-MM-DD）

1. 依 commit 前綴分組：feat →「新功能」、fix →「修正」、docs 與 test →「文件與測試」。沒有內容的組別不要寫。
2. 每項一行，改寫成使用者看得懂的句子，不要照抄 commit 前綴。
3. 把新段落插在 CHANGELOG.md 的「# 更新紀錄」標題下方、上一個版本之前，標題格式：`## <版本號>（<日期>）`。
4. 不要建立 commit 或標籤。完成後回報新增了幾項。
