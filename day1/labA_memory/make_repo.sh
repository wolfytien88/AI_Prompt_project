#!/bin/bash
# 建立實作 A 的練習專案 order-portal（虛構的訂單系統）。
# 用法：bash make_repo.sh [目的資料夾，預設 ./order-portal]
set -e
DEST="${1:-./order-portal}"
[ -e "$DEST" ] && { echo "$DEST 已存在，請換一個位置或先刪除"; exit 1; }
mkdir -p "$DEST"/{src/api,src/web,services/billing,tests,docs}
cd "$DEST"

cat > README.md <<'MD'
# order-portal

虛構的訂單入口網站，用來練習 Agent 的專案記憶與指令檔。

- `src/api/`：訂單 API（建立、查詢）
- `src/web/`：畫面用的格式化函式
- `services/billing/`：帳務服務（金額計算）
- `tests/`：pytest 測試

執行測試：`python3 -m pytest -q`
MD

cat > src/__init__.py <<'PY'
PY
cat > src/api/__init__.py <<'PY'
PY
cat > src/api/orders.py <<'PY'
"""訂單 API：建立與查詢訂單（資料只存在記憶體）。"""
_ORDERS = {}


def create_order(order_id, customer, items):
    _ORDERS[order_id] = {"customer": customer, "items": items}
    return _ORDERS[order_id]


def get_order(order_id):
    return _ORDERS.get(order_id)
PY

cat > src/web/__init__.py <<'PY'
PY
cat > src/web/format.py <<'PY'
"""畫面顯示用的格式化函式。"""


def order_title(order_id, customer):
    return f"#{order_id} {customer}"
PY

cat > services/__init__.py <<'PY'
PY
cat > services/billing/__init__.py <<'PY'
PY
cat > services/billing/invoice.py <<'PY'
"""帳務：計算訂單總額。"""


def order_total(items):
    return sum(i["price"] * i["qty"] for i in items)
PY

cat > tests/test_orders.py <<'PY'
from src.api.orders import create_order, get_order
from services.billing.invoice import order_total


def test_create_and_get():
    create_order("A001", "星河貿易", [{"sku": "P1", "price": 100, "qty": 2}])
    assert get_order("A001")["customer"] == "星河貿易"


def test_total():
    assert order_total([{"price": 100, "qty": 2}, {"price": 50, "qty": 1}]) == 250
PY

cat > docs/conventions.md <<'MD'
# 程式慣例（團隊共用）

- 函式名稱用 snake_case，模組開頭要有一行 docstring。
- 錯誤訊息格式：`[錯誤代碼] 說明`，錯誤代碼見下表。

| 代碼 | 意義 |
|---|---|
| ORD-001 | 訂單編號格式錯誤 |
| ORD-002 | 品項清單為空 |
| BIL-001 | 金額不可為負 |
MD

git init -q -b main
git -c user.email=lab@example.com -c user.name=lab add -A
git -c user.email=lab@example.com -c user.name=lab commit -qm "init order-portal"
echo "已建立 $(pwd)"
