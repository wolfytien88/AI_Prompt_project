# 實作 J 參考結果（講師實測）

測試環境：Linux 容器、Claude Code 2.1.312（真實模型）、Codex CLI 0.165.0（模擬模型 `mock_codex_usage.py`）。

| 項目 | 結果 |
|---|---|
| `statusline.sh` 與 `statusline.py` 讀範例 JSON | 兩者都印出 `[Sonnet 5] ctx 73% \| $0.41 \| repo \| 5h 12%`，73% 顯示黃色 |
| 欄位缺漏（`{}`） | Python 版印出 `[?] ctx 0% \| $0.00 \|`，不會當掉 |
| `claude -p --output-format json` | 有 `total_cost_usd`、`num_turns`、`usage`（含 `cache_read_input_tokens`、`cache_creation_input_tokens`）、`modelUsage`（依模型拆分，可能同時出現 Sonnet 與 Haiku） |
| `--max-budget-usd 0.01` | `subtype: error_max_budget_usd`、`terminal_reason: budget_exhausted`。實際花費約 0.056–0.059 美元，因為預算在每一輪之間才檢查 |
| `codex exec --json` | `turn.completed.usage` 欄位：`input_tokens`、`cached_input_tokens`、`cache_write_input_tokens`、`output_tokens`、`reasoning_output_tokens`。同一輪有多次模型請求時會累加 |
| `notify` | `codex exec` 每一輪都會呼叫一次，事件 `type` 為 `agent-turn-complete`，含 `thread-id`、`turn-id`、`cwd`、`input-messages`、`last-assistant-message` |
| `[tui] notifications`、`notification_method` | 設定可被 0.165 載入，不會報錯 |
| `run_both.sh` | `costs.csv` 有兩列：Claude 的費用是回報值；Codex 在單價為 0 時只列 token |

## 討論題參考答案

- **`--max-budget-usd` 不是硬上限**：超出後要等這一輪結束才停。要卡住預算，要搭配：
  - 組織層級的花費上限
  - `--max-turns`
  - 選較小的模型
  - CI 中累計費用的門檻檢查（延伸題 3）
- **快取比例**：講師實測一次 `claude -p`，約 3.2 萬個快取讀取 token、1.4 萬個快取寫入 token，而一般輸入只有個位數。系統提示與工具定義幾乎都走快取，這就是 Prompt Caching 的效果（呼應單元一的 Caching）。
