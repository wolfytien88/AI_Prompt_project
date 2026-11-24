# 實作 2：兩家同題 Eval

> 在 VS Code 中操作本實作的方式，見 [`../vscode.md`](../vscode.md)。

## 目的
用固定的測試集與評分方式，比較實作 1 的三版 Prompt 與兩家模型，把「這版比較好」變成可以重複驗證的數字。

## 形式
個人。

## 前置
- 實作 1 的 `my_prompts/v1.txt`～`v3.txt`
- 沒有 API Key 時，可先用模擬伺服器驗證流程（分數沒有意義，只確認程式能跑）：
  ```bash
  python3 ../mock/mock_api.py 8899 &
  export ANTHROPIC_BASE_URL=http://127.0.0.1:8899 ANTHROPIC_API_KEY=x
  export OPENAI_BASE_URL=http://127.0.0.1:8899/v1 OPENAI_API_KEY=x
  ```

## 測試集格式
```json
{
  "id": "A-10",
  "input": "我要退貨，但是找不到訂單編號。",
  "must_include": ["手機號碼"],
  "must_not_include": [],
  "tag": "資訊不足"
}
```
- `must_include`：輸出必須包含的每一個字串
- `must_not_include`：輸出不可出現的字串（例如被夾帶指令誘導出的「已同意全額退款」）
- `tag`：題目類型，分為「典型」「資訊不足」「內容矛盾」「超出範圍」「夾帶指令」

`cases/cases_A.json` 是完整的 20 題範例；`cases_B.json`、`cases_C.json` 是起始題目，請自行補到 20 題。

## 步驟
1. **寫測試集**：為你的任務準備 20 題，其中至少 5 題是刁鑽題（資訊不足、內容矛盾、超出範圍、夾帶指令）。可以從範例檔複製後修改。
2. **最簡版評分**：先用 `eval.py` 跑一次，理解最基本的流程：
   ```bash
   cp my_prompts/v2.txt prompt_v2.txt
   cp cases/cases_A.json cases.json     # 換成你的測試集
   python3 eval.py
   python3 eval_openai.py
   ```
3. **完整比較**：把你的 Prompt 放到 `prompts/<任務>/v1.txt`～`v3.txt`，測試集放到 `cases/cases_<任務>.json`，執行：
   ```bash
   python3 compare.py --task A --runs 2
   ```
   畫面會印出 3 版 × 2 家的分數表，失敗題目的明細寫在 `results/`。
4. **逐題檢查**：打開 `results/` 的明細，挑出兩家差最多的 3 題，閱讀實際輸出。
5. **填寫比較表**：使用 `results_template.md`。
6. **（選做）模型評分**：任務 A 可用 LLM-as-judge 補充語氣與完整度的評分：
   ```bash
   python3 llm_judge.py --prompt prompts/A/v3.txt --generator claude --judge openai --limit 5
   ```
   再人工評同樣 5 題，比較兩者差異。

## 討論
- 分數差異來自模型，還是來自 Prompt 寫法？證據是什麼？
- 同一組合跑兩次，分數差多少？差 1–2 題時能下結論嗎？
- `eval.py` 用精確比對，`compare.py` 先移除空白、全形數字轉半形。哪些題目因此結果不同？關鍵字比對有什麼侷限？
- 哪些題目只能靠 LLM-as-judge 或人工判斷？

## 檢核點
- [ ] 測試集 20 題，至少 5 題刁鑽題，每題都有 `tag`
- [ ] 3 版 × 2 家都至少跑 2 次
- [ ] 比較表填完，並寫下 3 題差異最大的題目與原因
- [ ] 至少找出 1 題「關鍵字比對判錯」的情況

## 延伸題
1. 把 `must_include` 改成正規表示式比對（例如日期格式、8 位數統編）。
2. 任務 C：改成解析 JSON 後逐欄位比對標準答案，計算欄位正確率。
3. 把每次分數存成 CSV，畫出 v1–v3 的分數變化。

## 交付
`cases/cases_<任務>.json`、`results/` 的比較結果、填好的 `results_template.md`。拆除實驗會沿用這份測試集與 `compare.py`。
