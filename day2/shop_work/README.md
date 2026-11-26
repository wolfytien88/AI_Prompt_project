# buggy_shop：實作 3 練習專案

一個購物車金額計算模組，內含 3 個 bug，用來讓 Agent 練習「執行測試 → 找出原因 → 修正」。

```
buggy_shop/
├── shop/pricing.py      ← 有 bug 的程式
├── tests/test_pricing.py
└── pytest.ini
```

在本資料夾執行：

```bash
python3 -m pytest -q
```

修正前應看到 `5 failed, 2 passed`（3 個 bug 造成 5 個測試失敗）。只能修改 `shop/pricing.py`，不要改測試。
