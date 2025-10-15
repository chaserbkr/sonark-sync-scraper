from __future__ import annotations
import argparse
import pandas as pd
from sqlalchemy import create_engine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--table", default="sync_events")
    parser.add_argument("--db", default=None, help="Override DATABASE_URL; default reads env")
    args = parser.parse_args()

    import os
    url = args.db or os.getenv("DATABASE_URL", "sqlite:///data/sync.db")
    engine = create_engine(url)
    df = pd.read_csv(args.csv)
    df.to_sql(args.table, engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into {args.table} @ {url}")

if __name__ == "__main__":
    main()
