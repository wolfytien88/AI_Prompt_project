# 實作 A：專案記憶與指令檔（CLAUDE.md／AGENTS.md）

> 在 VS Code 中操作本實作的方式，見 [`../../vscode.md`](../../vscode.md)。

## 目的

- 替同一個專案寫兩套指令檔：Claude Code 的 CLAUDE.md 系列與 Codex 的 AGENTS.md 系列。
- 學會分層：全專案規則、只在特定路徑生效的規則、個人設定、暫時覆寫。
- 確認「Agent 實際讀到了什麼」，而不是假設它讀到了。
- 看見兩家的差異：Claude Code 有路徑規則（`.claude/rules/` 的 `paths:`）與 `@` 匯入；Codex 靠每一層資料夾各放一份 AGENTS.md，並有大小上限。

## 形式

個人實作。

## 前置

| 項目 | 指令或說明 |
| --- | --- |
| Claude Code | `claude --version`（本教材以 2.1.312 驗證） |
| Codex CLI | `codex --version`（本教材以 0.165.0 驗證） |
| 練習專案 | `bash make_repo.sh ~/lab/order-portal`：建立虛構的訂單系統並做第一個 commit |
| 參考答案 | `instructor/ref/`（講師用，先自己寫） |

練習專案的結構：

```
order-portal/
├── src/api/orders.py          訂單 API（目前沒有任何輸入驗證）
├── src/web/format.py          畫面格式化
├── services/billing/invoice.py 帳務（目前用 float 算金額）
├── tests/test_orders.py
└── docs/conventions.md        錯誤代碼表（ORD-001、ORD-002、BIL-001）
```

## 步驟

### Part 1：Claude Code

1. **專案共用指令**：在專案根目錄寫 `AGENTS.md`，內容包含專案概要、測試指令（`python3 -m pytest -q`）、「回覆一律使用繁體中文」、「不要新增相依套件」。
   接著寫 `CLAUDE.md`，用匯入把它和慣例文件接進來，再加一條只給 Claude Code 的規則：

   ```markdown
   # order-portal 專案指令（Claude Code）

   @AGENTS.md
   @docs/conventions.md

   ## 只給 Claude Code 的補充
   - 修改程式後先執行 `python3 -m pytest -q`，全部通過才回報完成。
   ```

   這樣兩套工具共用同一份 AGENTS.md，只維護一處。

2. **路徑規則**：建立 `.claude/rules/api.md`，只在 `src/api/` 底下生效：

   ```markdown
   ---
   paths:
     - "src/api/**/*.py"
   ---
   # 訂單 API 規則
   - 每個公開函式都要先驗證輸入：order_id 必須是 1 個大寫英文字母加 3 位數字（例如 A001），
     不符合就 raise ValueError("[ORD-001] 訂單編號格式錯誤")。
   - items 為空時 raise ValueError("[ORD-002] 品項清單為空")。
   - 新增函式要同步在 tests/test_orders.py 加測試。
   ```

3. **子資料夾指令**：在 `services/billing/CLAUDE.md` 寫帳務規則（金額用 `decimal.Decimal`、負數拋 `BIL-001`）。這份檔案平常不載入，Claude 讀到該資料夾的檔案時才載入。

4. **個人設定**：在根目錄寫 `CLAUDE.local.md`（例如「執行測試時加上 `-x`」），並把它加進 `.gitignore`。

5. **確認載入了什麼**：
   - 互動模式輸入 `/memory`，看列出的檔案；輸入 `/context`，看「Memory files」佔多少 Token。
   - 非互動也可以：`claude -p "/context"`。
   - 請 Claude 列出它收到的指令來源（不准讀檔）：

     ```bash
     claude -p "不要讀任何檔案也不要執行工具。只根據你目前已經收到的專案指令與記憶檔，逐一列出來源檔名，每個檔案引用一條規則。"
     ```

     預期看到 CLAUDE.md、AGENTS.md、docs/conventions.md、CLAUDE.local.md；**看不到** `.claude/rules/api.md` 與 `services/billing/CLAUDE.md`。

6. **驗證路徑規則只在該路徑生效**：

   ```bash
   claude -p "讀 src/web/format.py，然後回答：你現在有沒有收到任何只適用於特定路徑的規則？" --allowedTools Read
   claude -p "讀 src/api/orders.py，然後回答：你現在有沒有收到任何只適用於特定路徑的規則？" --allowedTools Read
   claude -p "讀 services/billing/invoice.py，然後回答：讀檔之後你有沒有新收到哪個子資料夾的指令檔？" --allowedTools Read
   ```

7. **讓規則真的發揮作用**：

   ```bash
   claude -p "幫 create_order 加上輸入驗證。" --permission-mode acceptEdits --allowedTools "Bash(python3 -m pytest *)"
   ```

   提示詞裡沒提到錯誤代碼，檢查產出的程式是否用了 `[ORD-001]`、`[ORD-002]`，測試指令是否加了 `-x`。

### Part 2：Codex

8. **根目錄**：Part 1 寫的 `AGENTS.md` 直接沿用，Codex 會自動讀取。

9. **Codex 沒有路徑規則**：把 `.claude/rules/api.md` 的內容（去掉 `paths:` 標頭）放到 `src/api/AGENTS.md`。Codex 從專案根目錄走到目前資料夾，沿路每層最多取一份檔案，越接近目前資料夾的放在越後面。

10. **暫時覆寫**：在 `services/billing/` 放兩份檔案：
    - `AGENTS.md`：帳務規則（同 Part 1 第 3 步）
    - `AGENTS.override.md`：「結帳凍結期間不修改 invoice.py，只允許新增或修改測試」

    同一層有 override 時，Codex **不讀**同層的 AGENTS.md。先只在 override 寫凍結規則，看 Decimal 規則是否消失，再把需要保留的規則補進 override。

11. **大小上限**：建立 `.codex/config.toml`（專案層設定，只在專案被信任時載入）：

    ```toml
    project_doc_max_bytes = 65536   # 預設 32 KiB，超過的部分會被截掉
    ```

12. **確認載入了什麼**：

    ```bash
    codex --cd services/billing --ask-for-approval never "List the instruction sources you loaded."
    codex --cd src/api --ask-for-approval never "List the instruction sources you loaded."
    ```

    預期順序：全域（`~/.codex/AGENTS.md`，如果有）→ 根目錄 AGENTS.md → 該資料夾的檔案。在 `src/api` 看不到帳務規則，在 `services/billing` 看不到訂單 API 規則。

13. **截斷實驗**：把 `project_doc_max_bytes` 暫時改成 `200`，再跑一次第 12 步，觀察哪些規則不見了，再改回來。

## 觀察重點

- Claude Code 的路徑規則與子資料夾 CLAUDE.md 都是「讀到相關檔案才載入」，一開始的 Context 不含它們。
- Codex 每次執行都重新組出指令鏈；同一層 override 會取代 AGENTS.md，而不是疊加。
- `project_doc_max_bytes` 是所有檔案合併後的上限：根目錄寫太長，下層的規則會先被截掉。
- 指令檔是建議，不是強制。要真的擋下某個動作，用單元四的 Hook 或權限規則。

## 檢核點

- [ ] `claude -p` 列出的來源不含 `.claude/rules/api.md`，讀了 `src/api/` 的檔案後才出現
- [ ] Claude 產出的驗證程式使用 `[ORD-001]`、`[ORD-002]`，測試全部通過
- [ ] Codex 在 `services/billing` 與 `src/api` 載入的規則不同
- [ ] 能說明為什麼 override 存在時 Decimal 規則會消失
- [ ] `CLAUDE.local.md` 已加進 `.gitignore`

## 兩家對照

| 面向 | Claude Code | Codex |
| --- | --- | --- |
| 專案檔名 | `CLAUDE.md`、`.claude/CLAUDE.md`；沒有 CLAUDE.md 時讀 AGENTS.md | `AGENTS.md`（另可設定 `project_doc_fallback_filenames`） |
| 全域 | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md`（或 `AGENTS.override.md`） |
| 個人、不進版控 | `CLAUDE.local.md` | 無專用檔名，可用全域檔 |
| 只在特定路徑生效 | `.claude/rules/*.md` 的 `paths:` | 在該資料夾放 AGENTS.md |
| 匯入其他檔案 | `@path`，最多 4 層 | 無；直接寫在 AGENTS.md 或叫 Agent 去讀 |
| 暫時覆寫 | 無專用機制 | `AGENTS.override.md` 取代同層 AGENTS.md |
| 大小限制 | 無硬上限，建議每檔 200 行以內 | `project_doc_max_bytes`，預設 32 KiB |
| 確認載入內容 | `/memory`、`/context` | 請 Codex 列出指令來源 |

## 延伸題

1. 執行 `/init`（兩家都有），比較自動產生的 CLAUDE.md 與 AGENTS.md 和你手寫的差在哪。
2. 在 `~/.codex/config.toml` 設 `project_doc_fallback_filenames = ["TEAM_GUIDE.md"]`，把某層的 AGENTS.md 改名為 TEAM_GUIDE.md，確認 Codex 仍讀得到。
3. 用 `/doctor prompt-audit`（Claude Code）檢查你的指令檔，看它建議刪掉哪些內容。
4. 想一想：哪些規則應該從指令檔搬到 Hook 或權限設定？（單元四會實作）

## 沒有 API 金鑰時

Part 1 的第 5 步 `/memory`、`/context` 不需要模型回覆就能看到載入的檔案。Codex 部分可用講師提供的模擬伺服器（`../../mock/mock_responses.py`），再檢查送出的請求內容：Codex 會把整串指令放在一則以 `# AGENTS.md instructions for <資料夾>` 開頭的訊息裡，用文字搜尋就能確認哪些規則被送出。做法見 `VERIFY.md`。

## 參考

- Claude Code：Memory https://code.claude.com/docs/en/memory.md
- Codex：AGENTS.md https://learn.chatgpt.com/codex/agent-configuration/agents-md
- Codex：設定檔 https://learn.chatgpt.com/docs/config-file/config-reference
