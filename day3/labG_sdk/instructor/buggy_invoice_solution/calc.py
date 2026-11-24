"""發票金額計算（參考解答）"""
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP


def subtotal(items):
    return sum(i["price"] * i["qty"] for i in items)


def vat_amount(net, rate):
    # bug 1：int() 是無條件捨去；改用 Decimal 的 .5 進位，也避開浮點誤差（110 × 0.05 = 5.5000000000000004）
    return int((Decimal(str(net)) * Decimal(str(rate))).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def invoice_total(items, rate=0.05, discount=0):
    """discount 為折扣金額（元），不是百分比。"""
    # bug 2：營業稅要以折扣後金額計算
    net = subtotal(items) - discount
    return net + vat_amount(net, rate)


def due_date(issued: date, terms_days: int) -> date:
    # bug 3：多減了一天
    return issued + timedelta(days=terms_days)
