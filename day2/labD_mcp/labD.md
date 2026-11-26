# 實作 D：用 MCP 接上公司資料

> 在 VS Code 中操作本實作的方式，見 [`../../vscode.md`](../../vscode.md)。

## 目的

- 了解 MCP Server 的最小結構：一支程式透過 stdio 收發 JSON-RPC，宣告幾個工具。
- 把同一個 MCP Server 接到 Claude Code 與 Codex，練習兩家的註冊方式與設定範圍（個人、專案）。
- 用權限控管工具：唯讀查詢直接執行，寫入資料的工具每次都要核准。
- 看見 MCP 工具在兩家 Agent 裡的名字與載入方式。

## 形式

個人實作。

## 前置

| 項目 | 指令或說明 |
| --- | --- |
| Python 套件 | `pip install -r requirements.txt`（官方 MCP Python SDK 2.x） |
| 練習資料夾 | `mkdir -p ~/lab/orders-lab && cp orders_server.py seed_db.py smoke_test.py ~/lab/orders-lab/ && cd ~/lab/orders-lab && git init -q` |
| 資料庫 | `python3 seed_db.py orders.db`：虛構的 5 位客戶、8 筆訂單 |
| 參考答案 | `instructor/ref/` |

`orders_server.py` 提供四個工具：

| 工具 | 類型 | 說明 |
| --- | --- | --- |
| `list_customers(city)` | 唯讀 | 列出客戶，可依城市篩選 |
| `query_orders(customer_id, status, limit)` | 唯讀 | 查詢訂單 |
| `order_summary(month)` | 唯讀 | 某月各狀態的筆數與金額 |
| `update_order_status(order_id, status)` | 寫入 | 修改訂單狀態 |

工具都用 `@server.tool(...)` 宣告，唯讀工具加上 `readOnlyHint=True` 標註；資料庫位置由環境變數 `ORDERS_DB` 決定。

## 步驟

### Part 1：不經過 Agent，先確認 Server 正常

1. 讀 `orders_server.py`，找出四個工具的宣告與 `ToolError` 的用法（錯誤訊息會原樣回給 Agent）。
2. 執行煙霧測試：

   ```bash
   ORDERS_DB=$PWD/orders.db python3 smoke_test.py
   ```

   預期看到 4 個工具（三個 `readOnly=True`）、十月的狀態統計，以及查無訂單時的錯誤回應。這支程式就是在做 Agent 連上 MCP Server 時做的事：`initialize` → `tools/list` → `tools/call`。

### Part 2：Claude Code

3. **個人範圍**（local，只有你、只在這個專案）：

   ```bash
   claude mcp add orders --env ORDERS_DB=$PWD/orders.db -- python3 $PWD/orders_server.py
   claude mcp list          # orders 應顯示 Connected
   claude mcp get orders
   ```

   `--` 之後的內容整段交給 Server 執行。設定存在 `~/.claude.json`，不進版控。

4. **只開放唯讀工具**，問一個查詢問題：

   ```bash
   claude -p "十月有哪些訂單還沒出貨？金額合計多少？" \
     --allowedTools "mcp__orders__query_orders,mcp__orders__order_summary,mcp__orders__list_customers"
   ```

   MCP 工具在 Claude Code 的名字是 `mcp__<伺服器>__<工具>`。答案應為 3 筆、49,400 元。

5. **試著寫入**：

   ```bash
   claude -p "把訂單 O-1005 的狀態改成 shipped" --allowedTools "mcp__orders__query_orders"
   ```

   ```bash
   claude -p "把訂單 O-1005 的狀態改成 shipped，並確認結果" --allowedTools "mcp__orders__query_orders,mcp__orders__update_order_status"
   ```
   寫入工具沒有被核准，非互動模式直接拒絕，訂單不會改變。

6. **改成專案範圍**，讓同組的人共用。先移除個人設定（`claude mcp remove orders -s local`），在專案根目錄建立 `.mcp.json`：

   ```json
   {
     "mcpServers": {
       "orders": {
         "type": "stdio",
         "command": "python3",
         "args": ["${LAB_DIR:-.}/orders_server.py"],
         "env": { "ORDERS_DB": "${ORDERS_DB:-./orders.db}" }
       }
     }
   }
   ```

   `${變數:-預設值}` 在載入時展開，路徑與金鑰不必寫死在檔案裡。

7. **用權限規則管理工具**，建立 `.claude/settings.json`：

   ```json
   {
     "permissions": {
       "allow": [
         "mcp__orders__list_customers",
         "mcp__orders__query_orders",
         "mcp__orders__order_summary"
       ],
       "ask": ["mcp__orders__update_order_status"]
     }
   }
   ```

8. 在互動模式執行一次 `claude`：接受資料夾信任、核准 `.mcp.json` 的伺服器（`/mcp` 可查看狀態）。接著：
   - 問「台北的客戶各有幾筆訂單？」：不會跳出詢問。
   - 說「把 O-1005 改成 shipped」：跳出核准詢問。
   - 非互動模式再試一次寫入，就算加上 `--allowedTools mcp__orders__update_order_status`，仍會被拒絕。

### Part 3：Codex

9. 註冊：

   ```bash
   codex mcp add orders --env ORDERS_DB=$PWD/orders.db -- python3 $PWD/orders_server.py
   codex mcp list
   codex mcp get orders --json
   ```

   設定寫進 `~/.codex/config.toml` 的 `[mcp_servers.orders]`。

10. 打開 `~/.codex/config.toml`，在 `[mcp_servers.orders]` 補上工具清單與核准方式：

    ```toml
    [mcp_servers.orders]
    command = "python3"
    args = ["/home/you/lab/orders-lab/orders_server.py"]
    enabled_tools = ["list_customers", "query_orders", "order_summary", "update_order_status"]
    default_tools_approval_mode = "auto"
    startup_timeout_sec = 20

    [mcp_servers.orders.env]
    ORDERS_DB = "/home/you/lab/orders-lab/orders.db"

    [mcp_servers.orders.tools.update_order_status]
    approval_mode = "prompt"
    ```

11. 執行 `codex`，輸入 `/mcp` 確認伺服器狀態，再問同樣兩個問題：查詢直接執行，修改訂單要核准。
12. 把 `update_order_status` 從 `enabled_tools` 拿掉，重新啟動 Codex，再要求修改訂單。這次 Codex 根本看不到這個工具。

## 觀察重點

- MCP 讓「接資料」與「Agent 本身」分開：同一支 Server，兩家都能用，不用各寫一套整合。
- Server 的描述與工具說明會進到模型的 Context。描述寫得清楚，模型才知道何時呼叫哪個工具。
- Claude Code 預設延後載入工具定義（tool search），模型需要時才載入；Codex 把伺服器的工具組成一個 `mcp__orders` 命名空間送給模型。
- 「不給工具」比「給了再擋」更保險：Claude Code 在 deny 寫裸工具名、Codex 用 `enabled_tools`／`disabled_tools`，模型根本看不到該工具。
- ask 規則會蓋過 `--allowedTools`，規則的判斷順序是 deny → ask → allow。

## 檢核點

- [ ] `smoke_test.py` 列出 4 個工具並回傳十月統計
- [ ] `claude mcp list` 顯示 orders 已連線；`codex mcp list` 顯示 enabled
- [ ] 查詢問題得到正確答案：十月未出貨 3 筆、49,400 元
- [ ] 修改訂單在兩家都需要核准；未核准時資料庫沒有變動
- [ ] `.mcp.json` 沒有寫死任何本機路徑或金鑰

## 兩家對照

| 面向 | Claude Code | Codex |
| --- | --- | --- |
| 新增 stdio Server | `claude mcp add <名稱> --env K=V -- <指令>` | `codex mcp add <名稱> --env K=V -- <指令>` |
| 設定位置 | 個人：`~/.claude.json`；專案：`.mcp.json` | `~/.codex/config.toml` 的 `[mcp_servers.<名稱>]` |
| 環境變數展開 | `.mcp.json` 支援 `${VAR}`、`${VAR:-預設}` | `env`、`env_vars`、`bearer_token_env_var` |
| 工具名稱 | `mcp__<伺服器>__<工具>` | 命名空間 `mcp__<伺服器>` 下的工具 |
| 限制工具 | 權限規則 allow／ask／deny | `enabled_tools`、`disabled_tools` |
| 核准方式 | 權限規則 | `default_tools_approval_mode`、`tools.<工具>.approval_mode` |
| 查看狀態 | `claude mcp list`、`/mcp` | `codex mcp list`、`/mcp` |

## 延伸題

1. 新增一個 `top_customers(month, n)` 工具，回傳該月金額最高的 n 位客戶；改完後重新連線（Claude Code：`/mcp`；Codex：重開），確認兩家都看得到。
2. 把 `update_order_status` 改成只允許 `pending → shipped`，其他轉換回傳 `ToolError`，觀察 Agent 如何處理錯誤訊息。
3. 把 Server 的 `instructions` 刪掉，比較模型挑工具的準確度。
4. 用 `claude mcp add --transport http` 接一個遠端 MCP Server（例如公司內部的文件服務），比較 stdio 與 http 的設定差異。

## 沒有 API 金鑰時

Part 1 完全不需要金鑰。`claude mcp list`、`codex mcp list`、`codex mcp get orders --json` 也不需要模型回覆，可以確認伺服器能啟動、設定正確。Codex 的工具清單可用模擬伺服器（`../../mock/mock_responses.py`）檢查送出的請求，做法見 `VERIFY.md`。

## 參考

- Claude Code：MCP https://code.claude.com/docs/en/mcp.md
- Claude Code：Permissions https://code.claude.com/docs/en/permissions.md
- Codex：MCP https://learn.chatgpt.com/codex/extend/mcp
- Codex：設定檔參考 https://learn.chatgpt.com/docs/config-file/config-reference
