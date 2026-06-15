"""Pipeline orchestrator: ingest -> transform -> enrich -> load.

Run: python3 -m src.pipeline [--input data/raw_feedback.csv] [--db warehouse/feedback.db] [--skip-enrich]
"""

import argparse
from pathlib import Path

from src.ingest import ingest_csv
from src.transform import transform_rows
from src.load import get_connection, load_rows

DEFAULT_INPUT = "data/raw_feedback.csv"
DEFAULT_DB = "warehouse/feedback.db"


def run_pipeline(input_path=DEFAULT_INPUT, db_path=DEFAULT_DB, skip_enrich=False):
    print(f"Ingesting {input_path}...")
    raw_rows = ingest_csv(input_path)
    print(f"  {len(raw_rows)} raw rows")

    print("Transforming...")
    clean_rows, errors = transform_rows(raw_rows)
    print(f"  {len(clean_rows)} clean rows, {len(errors)} errors")
    for row, err in errors[:5]:
        print(f"    skipped: {err}")

    if skip_enrich:
        print("Skipping enrichment (--skip-enrich)")
        enriched_rows = clean_rows
    else:
        from src.enrich import enrich_rows
        print("Enriching via LLM (this calls the API for each row)...")
        enriched_rows = enrich_rows(clean_rows)

    print(f"Loading into {db_path}...")
    conn = get_connection(db_path)
    load_rows(conn, enriched_rows)
    conn.close()

    print("Done.")
    return len(enriched_rows), len(errors)


def main():
    parser = argparse.ArgumentParser(description="Customer insights ETL pipeline")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--skip-enrich", action="store_true",
                         help="Skip LLM enrichment (loads raw sentiment fields as null)")
    args = parser.parse_args()

    run_pipeline(args.input, args.db, args.skip_enrich)


if __name__ == "__main__":
    main()
