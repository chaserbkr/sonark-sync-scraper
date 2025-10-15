from normalizer.schemas import RawItem
from normalizer.normalize import normalize_tunefind_popular, normalize_imdb_soundtrack, normalize_soundtrack_net

def test_normalize_tunefind_popular_basic():
    items = [RawItem(source="tunefind_popular", url="u", payload={"track_title":"A","artist":"B","show":"S","episode":"E"})]
    out = normalize_tunefind_popular(items)
    assert out[0].track_title == "A"
    assert out[0].artist == "B"
    assert out[0].show_or_brand == "S"
    assert out[0].episode_or_campaign == "E"

def test_normalize_imdb_and_soundtrack_net():
    items_imdb = [RawItem(source="imdb_soundtrack", url="u", payload={"track_title":"A","artist":"B","show":"S"})]
    out_imdb = normalize_imdb_soundtrack(items_imdb)
    assert out_imdb[0].track_title == "A"

    items_st = [RawItem(source="soundtrack_net", url="u", payload={"track_title":"C","artist":"D","show":"T"})]
    out_st = normalize_soundtrack_net(items_st)
    assert out_st[0].artist == "D"
