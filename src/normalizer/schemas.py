from __future__ import annotations
from typing import Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field


class RawItem(BaseModel):
    """
    One scraped list item before normalization.
    """
    source: str                     # e.g., "imdb_soundtrack" or "soundtrack_net"
    url: str                        # page URL we scraped it from
    payload: Dict[str, Any]         # raw fields from the scraper
    discovered_at: datetime = Field(default_factory=datetime.utcnow)


class SyncEvent(BaseModel):
    """
    Canonical row we write to CSV/master.
    Keep fields optional so partial pages don't crash the run.
    """
    source: str
    medium: Optional[str] = None                    # "TV" / "Film" / etc.
    show_or_brand: Optional[str] = None            # series/film/brand name
    episode_or_campaign: Optional[str] = None
    track_title: Optional[str] = None
    artist: Optional[str] = None
    air_date: Optional[date] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    url: Optional[str] = None
    confidence: float = 0.7
    notes: Optional[str] = None

    # NEW fields for PML use:
    usage_type: Optional[str] = None               # e.g., theme_open, credits, needle_drop
    feature_level: Optional[str] = None            # featured, prominent, background
    source_line_raw: Optional[str] = None          # exact line we parsed
