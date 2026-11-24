# 實作 D 驗證紀錄（2026-10-30）

環境：Python 3.13、mcp 2.3.0（官方 SDK，`MCPServer`）、Claude Code 2.1.312（真實模型）、Codex CLI 0.165.0（模擬 Responses API）。

## Server
1. `python3 seed_db.py orders.db` → 5 位客戶、8 筆訂單。
2. `ORDERS_DB=… python3 smoke_test.py` → 列出 4 個工具（三個 readOnly=True）；`order_summary(2026-10)` 回傳 pending 3 筆 49,400 等；`update_order_status(O-9999)` 回傳 `isError: true`，訊息「找不到訂單 O-9999」（使用 `ToolError`；改用前為無細節的「Error executing tool」）。
   註：mcp 2.x 已把 `FastMCP` 改名為 `MCPServer`（`from mcp.server.mcpserver import MCPServer`），1.x 的教學範例無法直接執行，requirements.txt 釘在 `mcp>=2,<3`。

## Claude Code（真實模型）
3. `claude mcp add orders --env ORDERS_DB=… -- python3 …/orders_server.py` → 寫入 local 範圍；`claude mcp list` 顯示 Connected。
4. 第 4 步查詢 → 依序呼叫 ToolSearch、`mcp__orders__query_orders(status=pending)`、`mcp__orders__order_summary(2026-10)`，回答「3 筆、NT$49,400」，正確。
5. 第 5 步寫入（未核准）→ `mcp__orders__update_order_status` 列入 permission_denials，資料庫 O-1005 仍為 pending。
6. 改用 `.mcp.json`（`${LAB_DIR:-.}`、`${ORDERS_DB:-./orders.db}`）→ `claude mcp list` 顯示「Pending approval」；`claude -p` 啟動時 MCP 狀態為 connected（source: project）。
7. 加上 `.claude/settings.json`（allow 三個唯讀工具、ask 寫入工具），資料夾未經信任時：唯讀查詢被拒（allow 未生效）；寫入工具即使加 `--allowedTools` 也被拒（ask 生效）。
8. 以 `--settings .claude/settings.json` 明確載入同一份設定：唯讀查詢不需核准，回答「台北 C01 2 筆、C04 1 筆，共 3 筆」，正確；寫入工具加 `--allowedTools` 仍被拒（ask 優先於 allow）。
9. 移除 settings.json，只用 `--allowedTools mcp__orders__update_order_status` → O-1005 改為 shipped，permission_denials 為空。

## Codex（Codex 真實執行，模型為模擬伺服器）
10. `codex mcp add orders --env … -- python3 …` → 寫入 `[mcp_servers.orders]`；`codex mcp list` 顯示 enabled；`codex mcp get orders --json` 顯示 enabled_tools 四個、startup_timeout_sec 20。
11. `codex exec` → Codex 啟動 orders Server，請求中出現 `{"type":"namespace","name":"mcp__orders","description":"虛構公司的客戶與訂單資料庫…","tools":[list_customers, order_summary, query_orders, update_order_status]}`。
12. `enabled_tools` 拿掉 update_order_status → 請求中不再出現該工具，其餘三個仍在。
13. `[mcp_servers.orders.tools.update_order_status] approval_mode = "prompt"` → 設定可正常載入，無錯誤。

## 尚未驗證
- 互動模式下的信任對話框與 `.mcp.json` 核准畫面（第 8 步）；本次以 `--settings` 代替。
- Codex `approval_mode = "prompt"` 在真實模型呼叫寫入工具時的核准畫面。
- 真實 GPT 模型使用 MCP 工具回答的結果。
