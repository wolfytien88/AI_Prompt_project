# 實作 J 驗證紀錄

環境：Linux 容器、Claude Code 2.1.312（真實模型）、Codex CLI 0.165.0（模擬模型）、jq 1.7、Python 3。

## 已實際執行（`instructor/verify.sh`）

| 項目 | 結果 |
|---|---|
| `statusline.sh`（jq 版）與 `statusline.py` 讀範例 JSON，包含欄位缺漏的情況 | 通過 |
| `notify.py` 直接以範例事件呼叫 | 通過，寫入 jsonl 並印出摘要 |
| `notify.py` 由 `codex exec` 呼叫 | 通過，每一輪一筆，事件欄位與文件一致 |
| `[tui] notifications` 設定載入 | 通過 |
| `codex exec --json` 的 `turn.completed.usage` | 通過（token 數為模擬值） |
| `claude -p --output-format json` 欄位 | 通過（真實模型） |
| `--max-budget-usd 0.01` | 回 `error_max_budget_usd`（真實模型，每次約 0.06 美元） |
| `cost_log.py`：Claude json、Claude stream-json、Codex jsonl 混合輸入；單價為 0 與非 0 兩種情況 | 通過；估算值已手算核對（0.0048 美元） |
| `run_both.sh` | 通過（Claude 真實、Codex 模擬） |

## 尚未驗證

- 狀態列在互動 TUI 中的實際顯示：容器內無法開 TUI，只用範例 stdin JSON 測腳本。範例 JSON 的欄位取自官方文件，不是從真實 Claude Code 擷取。
- `/usage`、`/context`、`/compact` 的畫面（只能在互動模式操作）。
- macOS 的 `osascript` 系統通知。
- 真實 OpenAI 模型的 token 數與快取比例。Codex 的 `samples/codex_exec_output.jsonl` 是模擬資料。
- `prices.toml` 不附任何真實單價，需講師依官方價目表填寫。
