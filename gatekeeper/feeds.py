"""Fake data feeds so the demo needs no real credentials.

Simulates: a bank transaction feed + an email inbox for "Michael".
Deterministic seed data = same demo every time.
"""
from __future__ import annotations
import json, os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

BANK_FEED = [
    # (date_offset_days_ago, merchant, amount, recurring_monthly)
    (2,  "Netflix",            15.49, True),
    (3,  "Spotify",             11.99, True),
    (4,  "Adobe Creative Cloud",59.99, True),
    (5,  "Netflix",            15.49, True),   # DUPLICATE subscription charged twice
    (6,  "GymFit Monthly",      45.00, True),
    (7,  "CloudBackup Pro",     9.99,  True),
    (10, "Comcast Xfinity",    21.50, True),   # was 12.00 -> price hike
    (12, "Amazon Prime",       14.99, True),
    (14, "NewsDaily Trial",    7.99,  False),  # trial converting to paid
    (18, "Comcast Xfinity",    12.00, True),
    (40, "Comcast Xfinity",    12.00, True),
]

INBOX = [
    {
        "id": "em1",
        "from": "billing@gymfit.example",
        "subject": "Your membership renews automatically",
        "body": "Your GymFit membership ($45.00/mo) will renew on the 1st. "
                "You have not checked in since March.",
        "days_ago": 1,
    },
    {
        "id": "em2",
        "from": "no-reply@newsdaily.example",
        "subject": "Your free trial has ended - now $7.99/month",
        "body": "Thank you for trying NewsDaily! Your trial has converted to a "
                "paid subscription at $7.99/month unless you cancel.",
        "days_ago": 1,
    },
    {
        "id": "em3",
        "from": "accounts@comcast.example",
        "subject": "Notice of rate adjustment",
        "body": "Beginning this billing cycle, your Xfinity Internet plan will "
                "increase from $12.00 to $21.50 per month.",
        "days_ago": 10,
    },
    {
        "id": "em4",
        "from": "hello@cloudbackup.example",
        "subject": "Receipt: CloudBackup Pro monthly",
        "body": "Payment received: $9.99 for CloudBackup Pro (monthly plan).",
        "days_ago": 7,
    },
]


def _write(name: str, obj) -> str:
    path = os.path.join(DATA_DIR, name)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
    return path


def seed() -> dict:
    today = datetime.now()
    bank = []
    for days_ago, merchant, amount, recurring in BANK_FEED:
        bank.append({
            "date": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "merchant": merchant,
            "amount": amount,
            "recurring": recurring,
        })
    inbox = []
    for em in INBOX:
        inbox.append({**em,
                      "date": (today - timedelta(days=em["days_ago"])).strftime("%Y-%m-%d")})
    return {"bank_path": _write("bank.json", bank), "inbox_path": _write("inbox.json", inbox)}


if __name__ == "__main__":
    print(seed())
