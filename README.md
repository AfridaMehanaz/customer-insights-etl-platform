# Customer Insights ETL Platform

[![CI](https://github.com/AfridaMehanaz/customer-insights-etl-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/AfridaMehanaz/customer-insights-etl-platform/actions/workflows/ci.yml)

End-to-end ETL + LLM enrichment platform for customer feedback. Ingests raw
feedback, cleans and normalizes it, enriches it with NLP (sentiment, topics,
entities, urgency) via an LLM, loads it into a SQLite warehouse, and
visualizes insights in a Streamlit dashboard.

## Pipeline

```
data/raw_feedback.csv
        │
        ▼
   ingest.py  ──► transform.py ──► enrich.py (LLM) ──► load.py ──► warehouse/feedback.db
                                                                          │
                                                                          ▼
                                                                       app.py (dashboard)
```

- **ingest** — read raw CSV feedback rows
- **transform** — clean/normalize fields, validate, drop bad rows
- **enrich** — LLM call per row: sentiment, topics, entities, urgency
- **load** — upsert into SQLite warehouse (`warehouse/feedback.db`)
- **dashboard** — Streamlit UI: sentiment trends, topic breakdown, urgency alerts, filters

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env, set LLM_API_KEY=<your real key>
```

Default config targets Groq (`llama-3.3-70b-versatile`,
`https://api.groq.com/openai/v1`). Swap `LLM_BASE_URL` / `LLM_MODEL` in `.env`
for any OpenAI-compatible provider.

## Usage

```bash
# 1. generate synthetic feedback data (300 rows)
python3 data/generate_synthetic.py

# 2. run the full pipeline (ingest -> transform -> enrich -> load)
python3 -m src.pipeline

# or skip LLM enrichment (no API key needed, sentiment/topics left null)
python3 -m src.pipeline --skip-enrich

# 3. launch the dashboard
streamlit run app.py
```

## Tests

```bash
pytest
```

16 tests cover ingest, transform, load, and enrichment response parsing —
all run without an API key or network calls (LLM responses are tested via
parsing functions, not live calls).

## Project structure

```
customer-insights-etl-platform/
  data/
    generate_synthetic.py   # synthetic feedback data generator
    raw_feedback.csv         # generated sample data (300 rows)
  src/
    ingest.py                # CSV -> list[dict]
    transform.py              # clean/validate rows
    enrich.py                  # LLM enrichment (sentiment/topics/entities/urgency)
    load.py                     # SQLite warehouse load
    llm_client.py               # provider-agnostic OpenAI-compatible client
    pipeline.py                  # orchestrator (CLI)
  tests/                      # pytest suite (no API key needed)
  app.py                      # Streamlit dashboard
  warehouse/                  # SQLite db (generated, gitignored)
  .env.example
  requirements.txt
```
