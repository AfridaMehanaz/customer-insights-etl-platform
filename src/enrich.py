"""LLM enrichment step: sentiment, topics, entities, urgency per feedback row.

Output schema per row (dict):
{
  "sentiment": "positive" | "negative" | "neutral",
  "topics": [str, ...],
  "entities": [str, ...],
  "urgency": "low" | "medium" | "high"
}
"""

import json
import re

from src.llm_client import chat_completion

ENRICH_KEYS = ["sentiment", "topics", "entities", "urgency"]
VALID_SENTIMENT = {"positive", "negative", "neutral"}
VALID_URGENCY = {"low", "medium", "high"}

SYSTEM_PROMPT = (
    "You are an NLP enrichment engine for customer feedback. Given a piece "
    "of customer feedback text, return ONLY a JSON object with these exact keys:\n"
    '  "sentiment": one of "positive", "negative", "neutral"\n'
    '  "topics": list of short topic strings (e.g. "billing", "app_crash", "customer_service")\n'
    '  "entities": list of named entities mentioned (products, services, amounts)\n'
    '  "urgency": one of "low", "medium", "high" (high = needs immediate attention, '
    "e.g. fraud, unauthorized charges, account access issues)\n"
    "Do not include markdown formatting, code fences, or any text outside the JSON object."
)


def build_prompt(text):
    return f"Customer feedback:\n\"{text}\""


def _extract_json(text):
    text = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
    return json.loads(text)


def parse_enrichment_response(raw_text):
    """Parse raw LLM output into the enrichment schema dict.

    Raises ValueError if the response cannot be parsed into valid JSON.
    Invalid/missing values fall back to safe defaults.
    """
    data = _extract_json(raw_text)
    if not isinstance(data, dict):
        raise ValueError("Enrichment response is not a JSON object")

    sentiment = str(data.get("sentiment", "neutral")).lower().strip()
    if sentiment not in VALID_SENTIMENT:
        sentiment = "neutral"

    urgency = str(data.get("urgency", "low")).lower().strip()
    if urgency not in VALID_URGENCY:
        urgency = "low"

    def _to_list(value):
        if isinstance(value, list):
            return [str(v) for v in value]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    return {
        "sentiment": sentiment,
        "topics": _to_list(data.get("topics", [])),
        "entities": _to_list(data.get("entities", [])),
        "urgency": urgency,
    }


def enrich_text(text):
    """Call the LLM and return a structured enrichment dict for one text."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_prompt(text)},
    ]
    raw = chat_completion(messages)
    return parse_enrichment_response(raw)


def enrich_rows(rows):
    """Enrich a list of transformed rows in place, returning new dicts with
    sentiment/topics/entities/urgency merged in. Rows that fail enrichment
    get safe defaults and an 'enrich_error' note.
    """
    enriched = []
    for row in rows:
        new_row = dict(row)
        try:
            result = enrich_text(row["text"])
            new_row.update(result)
        except Exception as e:
            new_row.update({
                "sentiment": "neutral",
                "topics": [],
                "entities": [],
                "urgency": "low",
                "enrich_error": str(e),
            })
        enriched.append(new_row)
    return enriched
