# 實作 J：看得見的上下文與費用

> 在 VS Code 中操作本實作的方式，見 [`../../vscode.md`](../../vscode.md)。

## 目的

- 讓「上下文用了多少、花了多少錢」隨時看得到，而不是月底看帳單才知道。
- Claude Code：自訂狀態列（statusline），並用 `/usage`、`/context` 與 `--output-format json` 讀出用量；用 `--max-budget-usd` 設預算上限。
- Codex：用 `notify` 腳本記錄每一輪，用 `codex exec --json` 讀出 token 用量。
- 把兩邊的紀錄彙整成一份 CSV，作為團隊追蹤成本的起點。

## 形式

個人實作。

## 前置

| 項目 | 說明 |
| --- | --- |
| 軟體 | Python 3.10+、Claude Code CLI、Codex CLI 0.165 以上；`jq`（沒有也可以，改用 Python 版） |
| 教材檔案 | `claude/statusline.sh`、`claude/statusline.py`、`claude/settings_statusline.json`、`codex/notify.py`、`codex/config_snippet.toml`、`cost_log.py`、`prices.toml`、`run_both.sh`、`samples/` |

## 步驟

### 1. 先用範例資料測腳本（不用模型）

```bash
cd <教材路徑>
bash claude/statusline.sh < samples/claude_status_input.json
python3 claude/statusline.py < samples/claude_status_input.json
python3 codex/notify.py "$(cat samples/codex_notify_event.json)"
python3 cost_log.py samples/claude_p_output.json samples/codex_exec_output.jsonl --codex-model demo
```

狀態列應印出 `[Sonnet 5] ctx 73% | $0.41 | repo | 5h 12%`，`ctx` 會變色：70% 以上黃、85% 以上紅。

### 2. 裝上 Claude Code 狀態列

```bash
cp <教材路徑>/claude/statusline.sh ~/.claude/statusline.sh && chmod +x ~/.claude/statusline.sh
```

把 `claude/settings_statusline.json` 的內容合併進 `~/.claude/settings.json`：

```json
{ "statusLine": { "type": "command", "command": "~/.claude/statusline.sh", "padding": 2 } }
```

Windows 或沒有 jq 時，`command` 改成 `python3 <絕對路徑>/statusline.py`。也可以在互動模式輸入 `/statusline 顯示模型、上下文百分比與費用`，讓 Claude Code 產生腳本，再和教材版本比較。

Claude Code 在狀態改變時執行腳本（約 300 毫秒去抖動），把狀態 JSON 從 stdin 傳進來。常用欄位：

| 欄位 | 意義 |
|---|---|
| `model.display_name` | 目前的模型 |
| `context_window.used_percentage` | 上下文用量百分比 |
| `cost.total_cost_usd` | 本次對話累計費用估算 |
| `workspace.current_dir` | 目前目錄 |
| `rate_limits.five_hour.used_percentage` | 五小時用量限制已使用的百分比 |

### 3. 在互動模式觀察用量

開一個專案，做幾輪對話後依序輸入：

| 指令 | 看什麼 |
|---|---|
| `/context` | 上下文的格狀分布：系統提示、工具定義、記憶檔、對話各占多少 |
| `/usage`（別名 `/cost`、`/stats`） | 本次費用估算、提示快取統計、依 Skill／Subagent／外掛／MCP 拆分的用量 |
| `/compact 只保留目前任務的決定` | 壓縮後回頭看狀態列的 `ctx %` 降了多少 |

### 4. 非互動模式的用量與預算上限

```bash
claude -p "用一句話說明 README.md" --output-format json | jq '{total_cost_usd, num_turns, usage: .usage | {input_tokens, cache_read_input_tokens, cache_creation_input_tokens, output_tokens}}'
claude -p "讀 a.py，再寫一份 50 行的說明文件 NOTES.md" --max-budget-usd 0.01 --allowedTools "Read,Write" --output-format json | jq '{subtype, is_error, total_cost_usd}'
```

第二個指令應回 `"subtype": "error_max_budget_usd"`。預算是在每一輪之間檢查的，所以實際花費會略超過上限（講師實測：上限 0.01 美元，第一輪就花了約 0.06 美元才停）。

`modelUsage` 會依模型拆開，例如 Sonnet 與 Haiku 各花多少。Claude Code 內部的輔助呼叫也會算在裡面。

### 5. Codex：每一輪的通知與紀錄

把 `codex/config_snippet.toml` 的內容加進 `~/.codex/config.toml`，並把路徑改成 `notify.py` 的絕對路徑：

```toml
notify = ["python3", "/絕對路徑/notify.py"]

[tui]
notifications = ["agent-turn-complete", "approval-requested"]
notification_method = "auto"
```

- `notify` 只能設在使用者層級，專案的 `.codex/config.toml` 不能設。
- Codex 每一輪結束時，會把一個 `agent-turn-complete` 事件的 JSON 當成參數交給腳本。教材的 `notify.py` 會把它附加到 `~/.codex/turns.jsonl`，在 macOS 上也會跳出系統通知。
- `tui.notifications` 控制互動介面本身的終端機通知，與 `notify` 腳本無關。

跑一次 `codex exec "列出這個專案的檔案"`，確認 `~/.codex/turns.jsonl` 多了一行。

### 6. Codex：從 `--json` 讀 token 用量

```bash
codex exec --json "用一句話說明 README.md" > run.jsonl
grep '"turn.completed"' run.jsonl | jq '.usage'
```

`usage` 有 `input_tokens`、`cached_input_tokens`、`cache_write_input_tokens`、`output_tokens`、`reasoning_output_tokens`。Codex 只回報 token，不回報金額。用 API 金鑰計費時，費用要自己依單價算；用 ChatGPT 方案登入時，是消耗方案額度。

### 7. 彙整成一份 CSV

```bash
bash <教材路徑>/run_both.sh "用一句話說明 README.md 的內容" ~/labJ/repo
```

腳本把同一個任務分別交給兩個工具，紀錄存在 `logs/`，再用 `cost_log.py` 彙整成 `costs.csv`：

| 欄位 | Claude Code 來源 | Codex 來源 |
|---|---|---|
| `cost_usd` | `total_cost_usd`（直接回報） | 依 `prices.toml` 的單價估算；單價為 0 時留空 |
| `cached_input_tokens` | `cache_read_input_tokens` | `cached_input_tokens` |
| `reasoning_tokens` | `output_tokens_details.thinking_tokens` | `reasoning_output_tokens` |

`prices.toml` 的單價請依官方價目表或你的合約自行填寫，教材不附數字。

## 觀察重點

- 同一個任務，兩邊的「快取讀取 token」占總輸入多少比例？
- 狀態列的 `ctx %` 在載入大型 Skill、連上 MCP 伺服器之後變化多少？
- `--max-budget-usd` 能當成硬上限嗎？要真正卡住預算，還需要什麼？

## 檢核點

- [ ] 狀態列在互動模式顯示模型、上下文百分比與費用
- [ ] 能用 `jq` 從 `claude -p --output-format json` 取出 `total_cost_usd`
- [ ] `--max-budget-usd` 觸發 `error_max_budget_usd`
- [ ] `~/.codex/turns.jsonl` 有 Codex 每一輪的紀錄
- [ ] `costs.csv` 同時包含兩個工具的資料列

## 延伸題

1. 在狀態列加上 git 分支名稱。腳本會頻繁執行，記得讓它跑得快。
2. 改寫 `notify.py`，當最後訊息包含「失敗」或「error」時，額外寫入 `~/.codex/alerts.log`。
3. 把 `cost_log.py` 放進 CI，每次 `claude -p` 或 `codex exec` 跑完就附加一列，累計超過門檻時讓工作失敗。
4. 對照官方建議的降成本做法：`/clear`、`/compact`、選較小的模型、把 CLAUDE.md 的長內容移到 Skill。挑一項實測前後差異。

## 沒有 API 金鑰時

- 步驟 1 全部不需要模型。
- `samples/` 裡的 `claude_p_output.json`、`claude_stream.jsonl` 是講師用真實模型跑出的紀錄（路徑與 ID 已改成示範值）。
- `codex_exec_output.jsonl` 是用 `instructor/mock_codex_usage.py` 模擬的，token 數是假的，只用來練習解析。

## 兩邊比較

| 面向 | Claude Code | Codex |
|---|---|---|
| 即時顯示 | 自訂狀態列（`statusLine`，stdin JSON） | 終端機通知（`tui.notifications`） |
| 每輪結束的外部腳本 | Hook（例如 `Stop`），本實作未使用 | `notify = [...]`，收到 `agent-turn-complete` JSON |
| 互動模式查用量 | `/usage`、`/context` | `/status` |
| 非互動模式用量 | `--output-format json` 的 `total_cost_usd`、`usage`、`modelUsage` | `--json` 的 `turn.completed.usage`（只有 token） |
| 預算上限 | `--max-budget-usd`（每一輪之間檢查） | 無對應參數 |
| 費用 | 直接回報美元 | 依單價自行估算，或計入 ChatGPT 方案額度 |

## 參考

- Claude Code 狀態列：https://code.claude.com/docs/en/statusline
- Claude Code 成本管理：https://code.claude.com/docs/en/costs
- Claude Code 非互動模式：https://code.claude.com/docs/en/headless
- Codex 進階設定（notify、tui.notifications）：https://learn.chatgpt.com/docs/config-file/config-advanced
- Codex 通知：https://learn.chatgpt.com/codex/notifications
- Codex 非互動模式（`--json` 事件）：https://learn.chatgpt.com/codex/non-interactive-mode
