import unittest
from datetime import date

from invoice.calc import subtotal, vat_amount, invoice_total, due_date


class TestCalc(unittest.TestCase):
    def test_subtotal(self):
        self.assertEqual(subtotal([{"price": 100, "qty": 2}, {"price": 50, "qty": 1}]), 250)

    def test_subtotal_empty(self):
        self.assertEqual(subtotal([]), 0)

    def test_vat_exact(self):
        self.assertEqual(vat_amount(1000, 0.05), 50)

    def test_vat_half_up(self):
        self.assertEqual(vat_amount(110, 0.05), 6)       # 5.5 → 6

    def test_vat_zero_rate(self):
        self.assertEqual(vat_amount(999, 0), 0)

    def test_total_no_discount(self):
        self.assertEqual(invoice_total([{"price": 1000, "qty": 1}]), 1050)

    def test_total_discount_before_tax(self):
        # (1000 - 200) × 1.05 = 840
        self.assertEqual(invoice_total([{"price": 1000, "qty": 1}], discount=200), 840)

    def test_due_date_30_days(self):
        self.assertEqual(due_date(date(2026, 10, 1), 30), date(2026, 10, 31))

    def test_due_date_cross_year(self):
        self.assertEqual(due_date(date(2026, 12, 15), 30), date(2027, 1, 14))
