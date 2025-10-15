from __future__ import annotations
from typing import List
from datetime import datetime
from playwright.sync_api import sync_playwright
from ..normalizer.schemas import RawItem

def scrape_ispot_example(ad_url: str) -> List[RawItem]:
    # Example: https://www.ispot.tv/ad/XXXX/example
    out: List[RawItem] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(ad_url, wait_until="domcontentloaded")
        # Heuristics: look for sections mentioning "Song" or "Music"
        content = page.content()
        # Very naive parse here; in practice, use bs4 on content or locator-based extraction
        lower = content.lower()
        track_title = None
        artist = None
        # simple heuristic markers
        for marker in ["song:", "music:", "soundtrack:"]:
            idx = lower.find(marker)
            if idx != -1:
                snippet = content[idx: idx+200]
                track_title = track_title or "Unknown"
                artist = artist or "Unknown"
        payload = {
            "track_title": track_title,
            "artist": artist,
            "show": None,
            "episode": None,
            "air_date": None,
            "medium": "Ad",
            "confidence": 0.5,
            "notes": "Heuristic extract; refine with specific selectors",
        }
        out.append(RawItem(source="ispot_ad_page", url=ad_url, payload=payload))
        browser.close()
    return out

if __name__ == "__main__":
    print("Usage: import and call scrape_ispot_example(ad_url)")
