"""The safety-protocol enforcement layer, exposed as Strands tools.

Every tool the actor agent can call routes through SafetyProtocol.execute().
The protocol decides: allow, block, or hold for human approval.
The agent cannot bypass it because the tools ARE the protocol.
"""
from __future__ import annotations
import json, os

from safety_protocol import (
    ActionRequest, AuditTrail, Monitor, SafetyProtocol, ScopeRule,
)

AUDIT_PATH = os.path.join(os.path.dirname(__file__), "data", "audit.jsonl")
PENDING_PATH = os.path.join(os.path.dirname(__file__), "data", "pending.json")


def _persist_pending(protocol: SafetyProtocol) -> None:
    """Mirror in-memory pending approvals to disk so a later process
    (dashboard, CLI) can decide them."""
    from safety_protocol.protocol import SafetyProtocol as _SP  # noqa
    pending = []
    for token, req in protocol._pending_approvals.items():
        pending.append({
            "token": token, "request_id": req.request_id,
            "action_type": req.action_type, "target": req.target,
            "params": req.params, "estimated_cost": req.estimated_cost,
        })
    with open(PENDING_PATH, "w") as f:
        json.dump(pending, f, indent=2)


def build_gatekeeper_protocol() -> SafetyProtocol:
    """Protocol for the Gatekeeper agent, bound to Michael.

    Scope: can only act on the merchant domains in the allowlist,
    only via 'cancel_subscription'/'send_message'/'dispute' actions.
    Budget: $50 total spend authority, anything over $20 needs a human.
    """
    audit = AuditTrail()
    # persist audit events to disk as they happen
    _orig_append = audit.append

    def _append(event, agent_id, data):
        _orig_append(event, agent_id, data)
        with open(AUDIT_PATH, "a") as f:
            f.write(json.dumps({"event": event, "agent": agent_id, "data": data}) + "\n")

    audit.append = _append  # type: ignore

    monitor = Monitor(audit=audit, agent_id="gatekeeper-01")

    protocol = SafetyProtocol(
        agent_id="gatekeeper-01",
        user_id="michael",
        scope_rules=[
            ScopeRule(
                action_type="cancel_subscription",
                allowed_targets=["netflix.com", "gymfit.example", "newsdaily.example"],
                requires_approval=False,
                max_cost=0.0,
            ),
            ScopeRule(
                action_type="dispute_charge",
                allowed_targets=["netflix.com"],
                requires_approval=True,   # disputes always need a human
            ),
            ScopeRule(
                action_type="send_message",
                allowed_targets=["gymfit.example", "newsdaily.example", "comcast.example"],
                requires_approval=True,   # outbound comms need a human
                max_cost=20.0,
            ),
        ],
        budget_limit=50.0,
        approval_threshold_cost=20.0,
        audit=audit,
        monitor=monitor,
        allowed_action_types=["cancel_subscription", "dispute_charge", "send_message"],
    )
    return protocol


PROTOCOL: SafetyProtocol | None = None


def get_protocol() -> SafetyProtocol:
    global PROTOCOL
    if PROTOCOL is None:
        PROTOCOL = build_gatekeeper_protocol()
    return PROTOCOL
