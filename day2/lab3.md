# 實作 3：從零寫一個只有 bash 工具的 Agent

> 在 VS Code 中操作本實作的方式，見 [`../vscode.md`](../vscode.md)。

## 目的

- 親手跑一次 Agent Loop：呼叫模型 → 執行工具 → 把結果送回 → 直到模型不再呼叫工具。
- 觀察模型如何探索專案、找出錯誤並修正。
- 記錄輪數與 Token，作為後續拆除實驗的比較基準。
- 進階：改用 OpenAI Responses API，比較兩家的差異。

## 前置

| 項目 | 指令或說明 |
| --- | --- |
| Python 3.10 以上 | `python3 --version` |
| 套件 | `pip install anthropic openai pytest` |
| API 金鑰 | `export ANTHROPIC_API_KEY="..."`（進階題另需 `OPENAI_API_KEY`） |
| 練習專案 | 本資料夾的 `buggy_shop/`（購物車金額計算，內含 3 個 bug） |
| 參考程式 | `mini_agent.py`、`mini_agent_logged.py`（加上記錄的參考答案）、`mini_agent_openai.py` |

> 安全提醒：這個 Agent 沒有任何權限控管，模型要執行什麼指令就執行什麼。只在練習用的複本資料夾內執行。

## 步驟

### 1. 複製練習專案並確認測試失敗

```bash
cp -r buggy_shop shop_work
cd shop_work
python3 -m pytest -q
```

預期看到 `5 failed, 2 passed`。之後所有指令都在 `shop_work/` 內執行，原始的 `buggy_shop/` 保持不動，方便重來。

### 2. 讓 Agent 印出每一個指令

打開 `mini_agent.py`，在執行工具前加一行，讓你看見模型要執行什麼：

```python
        if block.type == "tool_use":
            print("$", block.input["command"])          # ← 新增這一行
            out = subprocess.run(block.input["command"], shell=True,
```

### 3. 執行 Agent，直到測試全數通過

```bash
python3 ../mini_agent.py
python3 -m pytest -q
```

預期最後看到 `7 passed`。

### 4. 記錄輪數與 Token

在迴圈中累計 `resp.usage.input_tokens` 與 `resp.usage.output_tokens`，並計算呼叫模型的次數。寫法可對照 `mini_agent_logged.py`：

```bash
cd .. && rm -rf shop_work && cp -r buggy_shop shop_work && cd shop_work
python3 ../mini_agent_logged.py
```

`mini_agent_logged.py` 的最後一行會印出 `輪數：N　輸入 Token：N　輸出 Token：N`。把結果填入下表：

| 版本 | 輪數 | 輸入 Token | 輸出 Token | 測試結果 | 模型有沒有改到測試檔 |
| --- | --- | --- | --- | --- | --- |
| Claude | | | | ＿ passed | |
| OpenAI（進階） | | | | ＿ passed | |

### 5. 進階：改用 OpenAI Responses API

```bash
cd .. && rm -rf shop_work && cp -r buggy_shop shop_work && cd shop_work
export OPENAI_API_KEY="..."
python3 ../mini_agent_openai.py
python3 -m pytest -q
```

比較時注意三個差異：工具定義多一層 `"type": "function"`、參數欄位叫 `parameters`、`call.arguments` 是 JSON 字串要先 `json.loads`。要記錄 Token 時，Responses API 的用量在 `resp.usage.input_tokens` 與 `resp.usage.output_tokens`。

## 預期結果

- 模型通常會先執行測試或讀取 `shop/pricing.py`，再逐一修正 3 個 bug，最後重跑測試確認。
- 修正後 `python3 -m pytest -q` 顯示 `7 passed`。
- 輪數與 Token 會因模型與每次執行而不同，這是正常的。

## 檢核點

- [ ] 修正前確認過 `5 failed, 2 passed`
- [ ] Agent 執行的每個指令都有印出來
- [ ] 修正後 `7 passed`，而且 `tests/` 底下的檔案沒有被改動（可用 `diff -r -x __pycache__ ../buggy_shop/tests tests` 確認）
- [ ] 填好輪數與 Token 紀錄表
- [ ] （進階）OpenAI 版也能讓測試全數通過

## 沒有 API 金鑰時：用模擬伺服器驗證程式流程

模擬伺服器會固定要求執行一個指令，再回傳一段文字，只能確認程式能跑完，不會真的修好 bug。

```bash
python3 ../../mock/mock_api.py 8899 &
export ANTHROPIC_BASE_URL=http://127.0.0.1:8899 ANTHROPIC_API_KEY=x
export OPENAI_BASE_URL=http://127.0.0.1:8899/v1 OPENAI_API_KEY=x
python3 ../mini_agent_logged.py      # 預期：印出一個指令、[mock] 回覆、輪數：2
```

（指令中的 `../../mock/` 依你的資料夾位置調整，指向課程範例中的 `mock/mock_api.py`。）

## 延伸題

1. 在 `messages` 的第一則訊息加上「只能修改 shop/ 底下的程式，不要改測試」。加與不加，模型行為有沒有差別？
2. 加一個「最多 15 輪」的上限，超過就停止並印出目前狀態。為什麼正式的 Agent 需要這種上限？
3. 把 `[-5000:]` 改成 `[-200:]`，觀察模型是否因為看不到完整錯誤訊息而多跑幾輪。
4. 如果模型執行了 `rm -rf` 之類的危險指令，這個 Agent 有什麼機制能擋下？（答案：沒有。安全邊界單元會用 Hook 補上。）
