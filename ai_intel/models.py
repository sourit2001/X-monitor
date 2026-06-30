from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class XPost:
    id: str
    url: str
    author_handle: str
    author_name: str
    created_at: datetime
    text: str
    likes: int
    reposts: int
    replies: int
    quotes: int
    views: int
    author_followers: int
    author_followers_prev: int
    media: str = "text"


@dataclass(frozen=True)
class PostInsight:
    post: XPost
    score: float
    engagement: float
    velocity: float
    view_rate: float
    follower_adjusted: float
    hooks: list[str]
    traits: list[str]


@dataclass(frozen=True)
class AuthorInsight:
    handle: str
    name: str
    followers: int
    follower_delta: int
    follower_growth_rate: float
    post_count: int
    total_engagement: float
    dominant_media: str
    dominant_hooks: list[str]

