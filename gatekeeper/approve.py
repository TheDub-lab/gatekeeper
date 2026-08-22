"""Human approval loop: list pending approvals, approve/deny by token."""
from __future__ import annotations
import json, os
from .protocol_layer import get_protocol, PENDING_PATH, _persist_pending


def pending() -> list[dict]:
    protocol = get_protocol()
    out = []
    for item in protocol.get_pending_approvals():
        req = item["request"] if isinstance(item, dict) else item.request
        token = item["token"] if isinstance(item, dict) else item.token
        out.append({
            "token": token,
            "action": req.action_type,
            "target": req.target,
            "params": req.params,
            "detail": f"{req.action_type} on {req.target} {req.params}",
        })
    return out


def decide(token: str, approve: bool) -> str:
    protocol = get_protocol()
    # reload pending tokens persisted by a previous run
    if os.path.exists(PENDING_PATH):
        with open(PENDING_PATH) as f:
            for item in json.load(f):
                from safety_protocol import ActionRequest
                req = ActionRequest(
                    action_type=item["action_type"], target=item["target"],
                    params=item.get("params", {}), estimated_cost=item.get("estimated_cost", 0.0),
                    request_id=item["request_id"],
                )
                if item["token"] not in protocol._pending_approvals:
                    protocol._pending_approvals[item["token"]] = req
    result = protocol.decide_approval(token, approved=approve, approver="michael")
    _persist_pending(protocol)
    return f"{'APPROVED' if approve else 'DENIED'}: {result}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        print(decide(sys.argv[1], sys.argv[2].lower() != "deny"))
    else:
        for p in pending():
            print(f"{p['token']}  {p['detail']}")
