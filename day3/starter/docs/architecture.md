# 架構總覽

待辦清單 App，只使用 Python 標準函式庫，不需要安裝套件。

## 分層

依賴方向只能由左往右：

```
types → repo → service → ui
```

| 層 | 路徑 | 職責 | 可以依賴 |
| --- | --- | --- | --- |
| types | src/types/ | 資料型別、純函式驗證 | 無 |
| repo | src/repo/ | 讀寫 data/todos.json | types |
| service | src/service/ | 業務邏輯（新增、完成、篩選…） | types、repo |
| ui | src/ui/ | HTTP API 與網頁 | 以上全部 |

service 層不可 import ui 層，由 `make lint`（tools/check_layers.py）檢查。

## API

| 方法 | 路徑 | 說明 |
| --- | --- | --- |
| GET | /api/health | 健康檢查，回傳 {"status": "ok"} |
| GET | /api/todos | 回傳全部待辦（JSON 陣列） |

其他 API 依 spec.md 與 feature_list.json 逐項新增，新增後更新此表。

## 資料

存在 `data/todos.json`，可用環境變數 `TODO_DATA` 改路徑；伺服器埠號用 `PORT`（預設 5173）。
