"""Transform step: clean and normalize raw feedback rows."""

REQUIRED_FIELDS = ["feedback_id", "customer_id", "channel", "product", "rating", "text", "created_at"]


def clean_row(row):
    """Normalize a single row: strip whitespace, cast types, validate fields."""
    cleaned = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}

    for field in REQUIRED_FIELDS:
        if field not in cleaned or cleaned[field] in (None, ""):
            raise ValueError(f"Missing required field '{field}' in row: {row}")

    cleaned["feedback_id"] = int(cleaned["feedback_id"])
    cleaned["rating"] = int(cleaned["rating"])
    cleaned["channel"] = cleaned["channel"].lower()
    cleaned["text"] = " ".join(cleaned["text"].split())  # collapse whitespace

    if not (1 <= cleaned["rating"] <= 5):
        raise ValueError(f"Rating out of range (1-5): {cleaned['rating']}")

    return cleaned


def transform_rows(rows):
    """Clean a list of raw rows, skipping invalid ones.

    Returns (clean_rows, errors) where errors is a list of (row, exception_str).
    """
    clean_rows = []
    errors = []
    for row in rows:
        try:
            clean_rows.append(clean_row(row))
        except (ValueError, KeyError) as e:
            errors.append((row, str(e)))
    return clean_rows, errors
