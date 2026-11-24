# 參考：Claude Code plan mode 產生的計畫（claude -p --permission-mode plan，2026-10-29）

以下為實際輸出，每次執行內容會不同。計畫檔由 Claude Code 寫在 ~/.claude/plans/ 底下，專案檔案沒有任何變動。

我還沒有修改任何專案檔案，只把計畫寫到 `~/.claude/plans/post-api-todos-1-100-floofy-shamir.md`。這個工作階段沒有提供 ExitPlanMode 工具，所以請直接在這裡回覆「照做」或提出調整，我再開始實作。

## 計畫摘要

**現況**
- `src/types/todo.py` 已有 `validate_title()`，但 `MAX_TITLE_LENGTH` 是 200，需求是 100。
- service 層只有 `list_todos()`，server 只有 `do_GET`。
- `docs/architecture.md` 提到 `make lint` 和 `tools/check_layers.py`，但兩者都不存在。這次不處理，只提醒你。

**修改順序（依 `types → repo → service → ui` 由下往上）**
1. **types**：把 `MAX_TITLE_LENGTH` 改成 100，`validate_title` 邏輯不變。
2. **service**：新增 `create_todo(title)`。
   - 它呼叫 `validate_title`，不合法就丟 `ValueError`。
   - 標題去頭尾空白後存檔，id 取現有最大 id 加 1，`done=False`。
   - 只 import types 和 repo。
3. **repo**：不改。
4. **ui**：新增 `do_POST`，只處理 `/api/todos`。
   - 讀 JSON body。body 不是 JSON 物件，或沒有 `title`，回 400。
   - `ValueError` 回 400 和 `{"error": msg}`，成功回 201 和新項目。
   - 驗證規則只放在 types 和 service，ui 只負責轉成 HTTP 狀態碼。
5. **文件**：在 `docs/architecture.md` 的 API 表加上 `POST /api/todos`。

**測試（unittest，`make test` 會跑）**
- **types**：100 字合法，101 字不合法，全空白不合法，前後空白不計入長度。
- **service**：用暫存目錄的 repo，確認標題被 strip、id 遞增、能讀回，不合法時不寫檔。
- **HTTP**：測試在背景啟動伺服器，並 patch 全域 `service` 指向暫存檔。
  - 合法標題和 100 字邊界回 201。
  - 空白、101 字、缺 title、title 不是字串、壞 JSON 回 400。
  - 建立後再 GET，確認看得到新項目。

**驗證**
- 跑 `make test`。
- 用 curl 對暫時啟動的伺服器打合法和非法 POST。
- 用 grep 確認各層依賴方向沒被破壞。

**需要你確認的兩件事**
1. 長度以 Python `len()`（Unicode 字元數）計算，組合 emoji 可能算成多個字。預設接受。
2. 上限改成 100 後，日後「編輯」功能共用同一個驗證，也會受 100 字限制。預設視為期望行為。
