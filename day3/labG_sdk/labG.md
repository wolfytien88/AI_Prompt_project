# 實作 G：用 SDK 寫自己的 Agent

> 在 VS Code 中操作本實作的方式，見 [`../../vscode.md`](../../vscode.md)。

## 目的

單元二用三十行程式自己寫過 Agent Loop。這次改用兩家的 SDK：Agent Loop、工具、沙箱與權限都由 SDK 底下的 Claude Code／Codex 提供，你只寫「任務、可以用哪些工具、結果怎麼處理」。完成同一個修 bug 任務後，比較兩家 SDK 的事件、權限設定、Session 接續與結構化輸出。

## 形式

個人實作。

## 前置

- Python 3.10 以上、Node 18 以上
- Claude Agent SDK：`pip install claude-agent-sdk`（套件內含 CLI），環境變數 `ANTHROPIC_API_KEY`。SDK 不會自動讀 `.env`
- Codex SDK：`npm install @openai/codex-sdk`，已登入的 Codex（`codex login`）或環境變數 `CODEX_API_KEY`。SDK 只能在伺服器端執行

```bash
export G=/你的路徑/範例程式/day3/labG_sdk
```

## 會用到的檔案

| 檔案 | 用途 |
| --- | --- |
| `buggy_invoice/` | 練習專案：發票金額計算，3 個 bug、4 個測試失敗 |
| `fix_agent_claude.py` | Claude Agent SDK 版的修 bug Agent |
| `fix_agent_codex.mjs` | Codex SDK 版的修 bug Agent |
| `instructor/verify_codex_sdk_mock.sh` | 講師用：不需金鑰驗證 Codex SDK 流程 |

## 步驟

### 1. 準備兩份專案

```bash
cp -r "$G/buggy_invoice" ~/labG-claude
cp -r "$G/buggy_invoice" ~/labG-codex
cd ~/labG-claude && python3 -m unittest discover -s tests
```

應看到 `FAILED (failures=4)`。

### 2. 讀 Claude 版的設定

`fix_agent_claude.py` 的核心：

```python
options = ClaudeAgentOptions(
    cwd=project,
    allowed_tools=["Read", "Glob", "Grep", "Edit", "Bash(python3 -m unittest *)"],
    disallowed_tools=["Write", "WebFetch", "WebSearch"],
    permission_mode="acceptEdits",
    max_turns=20,
    max_budget_usd=1.0,
)
async for msg in query(prompt=TASK, options=options):
    show(msg)
```

`allowed_tools` 用的是和 `settings.json` 相同的權限規則語法；`Bash(python3 -m unittest *)` 只核准跑測試這一種指令。

### 3. 執行 Claude 版

```bash
python3 "$G/fix_agent_claude.py" ~/labG-claude
```

輸出每一行對應 Agent Loop 的一步：`[tool]` 是模型要求的工具呼叫，`[result]` 是工具結果送回模型，最後的 `[done]` 印出回合數、成本與 session ID。

如果出現 `[deny]`：模型嘗試了規則以外的指令（例如用 `python3 - <<EOF` 直接改檔），SDK 依權限設定拒絕，模型會改用 `Edit` 工具。這是權限規則在發揮作用，不是錯誤。

### 4. 讀 Codex 版的設定並執行

`fix_agent_codex.mjs` 的核心：

```js
const codex = new Codex();
const thread = codex.startThread({
  workingDirectory: path.resolve(project),
  skipGitRepoCheck: true,
  sandboxMode: "workspace-write",
  approvalPolicy: "never",
});
const { events } = await thread.runStreamed(TASK);
for await (const ev of events) show(ev);
```

```bash
cd "$G" && npm install @openai/codex-sdk
node "$G/fix_agent_codex.mjs" ~/labG-codex
```

Codex 的事件是 `thread.started`、`item.started`／`item.completed`（`command_execution`、`file_change`、`agent_message`）、`turn.completed`（附 token 用量）。

### 5. 驗證結果

```bash
(cd ~/labG-claude && python3 -m unittest discover -s tests)
(cd ~/labG-codex  && python3 -m unittest discover -s tests)
git diff --no-index "$G/buggy_invoice/tests" ~/labG-claude/tests
```

兩份都應 `OK`，測試資料夾沒有變動。

### 6. 接續 Session，取得結構化摘要

把第 3、4 步最後印出的 ID 帶回去：

```bash
python3 "$G/fix_agent_claude.py" ~/labG-claude --resume <session ID>
node "$G/fix_agent_codex.mjs" ~/labG-codex --resume <thread ID>
```

兩邊都會輸出同一份 Schema 的 JSON：`tests_passed` 與每個 bug 的 `function`、`cause`、`fix`。Agent 沒有重新讀檔就知道剛才改了什麼，因為接續的是同一段對話。

| 項目 | Claude Agent SDK | Codex SDK |
| --- | --- | --- |
| 接續方式 | `ClaudeAgentOptions(resume=session_id)` | `codex.resumeThread(threadId)` |
| 結構化輸出 | `output_format={"type": "json_schema", "schema": ...}` → `ResultMessage.structured_output` | `run(input, { outputSchema })` → `finalResponse`（JSON 字串） |
| Session 存放處 | Claude Code 的 Session 記錄 | `~/.codex/sessions` |

### 7. 改權限，觀察差異

各做一項，記錄結果：

- Claude：把 `allowed_tools` 裡的 `Bash(python3 -m unittest *)` 拿掉再跑。Agent 還能確認測試通過嗎？`[deny]` 出現幾次？
- Codex：把 `sandboxMode` 改成 `"read-only"` 再跑。`file_change` 事件還會出現嗎？最終回覆怎麼說？

## 比較

| 項目 | Claude Agent SDK | Codex SDK |
| --- | --- | --- |
| 語言 | Python、TypeScript | TypeScript、Python（`openai-codex`） |
| 底層 | 內含的 Claude Code CLI | Codex CLI（Python 版透過 app-server） |
| 工具權限 | `allowed_tools`／`disallowed_tools` 規則、`permission_mode` | `sandboxMode`＋`approvalPolicy` |
| 防止失控 | `max_turns`、`max_budget_usd` | 沙箱範圍；`signal`（AbortSignal）中斷 |
| 成本資訊 | `ResultMessage.total_cost_usd`（美元） | `turn.completed.usage`（token 數） |
| 事件粒度 | 訊息：AssistantMessage、UserMessage、ResultMessage | 項目：command_execution、file_change、agent_message |

## 觀察重點

- 你寫的程式碼裡沒有任何 while 迴圈，Agent Loop 在哪裡？
- 兩家各用了幾次工具、幾個回合？Claude 的成本與 Codex 的 token 數怎麼換算比較？
- `[deny]` 與沙箱拒絕，對模型來說看起來有什麼不同？
- 第 6 步的摘要中，兩家對同一個 bug 的原因描述一致嗎？

## 檢核點

- [ ] 兩份專案的測試都通過，測試檔沒有變動
- [ ] 能指出 SDK 輸出中對應「呼叫模型、執行工具、送回結果」的事件
- [ ] 接續 Session 後取得合法的 JSON 摘要
- [ ] 第 7 步的兩個實驗都有記錄結果

## 延伸題

1. 用 Codex 的 Python SDK 改寫：
   ```python
   from openai_codex import Codex, Sandbox
   with Codex() as codex:
       thread = codex.thread_start(cwd="/home/you/labG-codex", sandbox=Sandbox.workspace_write)
       print(thread.run("執行測試並修正 invoice/calc.py").final_response)
   ```
2. 在 Claude 版加入 `hooks`：用 PreToolUse 擋下所有修改 `tests/` 的 `Edit`，讓「不能改測試」從 Prompt 規則變成程式強制。
3. 把 `fix_agent_claude.py` 包成一個小服務：收到 CI 失敗的 webhook 就修 bug 並開 PR。哪些權限要再收緊？

## 沒有 API 金鑰時

Codex SDK 的流程可用模擬伺服器驗證。假伺服器依序要求 Codex 執行「跑測試 → 套用參考解答 → 再跑測試」，Codex 的執行、沙箱、事件串流與接續 Thread 都是真的：

```bash
"$G/instructor/verify_codex_sdk_mock.sh"
```

## 參考

- Claude Agent SDK：https://code.claude.com/docs/en/agent-sdk/quickstart
- Claude Code 權限規則：https://code.claude.com/docs/en/permissions
- Codex SDK：https://learn.chatgpt.com/codex/codex-sdk
- Codex 沙箱與核准：https://learn.chatgpt.com/docs/agent-approvals-security
