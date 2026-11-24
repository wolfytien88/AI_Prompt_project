"""發票金額計算（練習用：內含 3 個 bug）

規則：
- 小計 = 每項 price × qty 的總和
- 折扣先套用在小計上，再計算營業稅
- 營業稅 = 折扣後金額 × 稅率，四捨五入到整數（.5 進位）
- 付款期限 = 開立日 + 付款天數（例：10/1 開立、30 天 → 10/31）
"""
from datetime import date, timedelta


def subtotal(items):
    return sum(i["price"] * i["qty"] for i in items)


def vat_amount(net, rate):
    return int(net * rate)


def invoice_total(items, rate=0.05, discount=0):
    """discount 為折扣金額（元），不是百分比。"""
    net = subtotal(items)
    tax = vat_amount(net, rate)
    return net - discount + tax


def due_date(issued: date, terms_days: int) -> date:
    return issued + timedelta(days=terms_days - 1)
