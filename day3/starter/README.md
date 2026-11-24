# 待辦清單 App｜起始專案

實作 5、實作 6 共用的起始專案。只用 Python 3.10 以上的標準函式庫，不需安裝套件。

目前只完成三件事：健康檢查 API、列出待辦的 API、會顯示清單的首頁。其餘功能由 Coding Agent 依 `feature_list.json` 逐項完成。

```bash
make test                          # 單元測試
python3 -m src.ui.server           # 手動啟動（Initializer 會寫 init.sh 取代這一步）
python3 tools/smoke_test.py        # 伺服器啟動後的基本端對端檢查
python3 tools/feature_status.py    # 檢查功能清單（Initializer 之後才有）
```

架構與分層規則見 `docs/architecture.md`。
