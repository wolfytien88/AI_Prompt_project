新增功能：POST /api/todos 建立待辦。

- 請求：JSON `{"title": "..."}`
- 標題去掉頭尾空白後須為 1–100 字；不符時回 400 與 `{"error": "原因"}`
- 成功回 201 與新項目（含 id、title、done=false）
- 要遵守 docs/architecture.md 的分層規則（ui → service → repo → types）
- 補上單元測試，`make test` 全部通過
