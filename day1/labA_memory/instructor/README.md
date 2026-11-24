# 實作 A 講師資料

- `ref/`：參考答案。把整個資料夾內容複製到 `make_repo.sh` 建出的專案根目錄即可（含隱藏資料夾 `.claude/`、`.codex/`）。
  - `CLAUDE.md` 以 `@AGENTS.md` 匯入共用規則，兩家共用一份 AGENTS.md。
  - `services/billing/` 同時有 `CLAUDE.md`（Claude Code 用）、`AGENTS.md` 與 `AGENTS.override.md`（Codex 用）。
- `check_codex_agents.sh`：不需金鑰，用模擬伺服器驗證 Codex 的指令鏈、override 與大小上限。

巡迴重點：
- 學員常把路徑規則寫成 `paths: src/api/*`（少了 `**`），子資料夾的檔案就不會套用。
- override 實驗是本實作最容易「看到」差異的一步，請學員先只寫凍結規則，觀察 Decimal 規則消失。
- 第 7 步請學員對照提示詞與產出：提示詞沒提錯誤代碼，程式卻用了 ORD-001，代表規則生效。
