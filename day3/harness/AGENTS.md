# AGENTS.md（目錄，不是百科）

- 產品規格：spec.md
- 架構總覽：docs/architecture.md
- 分層規則：types → repo → service → ui，只能由左往右依賴（make lint 會檢查）
- 進行中的計畫：docs/plans/active/
- 啟動：./init.sh；停止：make stop；測試：make test；基本端對端檢查：make smoke
- 進度紀錄：claude-progress.txt（每個 Session 開始先讀，結束前新增一段）
- 功能清單：feature_list.json（只能改 passes 欄位；改完執行 python3 tools/feature_status.py --check-baseline）
- 完成定義：feature_list.json 對應項目 passes=true，且 make lint、make test 全過
