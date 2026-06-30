from __future__ import annotations

import argparse
import os
from pathlib import Path

from ai_intel.collectors.x_api import XSearchConfig, fetch_recent_search
from ai_intel.io import load_posts
from ai_intel.report import build_markdown_report
from ai_intel.store import JsonHistoryStore, write_posts_snapshot


DEFAULT_QUERY = '(AI OR "artificial intelligence" OR agent OR agents) lang:en -is:retweet'


def run_daily(
    data_path: Path,
    report_path: Path,
    snapshot_path: Path,
    history_path: Path,
    source: str,
    query: str = DEFAULT_QUERY,
    max_results: int = 25,
) -> None:
    store = JsonHistoryStore(history_path)
    bearer_token = os.environ.get("X_BEARER_TOKEN", "").strip()

    if source == "x-api" and bearer_token:
        posts = fetch_recent_search(
            bearer_token,
            XSearchConfig(query=query, max_results=max_results),
            previous_followers=store.previous_followers(),
        )
    else:
        posts = load_posts(data_path)

    write_posts_snapshot(snapshot_path, posts)
    store.append_snapshot(posts, source=source if bearer_token else "sample")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = build_markdown_report(posts)
    report_path.write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the daily AI intelligence report")
    parser.add_argument("--data", default="samples/x_posts.json")
    parser.add_argument("--report", default="reports/daily.md")
    parser.add_argument("--snapshot", default="data/latest_posts.json")
    parser.add_argument("--history", default="data/history.json")
    parser.add_argument("--source", choices=["sample", "x-api"], default="x-api")
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--max-results", type=int, default=25)
    args = parser.parse_args()

    run_daily(
        data_path=Path(args.data),
        report_path=Path(args.report),
        snapshot_path=Path(args.snapshot),
        history_path=Path(args.history),
        source=args.source,
        query=args.query,
        max_results=args.max_results,
    )
    print(f"Wrote {args.report}")


if __name__ == "__main__":
    main()

