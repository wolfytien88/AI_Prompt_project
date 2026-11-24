import unittest

from src.service.report_service import daily_report


class TestReport(unittest.TestCase):
    def test_daily_report(self):
        report = daily_report([("買牛奶", True), ("寫報告", False)])
        self.assertEqual(report, "[完成] 買牛奶\n寫報告\n剩 1 項")


if __name__ == "__main__":
    unittest.main()
