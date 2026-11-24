# AI 提示工程師｜範例程式與實作教材

四個單元的實作說明、測試資料、Prompt 範本與程式。每個資料夾都有自己的 README 或實作說明（labN.md）。
所有公司、統編、電話、金鑰皆為虛構。

## 單元與實作

| 資料夾 | 單元 | 實作說明 | 主要檔案 |
|---|---|---|---|
| day1 | Prompt 與 Context Engineering | `lab1.md` Prompt 重構、`lab2.md` 兩家同題 Eval、`labA_memory/` 專案記憶與指令檔 | 測試資料 `data/`、三任務 × 三版 Prompt `prompts/`、測試集 `cases/`、`eval.py`、`compare.py`、`llm_judge.py` |
| day2 | 工具、Agent Loop 與 Harness 設計模式 | `lab3.md` 最小 Agent、`lab4.md` 一個 Skill 兩套 Harness、`ablation.md` 拆除實驗、`labB_skills/` Skills 與自訂指令、`labC_subagents/` Subagent 平行審查、`labD_mcp/` 用 MCP 接資料 | `buggy_shop/` 練習專案、`mini_agent*.py`、`edit_tool.py`、`skills/weekly-report/`、`ablation/` |
| day3 | 長週期 Agent 與 Harness Engineering | `lab5.md` 跨 Session 長任務、`lab6.md` Evaluator＋機械化約束、`labE_plan_rewind/` Plan mode 與 Rewind、`labF_ci/` 放進 CI 自動化、`labG_sdk/` 用 SDK 寫自己的 Agent | `spec.md`、`prompts/`（Planner／Initializer／Coding Agent／Evaluator）、`starter/` 起始專案、`harness/`、`layer_demo/`、`rubric.md` |
| day4 | 安全邊界、腦手解耦與專題實作 | `lab7.md` 一支 Hook 兩邊都擋、`labH_permissions/` 權限、沙箱與自動審查、`labI_plugins/` 打包成 Plugin、`labJ_observability/` 可觀測性與成本、`capstone.md` 專題實作 | `guard.py`、兩家設定檔、`redteam/`、`traps.md`、`harness_checklist.md`、`rubric.md`、講師驗證腳本 |
| vscode.md | 在 VS Code 中進行實作 | — | Model／Harness／Host、Session Target、各實作的操作方式、MCP 與權限設定 |
| mock | 離線測試工具 | — | `mock_api.py`（模擬兩家 API）、`mock_responses.py`（模擬 Codex 使用的 Responses API 串流） |

實作 A–J 是 Claude Code 與 Codex 的工具實作，每個資料夾有 `labX.md`（步驟）、`VERIFY.md`（驗證紀錄）與 `instructor/`（參考解答）。

`day2/instructor/` 與每個實作資料夾裡的 `instructor/` 是講師解答，發給學員前請移除。

## 環境
- Python 3.10 以上：`pip install anthropic openai pytest`
- 金鑰只放環境變數：`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`
- Claude Code CLI（2.1.312 以上）、Codex CLI（0.165 以上）；Playwright MCP（Evaluator 實作使用）
- VS Code 1.143 以上（建議）：編輯、內建終端機與 Agent 操作集中在同一個視窗，使用方式見 `vscode.md`
- 模型名稱可用環境變數覆寫：`CLAUDE_MODEL`、`OPENAI_MODEL`

## 沒有 API Key 時
```bash
python3 mock/mock_api.py 8899 &
export ANTHROPIC_BASE_URL=http://127.0.0.1:8899 ANTHROPIC_API_KEY=x
export OPENAI_BASE_URL=http://127.0.0.1:8899/v1 OPENAI_API_KEY=x
```
模擬伺服器只把輸入原樣回傳，用來確認程式流程，分數沒有意義。

## 驗證狀態

### 工具實作 A–J（2026-10-30）
- 以 Claude Code 2.1.312（真實模型）與 Codex CLI 0.165.0 實際執行；Codex 需要模型的步驟用模擬 Responses API 驗證流程。
- 詳細結果與未驗證項目（真實 GPT 行為、互動畫面、GitHub Actions 實際執行、macOS 沙箱）見各資料夾的 `VERIFY.md`。
- 實作 H 在 Linux 需要 `bubblewrap` 與 `socat`；實作 D 需要 `pip install mcp`（2.x）。

### 實作 1–7（2026-10-24）
- 所有程式與腳本都已實際執行。
- 用真實模型（Claude Code）跑過：buggy_shop 修復、weekly-report Skill、Initializer／Coding Agent／Evaluator Prompt、Hook 與 deny 規則測試。
- 用模擬伺服器驗證：兩家 Python SDK 範例、Codex Hook 與沙箱（模型回覆為模擬，Hook 與沙箱為 Codex 實際執行）。
- 尚未驗證：真實 GPT 模型的行為、Python SDK 對真實 API 的呼叫。開課前請用主辦單位的金鑰補跑。
