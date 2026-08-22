"""Bedrock model wiring for the Gatekeeper agent.

Reads standard AWS credentials (~/.aws or env vars). If unavailable,
the run falls back to the deterministic rules engine so the demo
always works. Set GATEKEEPER_LLM=1 to force LLM mode and fail loudly.
"""
from __future__ import annotations
import os

MODEL_ID = "us.amazon.nova-lite-v1:0"


def get_model():
    """Return a Strands BedrockModel, or None if AWS isn't configured."""
    try:
        import boto3
        from strands.models import BedrockModel

        session = boto3.Session(region_name=os.environ.get("AWS_REGION", "us-east-1"))
        # fail fast if no credentials resolve
        session.get_credentials()
        c = session.client("bedrock-runtime")
        # cheap auth check: list inference profiles reachable with these creds
        session.client("bedrock").list_foundation_models(byProvider="amazon")

        return BedrockModel(
            model_id=MODEL_ID,
            boto_session=session,
            max_tokens=1024,
            temperature=0.2,
        )
    except Exception as e:
        if os.environ.get("GATEKEEPER_LLM") == "1":
            raise
        print(f"[gatekeeper] LLM unavailable ({type(e).__name__}) — using rules engine.")
        return None


def llm_decide_and_act(findings, tools) -> list[dict]:
    """Let the LLM decide actions per finding using the gated tools.

    Returns list of {finding, action, merchant, domain, amount,
    monthly_savings, result} — same shape as the rules engine.
    """
    from strands import Agent

    agent = Agent(
        model=get_model(),
        tools=tools,
        system_prompt=(
            "You are Gatekeeper, an autonomous subscription watchdog acting for "
            "user 'michael'. For each finding below, take exactly the suggested "
            "action using your tools (one tool call per finding). Pass the "
            "merchant's domain as target. Be terse; report each tool result."
        ),
    )

    prompt = "\n".join(
        f"- Finding {i+1}: {f['detail']} Suggested action: {f['suggested_action']} "
        f"on domain {f['domain']} for merchant {f['merchant']}."
        for i, f in enumerate(findings)
    )
    out = agent(prompt)
    text = str(out)

    results = []
    for f in findings:
        marker = f["merchant"]
        # find the tool-result line following this finding in the transcript
        results.append({**_base(f), "result": _extract(text, marker)})
    return results


def _base(f):
    return {
        "finding": f["detail"],
        "action": f["suggested_action"],
        "merchant": f["merchant"],
        "domain": f["domain"],
        "amount": f.get("amount", 0.0),
        "monthly_savings": f.get("estimated_monthly_savings", 0.0),
    }


def _extract(transcript: str, merchant: str) -> str:
    lines = transcript.splitlines()
    hits = [l.strip() for l in lines if merchant.lower().split()[0] in l.lower()]
    for h in reversed(hits):
        if "[" in h:
            return h[:200]
    return hits[-1][:200] if hits else "[NO ACTION RECORDED]"
