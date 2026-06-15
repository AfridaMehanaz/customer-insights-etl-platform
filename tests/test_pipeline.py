import csv
from pathlib import Path

import pytest

from src.ingest import ingest_csv
from src.transform import transform_rows
from src.load import get_connection, load_rows, fetch_all


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "feedback.csv"
    rows = [
        {
            "feedback_id": "1",
            "customer_id": "CUST1000",
            "channel": "email",
            "product": "Checking Account",
            "rating": "5",
            "text": "Great experience overall",
            "created_at": "2026-01-01 00:00:00",
        },
        {
            "feedback_id": "2",
            "customer_id": "CUST1001",
            "channel": "chat",
            "product": "Mobile App",
            "rating": "1",
            "text": "App crashes constantly, urgent fix needed",
            "created_at": "2026-01-02 00:00:00",
        },
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_ingest_csv_reads_rows(sample_csv):
    rows = ingest_csv(sample_csv)
    assert len(rows) == 2
    assert rows[0]["customer_id"] == "CUST1000"


def test_ingest_csv_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        ingest_csv("does/not/exist.csv")


def test_load_rows_without_enrichment(tmp_path, sample_csv):
    rows = ingest_csv(sample_csv)
    clean_rows, errors = transform_rows(rows)
    assert errors == []

    db_path = tmp_path / "test.db"
    conn = get_connection(db_path)
    load_rows(conn, clean_rows)

    stored = fetch_all(conn)
    assert len(stored) == 2
    assert stored[0]["sentiment"] is None
    conn.close()


def test_load_rows_with_enrichment_fields(tmp_path, sample_csv):
    rows = ingest_csv(sample_csv)
    clean_rows, _ = transform_rows(rows)

    enriched = []
    for row in clean_rows:
        row = dict(row)
        row["sentiment"] = "positive"
        row["topics"] = ["billing", "support"]
        row["entities"] = ["Mobile App"]
        row["urgency"] = "low"
        enriched.append(row)

    db_path = tmp_path / "test.db"
    conn = get_connection(db_path)
    load_rows(conn, enriched)

    stored = fetch_all(conn)
    assert stored[0]["sentiment"] == "positive"
    assert stored[0]["topics"] == "billing,support"
    conn.close()
