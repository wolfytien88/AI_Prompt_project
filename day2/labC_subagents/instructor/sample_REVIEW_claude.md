# REVIEW：member_service/ 與 tests/

審查員：**資安**（security-reviewer）、**測試**（test-reviewer）、**效能**（perf-reviewer）。三者皆唯讀，未修改程式。
重複問題已合併，「找到者」欄標明由哪位審查員提出。嚴重度依各審查員原標示，同一問題被不同等級標示時取較高者。
原始 24 項 → 合併後 20 項。

## 總覽

| 嚴重度 | 項數 |
|---|---|
| Critical | 3 |
| High | 6 |
| Medium | 8 |
| Low | 3 |

## Critical

### 1. `add_member` SQL 注入
- 位置：member_service/store.py:17
- 找到者：資安、測試
- 問題：以 f-string 將 `email`、`name`、`tier` 串進 INSERT，可注入（例：`'); UPDATE members SET tier='vip'--`）。測試審查員也指出姓名含單引號（`O'Brien`）會直接讓 INSERT 出錯，且此行為沒有測試。
- 建議：改用參數化查詢 `conn.execute("INSERT INTO members (email,name,pw,tier) VALUES (?,?,?,?)", (...))`，`tier` 加白名單驗證；補上含特殊字元的測試。

### 2. `find_by_email` SQL 注入且完全沒有測試
- 位置：member_service/store.py:21-22
- 找到者：資安、測試
- 問題：`email` 串進 WHERE，`' OR '1'='1` 可取出任意會員資料；含單引號的 email（`o'brien@x.com`）會出錯。此函式完全沒有測試（找得到、找不到、大小寫、單引號皆未涵蓋）。
- 建議：改為 `WHERE email = ?` 參數化；新增找到、找不到、含單引號 email 的測試。

### 3. `export_csv` 測試只檢查檔案存在
- 位置：tests/test_export.py:14
- 找到者：測試
- 問題：export_csv 即使輸出空檔或錯誤資料，測試仍會通過；`.gz` 內容未驗證。
- 建議：用 `gzip.open` 讀回內容，斷言 CSV 列等於預期的 `[id, email, name, tier]`。

## High

### 4. `export_csv` 以 `os.system` 組 shell 指令（指令注入）
- 位置：member_service/export.py:27-28
- 找到者：資安（High）、測試（Low）、效能（Low）
- 問題：
  - 資安：`os.system(f"gzip -f {path}")` 中的 `out_dir`／`filename` 含 `;`、`$()`、空白即可執行任意指令。
  - 測試：測試依賴系統有 `gzip` 指令，回傳值被忽略，失敗時原因不明（例如 Windows CI）。
  - 效能：先把完整未壓縮 CSV 寫入磁碟再開 shell 壓縮，多一次完整寫入與一次處理程序啟動。
- 建議：改用 Python `gzip.open(path + ".gz", "wt", newline="")` 直接寫入壓縮檔；若必須呼叫外部指令，用 `subprocess.run(["gzip","-f","--",path], check=True)`。改完後補 gzip 失敗與檔名含空白／`;` 的測試。

### 5. 密碼使用無鹽 MD5
- 位置：member_service/store.py:16
- 找到者：資安
- 問題：容易被彩虹表與暴力破解，相同密碼的雜湊相同。
- 建議：改用 argon2-cffi、bcrypt，或 `hashlib.scrypt`／`pbkdf2_hmac`（每筆隨機 salt），比對時用 `hmac.compare_digest`。

### 6. `dedupe` 為 O(n²)，且無直接測試
- 位置：member_service/export.py:8-16
- 找到者：效能（High）、測試（Medium）
- 問題：
  - 效能：每筆都線性掃描 `result`，找到重複後仍跑完迴圈，內層每次比對呼叫兩次 `.lower()`。10 萬筆全不重複約 5×10⁹ 次比對，推估需數十分鐘以上（推估值，未實測）。
  - 測試：缺少大小寫不同的重複 email（`A@x.com` 與 `a@x.com`）、空清單、保留第一筆順序的案例。
- 建議：用 dict／set 以小寫 email 為鍵去重，保留第一次出現的列（O(n)）；直接以 tuple 清單測試，不經資料庫。

### 7. 測試修改全域 `store.DB_PATH` 且不還原
- 位置：tests/test_export.py:10
- 找到者：測試
- 問題：測試間互相污染，結果取決於執行順序；`DB_PATH` 在 import 時已固定。
- 建議：用 `monkeypatch.setattr(store, "DB_PATH", ...)`，或讓 `connect(path)` 可傳入路徑。

### 8. `export_csv` 缺少錯誤路徑測試
- 位置：member_service/export.py:20
- 找到者：測試
- 問題：輸出資料夾不存在、不可寫、檔名含空白或特殊字元皆未測。
- 建議：斷言資料夾不存在時丟出 `FileNotFoundError`；新增特殊檔名測試。

### 9. `tier_counts` 沒有測試
- 位置：member_service/export.py:31
- 找到者：測試
- 問題：空資料、未知 tier（如 "silver"）被靜默忽略，皆無案例。（效能問題見第 12 項。）
- 建議：新增空資料庫回傳全 0、各 tier 計數正確、未知 tier 不計入三項測試。

## Medium

### 10. `export_csv` 路徑走訪
- 位置：member_service/export.py:22-23
- 找到者：資安
- 問題：`out_dir + "/" + filename` 直接拼接，`filename` 為 `../../etc/x` 或絕對路徑時可寫到資料夾外。
- 建議：取 `os.path.basename(filename)` 並驗證字元；以 `os.path.realpath` 確認結果仍在 `out_dir` 下，再用 `os.path.join` 組合。

### 11. `all_members` 一次載入全部資料
- 位置：member_service/store.py:25-26
- 找到者：效能
- 問題：`fetchall()` 一次載入 10 萬列，`export_csv` 又在 `dedupe` 複製一份，峰值記憶體約 2 倍。
- 建議：迭代 cursor 逐列處理，或在 SQL 端去重，讓匯出以串流寫入。

### 12. `tier_counts` 對同一張表查三次
- 位置：member_service/export.py:33-34
- 找到者：效能
- 問題：list comprehension 內重複呼叫 `all_members(conn)`，3 次全表查詢、3 份暫存清單。
- 建議：改用 `SELECT tier, COUNT(*) FROM members GROUP BY tier`。

### 13. `email` 欄位無索引（`find_by_email` 全表掃描）
- 位置：member_service/store.py:21-22
- 找到者：效能
- 問題：每次查詢 O(n)；若被放進迴圈則整體變 O(n²)。
- 建議：建表後加 `CREATE UNIQUE INDEX IF NOT EXISTS idx_members_email ON members(LOWER(email))`，並讓大小寫規則與 `dedupe` 一致。

### 14. `add_member` 每筆都 `commit()`
- 位置：member_service/store.py:15-18
- 找到者：效能
- 問題：批次匯入 10 萬筆會觸發 10 萬次提交與 fsync。
- 建議：批次寫入用 `executemany` 並單次 `commit()`，或由呼叫端包交易。

### 15. `add_member` 缺少直接測試與資料約束
- 位置：member_service/store.py:15
- 找到者：測試
- 問題：預設 tier 為 basic、密碼雜湊是否寫入皆未驗證；資料表無 UNIQUE 限制，重複 email 會直接新增，此行為也沒被測試鎖定。
- 建議：先決定重複 email 的預期行為（拒絕或允許），再寫成測試；補預設 tier 測試。

### 16. `export_csv` 缺少邊界案例
- 位置：tests/test_export.py:8
- 找到者：測試、效能
- 問題：
  - 測試：空資料表、姓名含逗號／雙引號／換行、中文姓名皆未測；`open` 未指定 encoding，跨平台行為可能不同。
  - 效能：只匯入 1 筆會員，無法暴露 O(n²) 去重與全表載入，也沒有規模型測試。
- 建議：參數化測試涵蓋上述案例並讀回 CSV 比對；補一個大量資料、設時間上限的測試，或至少加入重複 email 去重案例。

### 17. 測試未清理暫存資料夾與連線
- 位置：tests/test_export.py:9, 11
- 找到者：測試
- 問題：`mkdtemp` 建立後不刪除，`conn` 未 close。
- 建議：改用 `tmp_path` fixture，並用 yield fixture 於結束時關閉連線。

## Low

### 18. CSV 公式注入
- 位置：member_service/export.py:26
- 找到者：資安
- 問題：`name`／`email` 以 `=`、`+`、`-`、`@` 開頭時，用 Excel 開啟會被當公式執行。
- 建議：寫入前對這類開頭的欄位加上前綴 `'`。

### 19. `connect()` 每次都執行建表 DDL
- 位置：member_service/store.py:9-12
- 找到者：效能
- 問題：每次連線都執行 `CREATE TABLE IF NOT EXISTS`。
- 建議：把建表與建索引移到只執行一次的初始化函式。

### 20. 缺少共用 fixture 與 `test_store.py`
- 位置：tests/ 整體組織
- 找到者：測試
- 問題：只有一個測試檔，沒有 `conftest.py`，`store` 沒有專屬測試檔。
- 建議：新增 `tests/conftest.py` 提供暫存資料庫 fixture，並新增 `tests/test_store.py`。

## 修復順序建議

1. 第 1、2、4、5 項（注入與密碼）先修，同時補上第 1–3、7–9 項測試，讓修改有保護網。
2. 第 6、11–14 項（效能）在測試就位後處理。
3. 其餘依優先序處理。

## 備註

- 效能審查的耗時與記憶體數字皆為推估，未實際執行基準測試。
- `member_service/__init__.py` 為空檔；`tests/test_export.py` 只使用固定測試值，資安審查未發現問題。
