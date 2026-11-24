# 實作 1：Prompt 重構

> 在 VS Code 中操作本實作的方式，見 [`../vscode.md`](../vscode.md)。

## 目的
同一個任務寫成三個版本的 Prompt，分別送到 Claude 與 GPT，觀察每加一個手法帶來的差異，並分辨差異來自模型還是來自寫法。

## 形式
小組（3–4 人）。每組選一個任務。

## 前置
- 已完成環境需求：`pip install anthropic openai`，並設定 `ANTHROPIC_API_KEY`、`OPENAI_API_KEY`
- 也可以直接在 Claude 與 ChatGPT 的網頁介面操作：System Prompt 貼在 Projects 的專案指令，或直接貼在訊息最前面

## 題庫

| 任務 | 情境 | 測試資料 | 讀者與用途 |
|---|---|---|---|
| A 客服回覆 | 依退換貨規定回覆客訴信 | `data/A_emails.md`（5 封）、`data/policy.md` | 客戶；要知道能不能退、怎麼退、誰付運費 |
| B 會議摘要 | 整理會議記錄 | `data/B_meetings.md`（2 份） | 部門主管；要決定是否延後上線 |
| C 發票抽取 | 發票文字轉 JSON | `data/C_invoices.md`（5 張，附標準答案） | 會計系統；程式要能直接讀取 |

所有公司、統編、電話皆為虛構。

## 步驟
1. **選題**：小組選定 A、B、C 其中一題，閱讀對應的測試資料。
2. **寫 v1**：只寫一句話，例如「請回覆這封客戶來信。」存成 `my_prompts/v1.txt`。
3. **寫 v2**：在 v1 上加三個手法：
   - 角色設定（放在 System Prompt）
   - XML 標籤分段（資料與指令分開）
   - 指定輸出格式（長度、段落、JSON 欄位）
   存成 `my_prompts/v2.txt`。
4. **寫 v3**：在 v2 上再加 2–3 個 Few-shot 範例，至少一個是邊界情況（例如沒有統編、食品不能退）。存成 `my_prompts/v3.txt`。
5. **送出測試**：三版各送 Claude 與 GPT，每份測試資料都送。用程式送出：
   ```bash
   python3 run_once.py --provider claude --prompt my_prompts/v2.txt --input "（貼上一封來信）"
   python3 run_once.py --provider openai --prompt my_prompts/v2.txt --input-file data_A01.txt
   ```
6. **並排比較**：把 6 組輸出（3 版 × 2 家）貼在小組共筆，標出差異。

## 觀察重點
- v1 → v2：格式是否從「每次不同」變成「固定」？
- v2 → v3：範例有沒有讓邊界情況處理得更好？有沒有出現「連內容都照抄範例」？
- 任務 A 的 A-05、任務 C 的 C-05 是刁鑽題，兩家模型分別怎麼處理？
- 兩家差最多的是哪一版？

## 檢核點
- [ ] v2 的資料確實放在 XML 標籤內，指令與資料沒有混在一起
- [ ] v3 的範例彼此差異夠大，且至少一個是邊界情況
- [ ] 任務 C 的輸出可以被 `json.loads()` 直接解析
- [ ] 共筆上有 6 組輸出與差異標記

## 參考答案
`prompts/A`、`prompts/B`、`prompts/C` 各有 v1–v3 的參考寫法。先自己寫完再對照。

## 延伸題
1. 任務 C：把 v2 改成用 Structured Outputs（JSON Schema）強制格式，比較與純 Prompt 的穩定度。
2. 任務 A：把 A-05 的「夾帶指令」換成更隱晦的寫法，看哪一版 Prompt 會被誤導。
3. 任務 B：把讀者改成「新進同仁」，Prompt 要改哪些地方？

## 交付
`my_prompts/v1.txt`～`v3.txt`，實作 2 會沿用。
