"""Generate synthetic customer feedback data for the ETL pipeline.

Produces data/raw_feedback.csv with columns:
  feedback_id, customer_id, channel, product, rating, text, created_at

Run: python3 data/generate_synthetic.py
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

CHANNELS = ["email", "chat", "phone", "app_review", "social_media"]
PRODUCTS = ["Checking Account", "Savings Account", "Credit Card", "Mobile App", "Loan Service"]

POSITIVE_TEMPLATES = [
    "The {product} has been great, customer service was fast and helpful.",
    "Really happy with my {product}. The app is easy to use and reliable.",
    "Switched to {product} last month and it's been smooth sailing so far.",
    "Support resolved my issue with {product} within minutes. Excellent!",
    "Love the new features on {product}. Would recommend to friends.",
]

NEGATIVE_TEMPLATES = [
    "I'm frustrated with {product} — the app keeps crashing during login.",
    "Waited over an hour on the phone about {product} and nobody helped.",
    "Hidden fees on my {product} statement again. Very disappointed.",
    "The {product} interface is confusing and support was unhelpful.",
    "My {product} payment failed twice this week, urgent issue needs fixing.",
]

NEUTRAL_TEMPLATES = [
    "Just opened a {product}, so far it's okay, nothing special.",
    "Question about how interest is calculated on {product}.",
    "Used {product} to transfer funds, took the usual processing time.",
    "Curious about upgrading my {product} plan, what are the options?",
    "Received a statement for {product}, reviewing the details now.",
]

URGENT_KEYWORDS = ["urgent", "immediately", "asap", "fraud", "unauthorized"]


def random_date(start_days_ago=90):
    delta = random.randint(0, start_days_ago)
    return (datetime.now() - timedelta(days=delta)).strftime("%Y-%m-%d %H:%M:%S")


def generate_row(feedback_id):
    product = random.choice(PRODUCTS)
    sentiment_bucket = random.choices(
        ["positive", "negative", "neutral"], weights=[0.35, 0.35, 0.30]
    )[0]

    if sentiment_bucket == "positive":
        template = random.choice(POSITIVE_TEMPLATES)
        rating = random.choice([4, 5])
    elif sentiment_bucket == "negative":
        template = random.choice(NEGATIVE_TEMPLATES)
        rating = random.choice([1, 2])
        if random.random() < 0.15:
            template += " This is " + random.choice(URGENT_KEYWORDS) + "."
    else:
        template = random.choice(NEUTRAL_TEMPLATES)
        rating = 3

    text = template.format(product=product)

    return {
        "feedback_id": feedback_id,
        "customer_id": f"CUST{random.randint(1000, 1999)}",
        "channel": random.choice(CHANNELS),
        "product": product,
        "rating": rating,
        "text": text,
        "created_at": random_date(),
    }


def main(n=300):
    out_path = Path(__file__).parent / "raw_feedback.csv"
    rows = [generate_row(i) for i in range(1, n + 1)]

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
