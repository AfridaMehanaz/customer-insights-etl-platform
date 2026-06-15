"""Streamlit dashboard for customer insights warehouse.

Reads warehouse/feedback.db (built by `python3 -m src.pipeline`) and shows
sentiment trends, topic breakdown, urgency alerts, with filters.
"""

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from src.load import get_connection, fetch_all

load_dotenv()

st.set_page_config(page_title="Customer Insights Dashboard", page_icon="📊", layout="wide")
st.title("📊 Customer Insights Dashboard")
st.caption("ETL + LLM-enriched customer feedback warehouse")

DB_PATH = "warehouse/feedback.db"


@st.cache_data
def load_data(db_path, mtime):
    conn = get_connection(db_path)
    rows = fetch_all(conn)
    conn.close()
    return pd.DataFrame(rows)


if not Path(DB_PATH).exists():
    st.warning(
        "No warehouse found yet. Run the pipeline first:\n\n"
        "```\npython3 data/generate_synthetic.py\n"
        "python3 -m src.pipeline\n```\n\n"
        "(Add `--skip-enrich` to load without calling the LLM.)"
    )
    st.stop()

mtime = Path(DB_PATH).stat().st_mtime
df = load_data(DB_PATH, mtime)

if df.empty:
    st.info("Warehouse is empty. Run the pipeline to populate it.")
    st.stop()

# --- Filters ---
with st.sidebar:
    st.header("Filters")
    products = st.multiselect("Product", sorted(df["product"].unique()), default=list(df["product"].unique()))
    channels = st.multiselect("Channel", sorted(df["channel"].unique()), default=list(df["channel"].unique()))
    sentiments = df["sentiment"].dropna().unique().tolist()
    sentiment_filter = st.multiselect("Sentiment", sorted(sentiments) if sentiments else [], default=sentiments)

filtered = df[df["product"].isin(products) & df["channel"].isin(channels)]
if sentiment_filter:
    filtered = filtered[filtered["sentiment"].isin(sentiment_filter)]

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Feedback", len(filtered))
col2.metric("Avg Rating", round(filtered["rating"].mean(), 2) if len(filtered) else "-")
neg_pct = (filtered["sentiment"] == "negative").mean() * 100 if len(filtered) and "sentiment" in filtered else 0
col3.metric("Negative %", f"{neg_pct:.1f}%")
high_urgency = (filtered["urgency"] == "high").sum() if "urgency" in filtered else 0
col4.metric("High Urgency", int(high_urgency))

st.divider()

# --- Sentiment breakdown ---
if "sentiment" in filtered and filtered["sentiment"].notna().any():
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sentiment Distribution")
        sentiment_counts = filtered["sentiment"].value_counts().reset_index()
        sentiment_counts.columns = ["sentiment", "count"]
        fig = px.pie(sentiment_counts, names="sentiment", values="count",
                      color="sentiment",
                      color_discrete_map={"positive": "#2ecc71", "negative": "#e74c3c", "neutral": "#95a5a6"})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Sentiment by Product")
        by_product = filtered.groupby(["product", "sentiment"]).size().reset_index(name="count")
        fig2 = px.bar(by_product, x="product", y="count", color="sentiment", barmode="stack",
                       color_discrete_map={"positive": "#2ecc71", "negative": "#e74c3c", "neutral": "#95a5a6"})
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No enrichment data yet. Run the pipeline without `--skip-enrich` to populate sentiment/topics.")

# --- Topics ---
if "topics" in filtered and filtered["topics"].notna().any():
    st.subheader("Top Topics")
    topic_series = filtered["topics"].dropna().str.split(",").explode().str.strip()
    topic_series = topic_series[topic_series != ""]
    top_topics = topic_series.value_counts().head(10).reset_index()
    top_topics.columns = ["topic", "count"]
    fig3 = px.bar(top_topics, x="count", y="topic", orientation="h")
    st.plotly_chart(fig3, use_container_width=True)

# --- High urgency table ---
if "urgency" in filtered and (filtered["urgency"] == "high").any():
    st.subheader("⚠️ High Urgency Feedback")
    urgent = filtered[filtered["urgency"] == "high"][
        ["feedback_id", "customer_id", "product", "channel", "text", "sentiment", "topics"]
    ]
    st.dataframe(urgent, use_container_width=True)

# --- Raw data ---
with st.expander("Raw data"):
    st.dataframe(filtered, use_container_width=True)
