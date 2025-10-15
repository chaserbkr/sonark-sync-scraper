# Sonark Sync Scraper Boilerplate

Production-ready starter to scrape publicly visible sync-related sources (e.g., Tunefind Popular) and normalize into a single dataset. 
Uses Python + Requests/BS4 + Playwright (for dynamic pages), Pydantic for schemas, and SQLite (or Postgres) for storage.

## Quickstart

```bash
# 1) Create & activate venv
python3 -m venv .venv && source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) (Optional) Install Playwright browsers for dynamic sites like iSpot
playwright install

# 4) Configure env
cp .env.example .env
# No external enrichment APIs (Spotify/TikTok/YouTube) are required in this version.

# 5) Run a scrape of Tunefind Popular + normalize + save
python src/pipeline.py --source tunefind_popular --out data/tunefind_popular.csv

# 6) (Optional) Load into SQLite
python src/storage/db.py --csv data/tunefind_popular.csv --table sync_events

# 7) (Optional) Schedule daily (GitHub Actions)
# See .github/workflows/scrape.yml
```

## Data Schema (CSV/DB)
Unified columns emitted by the normalizer:
- `source`: data origin (e.g., "tunefind_popular")
- `medium`: one of {TV, Film, Ad, Other}
- `show_or_brand`: show title or brand name
- `episode_or_campaign`: episode (SxxExx) or campaign label if known
- `track_title`: song title
- `artist`: primary performing artist
- `air_date`: ISO date when the content aired (if available)
- `discovered_at`: ISO timestamp when we observed it
- `url`: canonical URL where we saw this
- `confidence`: float 0..1 (our parser confidence)
- `notes`: free text notes

## Legal & Robots
- Check each site's robots.txt and Terms. Prefer official APIs where available (Spotify, YouTube, Reddit).
- Use polite rate limiting, backoff, and caching. This repo includes basic throttling hooks.

## Extending
Add a new scraper in `src/scrapers/your_source.py` that returns a list of `RawItem` objects. 
Then register it in `src/pipeline.py` and optionally create an enricher in `src/enrichment/`.


## New: IMDb & Soundtrack.net Scrapers

Run with a title-specific URL:

```bash
# IMDb title soundtrack page
python src/pipeline.py --source imdb_soundtrack --url https://www.imdb.com/title/tt0944947/soundtrack/ --out data/imdb_got_songs.csv

# Soundtrack.net title page (movie or series album page)
python src/pipeline.py --source soundtrack_net --url https://www.soundtrack.net/album/some-show-season-1/ --out data/soundtracknet_show.csv
```

Both scrapers output the same unified `SyncEvent` schema.
Note: HTML structure can vary; feel free to tighten selectors per-title as needed.


## Testing
Run unit tests with pytest:
```bash
pytest -q
```

## Dedupe Usage
Drop duplicate events (by `source + show_or_brand + track_title + episode_or_campaign`):
```bash
# New scrape, dedupe within batch
python src/pipeline.py --source tunefind_popular --out data/tunefind_popular.csv --dedupe

# Dedupe against an existing master CSV
python src/pipeline.py --source imdb_soundtrack --url https://www.imdb.com/title/tt0944947/soundtrack/   --out data/imdb_got_songs.csv --dedupe --existing data/master_sync_events.csv
```


## Master ingestion
Append only new rows (by duplicate key) into a master CSV:
```bash
python src/storage/master_ingest.py --in data/imdb_got_songs.csv --master data/master_sync_events.csv
```
