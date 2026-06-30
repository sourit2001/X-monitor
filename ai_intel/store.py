from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import XPost


class JsonHistoryStore:
    def __init__(self, path: Path):
        self.path = path

    def previous_followers(self) -> dict[str, int]:
        if not self.path.exists():
            return {}
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        followers: dict[str, int] = {}
        for snapshot in raw.get("snapshots", []):
            for post in snapshot.get("posts", []):
                followers[post["author_handle"]] = int(post.get("author_followers", 0))
        return followers

    def append_snapshot(self, posts: list[XPost], source: str) -> None:
        raw = {"snapshots": []}
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        raw.setdefault("snapshots", []).append(
            {
                "captured_at": datetime.now(timezone.utc).isoformat(),
                "source": source,
                "posts": [post_to_dict(post) for post in posts],
            }
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")


def write_posts_snapshot(path: Path, posts: list[XPost]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"posts": [post_to_dict(post) for post in posts]}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def post_to_dict(post: XPost) -> dict:
    return {
        "id": post.id,
        "url": post.url,
        "author_handle": post.author_handle,
        "author_name": post.author_name,
        "created_at": post.created_at.isoformat(),
        "text": post.text,
        "likes": post.likes,
        "reposts": post.reposts,
        "replies": post.replies,
        "quotes": post.quotes,
        "views": post.views,
        "author_followers": post.author_followers,
        "author_followers_prev": post.author_followers_prev,
        "media": post.media,
    }

