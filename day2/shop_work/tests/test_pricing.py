from shop.pricing import subtotal, apply_discount, shipping_fee, checkout


def test_subtotal_uses_quantity():
    items = [{"price": 100, "qty": 2}, {"price": 50, "qty": 3}]
    assert subtotal(items) == 350


def test_subtotal_empty_cart():
    assert subtotal([]) == 0


def test_discount_twenty_percent_off():
    assert apply_discount(1000, 20) == 800


def test_discount_zero_percent():
    assert apply_discount(999, 0) == 999


def test_shipping_free_at_exactly_1000():
    assert shipping_fee(1000) == 0


def test_shipping_charged_below_1000():
    assert shipping_fee(999) == 60


def test_checkout_end_to_end():
    items = [{"price": 600, "qty": 2}]          # 小計 1200
    assert checkout(items, discount_percent=10) == 1080   # 折後 1080，免運
