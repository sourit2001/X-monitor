from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass

from ai_intel.io import parse_datetime
from ai_intel.models import XPost


RECENT_SEARCH_URL = "https://api.x.com/2/tweets/search/recent"


@dataclass(frozen=True)
class XSearchConfig:
    query: str
    max_results: int = 25


def fetch_recent_search(
    bearer_token: str,
    config: XSearchConfig,
    previous_followers: dict[str, int] | None = None,
) -> list[XPost]:
    params = {
        "query": config.query,
        "max_results": str(config.max_results),
        "tweet.fields": "author_id,created_at,public_metrics",
        "expansions": "author_id",
        "user.fields": "name,username,public_metrics",
    }
    url = f"{RECENT_SEARCH_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "ai-intel-assistant/0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return parse_recent_search_response(payload, previous_followers=previous_followers or {})


def parse_recent_search_response(
    payload: dict,
    previous_followers: dict[str, int] | None = None,
) -> list[XPost]:
    previous_followers = previous_followers or {}
    users = {
        user["id"]: user
        for user in payload.get("includes", {}).get("users", [])
        if "id" in user
    }
    posts = []
    for item in payload.get("data", []):
        user = users.get(item.get("author_id"), {})
        handle = user.get("username", item.get("author_id", "unknown"))
        metrics = item.get("public_metrics", {})
        user_metrics = user.get("public_metrics", {})
        followers = int(user_metrics.get("followers_count", 0))
        posts.append(
            XPost(
                id=str(item["id"]),
                url=f"https://x.com/{handle}/status/{item['id']}",
                author_handle=handle,
                author_name=user.get("name", handle),
                created_at=parse_datetime(item["created_at"]),
                text=item.get("text", ""),
                likes=int(metrics.get("like_count", 0)),
                reposts=int(metrics.get("retweet_count", 0)),
                replies=int(metrics.get("reply_count", 0)),
                quotes=int(metrics.get("quote_count", 0)),
                views=int(metrics.get("impression_count", 0)),
                author_followers=followers,
                author_followers_prev=int(previous_followers.get(handle, followers)),
                media="text",
            )
        )
    return posts

