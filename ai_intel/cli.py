from __future__ import annotations

import argparse
from pathlib import Path

from .io import load_posts
from .report import build_markdown_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="ai-intel")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report = subparsers.add_parser("report", help="Generate an intelligence report")
    report.add_argument("--data", required=True, help="Path to X post JSON data")
    report.add_argument("--out", required=True, help="Path to write Markdown report")
    report.add_argument("--title", default="AI Intelligence Daily", help="Report title")

    args = parser.parse_args()

    if args.command == "report":
        posts = load_posts(Path(args.data))
        markdown = build_markdown_report(posts, title=args.title)
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markdown, encoding="utf-8")
        print(f"Wrote {out_path}")

