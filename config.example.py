"""
config.example.py — Copy this to config.py and fill in your Reddit API credentials.

How to get credentials:
  1. Go to https://www.reddit.com/prefs/apps
  2. Click "Create another app…" at the bottom
  3. Choose "script" as the app type
  4. Fill in a name (e.g. "wsb-tracker") and redirect URI: http://localhost:8080
  5. Copy the client_id (under the app name) and client_secret

Optional: username/password enable higher rate limits (authenticated requests).
"""

REDDIT_CLIENT_ID     = "YOUR_CLIENT_ID_HERE"
REDDIT_CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
REDDIT_USER_AGENT    = "wsb-ticker-tracker/1.0 by YOUR_USERNAME"

# Optional — leave blank for read-only (anonymous) access
REDDIT_USERNAME = ""
REDDIT_PASSWORD = ""

# ── Scraping settings ─────────────────────────────────────────────────────
SUBREDDIT     = "wallstreetbets"   # subreddit to scan
SORT          = "hot"              # hot | new | top | rising
POST_LIMIT    = 100                # number of posts to fetch (max 1000)
COMMENT_LIMIT = 20                 # top comments per post (0 = skip comments)

# ── Dashboard settings ────────────────────────────────────────────────────
TOP_N         = 25                 # how many tickers to show in the table
REFRESH_SECS  = 0                  # auto-refresh interval in seconds (0 = run once)
