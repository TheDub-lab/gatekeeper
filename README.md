# 🛡️ Gatekeeper

**An autonomous subscription watchdog with bounded autonomy.** Gatekeeper finds the money you're quietly losing — duplicate charges, price hikes, trials converting to paid, memberships you never use — and handles them end to end. It runs in the background and only surfaces when there's a real decision to make.

Built for the [Agents for Humans Hackathon](https://agentsforhumans.devpost.com) (AWS × Devpost) · **Everyday Agents track**

---

## The problem

The average person bleeds $60–100/month to subscription waste: charges they forgot, price hikes they never noticed, trials that silently converted. Existing apps show you *dashboards* — more work for you. Gatekeeper flips it: **the agent does the work**, and a hard safety protocol guarantees it can't move a dollar without your authorization.

## The idea: bounded autonomy

Most agent demos race toward more autonomy. Gatekeeper's differentiator is **trust infrastructure**: an enforcement layer between the LLM and every action.

Every action the agent takes is an `ActionRequest` that must pass through the safety protocol pipeline:

```
binding check → kill switch → scope whitelist → budget limit → approval gate → execute
```

- **Scope whitelist** — the agent can only act on approved merchant domains, via three action types (`cancel_subscription`, `dispute_charge`, `send_message`). Anything else is blocked.
- **Budget cap** — $50 total spend authority. Hard stop.
- **Approval gate** — disputes and outbound communications are *held* for human sign-off. The agent pings you only when there's a real decision.
- **Audit trail** — every event (requests, holds, decisions, executions) logged to a tamper-evident JSONL trail.

There is no bypass path. The tools ARE the protocol — the agent cannot call an un-gated action because un-gated tools don't exist.

## Architecture

![architecture](architecture.png)

*Interactive version: [`docs/architecture.html`](docs/architecture.html)*

| Layer | Tech |
|---|---|
| Agent loop | [Strands Agents SDK](https://github.com/strands-agents/harness-sdk) (`@tool` actions) |
| Decision model | Amazon Bedrock — Nova Lite |
| Enforcement | [safety-protocol](https://github.com/TheDub-lab/safety-protocol) library (binding / scope / budget / approval / audit / kill switch) |
| Dashboard | Single-file HTML — findings, pending decisions, full audit log, plain-English explanations |

## Quick start

```bash
git clone <this repo>
cd gatekeeper
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Linux/Mac: .venv/bin/pip ...
pip install -e ../path/to/safety-protocol       # or: pip install safety-protocol

# seed demo data + run
python -m gatekeeper.feeds
python -m gatekeeper.run_gate

# decide held actions
python -m gatekeeper.approve                    # list pending tokens
python -m gatekeeper.approve <token> approve    # approve or deny

# live dashboard
run_dashboard.bat        # Windows  (or: python -m gatekeeper.build_dashboard)
```

With AWS credentials configured (`~/.aws`), the run automatically uses Bedrock Nova Lite for decisions; without them it falls back to a deterministic rules engine producing identical outcomes — the demo always works.

## Demo walkthrough (60 seconds)

1. Scanner reviews seeded bank feed + inbox → finds **4 issues**
2. Auto-executes 2 in-scope cancellations (unused gym, converting trial)
3. **Holds** 2 actions at the approval gate: duplicate Netflix charge dispute, Comcast rate-hike negotiation email
4. You open the dashboard, see why each action was taken, approve by token
5. Full audit trail shows every decision — who, what, when, allowed or blocked

## Why this matters

Agents that touch money fail on trust, not capability. The missing piece isn't smarter models — it's enforceable authorization. This project demonstrates the pattern end to end:

- The agent is genuinely useful (finds real waste, acts autonomously)
- The human stays in command (approval gates, kill switch, budget caps)
- Every action is attributable and auditable

This is what deploying agents into domains like personal finance actually requires — and the same protocol layer generalizes to any high-stakes agent domain (health, legal, procurement).

## License

MIT
