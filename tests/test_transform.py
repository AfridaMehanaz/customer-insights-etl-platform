import pytest

from src.transform import clean_row, transform_rows


def make_row(**overrides):
    row = {
        "feedback_id": "1",
        "customer_id": "CUST1000",
        "channel": "Email",
        "product": "Checking Account",
        "rating": "4",
        "text": "  Great   service   here  ",
        "created_at": "2026-01-01 00:00:00",
    }
    row.update(overrides)
    return row


def test_clean_row_normalizes_types_and_whitespace():
    cleaned = clean_row(make_row())
    assert cleaned["feedback_id"] == 1
    assert cleaned["rating"] == 4
    assert cleaned["channel"] == "email"
    assert cleaned["text"] == "Great service here"


def test_clean_row_missing_field_raises():
    row = make_row()
    del row["product"]
    with pytest.raises(ValueError):
        clean_row(row)


def test_clean_row_empty_field_raises():
    with pytest.raises(ValueError):
        clean_row(make_row(customer_id=""))


def test_clean_row_rating_out_of_range_raises():
    with pytest.raises(ValueError):
        clean_row(make_row(rating="9"))


def test_transform_rows_separates_errors():
    rows = [make_row(feedback_id="1"), make_row(feedback_id="2", rating="bad")]
    clean_rows, errors = transform_rows(rows)
    assert len(clean_rows) == 1
    assert len(errors) == 1
