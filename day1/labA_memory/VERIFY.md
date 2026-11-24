# 實作 A 驗證紀錄（2026-10-30）

環境：Claude Code 2.1.312（真實模型）、Codex CLI 0.165.0（模擬 Responses API）、Python 3。

## Claude Code（真實模型）
專案：`make_repo.sh` 建立，複製 `instructor/ref/` 全部內容。
1. `claude -p "不要讀任何檔案…逐一列出來源檔名"` → 列出 CLAUDE.md、AGENTS.md（@匯入）、docs/conventions.md（@匯入）、CLAUDE.local.md；未列出 `.claude/rules/api.md` 與 `services/billing/CLAUDE.md`。
2. `claude -p "讀 src/web/format.py…" --allowedTools Read` → 無路徑規則。
3. `claude -p "讀 src/api/orders.py…" --allowedTools Read` → 回報讀檔後才載入 ORD-001／ORD-002 規則。
4. `claude -p "讀 services/billing/invoice.py…" --allowedTools Read` → 回報讀檔後新收到 `services/billing/CLAUDE.md`。
5. `claude -p "/context"` → 輸出含「Memory files 523 tokens」。
6. `claude -p "幫 create_order 加上輸入驗證。" --permission-mode acceptEdits --allowedTools "Bash(python3 -m pytest *)"` → 產出使用 `[ORD-001]`、`[ORD-002]`，新增測試，執行 `pytest -q -x`（採用 CLAUDE.local.md 的 -x），4 passed。
7. 只放 AGENTS.md、沒有 CLAUDE.md 的專案 → Claude Code 回報收到 AGENTS.md 並引用其規則。

## Codex（模擬伺服器，Codex 本身真實執行）
`instructor/check_codex_agents.sh`：3／3 通過。
- 在 `services/billing`：送出的指令含全域 AGENTS.md、根目錄 AGENTS.md、AGENTS.override.md；不含同層 AGENTS.md 與 `src/api/AGENTS.md`。
- 在 `src/api`：含根目錄與 `src/api/AGENTS.md`，不含帳務規則。
- `project_doc_max_bytes = 200`：根目錄內容被截斷，override 未被送出。
- 指令以一則 user 訊息送出，開頭為 `# AGENTS.md instructions for <資料夾>`，全域與專案檔之間以 `--- project-doc ---` 分隔。

## 尚未驗證
- 真實 GPT 模型回答「List the instruction sources you loaded.」的內容（模擬伺服器只回固定文字）。
- 互動模式下 `/memory` 的畫面（只驗證了 `-p "/context"`）。
- 講師機器若有使用者層 `~/.claude/CLAUDE.md`，第 1 步會多列出該檔，屬正常。
