from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from math import log10
from typing import Iterable

from .models import AuthorInsight, PostInsight, XPost


HOOK_KEYWORDS = {
    "prediction": ["will", "going to", "future", "next", "soon", "预测", "未来", "接下来"],
    "contrarian": ["wrong", "nobody", "myth", "actually", "反常识", "错了", "没人"],
    "tutorial": ["how to", "guide", "step", "tutorial", "here is", "教程", "方法", "步骤"],
    "resource": ["list", "tools", "resources", "template", "清单", "工具", "资源", "模板"],
    "news": ["breaking", "launch", "released", "announced", "最新", "发布", "突发"],
    "debate": ["why", "should", "hot take", "agree", "争议", "为什么", "应该"],
}


def analyze_posts(posts: Iterable[XPost], now: datetime | None = None) -> list[PostInsight]:
    now = now or datetime.now(timezone.utc)
    insights = []
    for post in posts:
        age_hours = max((now - post.created_at).total_seconds() / 3600, 0.25)
        engagement = post.likes + post.reposts * 2 + post.quotes * 2.5 + post.replies * 1.5
        velocity = engagement / age_hours
        view_rate = engagement / max(post.views, 1)
        follower_adjusted = engagement / max(post.author_followers, 1)

        score = (
            min(log10(engagement + 1) * 18, 42)
            + min(log10(velocity + 1) * 22, 35)
            + min(view_rate * 250, 15)
            + min(follower_adjusted * 1800, 18)
        )

        hooks = detect_hooks(post.text)
        traits = detect_traits(post, age_hours, velocity, view_rate, follower_adjusted)
        insights.append(
            PostInsight(
                post=post,
                score=round(score, 1),
                engagement=round(engagement, 1),
                velocity=round(velocity, 1),
                view_rate=round(view_rate, 4),
                follower_adjusted=round(follower_adjusted, 4),
                hooks=hooks,
                traits=traits,
            )
        )

    return sorted(insights, key=lambda item: item.score, reverse=True)


def analyze_authors(posts: Iterable[XPost]) -> list[AuthorInsight]:
    grouped: dict[str, list[XPost]] = defaultdict(list)
    for post in posts:
        grouped[post.author_handle].append(post)

    insights = []
    for handle, author_posts in grouped.items():
        newest = max(author_posts, key=lambda post: post.created_at)
        follower_delta = newest.author_followers - newest.author_followers_prev
        follower_growth_rate = follower_delta / max(newest.author_followers_prev, 1)
        total_engagement = sum(
            post.likes + post.reposts * 2 + post.quotes * 2.5 + post.replies * 1.5
            for post in author_posts
        )
        top_media = Counter(post.media for post in author_posts).most_common(1)
        hooks = Counter(hook for post in author_posts for hook in detect_hooks(post.text))
        insights.append(
            AuthorInsight(
                handle=handle,
                name=newest.author_name,
                followers=newest.author_followers,
                follower_delta=follower_delta,
                follower_growth_rate=round(follower_growth_rate, 4),
                post_count=len(author_posts),
                total_engagement=round(total_engagement, 1),
                dominant_media=top_media[0][0] if top_media else "text",
                dominant_hooks=[name for name, _ in hooks.most_common(3)],
            )
        )

    return sorted(
        insights,
        key=lambda item: (item.follower_delta, item.total_engagement),
        reverse=True,
    )


def detect_hooks(text: str) -> list[str]:
    lowered = text.lower()
    hooks = []
    for name, keywords in HOOK_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            hooks.append(name)
    return hooks or ["observation"]


def detect_traits(
    post: XPost,
    age_hours: float,
    velocity: float,
    view_rate: float,
    follower_adjusted: float,
) -> list[str]:
    traits = []
    text = post.text.strip()
    if len(text) < 180:
        traits.append("short-form")
    if "\n" in text or post.media == "thread":
        traits.append("thread-like")
    if "?" in text:
        traits.append("question-led")
    if post.media != "text":
        traits.append(f"media:{post.media}")
    if age_hours <= 6 and velocity >= 50:
        traits.append("early-velocity")
    if view_rate >= 0.04:
        traits.append("high-view-conversion")
    if follower_adjusted >= 0.03:
        traits.append("small-account-outperforming")
    return traits or ["plain-text"]

