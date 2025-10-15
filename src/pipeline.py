from __future__ import annotations
import argparse, csv
from datetime import datetime
from typing import List

from .normalizer.schemas import RawItem, SyncEvent
from .normalizer.normalize import (
    normalize_tunefind_popular,
    normalize_imdb_soundtrack,
    normalize_soundtrack_net,
)
from .scrapers.tunefind_popular import scrape_tunefind_popular
from .scrapers.imdb_soundtrack_pw import scrape_imdb_soundtrack
from .scrapers.soundtrack_net import scrape_soundtrack_net
from .utils.dedupe import dedupe_events  # if present in your file


def to_csv(path: str, rows: List[SyncEvent]):
    import polars as pl
    df = pl.DataFrame([r.model_dump() for r in rows])
    df.write_csv(path)
    print(f"Wrote {df.height} rows -> {path}")
    return df

def run(source: str, out: str, url: str | None = None, dedupe: bool = False, existing: str | None = None):
    if source == "tunefind_popular":
        raw: List[RawItem] = scrape_tunefind_popular()
        events: List[SyncEvent] = normalize_tunefind_popular(raw)
        if dedupe:
            if existing:
                # merge with existing CSV to drop previously-seen rows
                import pandas as pd, os
                if os.path.exists(existing):
                    prev = pd.read_csv(existing)
                    # Convert prev rows to SyncEvent to reuse dedupe
                    prev_events = [SyncEvent(**{**r}) for r in prev.to_dict(orient='records')]
                    events = dedupe_events(prev_events + events)
                else:
                    events = dedupe_events(events)
            else:
                events = dedupe_events(events)
        to_csv(out, events)
    elif source == "imdb_soundtrack":
        if not url:
            raise SystemExit("--url is required for imdb_soundtrack")
        raw = scrape_imdb_soundtrack(url)
        events = normalize_imdb_soundtrack(raw)
        if dedupe:
            if existing:
                import pandas as pd, os
                if os.path.exists(existing):
                    prev = pd.read_csv(existing)
                    prev_events = [SyncEvent(**{**r}) for r in prev.to_dict(orient='records')]
                    events = dedupe_events(prev_events + events)
                else:
                    events = dedupe_events(events)
            else:
                events = dedupe_events(events)
        to_csv(out, events)
    elif source == "soundtrack_net":
        if not url:
            raise SystemExit("--url is required for soundtrack_net")
        raw = scrape_soundtrack_net(url)
        events = normalize_soundtrack_net(raw)
        if dedupe:
            if existing:
                import pandas as pd, os
                if os.path.exists(existing):
                    prev = pd.read_csv(existing)
                    prev_events = [SyncEvent(**{**r}) for r in prev.to_dict(orient='records')]
                    events = dedupe_events(prev_events + events)
                else:
                    events = dedupe_events(events)
            else:
                events = dedupe_events(events)
        to_csv(out, events)
    else:
        raise SystemExit(f"Unknown source: {source}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["tunefind_popular", "imdb_soundtrack", "soundtrack_net"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--url", required=False)
    ap.add_argument("--dedupe", action="store_true", help="Drop duplicate events by key")
    ap.add_argument("--existing", required=False, help="Path to previous CSV to dedupe against")
    args = ap.parse_args()
    run(args.source, args.out, url=args.url, dedupe=args.dedupe, existing=args.existing)
