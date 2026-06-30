import unittest
from datetime import datetime, timezone

from ai_intel.models import XPost
from ai_intel.store import JsonHistoryStore


class JsonHistoryStoreTest(unittest.TestCase):
    def test_reads_previous_followers_and_appends_snapshot(self):
        with self.subTest("store round trip"):
            from tempfile import TemporaryDirectory
            from pathlib import Path

            with TemporaryDirectory() as temp_dir:
                store = JsonHistoryStore(Path(temp_dir) / "history.json")
                post = XPost(
                    id="1",
                    url="https://x.com/example/status/1",
                    author_handle="example",
                    author_name="Example",
                    created_at=datetime(2026, 6, 30, 8, 0, tzinfo=timezone.utc),
                    text="test",
                    likes=1,
                    reposts=0,
                    replies=0,
                    quotes=0,
                    views=10,
                    author_followers=101,
                    author_followers_prev=100,
                )

                self.assertEqual(store.previous_followers(), {})

                store.append_snapshot([post], source="test")

                self.assertEqual(store.previous_followers(), {"example": 101})
                raw = (Path(temp_dir) / "history.json").read_text(encoding="utf-8")
                self.assertIn('"source": "test"', raw)
                self.assertIn('"author_handle": "example"', raw)


if __name__ == "__main__":
    unittest.main()
