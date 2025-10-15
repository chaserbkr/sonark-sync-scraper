from __future__ import annotations
from typing import List
from bs4 import BeautifulSoup
from datetime import datetime
from ..utils.http import get, RateLimiter
from ..normalizer.schemas import RawItem

BASE = "https://www.tunefind.com/popular"

def scrape_tunefind_popular() -> List[RawItem]:
    rl = RateLimiter(min_interval=1.0)
    rl.wait()
    resp = get(BASE)
    soup = BeautifulSoup(resp.text, "html.parser")

    items: List[RawItem] = []
    # Tunefind popular page lists weekly charts with track rows
    # We look for common CSS patterns: 'chart', 'chart-row', etc.
    for row in soup.select(".chart-row, .Main .SongRow, .SongListItem"):
        try:
            track = row.select_one(".songTitle, .title, .SongTitle")
            artist = row.select_one(".artist, .Artist, .subtitle")
            link = row.select_one("a[href]")
            # show/episode context sometimes present near the row
            context = row.select_one(".details, .context, .source")
            url = link["href"] if link else BASE

            payload = {
                "track_title": track.get_text(strip=True) if track else None,
                "artist": artist.get_text(strip=True) if artist else None,
                "show": None,
                "episode": None,
                "air_date": None,
                "medium": "TV",
                "confidence": 0.75,
                "notes": context.get_text(" ", strip=True) if context else None,
            }
            items.append(RawItem(source="tunefind_popular", url=url, payload=payload))
        except Exception:
            # skip malformed rows
            continue
    return items

if __name__ == "__main__":
    data = scrape_tunefind_popular()
    print(f"Scraped {len(data)} rows at {datetime.utcnow().isoformat()}Z")
