from __future__ import annotations
from typing import List
from .schemas import RawItem, SyncEvent

def normalize_tunefind_popular(items: List[RawItem]) -> List[SyncEvent]:
    out = []
    for it in items:
        p = it.payload
        out.append(SyncEvent(
            source=it.source,
            medium=p.get("medium", "TV"),
            show_or_brand=p.get("show"),
            episode_or_campaign=p.get("episode"),
            track_title=p.get("track_title"),
            artist=p.get("artist"),
            air_date=p.get("air_date"),
            url=it.url,
            confidence=p.get("confidence", 0.8),
            notes=p.get("notes"),
            discovered_at=it.discovered_at,
        ))
    return out


def normalize_imdb_soundtrack(items: List[RawItem]) -> List[SyncEvent]:
    out = []
    for it in items:
        p = it.payload
        out.append(SyncEvent(
            source=it.source,
            medium=p.get("medium", "TV"),
            show_or_brand=p.get("show"),
            episode_or_campaign=p.get("episode"),
            track_title=p.get("track_title"),
            artist=p.get("artist"),
            air_date=p.get("air_date"),
            url=it.url,
            confidence=p.get("confidence", 0.7),
            notes=p.get("notes"),
            discovered_at=it.discovered_at,
            # NEW:
            usage_type=p.get("usage_type"),
            feature_level=p.get("feature_level"),
            source_line_raw=p.get("source_line_raw"),
        ))
    return out

def normalize_soundtrack_net(items: List[RawItem]) -> List[SyncEvent]:
    out = []
    for it in items:
        p = it.payload
        out.append(SyncEvent(
            source=it.source,
            medium=p.get("medium", "Film"),
            show_or_brand=p.get("show"),
            episode_or_campaign=p.get("episode"),
            track_title=p.get("track_title"),
            artist=p.get("artist"),
            air_date=p.get("air_date"),
            url=it.url,
            confidence=p.get("confidence", 0.7),
            notes=p.get("notes"),
            discovered_at=it.discovered_at,
            # NEW:
            usage_type=p.get("usage_type"),
            feature_level=p.get("feature_level"),
            source_line_raw=p.get("source_line_raw"),
        ))
    return out

