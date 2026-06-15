import json
import pytest

from src.enrich import parse_enrichment_response, ENRICH_KEYS


def test_parse_enrichment_response_clean_json():
    raw = json.dumps({
        "sentiment": "negative",
        "topics": ["billing", "app_crash"],
        "entities": ["Mobile App"],
        "urgency": "high",
    })
    result = parse_enrichment_response(raw)
    assert result["sentiment"] == "negative"
    assert result["topics"] == ["billing", "app_crash"]
    assert result["entities"] == ["Mobile App"]
    assert result["urgency"] == "high"
    assert set(result.keys()) == set(ENRICH_KEYS)


def test_parse_enrichment_response_with_code_fence():
    raw = "```json\n" + json.dumps({
        "sentiment": "positive", "topics": [], "entities": [], "urgency": "low"
    }) + "\n```"
    result = parse_enrichment_response(raw)
    assert result["sentiment"] == "positive"


def test_parse_enrichment_response_invalid_sentiment_defaults_neutral():
    raw = json.dumps({"sentiment": "ecstatic", "topics": [], "entities": [], "urgency": "low"})
    result = parse_enrichment_response(raw)
    assert result["sentiment"] == "neutral"


def test_parse_enrichment_response_invalid_urgency_defaults_low():
    raw = json.dumps({"sentiment": "neutral", "topics": [], "entities": [], "urgency": "critical"})
    result = parse_enrichment_response(raw)
    assert result["urgency"] == "low"


def test_parse_enrichment_response_coerces_string_topics():
    raw = json.dumps({"sentiment": "neutral", "topics": "billing", "entities": [], "urgency": "low"})
    result = parse_enrichment_response(raw)
    assert result["topics"] == ["billing"]


def test_parse_enrichment_response_invalid_json_raises():
    with pytest.raises(ValueError):
        parse_enrichment_response("not json")


def test_parse_enrichment_response_missing_keys_default():
    raw = json.dumps({})
    result = parse_enrichment_response(raw)
    assert result["sentiment"] == "neutral"
    assert result["urgency"] == "low"
    assert result["topics"] == []
    assert result["entities"] == []
