# 帳務服務規則
- 金額一律使用 `decimal.Decimal`，不可使用 float。
- 金額為負時 `raise ValueError("[BIL-001] 金額不可為負")`。
