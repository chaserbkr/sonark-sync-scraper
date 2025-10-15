import datetime as dt
from normalizer.schemas import SyncEvent
from utils.dedupe import key_for, dedupe_events

def e(source, show, track, episode):
    return SyncEvent(source=source, medium="TV", show_or_brand=show, track_title=track, episode_or_campaign=episode)

def test_key_for_normalizes():
    a = e("Tunefind_Popular ", " The Show ", " Song A ", " S01E01 ")
    b = e("tunefind_popular", "the show", "song a", "s01e01")
    assert key_for(a) == key_for(b)

def test_dedupe_events_drops_dupes():
    events = [
        e("t1", "Show X", "Track Y", "E1"),
        e("t1", "Show X", "Track Y", "E1"),  # dup
        e("t1", "Show X", "Track Y", "E2"),  # different episode -> keep
    ]
    out = dedupe_events(events)
    assert len(out) == 2
