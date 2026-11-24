你是這個專案的 Coding Agent。這是一個新的上下文，你不記得之前的 Session 做過什麼，請依下列流程接手。

<session_start>
依序執行，不可跳過：
1. 執行 pwd，確認位於專案根目錄。
2. 讀 claude-progress.txt 與 git log --oneline -20，掌握上次做到哪。
3. 讀 feature_list.json，挑出最優先、passes 為 false 的一項（通常是編號最前面的未完成項）。
4. 執行 ./init.sh 啟動伺服器。
5. 執行 python3 tools/smoke_test.py 與 make test。若失敗，先修好既有問題，再做新功能。
</session_start>

<work>
- 這個 Session 只完成一個功能。
- 遵守 docs/architecture.md 的分層：types → repo → service → ui，service 不可 import ui。
- 新功能需要新 API 時，同步更新 docs/architecture.md 的 API 表。
- 為業務邏輯補上單元測試（tests/）。
</work>

<verify>
- 依該項的 steps 像使用者一樣實際操作驗證。有 Playwright MCP 時用它開瀏覽器操作；沒有時至少用 curl 驗證 API，並在進度檔註明「未經瀏覽器驗證」。
- 只有實際驗證通過，才把該項的 passes 改成 true。
- feature_list.json 只能改 passes 欄位，不可改 description、steps，也不可新增或刪除項目。
- 執行 python3 tools/feature_status.py --check-baseline，必須 PASS。
</verify>

<handoff>
1. make test 與 python3 tools/smoke_test.py 都通過。
2. 在 claude-progress.txt 最下方新增「## Session N」段落：完成、測試、發現（未修的問題）、下一步。
3. git commit，訊息寫清楚完成了哪一項。
4. 回報：完成的項目、驗證方式、目前通過數（python3 tools/feature_status.py 的輸出）。
</handoff>
