"""
scraper.py — Fetches posts and comments from r/wallstreetbets via PRAW.
"""

from __future__ import annotations
import time
import praw
from dataclasses import dataclass, field
from typing import List


@dataclass
class Post:
    id: str
    title: str
    body: str
    score: int
    url: str
    comments: List["Comment"] = field(default_factory=list)


@dataclass
class Comment:
    id: str
    body: str
    score: int


def build_reddit_client(
    client_id: str,
    client_secret: str,
    user_agent: str,
    username: str = "",
    password: str = "",
) -> praw.Reddit:
    """Initialise and return an authenticated PRAW Reddit client."""
    kwargs = dict(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )
    if username and password:
        kwargs["username"] = username
        kwargs["password"] = password
    return praw.Reddit(**kwargs)


def fetch_posts(
    reddit: praw.Reddit,
    subreddit_name: str = "wallstreetbets",
    sort: str = "hot",
    limit: int = 100,
    comment_limit: int = 20,
    verbose: bool = True,
) -> List[Post]:
    """
    Fetch posts (and their top comments) from a subreddit.

    Parameters
    ----------
    reddit        : authenticated PRAW Reddit instance
    subreddit_name: target subreddit (default 'wallstreetbets')
    sort          : 'hot' | 'new' | 'top' | 'rising'
    limit         : number of posts to fetch (max 1000)
    comment_limit : top-N comments to fetch per post (0 = skip comments)
    verbose       : print progress to stdout
    """
    sub = reddit.subreddit(subreddit_name)
    sort_map = {
        "hot":    sub.hot,
        "new":    sub.new,
        "top":    sub.top,
        "rising": sub.rising,
    }
    fetcher = sort_map.get(sort, sub.hot)

    posts: List[Post] = []

    if verbose:
        print(f"[scraper] Fetching {limit} '{sort}' posts from r/{subreddit_name}…")

    for submission in fetcher(limit=limit):
        # Skip stickied mod posts
        if submission.stickied:
            continue

        post = Post(
            id=submission.id,
            title=submission.title,
            body=submission.selftext or "",
            score=submission.score,
            url=f"https://reddit.com{submission.permalink}",
        )

        if comment_limit > 0:
            try:
                submission.comments.replace_more(limit=0)
                for comment in submission.comments[:comment_limit]:
                    if hasattr(comment, "body") and comment.body not in ("[deleted]", "[removed]"):
                        post.comments.append(
                            Comment(
                                id=comment.id,
                                body=comment.body,
                                score=comment.score,
                            )
                        )
            except Exception:
                pass  # skip comment errors silently

        posts.append(post)

    if verbose:
        total_comments = sum(len(p.comments) for p in posts)
        print(f"[scraper] Retrieved {len(posts)} posts, {total_comments} comments.")

    return posts
