import unittest
from datetime import timezone

from ai_intel.collectors.x_api import parse_recent_search_response


class XApiCollectorTest(unittest.TestCase):
    def test_parse_recent_search_response_maps_metrics_and_users(self):
        payload = {
            "data": [
                {
                    "id": "123",
                    "text": "How to spot agent workflow breakouts",
                    "created_at": "2026-06-30T08:00:00Z",
                    "author_id": "u1",
                    "public_metrics": {
                        "like_count": 10,
                        "retweet_count": 3,
                        "reply_count": 2,
                        "quote_count": 1,
                        "impression_count": 900,
                    },
                }
            ],
            "includes": {
                "users": [
                    {
                        "id": "u1",
                        "username": "agentwatch",
                        "name": "Agent Watch",
                        "public_metrics": {"followers_count": 1200},
                    }
                ]
            },
        }

        posts = parse_recent_search_response(payload, previous_followers={"agentwatch": 1100})

        self.assertEqual(len(posts), 1)
        post = posts[0]
        self.assertEqual(post.id, "123")
        self.assertEqual(post.author_handle, "agentwatch")
        self.assertEqual(post.author_name, "Agent Watch")
        self.assertEqual(post.created_at.tzinfo, timezone.utc)
        self.assertEqual(post.likes, 10)
        self.assertEqual(post.reposts, 3)
        self.assertEqual(post.replies, 2)
        self.assertEqual(post.quotes, 1)
        self.assertEqual(post.views, 900)
        self.assertEqual(post.author_followers, 1200)
        self.assertEqual(post.author_followers_prev, 1100)
        self.assertEqual(post.url, "https://x.com/agentwatch/status/123")


if __name__ == "__main__":
    unittest.main()
