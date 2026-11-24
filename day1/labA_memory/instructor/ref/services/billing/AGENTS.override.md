# 帳務服務：結帳凍結期間的暫時規則
- 凍結期間不修改 `invoice.py`，只允許新增或修改測試。
- 金額一律使用 `decimal.Decimal`，不可使用 float。
- 金額為負時 `raise ValueError("[BIL-001] 金額不可為負")`。
（同一層有 AGENTS.override.md 時，Codex 不讀同層的 AGENTS.md，所以要保留的規則必須寫進來。）
