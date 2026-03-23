"""
parser.py — Scans post titles, bodies, and comments for ticker mentions.

Dictionary approach:
  - Only tickers that exist in our TICKERS dict are counted.
  - Uses whole-word regex matching (\\b) so "GAMES" won't match "GME".
  - Aggregates mention count + cumulative vote score per ticker.
"""

from __future__ import annotations
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

from src.tickers import get_ticker_dict, get_blacklist
from src.scraper import Post


@dataclass
class TickerResult:
    ticker: str
    company: str
    mentions: int = 0
    total_score: int = 0
    post_ids: List[str] = field(default_factory=list)

    @property
    def avg_score(self) -> float:
        return round(self.total_score / self.mentions, 1) if self.mentions else 0.0


def _build_pattern(ticker: str) -> re.Pattern:
    """Compile a whole-word, case-sensitive regex for a ticker symbol."""
    return re.compile(rf"\b{re.escape(ticker)}\b")


def parse_posts(posts: List[Post]) -> Dict[str, TickerResult]:
    """
    Scan all posts (title + body + comments) for ticker mentions.

    Returns a dict of  ticker -> TickerResult  sorted by mention count desc.
    """
    tickers = get_ticker_dict()
    blacklist = get_blacklist()

    # Pre-compile all patterns once
    patterns: Dict[str, re.Pattern] = {
        t: _build_pattern(t) for t in tickers if t not in blacklist
    }

    results: Dict[str, TickerResult] = defaultdict(
        lambda: TickerResult(ticker="", company="")
    )

    for post in posts:
        # Build list of (text_chunk, score) tuples to scan
        chunks = [
            (post.title, post.score),
            (post.body,  post.score),
        ] + [
            (c.body, c.score) for c in post.comments
        ]

        seen_in_post: set[str] = set()  # avoid double-counting per post

        for text, score in chunks:
            if not text:
                continue
            for ticker, pattern in patterns.items():
                if pattern.search(text):
                    if ticker not in results:
                        results[ticker] = TickerResult(
                            ticker=ticker,
                            company=tickers[ticker],
                        )
                    r = results[ticker]
                    r.mentions += 1
                    # Add score only once per post (not per chunk)
                    if post.id not in seen_in_post:
                        r.total_score += max(score, 0)  # floor at 0
                        r.post_ids.append(post.id)
                        seen_in_post.add(ticker + post.id)

    # Sort by mentions desc, then total_score desc
    sorted_results = dict(
        sorted(results.items(), key=lambda x: (-x[1].mentions, -x[1].total_score))
    )
    return sorted_results
