# 實作 C 刻意埋的問題（講師對照用）

| 編號 | 類別 | 位置 | 問題 | 建議 |
|---|---|---|---|---|
| S1 | 安全 | store.py `add_member`、`find_by_email` | f-string 組 SQL，可注入 | 參數化查詢 `?` |
| S2 | 安全 | store.py `add_member` | 密碼用 MD5 且未加鹽 | `hashlib.scrypt`／`pbkdf2_hmac` 加鹽 |
| S3 | 安全 | export.py `export_csv` | `os.system(f"gzip -f {path}")`，檔名可注入指令 | 用 `gzip` 模組或 `subprocess.run([...])` |
| S4 | 安全 | export.py `export_csv` | `out_dir + "/" + filename` 可路徑走訪（`../`） | 驗證檔名、`os.path.basename`、限定輸出目錄 |
| T1 | 測試 | tests/test_export.py | 只驗證 .gz 存在，沒驗證內容 | 讀回 gzip 內容比對 |
| T2 | 測試 | tests/test_export.py | 直接改 `store.DB_PATH` 全域變數且不還原 | 用 `monkeypatch` 或 fixture |
| T3 | 測試 | export.py `dedupe`、`tier_counts`；store.py `find_by_email` | 完全沒有測試 | 補重複 Email（大小寫不同）、各等級計數、找不到的案例 |
| T4 | 測試 | store.py | 沒有特殊字元（單引號）的測試，正好會暴露 S1 | 加 `O'Brien` 案例 |
| P1 | 效能 | export.py `dedupe` | 雙層迴圈 O(n²)，且找到重複後不中斷 | 用 set 存小寫 Email，O(n) |
| P2 | 效能 | export.py `tier_counts` | 每個等級都呼叫一次 `all_members`，全表掃描 3 次 | `SELECT tier, COUNT(*) … GROUP BY tier` |
| P3 | 效能 | store.py `all_members` | `fetchall()` 一次載入全部會員 | 逐列迭代或分批寫入 CSV |

真實模型驗證時，合併報告找出上表全部項目，另提出「測試寫在暫存資料夾卻沒清除」等額外項目（見 `sample_REVIEW_claude.md`）。
