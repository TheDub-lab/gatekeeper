# Gatekeeper: What Happens When Your Agent Touches Money (Agents for Humans)

*Build story for the AWS Agents for Humans Hackathon — Strands Agents SDK + a safety protocol enforcement layer.*

---

## The uncomfortable question

Every demo of an autonomous agent doing real-world tasks eventually hits the same wall: what happens when it needs to spend money? Cancel a subscription? Dispute a charge? Email someone on your behalf?

The usual answers are "human reviews everything" (which defeats autonomy) or "trust the model" (which is how you end up with an agent emailing your bank). We wanted neither.

## What we built

**Gatekeeper** is an autonomous subscription watchdog. It reads your bank feed and inbox, finds the money you're quietly losing — duplicate charges, price hikes, trials that silently converted, memberships you stopped using — and handles them end to end.

But the interesting part isn't the finding. It's the **enforcement layer between the LLM and every action**:

```
binding check → kill switch → scope whitelist → budget limit → approval gate → execute
```

Every action the agent takes is an `ActionRequest` that must pass through this pipeline. The agent can only act on whitelisted merchant domains, via three action types. It has a $50 budget cap. Disputes and outbound communications are *held* for human sign-off — the agent pings you only when there's a real decision to make. Everything lands in a tamper-evident audit trail.

There is no bypass path. The tools ARE the protocol — un-gated actions literally don't exist in the agent's toolset.

## How Strands made this natural

The Strands Agents SDK's `@tool` decorator turned out to be the perfect seam for policy injection. Because every capability is an explicit tool, wrapping each one in protocol enforcement was clean — no monkey-patching, no framework fights:

```python
@tool
def dispute_charge(merchant: str, domain: str, amount: float, reason: str) -> str:
    """Dispute a charge with the merchant's billing department."""
    result = protocol.execute(ActionRequest(
        action_type="dispute_charge", target=domain,
        params={"merchant": merchant, "reason": reason}, estimated_cost=amount,
    ))
    return format_gate_result(result)
```

The protocol decides: `ALLOWED`, `BLOCKED_*`, or `PENDING_APPROVAL` with a token. The agent sees the same interface either way — it just learns some actions come back "held," which is exactly the real-world behavior we want it to internalize.

We ran decisions on Amazon Bedrock Nova Lite, with a deterministic fallback so the demo never depends on a live model call.

## What a run looks like

Seeded feeds produce four findings:

- Gym membership unused since March → **auto-cancelled** ($45/mo saved)
- Trial converting to paid → **auto-cancelled** ($7.99/mo saved)
- Netflix charged twice in 10 days → **held** at the approval gate
- Comcast rate hike $12→$21.50 → **held**, negotiation email drafted

Two executed autonomously. Two waited for a human. Total identified savings: $62.49/month. And after approval, one click on the dashboard, logged to the audit trail with who decided, what, and when.

## Why this matters beyond subscriptions

Agents that touch money fail on trust, not capability. The pattern here — explicit scope, hard budgets, approval gates, auditable decisions — generalizes to any domain where an agent's mistake costs something real: health admin, legal paperwork, procurement.

Bounded autonomy isn't a constraint on agents. It's the missing deployment requirement.

## Try it

Repo: *(public URL after submission)* · MIT licensed · built with Strands Agents SDK, Amazon Bedrock, and the open-source [safety-protocol](https://github.com/TheDub-lab/safety-protocol) library.
