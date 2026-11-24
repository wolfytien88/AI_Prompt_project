# 實作 E 驗證紀錄（2026-10-29／30，Claude Code 2.1.312、Codex CLI 0.165.0）

## 已實際執行
| 項目 | 指令 | 結果 |
| --- | --- | --- |
| Plan mode 不改檔 | `claude -p "<feature_request.md> 先規劃，不要修改檔案。" --permission-mode plan --output-format json` | subtype=success，4–5 回合，約 US$0.14–0.15；`git status --short` 為空。計畫檔寫在 `~/.claude/plans/` 底下（本次觀察，見 `instructor/sample_plan.md`） |
| 參考實作 | `claude -p "<feature_request.md>" --permission-mode acceptEdits --allowedTools ...` | 17 回合、約 US$0.20；`make test` 8 個測試通過。差異存為 `instructor/reference.patch`，已確認可套用到乾淨的 starter 並通過測試 |
| Codex worktree 隔離 | `codex exec --worktree -s workspace-write`（假伺服器要求執行 `echo changed >> README.md`） | 指令在 `$CODEX_HOME/worktrees/<id>/<repo>`（detached HEAD）執行；原工作目錄 `git status` 為空 |
| 自動驗證腳本 | `instructor/verify_labE.sh` | 兩項皆「通過」 |

## 尚未驗證（需要互動終端機，課前請手動走一次）
- Shift+Tab 切換到 plan mode、Ctrl+G 編輯計畫、核准選項的畫面
- Esc Esc／`/rewind` 的五個選項與「restore code and conversation」
- 第 5 步「Bash 的改動不被 checkpoint 還原」（依官方 checkpointing 文件，未在本環境實測）
- `/branch`、`--resume <id> --fork-session`
- Codex 的 `/plan`、`/fork`、`/side`、`/worktree`（文件列出的斜線指令；未實際操作）
- 真實 GPT 模型的規劃與實作品質（本環境無 OpenAI 金鑰）
