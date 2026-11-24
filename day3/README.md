# 長週期 Agent 與 Harness Engineering｜範例與實作教材

只使用 Python 3.10 以上的標準函式庫，不需安裝套件；Playwright MCP 需要 Node.js 18 以上。

| 路徑 | 內容 |
| --- | --- |
| `lab5.md` | 實作 5：跨 Session 的長任務 |
| `lab6.md` | 實作 6：Evaluator ＋ 機械化約束 |
| `spec.md` | 待辦清單 App 產品規格（Planner 輸出範例） |
| `rubric.md` | 評分標準：功能完整度（門檻 4）、產品深度（3）、視覺設計（3）、程式品質（3） |
| `prompts/planner.md` | Planner 指令：把 1–4 句需求擴寫成規格 |
| `prompts/initializer.md` | Initializer 指令：功能清單、init.sh、進度檔、第一個 commit |
| `prompts/coding_agent.md` | Coding Agent 指令：開場五步驟、一次一項、驗證後才改 passes |
| `prompts/evaluator.md` | Evaluator 指令：Playwright MCP 實測、硬性門檻、缺陷附重現步驟 |
| `examples/feature_list.json` | 功能清單參考答案（22 項，passes 全為 false） |
| `examples/claude-progress.txt` | 進度檔範例 |
| `examples/init.sh` | init.sh 範例，可直接在起始專案中使用 |
| `starter/` | 待辦清單 App 起始專案 |
| `harness/` | 實作 6 要加進專案的 AGENTS.md、CLAUDE.md、Makefile、tools/check_layers.py |
| `layer_demo/` | 分層檢查示範，含一個故意違規的檔案 |
| `check_layers.py` | 分層檢查腳本（與 harness/tools/、layer_demo/tools/ 中的相同） |

起始專案的工具：

| 指令 | 用途 |
| --- | --- |
| `make test` | 單元測試 |
| `./init.sh` | 背景啟動伺服器（http://localhost:5173），重複執行不會重開 |
| `make smoke` | 基本端對端檢查 |
| `make stop` | 停止伺服器 |
| `python3 tools/feature_status.py --save-baseline` | Initializer 後存下需求快照 |
| `python3 tools/feature_status.py --check-baseline` | 檢查 Agent 是否只改了 passes 欄位 |
