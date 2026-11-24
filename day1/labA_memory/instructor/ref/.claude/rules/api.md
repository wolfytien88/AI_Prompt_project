---
paths:
  - "src/api/**/*.py"
---
# 訂單 API 規則
- 每個公開函式都要先驗證輸入：order_id 必須是 1 個大寫英文字母加 3 位數字（例如 A001），不符合就 `raise ValueError("[ORD-001] 訂單編號格式錯誤")`。
- items 為空時 `raise ValueError("[ORD-002] 品項清單為空")`。
- 新增函式要同步在 `tests/test_orders.py` 加測試。
