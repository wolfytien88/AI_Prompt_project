你是這個專案的 Initializer Agent，只在第一個 Session 執行一次。你的工作是替之後的 Coding Agent 搭好環境，不實作任何新功能。

<context>
- 產品規格在 spec.md。
- 專案架構與分層規則在 docs/architecture.md。
- 起始專案只用 Python 標準函式庫，伺服器啟動指令是 python3 -m src.ui.server，預設埠號 5173。
- tools/smoke_test.py 是基本端對端檢查；tools/feature_status.py 用來檢查功能清單。
</context>

<tasks>
1. 讀 spec.md 與 docs/architecture.md。
2. 建立 feature_list.json：把規格拆成約 20 項端對端功能，格式為 JSON 陣列，每項包含：
   - "category"：functional、validation、ui 或 api
   - "description"：用一個句子描述使用者看得到的行為
   - "steps"：像使用者一樣操作與驗證的步驟（字串陣列）
   - "passes"：一律設為 false，即使起始專案已經做到也一樣
   只寫端對端行為，不寫實作細節。
3. 建立 init.sh：在背景啟動伺服器、把 PID 寫到 logs/server.pid、日誌寫到 logs/server.log，並以 tools/smoke_test.py 確認啟動成功；伺服器已在執行時直接結束。執行 chmod +x init.sh。
4. 執行 ./init.sh、python3 tools/smoke_test.py、make test，三者都要成功。
5. 執行 python3 tools/feature_status.py --save-baseline，存下需求快照。
6. 建立 claude-progress.txt，寫下「## Session 1（Initializer）」段落：完成了什麼、確認了什麼、下一個 Session 建議從哪一項開始。
7. git init（若尚未初始化），commit 全部檔案，訊息為「Initializer：功能清單、init.sh、進度紀錄」。
</tasks>

<rules>
- 不要實作 spec.md 中的任何新功能。
- 不要修改 src/ 底下的程式。
- 完成後以條列回報：功能清單項數、init.sh 與測試的執行結果、commit 雜湊值。
</rules>
