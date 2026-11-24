"""購物車金額計算（講師解答：3 個 bug 已修正）"""


def subtotal(items):
    """商品小計：每項 price × qty 的總和。items 例：[{"price": 100, "qty": 2}]"""
    return sum(item["price"] * item["qty"] for item in items)          # 修正 1：乘上數量


def apply_discount(total, percent):
    """打折後金額。percent=20 代表打八折（折扣 20%），結果四捨五入到整數。"""
    return round(total * (100 - percent) / 100)                        # 修正 2：扣掉折扣比例


def shipping_fee(total):
    """運費：滿 1000 元（含）免運，未滿收 60 元。"""
    if total >= 1000:                                                  # 修正 3：含 1000
        return 0
    return 60


def checkout(items, discount_percent=0):
    """結帳金額 = 折扣後小計 + 運費（運費以折扣後金額判斷）。"""
    discounted = apply_discount(subtotal(items), discount_percent)
    return discounted + shipping_fee(discounted)
