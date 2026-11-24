# 實作 G 驗證紀錄（2026-10-29／30，claude-agent-sdk 0.2.165、@openai/codex-sdk 0.165.0、Codex CLI 0.165.0）

## 已實際執行
| 項目 | 結果 |
| --- | --- |
| `buggy_invoice` 修正前 | 9 個測試，`FAILED (failures=4)` |
| 參考解答 `instructor/buggy_invoice_solution/calc.py` | 9 個測試 `OK` |
| `fix_agent_claude.py`（真實模型） | 兩次執行皆 `subtype=success`，6–10 回合、約 US$0.08–0.33；測試全部通過，`tests/` 未變動。其中一次模型先嘗試以 `python3 - <<EOF` 改檔，被 `allowed_tools` 規則拒絕（`permission_denials` 有 1 筆）後改用 Edit |
| `--resume <session ID>` + `output_format` | `structured_output` 回傳 `tests_passed: true` 與 3 個 bug 的 function／cause／fix |
| `fix_agent_codex.mjs`（假伺服器） | `instructor/verify_codex_sdk_mock.sh`：事件 thread.started → command_execution × 3 → agent_message → turn.completed；workspace-write 沙箱內成功改檔；`resumeThread` 的請求帶入前一輪歷史（輸入項目 10→12）且 `text.format` 為 json_schema；最後 `OK` |

## 注意
- 本驗證環境以環境變數 `CLAUDE_CODE_SESSION_ID` 固定了 session ID，所以印出的 ID 與外層工作階段相同；學員電腦上每次執行會得到不同的 ID。驗證時以 `env -u CLAUDE_CODE_SESSION_ID` 執行。
- `output_format` 的寫法（`{"type": "json_schema", "schema": ...}`）取自已安裝的 SDK 原始碼與型別定義。

## 尚未驗證
- 真實 GPT 模型修 bug 的表現（本環境無 OpenAI 金鑰；假伺服器是直接套用參考解答）
- 第 7 步兩個權限實驗的實際輸出
- 延伸題的 Codex Python SDK（`openai-codex`）範例：已確認套件可安裝、`Codex.thread_start` 存在（預設 `approval_mode=auto_review`），但未執行
