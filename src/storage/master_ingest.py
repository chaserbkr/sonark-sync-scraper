from __future__ import annotations
import argparse, os
import polars as pl
from ..normalizer.schemas import SyncEvent
from ..utils.dedupe import key_for


COLUMNS = [
    'source','medium','show_or_brand','episode_or_campaign',
    'track_title','artist','air_date','discovered_at','url','confidence','notes'
]

def ensure_cols(df: pl.DataFrame) -> pl.DataFrame:
    # add any missing columns with nulls, then order columns
    for c in COLUMNS:
        if c not in df.columns:
            df = df.with_columns(pl.lit(None).alias(c))
    return df.select(COLUMNS)

def load_csv(path: str) -> pl.DataFrame:
    if not os.path.exists(path):
        return pl.DataFrame({c: [] for c in COLUMNS})
    return pl.read_csv(path, null_values=["", "None"])

def build_keys(df: pl.DataFrame) -> set[tuple[str, str, str, str]]:
    keys: set[tuple[str, str, str, str]] = set()
    for r in df.iter_rows(named=True):
        ev = SyncEvent(**r)
        keys.add(key_for(ev))
    return keys

def main():
    ap = argparse.ArgumentParser(description='Append only new rows into a master CSV (by duplicate key).')
    ap.add_argument('--in', dest='inp', required=True, help='Input CSV from latest scrape')
    ap.add_argument('--master', dest='master', required=True, help='Master CSV path (created if missing)')
    args = ap.parse_args()

    new_df = ensure_cols(load_csv(args.inp))
    master_df = ensure_cols(load_csv(args.master))

    master_keys = build_keys(master_df)
    new_rows = []
    for r in new_df.iter_rows(named=True):
        ev = SyncEvent(**r)
        k = key_for(ev)
        if k not in master_keys:
            new_rows.append(r)
            master_keys.add(k)

    out_df = master_df if not new_rows else pl.concat([master_df, pl.DataFrame(new_rows, schema=master_df.schema)], how="vertical")
    os.makedirs(os.path.dirname(args.master), exist_ok=True)
    out_df.write_csv(args.master)
    print(f"Master updated: +{len(new_rows)} new / total {out_df.height} rows -> {args.master}")

if __name__ == '__main__':
    main()
