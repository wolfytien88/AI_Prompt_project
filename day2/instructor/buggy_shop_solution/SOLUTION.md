# 講師解答：buggy_shop 的 3 個 bug

修正前：`5 failed, 2 passed`。修正後：`7 passed`。

| # | 位置 | 錯誤 | 修正 | 影響的測試 |
| --- | --- | --- | --- | --- |
| 1 | `subtotal` | 只加總 `price`，忽略 `qty` | `item["price"] * item["qty"]` | `test_subtotal_uses_quantity`、`test_checkout_end_to_end` |
| 2 | `apply_discount` | 把「折扣比例」當成「剩餘比例」：`total * percent / 100` | `total * (100 - percent) / 100` | `test_discount_twenty_percent_off`、`test_discount_zero_percent`、`test_checkout_end_to_end` |
| 3 | `shipping_fee` | 邊界條件用 `>`，剛好 1000 元仍收運費 | 改成 `>=` | `test_shipping_free_at_exactly_1000` |

## 驗證方式

```bash
cp ../instructor/buggy_shop_solution/pricing.py shop/pricing.py   # 在 buggy_shop/ 內執行
python3 -m pytest -q        # 預期：7 passed
git checkout shop/pricing.py   # 若專案在 git 中，還原練習狀態
```

## 巡迴時可觀察的重點

- `test_checkout_end_to_end` 同時受 bug 1 與 bug 2 影響，只修一個仍會失敗，可用來討論「一個失敗測試可能有多個原因」。
- bug 3 是邊界條件，Agent 容易只看錯誤訊息就改對；可以請學員看 Agent 是否先讀了 docstring 再改。
- 若 Agent 修改了測試檔而不是程式，屬於錯誤做法，可以用來引出「用 Hook 或權限禁止修改 tests/」的話題（安全邊界單元）。
