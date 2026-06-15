"""Ingest step: read raw feedback CSV into a list of dicts."""

import csv
from pathlib import Path


def ingest_csv(path):
    """Read a CSV file and return a list of row dicts."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]
