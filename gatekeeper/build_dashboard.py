"""Export run + audit state into the dashboard HTML as embedded JSON."""
from __future__ import annotations
import json, os

from .run_gate import run
from .protocol_layer import PENDING_PATH

HERE = os.path.dirname(__file__)
DASH = os.path.join(HERE, "dashboard.html")


def build() -> str:
    summary = run()
    pending = []
    if os.path.exists(PENDING_PATH):
        with open(PENDING_PATH) as f:
            pending = json.load(f)
    audit_lines = []
    audit_path = os.path.join(HERE, "data", "audit.jsonl")
    if os.path.exists(audit_path):
        with open(audit_path) as f:
            audit_lines = [json.loads(l) for l in f if l.strip()]

    with open(DASH) as f:
        html = f.read()
    payload = json.dumps({"summary": summary, "pending": pending, "audit": audit_lines})
    html = html.replace("__DATA__", payload.replace("</", "<\\/"))
    out = os.path.join(HERE, "data", "dashboard_live.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


if __name__ == "__main__":
    print(build())
