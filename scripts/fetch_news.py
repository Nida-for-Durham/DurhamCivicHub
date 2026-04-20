"""
fetch_news.py
=============
Fetches RSS feeds from Durham-area news sources, filters for Durham County
relevance, deduplicates, sorts by date, and writes to ../news.json.

Run by the GitHub Action daily, or manually:
    python scripts/fetch_news.py
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import requests

# ── RSS feed sources ────────────────────────────────────────────────────────
FEEDS = [
    {
        "source": "WRAL News",
        "url": "https://www.wral.com/rss/news/local/",
        "default_tag": "local",
    },
    {
        "source": "Indy Week",
        "url": "https://indyweek.com/feed/",
        "default_tag": "local",
    },
    {
        "source": "9th Street Journal",
        "url": "https://9thstreetjournal.org/feed/",
        "default_tag": "local",
        "always_durham": True,   # This outlet covers Durham exclusively
    },
    {
        "source": "WUNC (NPR)",
        "url": "https://www.wunc.org/rss.xml",
        "default_tag": "local",
    },
    {
        "source": "NC Policy Watch",
        "url": "https://ncpolicywatch.com/feed/",
        "default_tag": "commissioners",
    },
    {
        "source": "Triangle Business Journal",
        "url": "https://www.bizjournals.com/triangle/rss/all",
        "default_tag": "development",
    },
    {
        "source": "Durham County Government",
        "url": "https://www.dconc.gov/Home/Components/News/News/RSSFeed.aspx",
        "default_tag": "commissioners",
        "always_durham": True,
    },
]

# ── Durham relevance filter ─────────────────────────────────────────────────
DURHAM_KEYWORDS = [
    r"\bdurham\b",
    r"\bdurham county\b",
    r"\bdurham public schools\b",
    r"\bdps\b",
    r"\bnida allam\b",
    r"\bboard of commissioners\b",
    r"\bwendy jacobs\b",
    r"\bheidi carter\b",
    r"\bamerican tobacco\b",
    r"\bbriar creek\b",
    r"\bellerbe creek\b",
    r"\bgotriangl\b",          # catches GoTriangle
    r"\bdurham center access\b",
    r"\bdcaelections\b",
    r"\bsouthpoint\b",
    r"\bfive points\b",
    r"\beast durham\b",
    r"\bnorth durham\b",
    r"\bsouth durham\b",
]
DURHAM_RE = re.compile("|".join(DURHAM_KEYWORDS), re.IGNORECASE)

# ── Tag inference ───────────────────────────────────────────────────────────
TAG_RULES = [
    (r"\bschool|dps|superintendent|student|education|teacher\b",  "schools"),
    (r"\bbudget|tax|fiscal|appropriat|spending|revenue\b",        "budget"),
    (r"\bhousing|afford|rent|eviction|tenant|zoning\b",           "housing"),
    (r"\bshootings?|crime|police|sheriff|safety|arrest\b",        "public-safety"),
    (r"\benvironment|creek|stormwater|flood|tree|park|open space\b", "environment"),
    (r"\btransit|bus|brt|light rail|gotriangle|commute\b",        "transit"),
    (r"\bcommissioner|county manager|board|county council\b",     "commissioners"),
]
TAG_RES = [(re.compile(p, re.IGNORECASE), tag) for p, tag in TAG_RULES]

MAX_STORIES  = 40   # cap on total stories in news.json
MAX_PER_FEED = 10   # max stories pulled from any single feed


def is_durham_relevant(entry, always_durham=False):
    if always_durham:
        return True
    text = " ".join([
        entry.get("title", ""),
        entry.get("summary", ""),
        entry.get("description", ""),
    ])
    return bool(DURHAM_RE.search(text))


def infer_tag(entry, default_tag):
    text = entry.get("title", "") + " " + entry.get("summary", "")
    for pattern, tag in TAG_RES:
        if pattern.search(text):
            return tag
    return default_tag


def parse_date(entry):
    """Return an ISO-8601 date string, falling back to today."""
    for field in ("published", "updated"):
        raw = entry.get(field)
        if raw:
            try:
                dt = parsedate_to_datetime(raw)
                return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
            except Exception:
                pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def format_display_date(iso_date):
    try:
        dt = datetime.strptime(iso_date, "%Y-%m-%d")
        return dt.strftime("%B %-d, %Y")
    except Exception:
        return iso_date


def clean_text(text):
    if not text:
        return ""
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_feed(feed_cfg):
    url          = feed_cfg["url"]
    source       = feed_cfg["source"]
    default_tag  = feed_cfg.get("default_tag", "local")
    always_durham = feed_cfg.get("always_durham", False)

    print(f"  Fetching: {source} …", end=" ", flush=True)
    try:
        # feedparser handles most RSS quirks; set a User-Agent to avoid blocks
        headers = {"User-Agent": "DurhamCivicHub/1.0 (https://github.com/nidaallam/durham-civic-hub)"}
        resp = requests.get(url, headers=headers, timeout=12)
        parsed = feedparser.parse(resp.text)
    except Exception as e:
        print(f"FAILED ({e})")
        return []

    stories = []
    for entry in parsed.entries[:MAX_PER_FEED]:
        if not is_durham_relevant(entry, always_durham):
            continue

        title   = clean_text(entry.get("title", "")).strip()
        excerpt = clean_text(entry.get("summary", entry.get("description", "")))
        link    = entry.get("link", "")
        date    = parse_date(entry)
        tag     = infer_tag(entry, default_tag)

        if not title or not link:
            continue

        # Truncate excerpt to ~200 chars without cutting words
        if len(excerpt) > 200:
            excerpt = excerpt[:200].rsplit(" ", 1)[0] + "…"

        stories.append({
            "title":       title,
            "excerpt":     excerpt,
            "link":        link,
            "source":      source,
            "date":        date,
            "displayDate": format_display_date(date),
            "tag":         tag,
        })

    print(f"{len(stories)} Durham stories found")
    return stories


def deduplicate(stories):
    """Remove duplicates by normalizing titles."""
    seen  = set()
    out   = []
    for s in stories:
        key = re.sub(r"[^a-z0-9]", "", s["title"].lower())[:60]
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out


def main():
    all_stories = []

    print("\n📡 Fetching Durham news feeds…\n")
    for feed_cfg in FEEDS:
        stories = fetch_feed(feed_cfg)
        all_stories.extend(stories)
        time.sleep(0.5)   # be polite to servers

    # Sort newest first
    all_stories.sort(key=lambda s: s["date"], reverse=True)

    # Deduplicate and cap
    all_stories = deduplicate(all_stories)[:MAX_STORIES]

    # Write output
    out_path = os.path.join(os.path.dirname(__file__), "..", "news.json")
    out_path = os.path.normpath(out_path)

    payload = {
        "updated":  datetime.now(timezone.utc).isoformat(),
        "count":    len(all_stories),
        "stories":  all_stories,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Wrote {len(all_stories)} stories to news.json")


if __name__ == "__main__":
    main()
