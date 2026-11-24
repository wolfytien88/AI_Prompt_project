---
name: pr-summary
description: 依目前尚未提交的變更寫出 PR 摘要。使用者要求寫 PR 說明、整理這次改了什麼時使用。
argument-hint: "[讀者，例如 reviewer 或 PM]"
---
## 目前的變更
!`git diff HEAD --stat || true`

!`git diff HEAD || true`

## 指示
讀者是：$ARGUMENTS（沒有指定時以 reviewer 為讀者）。
用繁體中文輸出三段：
1. **改了什麼**：最多三點。
2. **為什麼**：一句話。
3. **風險與測試**：列出需要特別檢查的地方；沒有測試變更時明確寫出。
不要編造 diff 裡沒有的內容。
