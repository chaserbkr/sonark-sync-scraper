from __future__ import annotations
from typing import List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from ..utils.http import get, RateLimiter
from ..normalizer.schemas import RawItem

def scrape_soundtrack_net(title_url: str) -> List[RawItem]:
    """Scrape a Soundtrack.net title page listing tracks.
    Example: https://www.soundtrack.net/album/series-name-season-1/  OR /movie/xyz/
    """
    rl = RateLimiter(min_interval=1.0)
    rl.wait()
    resp = get(title_url)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Title context
    title_tag = soup.select_one("h1.entry-title, h1")
    title_text = title_tag.get_text(" ", strip=True) if title_tag else None

    items: List[RawItem] = []
    # Typical content: tracklists under .tracklisting or tables
    rows = soup.select(".tracklisting li, table tr, .tracklist li, .albumtracks li")
    if not rows:
        rows = soup.select("li")  # very loose fallback

    for r in rows:
        text = r.get_text(" ", strip=True)
        if not text:
            continue
        # Basic parse: "01. Song Name – Artist" or "Song Name - Performer"
        track_title = None
        artist = None
        parts = [p.strip() for p in text.split("–")]
        if len(parts) == 2:
            track_title, artist = parts[0], parts[1]
            # Strip leading track numbers like "01. "
            track_title = track_title.split(". ", 1)[-1]
        else:
            # Try hyphen
            parts = [p.strip() for p in text.split("-")]
            if len(parts) == 2:
                track_title, artist = parts[0], parts[1]
                track_title = track_title.split(". ", 1)[-1]

        payload = {
            "track_title": track_title,
            "artist": artist,
            "show": title_text,
            "episode": None,
            "air_date": None,
            "medium": "TV" if "tv" in title_url else "Film",
            "confidence": 0.65 if track_title else 0.5,
            "notes": text[:400],
        }
        items.append(RawItem(source="soundtrack_net", url=title_url, payload=payload))

    return items
