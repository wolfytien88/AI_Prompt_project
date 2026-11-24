# 拆除實驗：一次只拿掉一個元件，找出真正承重的部分

> 在 VS Code 中操作本實作的方式，見 [`../vscode.md`](../vscode.md)。

## 目的

- 檢驗 Harness 裡每個元件是否仍然必要：模型升級後，有些步驟會變成多餘的負擔。
- 練習用數字而不是印象做判斷：同一份測試集、同樣的重複次數，只改一個變因。

## 前置

| 項目 | 說明 |
| --- | --- |
| 套件與金鑰 | `pip install anthropic`；`export ANTHROPIC_API_KEY="..."` |
| 執行器 | `ablation/ablate.py`：以 Agent Loop（含 bash 工具）逐題作答，最後的回覆包含所有 `must_include` 才算通過 |
| 測試集 | `ablation/cases.json`（5 題範例）；建議改用前一單元自己寫的 20 題 `cases.json`，格式相同 |
| 待拆元件 | `system_full.txt`（三段規則）、`system_no_rule2.txt`（拿掉第 2 段）、`fewshot.txt`（兩個範例） |
| 紀錄表 | `ablation/ablation_sheet.md` 或 `ablation_sheet.csv` |

> 費用估算：每組實驗呼叫模型約「題數 × 重複次數 × 2」次。20 題、2 次、5 組約 400 次呼叫，開始前先確認額度。

## 步驟

以下指令都在 `ablation/` 資料夾內執行。

### 1. 建立基準

```bash
cd ablation
python3 ablate.py --label 基準 --system system_full.txt --fewshot fewshot.txt --runs 2
```

`--runs 2` 會把整份測試集跑兩次。畫面會逐題印出 PASS／FAIL 與輪數，最後一行是摘要，同時附加一列到 `ablation_results.csv`。

### 2. 一次只拿掉一個元件，用同樣設定重跑

```bash
# A：拿掉 System Prompt 第 2 段（政策重點）
python3 ablate.py --label A --removed "System Prompt 第 2 段" --system system_no_rule2.txt --fewshot fewshot.txt --runs 2

# B：拿掉 Few-shot 範例（不給 --fewshot）
python3 ablate.py --label B --removed "Few-shot 範例" --system system_full.txt --runs 2

# C：工具輸出不截斷（預設保留最後 5000 字元）
python3 ablate.py --label C --removed "截斷長度 5000 → 不截斷" --system system_full.txt --fewshot fewshot.txt --truncate 0 --runs 2
```

D 組自選，例如自己寫一個拿掉第 3 段的 System Prompt 檔。每一組只能和基準差一個地方。

### 3. 整理結果

```bash
cat ablation_results.csv
```

CSV 欄位與紀錄表相同：實驗、拿掉的元件、通過數（平均）、各次通過數、平均輪數、平均 Token（每題）、判讀。把數字抄進 `ablation_sheet.md`，或直接用試算表開啟 CSV。

### 4. 判讀

| 結果 | 判讀 |
| --- | --- |
| 通過數與基準相同（差距在各次波動範圍內） | 可拿掉 |
| 通過數明顯下降 | 承重元件，保留 |
| 拿掉後通過數上升 | 這個元件反而干擾模型 |
| 通過數不變但 Token 大幅下降 | 也是拿掉的理由 |

各次通過數差 1–2 題可能只是隨機波動。結論不明確時，把 `--runs` 提高到 3 再跑一次。

## 不要拿掉的元件

權限、檔案過期檢查、Hook 等安全防護，不以分數決定去留。它們防的是少見但代價高的錯誤，測試集多半測不到。

## 預期結果

- 範例測試集中，「找不到訂單編號」一題需要第 2 段的「手機號碼」規則，拿掉第 2 段後模型很可能答不出這個做法，A 組通過數預期低於基準。
- Few-shot 範例與截斷長度的影響因模型而異，這正是要用數字判斷的部分。
- `ablation_results.csv` 至少有基準與三組拆除，共四列。

## 檢核點

- [ ] 基準至少跑 2 次，並記下各次通過數
- [ ] 每組拆除只改一個變因
- [ ] 紀錄表的判讀欄都有填寫，並寫下保留／拿掉的結論
- [ ] 沒有把安全防護列入拆除對象

## 沒有 API 金鑰時：用模擬伺服器驗證執行器

模擬伺服器的回覆是固定文字，所有題目都會 FAIL，只用來確認執行器與 CSV 輸出正常。

```bash
python3 ../../mock/mock_api.py 8899 &
export ANTHROPIC_BASE_URL=http://127.0.0.1:8899 ANTHROPIC_API_KEY=x
python3 ablate.py --label 基準 --system system_full.txt --fewshot fewshot.txt --runs 1 --out mock_results.csv
```

（`mock/mock_api.py` 的相對路徑依你的資料夾位置調整。）

## 延伸題

1. 換一個模型（例如較小、較便宜的版本）重做基準與 A、B 兩組。哪些元件在小模型上變成必要？
2. 把 `--max-rounds` 從 10 降到 2，觀察通過數與 Token 的變化。輪數上限算不算一個可以拆的元件？
3. 對實作 3 的 Agent 做拆除：拿掉 `edit_file` 只留 bash，以 buggy_shop 修完後的 `pytest` 通過數作為分數。
