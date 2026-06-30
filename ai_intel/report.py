from __future__ import annotations

from datetime import datetime, timezone

from .analyzer import analyze_authors, analyze_posts
from .models import XPost


def build_markdown_report(posts: list[XPost], title: str = "AI Intelligence Daily") -> str:
    post_insights = analyze_posts(posts)
    author_insights = analyze_authors(posts)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# {title}",
        "",
        f"Generated: {generated_at}",
        f"Posts analyzed: {len(posts)}",
        "",
        "## Potential Breakouts",
        "",
    ]

    for insight in post_insights[:10]:
        post = insight.post
        lines.extend(
            [
                f"### {insight.score:.1f} - @{post.author_handle}",
                "",
                post.text.replace("\n", " "),
                "",
                f"- Link: {post.url or post.id}",
                f"- Engagement: {insight.engagement:.1f}; velocity/hour: {insight.velocity:.1f}; view rate: {insight.view_rate:.2%}",
                f"- Hooks: {', '.join(insight.hooks)}",
                f"- Traits: {', '.join(insight.traits)}",
                "",
            ]
        )

    lines.extend(["## Fast-Growing Authors", ""])
    for author in author_insights[:10]:
        lines.extend(
            [
                f"### @{author.handle} - {author.name}",
                "",
                f"- Followers: {author.followers:,} ({author.follower_delta:+,}, {author.follower_growth_rate:.2%})",
                f"- Posts analyzed: {author.post_count}; weighted engagement: {author.total_engagement:.1f}",
                f"- Dominant media: {author.dominant_media}",
                f"- Common hooks: {', '.join(author.dominant_hooks) or 'n/a'}",
                "",
            ]
        )

    lines.extend(
        [
            "## Editorial Takeaways",
            "",
            *build_takeaways(post_insights),
            "",
        ]
    )
    return "\n".join(lines)


def build_takeaways(post_insights) -> list[str]:
    top = post_insights[:10]
    if not top:
        return ["- No posts found."]

    hook_counts = {}
    trait_counts = {}
    for insight in top:
        for hook in insight.hooks:
            hook_counts[hook] = hook_counts.get(hook, 0) + 1
        for trait in insight.traits:
            trait_counts[trait] = trait_counts.get(trait, 0) + 1

    top_hooks = sorted(hook_counts.items(), key=lambda item: item[1], reverse=True)[:3]
    top_traits = sorted(trait_counts.items(), key=lambda item: item[1], reverse=True)[:5]
    return [
        f"- Strongest hooks today: {', '.join(name for name, _ in top_hooks)}.",
        f"- Repeated traits: {', '.join(name for name, _ in top_traits)}.",
        "- Good candidates for deeper review are posts with early-velocity plus high-view-conversion.",
    ]

