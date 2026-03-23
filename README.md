# 📈 WSB Ticker Tracker

A Python tool that scrapes **r/wallstreetbets** and ranks stock tickers by how often they're mentioned — and how many upvotes those posts/comments carry.

Uses a **dictionary-based matching approach**: only tickers in the curated dictionary are counted, with whole-word regex matching to avoid false positives.

---

## Features

- Scans **post titles, bodies, and comments**
- Ranks tickers by **mention count** and **aggregate vote score**
- Beautiful **terminal dashboard** powered by `rich`
- Optional **auto-refresh** mode for live monitoring
- CLI flags to override sort, post limit, and display count
- 200+ tickers pre-loaded including S&P 500, WSB meme stocks, and crypto-adjacent plays

---

## Quickstart

### 1. Clone & install dependencies

```bash
git clone https://github.com/YOUR_USERNAME/wsb-ticker-tracker.git
cd wsb-ticker-tracker
pip install -r requirements.txt
```

### 2. Set up Reddit API credentials

Go to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) and create a **script** app.

Then copy the example config:

```bash
cp config.example.py config.py
```

Open `config.py` and fill in your `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, and `REDDIT_USER_AGENT`.

### 3. Run it

```bash
python main.py
```

---

## Usage

```
python main.py [OPTIONS]

Options:
  --subreddit   Subreddit to scan (default: wallstreetbets)
  --sort        Sort mode: hot | new | top | rising  (default: hot)
  --limit       Number of posts to fetch, max 1000   (default: 100)
  --comments    Top comments per post, 0 = skip      (default: 20)
  --top         Tickers to display in dashboard      (default: 25)
  --refresh     Auto-refresh interval in seconds, 0 = run once (default: 0)
```

### Examples

```bash
# Scan top 200 hot posts, show top 30 tickers
python main.py --limit 200 --top 30

# Scan 'new' posts, refresh every 5 minutes
python main.py --sort new --refresh 300

# Scan only titles and bodies (no comments)
python main.py --comments 0
```

---

## Project Structure

```
wsb-ticker-tracker/
├── main.py              # Entry point & CLI
├── config.example.py    # Template — copy to config.py
├── requirements.txt
└── src/
    ├── tickers.py       # Ticker → Company Name dictionary
    ├── scraper.py       # Reddit API fetching via PRAW
    ├── parser.py        # Ticker extraction & scoring logic
    └── dashboard.py     # Rich terminal dashboard renderer
```

---

## How It Works

1. **Scraper** (`scraper.py`) — Uses PRAW to pull posts from the target subreddit. For each post it grabs the title, body text, and top N comments.
2. **Parser** (`parser.py`) — Iterates over every text chunk and applies whole-word regex patterns for each ticker in the dictionary. For each match it increments the mention counter and adds the post's vote score to a running total.
3. **Dashboard** (`dashboard.py`) — Uses `rich` to render a sorted table with rank, ticker, company name, mention count, a visual bar chart, total vote score, and average score per mention.

### Why dictionary-based?

Pure regex on uppercase words generates tons of noise (`I`, `THE`, `FOR`, `DD`, `YOLO`, etc.). By only counting tickers that exist in our curated dictionary, false positives are dramatically reduced. The `BLACKLIST` in `tickers.py` handles edge cases where real tickers are also common English words.

---

## Adding Tickers

Open `src/tickers.py` and add entries to the `TICKERS` dict:

```python
"NVDA": "NVIDIA Corporation",
"PLTR": "Palantir Technologies",
```

If a ticker clashes with a common word, add it to `BLACKLIST` instead.

---

## License

MIT
