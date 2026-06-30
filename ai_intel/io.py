from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .models import XPost


def load_posts(path: Path) -> list[XPost]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [post_from_dict(item) for item in raw["posts"]]


def post_from_dict(item: dict) -> XPost:
    return XPost(
        id=str(item["id"]),
        url=item.get("url", ""),
        author_handle=item["author_handle"],
        author_name=item.get("author_name", item["author_handle"]),
        created_at=parse_datetime(item["created_at"]),
        text=item["text"],
        likes=int(item.get("likes", 0)),
        reposts=int(item.get("reposts", 0)),
        replies=int(item.get("replies", 0)),
        quotes=int(item.get("quotes", 0)),
        views=int(item.get("views", 0)),
        author_followers=int(item.get("author_followers", 0)),
        author_followers_prev=int(item.get("author_followers_prev", item.get("author_followers", 0))),
        media=item.get("media", "text"),
    )


def parse_datetime(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)

