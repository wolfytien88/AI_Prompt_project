# 實作 C 講師資料

- `ref/`：三個審查員的設定（`.claude/agents/*.md`、`.codex/agents/*.toml`），複製到練習專案根目錄。
- `ANSWER.md`：刻意埋的 11 個問題，用來對照學員的合併報告。
- `sample_REVIEW_claude.md`：用真實模型跑出的合併報告範例（Claude Code 2.1.312）。

巡迴重點：
- 學員常讓審查員也能寫檔。`tools: Read, Grep, Glob` 是刻意的限制，審查員只讀不改。
- Claude Code 的子 Agent 預設在背景執行，主對話會先回一句「已派出」，等結果回來再合併；非互動模式下一次 `claude -p` 就會等到全部完成。
- 寫報告的權限用 `Edit(REVIEW.md)` 開放（檔案寫入類工具共用 Edit 規則）；驗證時寫成 `Write(REVIEW.md)` 的那次執行，寫檔被拒絕。
