"""
main.py — Entry point for WSB Ticker Tracker.

Usage:
    python main.py                        # run once with settings from config.py
    python main.py --sort hot --limit 200 # override settings via CLI flags
    python main.py --refresh 60           # auto-refresh every 60 seconds
"""

from __future__ import annotations
import argparse
import time
import sys
import os

# ── Config import (with helpful error if missing) ─────────────────────────
try:
    import config
except ImportError:
    print("\n[ERROR] config.py not found.")
    print("  Copy config.example.py to config.py and fill in your Reddit API credentials.\n")
    sys.exit(1)

from src.scraper import build_reddit_client, fetch_posts
from src.parser import parse_posts
from src.dashboard import render_dashboard, console


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Track ticker mentions on r/wallstreetbets in real time."
    )
    parser.add_argument("--subreddit", default=getattr(config, "SUBREDDIT", "wallstreetbets"))
    parser.add_argument("--sort",      default=getattr(config, "SORT", "hot"),
                        choices=["hot", "new", "top", "rising"])
    parser.add_argument("--limit",     type=int, default=getattr(config, "POST_LIMIT", 100),
                        help="Number of posts to fetch (max 1000)")
    parser.add_argument("--comments",  type=int, default=getattr(config, "COMMENT_LIMIT", 20),
                        help="Top comments to fetch per post (0 = skip)")
    parser.add_argument("--top",       type=int, default=getattr(config, "TOP_N", 25),
                        help="Number of tickers to display")
    parser.add_argument("--refresh",   type=int, default=getattr(config, "REFRESH_SECS", 0),
                        help="Auto-refresh every N seconds (0 = run once)")
    return parser.parse_args()


def run(args: argparse.Namespace) -> None:
    """Fetch, parse, and display one cycle."""
    reddit = build_reddit_client(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
        username=getattr(config, "REDDIT_USERNAME", ""),
        password=getattr(config, "REDDIT_PASSWORD", ""),
    )

    posts = fetch_posts(
        reddit=reddit,
        subreddit_name=args.subreddit,
        sort=args.sort,
        limit=args.limit,
        comment_limit=args.comments,
        verbose=True,
    )

    results = parse_posts(posts)

    render_dashboard(
        results=results,
        top_n=args.top,
        subreddit=args.subreddit,
        sort_mode=args.sort,
        post_count=len(posts),
    )


def main() -> None:
    args = parse_args()

    if args.refresh > 0:
        console.print(f"[dim]Auto-refresh every {args.refresh}s — press Ctrl+C to stop.[/dim]")
        try:
            while True:
                run(args)
                console.print(f"[dim]Next refresh in {args.refresh}s…[/dim]")
                time.sleep(args.refresh)
        except KeyboardInterrupt:
            console.print("\n[dim]Stopped.[/dim]")
    else:
        run(args)


if __name__ == "__main__":
    main()
