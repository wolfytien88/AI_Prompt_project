# 實作 D 講師資料

- `ref/.mcp.json`、`ref/.claude/settings.json`：Claude Code 專案層設定（伺服器＋權限規則）。
- `ref/codex_config_snippet.toml`：Codex 的對應設定。
- 練習資料：`seed_db.py` 產生 5 位客戶、8 筆訂單；十月未出貨（pending）3 筆、合計 49,400 元，台北客戶 C01、C04 共 3 筆訂單。可用來核對答案。

巡迴重點：
- `claude mcp list` 顯示「Pending approval」：`.mcp.json` 的伺服器要在互動模式執行 `claude` 時核准；`claude -p` 會直接載入。
- 專案 `settings.json` 的 allow 規則在驗證時，要等資料夾被信任（第一次執行 `claude` 時接受信任對話框）才生效；ask 規則則是一開始就生效。課堂上請學員先在互動模式開一次 `claude`。
- ask 規則會蓋過 `--allowedTools`：規則的判斷順序是 deny → ask → allow。
- `smoke_test.py` 的錯誤訊息測試會在 stderr 印出一段 Traceback，屬正常（伺服器端的記錄）。
