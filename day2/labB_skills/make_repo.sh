#!/bin/bash
# 建立實作 B 的練習專案 invoice-tool（虛構）：有 v1.1.0 標籤、之後 5 筆 commit、一筆未提交的修改。
# 用法：bash make_repo.sh [目的資料夾，預設 ./invoice-tool]
set -e
DEST="${1:-./invoice-tool}"
[ -e "$DEST" ] && { echo "$DEST 已存在"; exit 1; }
mkdir -p "$DEST" && cd "$DEST"
g() { git -c user.email=lab@example.com -c user.name=lab "$@"; }
git init -q -b main
cat > invoice.py <<'PY'
"""發票工具：計算含稅金額。"""
TAX_RATE = 0.05


def with_tax(amount):
    if amount < 0:
        raise ValueError("金額不可為負")
    return round(amount * (1 + TAX_RATE))
PY
printf '# invoice-tool\n\n虛構的發票小工具。\n' > README.md
printf '# 更新紀錄\n\n## v1.1.0（2026-09-15）\n- 第一個正式版本\n' > CHANGELOG.md
g add -A; g commit -qm "feat: 第一個正式版本"; g tag v1.1.0
cat >> invoice.py <<'PY'


def split_amount(total, n):
    """把總額平均分給 n 個人，餘數加在第一個人。"""
    base, rest = divmod(total, n)
    return [base + rest] + [base] * (n - 1)
PY
g commit -qam "feat: 新增分攤金額 split_amount"
sed -i 's/round(amount \* (1 + TAX_RATE))/int(amount * (1 + TAX_RATE) + 0.5)/' invoice.py
g commit -qam "fix: 含稅金額改為四捨五入到整數，修正 0.5 進位錯誤"
printf '\n## 使用方式\n\n```python\nfrom invoice import with_tax\nwith_tax(100)  # 105\n```\n' >> README.md
g commit -qam "docs: README 加上使用方式"
cat > test_invoice.py <<'PY'
from invoice import with_tax, split_amount


def test_with_tax():
    assert with_tax(100) == 105


def test_split():
    assert split_amount(100, 3) == [34, 33, 33]
PY
g add -A; g commit -qm "test: 補上 with_tax 與 split_amount 測試"
sed -i 's/"""把總額平均分給 n 個人，餘數加在第一個人。"""/"""把總額平均分給 n 個人，餘數加在第一個人。n 必須大於 0。"""/' invoice.py
g commit -qam "docs: split_amount 註明 n 的限制"
# 未提交的修改：拿掉負數檢查、寫死測試金鑰（供 diff-risk 找出風險）
sed -i '/if amount < 0:/,+1d' invoice.py
printf '\nAPI_KEY = "sk-test-FAKE-0000"  # 暫時測試用\n' >> invoice.py
echo "已建立 $(pwd)：標籤 v1.1.0 之後有 5 筆 commit，另有未提交的修改"
