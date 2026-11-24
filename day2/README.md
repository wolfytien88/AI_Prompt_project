# 工具、Agent Loop 與 Harness 設計模式：範例與實作教材

| 檔案／資料夾 | 用途 | 對應投影片 |
| --- | --- | --- |
| `lab3.md` | 實作 3：從零寫一個只有 bash 工具的 Agent | 實作 3、mini_agent.py |
| `lab4.md` | 實作 4：一個 Skill 兩套 Harness、edit 工具 | 實作 4、SKILL.md、edit 工具 |
| `ablation.md` | 拆除實驗步驟與判讀 | 拆除實驗、紀錄表 |
| `mini_agent.py` | 30 行 Agent Loop（Claude） | mini_agent.py 1/2、2/2 |
| `mini_agent_openai.py` | 同上，OpenAI Responses API 版 | mini_agent_openai.py 1/2、2/2 |
| `mini_agent_logged.py` | 實作 3 參考答案：印出指令、記錄輪數與 Token | 實作 3 |
| `edit_tool.py`、`test_edit_tool.py` | 含過期檢查的 edit 工具與 6 個測試 | edit 工具 |
| `mini_agent_edit.py`、`test_mini_agent_edit.py` | 實作 4 參考答案：Agent 加上 read_file／edit_file，與分派測試 | 實作 4 |
| `skills/weekly-report/SKILL.md` | 兩套 Harness 共用的 Skill | SKILL.md |
| `make_sample_repo.sh` | 建立 8 筆 commit 的範例 Repo，並放好兩份 SKILL.md | 實作 4 |
| `buggy_shop/` | 實作 3 練習專案：3 個 bug、7 個測試（修正前 5 failed, 2 passed） | 實作 3 |
| `ablation/` | 拆除實驗執行器 `ablate.py`、System Prompt 變體、Few-shot、範例測試集、紀錄表範本 | 拆除實驗 |
| `instructor/buggy_shop_solution/` | 講師解答與說明（不要發給學員） | — |

沒有 API 金鑰時，用課程範例的 `mock/mock_api.py` 驗證程式流程：

```bash
python3 mock/mock_api.py 8899 &
export ANTHROPIC_BASE_URL=http://127.0.0.1:8899 ANTHROPIC_API_KEY=x
export OPENAI_BASE_URL=http://127.0.0.1:8899/v1 OPENAI_API_KEY=x
```
