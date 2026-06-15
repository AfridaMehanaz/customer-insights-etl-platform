"""Load step: write enriched feedback rows into a SQLite warehouse."""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id   INTEGER PRIMARY KEY,
    customer_id   TEXT NOT NULL,
    channel       TEXT NOT NULL,
    product       TEXT NOT NULL,
    rating        INTEGER NOT NULL,
    text          TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    sentiment     TEXT,
    topics        TEXT,
    entities      TEXT,
    urgency       TEXT
);
"""

INSERT_SQL = """
INSERT OR REPLACE INTO feedback
    (feedback_id, customer_id, channel, product, rating, text, created_at,
     sentiment, topics, entities, urgency)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def get_connection(db_path):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def load_rows(conn, rows):
    """Insert enriched rows into the feedback table. Rows may lack enrichment keys."""
    for row in rows:
        conn.execute(
            INSERT_SQL,
            (
                row["feedback_id"],
                row["customer_id"],
                row["channel"],
                row["product"],
                row["rating"],
                row["text"],
                row["created_at"],
                row.get("sentiment"),
                ",".join(row.get("topics", [])) if isinstance(row.get("topics"), list) else row.get("topics"),
                ",".join(row.get("entities", [])) if isinstance(row.get("entities"), list) else row.get("entities"),
                row.get("urgency"),
            ),
        )
    conn.commit()


def fetch_all(conn):
    cur = conn.execute("SELECT * FROM feedback")
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]
