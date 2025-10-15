from __future__ import annotations
from typing import Iterable, List, Tuple, Set
from dataclasses import dataclass

from ..normalizer.schemas import SyncEvent


def key_for(event: SyncEvent) -> tuple[str, str, str, str]:
    import hashlib
    def norm(x: str | None) -> str:
        return (x or "").strip().lower()
    sig = (event.source_line_raw or event.notes or "")[:200] + "|" + (event.url or "")
    h = hashlib.md5(sig.encode("utf-8")).hexdigest()[:8]
    return (
        norm(event.source),
        norm(event.show_or_brand),
        (norm(event.track_title) or "no-title") + f"|{h}",
        norm(event.episode_or_campaign),
    )


def dedupe_events(events: Iterable[SyncEvent]) -> List[SyncEvent]:
    seen: Set[Tuple[str, str, str, str]] = set()
    out: List[SyncEvent] = []
    for e in events:
        k = key_for(e)
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    return out
