"""Run the Gatekeeper end-to-end: scan -> decide -> act (through the protocol) -> report."""
from __future__ import annotations
import json, os, sys

from .agent import scan, ACTION_TOOLS
from .protocol_layer import get_protocol

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _make_strands_agent():
    """Bedrock/Nova if AWS credentials resolve; otherwise None -> rules mode."""
    try:
        from .llm import get_model
        from strands import Agent
        model = get_model()
        if model is None:
            return None
        return Agent(tools=ACTION_TOOLS, model=model,
                     system_prompt="You are Gatekeeper, an autonomous subscription watchdog. "
                                   "For each finding, take the suggested action using your tools. "
                                   "Be terse.")
    except Exception:
        return None


def _rules_decide(findings):
    """Deterministic decision layer: same outcome as the LLM would pick."""
    decisions = []
    for f in findings:
        decisions.append({
            "finding": f["detail"],
            "action": f["suggested_action"],
            "merchant": f["merchant"],
            "domain": f["domain"],
            "amount": f.get("amount", 0.0),
            "monthly_savings": f.get("estimated_monthly_savings", 0.0),
        })
    return decisions


def run() -> dict:
    # reset audit for clean demo runs
    os.makedirs(DATA_DIR, exist_ok=True)
    audit_path = os.path.join(DATA_DIR, "audit.jsonl")
    if os.path.exists(audit_path):
        os.remove(audit_path)

    protocol = get_protocol()
    findings = scan()
    decisions = _rules_decide(findings)

    agent = _make_strands_agent()
    results = []
    for d in decisions:
        if agent is not None and d["action"] == "cancel_subscription":
            out = agent.tool.cancel_subscription(merchant=d["merchant"], domain=d["domain"])
            status = str(out)
        else:
            from safety_protocol import ActionRequest
            req = ActionRequest(
                action_type=d["action"], target=d["domain"],
                params={"merchant": d["merchant"]},
                estimated_cost=d["amount"] if d["action"] == "dispute_charge" else 0.0,
            )
            res = protocol.execute(req)
            parts = [f"[{res.outcome.name}]"]
            if getattr(res, "block_reason", None):
                parts.append(res.block_reason)
            if getattr(res, "requires_approval_for", None):
                parts.append(f"HELD FOR HUMAN APPROVAL (token={res.requires_approval_for})")
            status = " ".join(parts)
        results.append({**d, "result": status})

    from .protocol_layer import _persist_pending
    _persist_pending(protocol)

    summary = {
        "findings": len(findings),
        "allowed": sum(1 for r in results if "ALLOWED" in r["result"]),
        "blocked": sum(1 for r in results if "BLOCKED" in r["result"]),
        "held": sum(1 for r in results if "PENDING_APPROVAL" in r["result"]),
        "monthly_savings_identified": round(sum(d["monthly_savings"] for d in decisions), 2),
        "results": results,
    }
    with open(os.path.join(DATA_DIR, "last_run.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Gatekeeper run: {summary['findings']} findings | "
          f"{summary['allowed']} allowed | {summary['blocked']} blocked | "
          f"{summary['held']} held for approval")
    for r in results:
        print(f"  - {r['merchant']:<16} {r['action']:<20} {r['result']}")
    return summary


if __name__ == "__main__":
    run()
