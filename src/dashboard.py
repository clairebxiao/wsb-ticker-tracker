"""
dashboard.py — Renders a rich terminal dashboard of ticker mention results.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.style import Style

from src.parser import TickerResult

console = Console()


def _rank_badge(rank: int) -> str:
    if rank == 1:
        return "🥇"
    if rank == 2:
        return "🥈"
    if rank == 3:
        return "🥉"
    return f"#{rank}"


def _score_color(score: int) -> str:
    if score >= 10_000:
        return "bold bright_green"
    if score >= 5_000:
        return "green"
    if score >= 1_000:
        return "yellow"
    if score >= 100:
        return "white"
    return "dim white"


def _bar(value: int, max_value: int, width: int = 20) -> str:
    if max_value == 0:
        return ""
    filled = int((value / max_value) * width)
    return "█" * filled + "░" * (width - filled)


def render_dashboard(
    results: Dict[str, TickerResult],
    top_n: int = 25,
    subreddit: str = "wallstreetbets",
    sort_mode: str = "hot",
    post_count: int = 0,
) -> None:
    """Print a full terminal dashboard for the parsed ticker results."""

    console.clear()

    # ── Header ────────────────────────────────────────────────────────────
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    header = Text()
    header.append("📈  WSB Ticker Tracker", style="bold bright_white")
    header.append(f"   r/{subreddit}  ·  {sort_mode.upper()}  ·  {post_count} posts scanned", style="dim")
    header.append(f"\n🕐  {now}", style="dim")

    console.print(Panel(header, box=box.ROUNDED, border_style="bright_blue", padding=(0, 2)))
    console.print()

    if not results:
        console.print("[yellow]No ticker mentions found.[/yellow]")
        return

    top_results = list(results.values())[:top_n]
    max_mentions = top_results[0].mentions if top_results else 1
    max_score = max((r.total_score for r in top_results), default=1)

    # ── Main table ────────────────────────────────────────────────────────
    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style="bright_blue",
        header_style="bold bright_cyan",
        show_edge=True,
        expand=False,
    )

    table.add_column("Rank",        justify="center", width=6,  no_wrap=True)
    table.add_column("Ticker",      justify="left",   width=8,  style="bold bright_yellow")
    table.add_column("Company",     justify="left",   width=30, style="white")
    table.add_column("Mentions",    justify="right",  width=10, style="bright_cyan")
    table.add_column("Mention Bar", justify="left",   width=22, no_wrap=True)
    table.add_column("Vote Score",  justify="right",  width=12)
    table.add_column("Avg Score",   justify="right",  width=10, style="dim")

    for rank, result in enumerate(top_results, start=1):
        mention_bar = _bar(result.mentions, max_mentions)
        score_style = _score_color(result.total_score)
        score_text = Text(f"{result.total_score:,}", style=score_style)

        table.add_row(
            _rank_badge(rank),
            result.ticker,
            result.company[:28] + ("…" if len(result.company) > 28 else ""),
            str(result.mentions),
            f"[bright_cyan]{mention_bar}[/bright_cyan]",
            score_text,
            f"{result.avg_score:,.1f}",
        )

    console.print(table)

    # ── Summary stats ─────────────────────────────────────────────────────
    total_mentions = sum(r.mentions for r in results.values())
    unique_tickers = len(results)

    stats = [
        Panel(
            f"[bold bright_yellow]{unique_tickers}[/bold bright_yellow]\n[dim]Unique Tickers[/dim]",
            box=box.ROUNDED, border_style="dim", padding=(0, 2), expand=False
        ),
        Panel(
            f"[bold bright_cyan]{total_mentions:,}[/bold bright_cyan]\n[dim]Total Mentions[/dim]",
            box=box.ROUNDED, border_style="dim", padding=(0, 2), expand=False
        ),
        Panel(
            f"[bold bright_green]{top_results[0].ticker if top_results else '—'}[/bold bright_green]\n[dim]Most Mentioned[/dim]",
            box=box.ROUNDED, border_style="dim", padding=(0, 2), expand=False
        ),
        Panel(
            f"[bold bright_magenta]{max(results.values(), key=lambda r: r.total_score).ticker if results else '—'}[/bold bright_magenta]\n[dim]Highest Vote Score[/dim]",
            box=box.ROUNDED, border_style="dim", padding=(0, 2), expand=False
        ),
    ]

    console.print(Columns(stats, equal=False, expand=False))
    console.print()
