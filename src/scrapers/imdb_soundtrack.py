from __future__ import annotations
from typing import List, Optional
from bs4 import BeautifulSoup
from ..utils.http import get, RateLimiter
from ..normalizer.schemas import RawItem
import re

def _title_from_head(soup: BeautifulSoup) -> Optional[str]:
    # Prefer <title>, fall back to og:title, strip " - Soundtracks - IMDb"
    t = soup.select_one("title")
    if t and t.get_text(strip=True):
        raw = t.get_text(" ", strip=True)
        return re.sub(r"\s*-\s*Soundtracks.*$", "", raw)
    og = soup.select_one('meta[property="og:title"]')
    if og and og.get("content"):
        raw = og["content"]
        return re.sub(r"\s*-\s*Soundtracks.*$", "", raw)
    # last resort: h1 on some layouts
    h1 = soup.select_one("h1")
    return h1.get_text(" ", strip=True) if h1 else None

def _guess_medium(title_text: Optional[str]) -> str:
    if title_text and "TV Series" in title_text:
        return "TV"
    return "Film"

def _classify_usage(line: str) -> tuple[str, str]:
    t = line.lower()
    if "opening theme" in t or "main title" in t:
        return "theme_open", "featured"
    if "end credits" in t or "closing theme" in t:
        return "credits", "featured"
    if "theme" in t:
        return "theme_open", "prominent"
    return "needle_drop", "background"

def _parse_line(text: str) -> tuple[Optional[str], Optional[str], float, str]:
    # normalize whitespace
    clean = " ".join(text.split())

    # 1) Quoted song title (handles “ ” or " ")
    m = re.search(r"[“\"]([^”\"]+)[”\"]", clean)
    track = m.group(1).strip() if m else None

    # 2) Fallback: "Title - Artist"
    if not track:
        parts = clean.split(" - ", 1)
        if len(parts) == 2 and 1 <= len(parts[0].split()) <= 12:
            track = parts[0].strip()

    # artist from "Performed by X" or "by X"
    artist = None
    m2 = re.search(r"Performed by\s+([^.;|]+)", clean, flags=re.I)
    if m2:
        artist = m2.group(1).strip()
    else:
        m3 = re.search(r"\bby\s+([^.;|]+)", clean, flags=re.I)
        if m3:
            artist = m3.group(1).strip()

    conf = 0.9 if track else 0.6
    return track, artist, conf, clean

def scrape_imdb_soundtrack(title_url: str) -> List[RawItem]:
    if not title_url.endswith("/soundtrack/"):
        title_url = title_url.rstrip("/") + "/soundtrack/"

    rl = RateLimiter(min_interval=1.0)
    rl.wait()
    resp = get(title_url)
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    title_text = _title_from_head(soup) or "Unknown Title"
    medium = _guess_medium(title_text)

    # IMDb often uses #soundtracks_content; back up with common list selectors
    container = soup.select_one("#soundtracks_content") or soup
    nodes = container.select("li, .soundTrack li, .ipc-metadata-list__item")

    items: List[RawItem] = []
    for n in nodes:
        txt = n.get_text(" ", strip=True)
        if not txt:
            continue
        track, artist, conf, clean = _parse_line(txt)
        u_type, feat = _classify_usage(clean)
        payload = {
            "track_title": track,
            "artist": artist,
            "show": title_text,
            "episode": None,
            "air_date": None,
            "medium": medium,
            "confidence": conf,
            "notes": clean[:600],
            "usage_type": u_type,
            "feature_level": feat,
            "source_line_raw": clean,
        }
        items.append(RawItem(source="imdb_soundtrack", url=title_url, payload=payload))

    # Debug: if we somehow found zero nodes, save HTML to inspect
    if not items:
        with open("data/imdb_debug.html", "w", encoding="utf-8") as f:
            f.write(html)

    return items
