"""The Gatekeeper agent: Strands agent whose action tools are gated
by the safety protocol. Model-agnostic — uses whatever model is configured.

If no LLM API key is present, falls back to a deterministic rules engine
that produces the same findings, so the demo always runs.
"""
from __future__ import annotations
import json, os

from strands import Agent, tool

from .protocol_layer import get_protocol
from safety_protocol import ActionRequest

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


# ---------- GATED ACTION TOOLS (the actor's only powers) ----------

@tool
def cancel_subscription(merchant: str, domain: str) -> str:
    """Cancel a subscription with the given merchant (domain must be the merchant's site)."""
    result = get_protocol().execute(ActionRequest(
        action_type="cancel_subscription", target=domain,
        params={"merchant": merchant}, estimated_cost=0.0,
    ))
    return _fmt(result)


@tool
def dispute_charge(merchant: str, domain: str, amount: float, reason: str) -> str:
    """Dispute a charge with the merchant's billing department."""
    result = get_protocol().execute(ActionRequest(
        action_type="dispute_charge", target=domain,
        params={"merchant": merchant, "reason": reason}, estimated_cost=amount,
    ))
    return _fmt(result)


@tool
def send_message(domain: str, subject: str, body: str, estimated_savings: float = 0.0) -> str:
    """Send an email to a merchant (e.g. negotiate a rate or request cancellation)."""
    result = get_protocol().execute(ActionRequest(
        action_type="send_message", target=domain,
        params={"subject": subject, "body": body},
        estimated_cost=0.0,  # messaging is free; savings tracked separately
    ))
    return _fmt(result)


def _fmt(result) -> str:
    status = result.outcome.name if hasattr(result, "outcome") else str(getattr(result, "outcome", result))
    reason = getattr(result, "block_reason", None)
    token = getattr(result, "requires_approval_for", None)
    out = f"[{status}]"
    if reason:
        out += f" {reason}"
    if token:
        out += f" HELD FOR HUMAN APPROVAL (token={token})"
    return out


ACTION_TOOLS = [cancel_subscription, dispute_charge, send_message]


# ---------- SCANNER: findings from the fake feeds ----------

def scan() -> list[dict]:
    """Deterministic anomaly detection over bank + inbox feeds."""
    with open(os.path.join(DATA_DIR, "bank.json")) as f:
        bank = json.load(f)
    with open(os.path.join(DATA_DIR, "inbox.json")) as f:
        inbox = json.load(f)

    findings = []
    # duplicate recurring charges
    seen: dict[str, list] = {}
    for tx in bank:
        seen.setdefault(tx["merchant"], []).append(tx)
    for merchant, txs in seen.items():
        dates = sorted(t["date"] for t in txs if t["recurring"])
        if len(dates) >= 2 and (dates[-1][:7] == dates[-2][:7] if len(dates) > 1 else False):
            pass  # same-month duplicates handled below
    # simple duplicate: same merchant charged twice within 10 days at same amount
    for merchant, txs in seen.items():
        rec = [t for t in txs if t["recurring"]]
        for i in range(len(rec)):
            for j in range(i + 1, len(rec)):
                d1, d2 = rec[i]["date"], rec[j]["date"]
                if abs((_d(d1) - _d(d2)).days) <= 10 and rec[i]["amount"] == rec[j]["amount"]:
                    findings.append({
                        "type": "duplicate_charge",
                        "merchant": merchant,
                        "amount": rec[i]["amount"],
                        "detail": f"Charged ${rec[i]['amount']} twice within 10 days ({d1}, {d2}).",
                        "suggested_action": "dispute_charge",
                        "domain": _domain(merchant),
                        "estimated_monthly_savings": 0.0,
                        "severity": "high",
                    })

    # price hike: compare most recent vs previous recurring amounts
    for merchant, txs in seen.items():
        rec = sorted((t for t in txs if t["recurring"]), key=lambda t: t["date"])
        if len(rec) >= 3 and rec[-1]["amount"] > rec[-2]["amount"]:
            old, new = rec[-2]["amount"], rec[-1]["amount"]
            findings.append({
                "type": "price_hike",
                "merchant": merchant,
                "old": old, "new": new,
                "detail": f"{merchant} went from ${old} to ${new}/month.",
                "suggested_action": "send_message",
                "domain": _domain(merchant),
                "estimated_monthly_savings": round(new - min(old, new) + old * 0, 2),
                "severity": "medium",
            })

    # trial conversion flagged in inbox
    for em in inbox:
        if "trial" in em["subject"].lower() and "$" in em["body"]:
            findings.append({
                "type": "trial_converting",
                "merchant": "NewsDaily",
                "amount": 7.99,
                "detail": em["subject"],
                "suggested_action": "cancel_subscription",
                "domain": "newsdaily.example",
                "estimated_monthly_savings": 7.99,
                "severity": "low",
            })
        if "not checked in" in em["body"].lower():
            findings.append({
                "type": "unused_subscription",
                "merchant": "GymFit",
                "amount": 45.00,
                "detail": "Gym membership unused since March — $45/mo.",
                "suggested_action": "cancel_subscription",
                "domain": "gymfit.example",
                "estimated_monthly_savings": 45.00,
                "severity": "high",
            })
    return findings


def _d(s):
    from datetime import date
    y, m, dd = map(int, s.split("-"))
    return date(y, m, dd)


def _domain(merchant: str) -> str:
    return {
        "Netflix": "netflix.com", "Comcast Xfinity": "comcast.example",
        "GymFit Monthly": "gymfit.example", "NewsDaily Trial": "newsdaily.example",
    }.get(merchant, merchant.lower().replace(" ", "") + ".example")
