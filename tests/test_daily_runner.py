import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.run_daily import run_daily


class DailyRunnerTest(unittest.TestCase):
    def test_run_daily_with_sample_data_writes_report_and_snapshot(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report_path = root / "reports" / "daily.md"
            snapshot_path = root / "data" / "latest_posts.json"
            history_path = root / "data" / "history.json"

            run_daily(
                data_path=Path("samples/x_posts.json"),
                report_path=report_path,
                snapshot_path=snapshot_path,
                history_path=history_path,
                source="sample",
            )

            self.assertTrue(report_path.exists())
            self.assertTrue(snapshot_path.exists())
            self.assertTrue(history_path.exists())
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("Potential Breakouts", report)
            self.assertIn("Fast-Growing Authors", report)


if __name__ == "__main__":
    unittest.main()
