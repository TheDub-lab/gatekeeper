# Gatekeeper: Agents That Touch Your Money, Without the Terror (Agents for Humans)

*Built with the Strands Agents SDK for the AWS Agents for Humans Hackathon.*

You don't need another dashboard telling you where your money went. You need an agent that does something about it — and that you can actually trust.

**Gatekeeper** is an autonomous subscription watchdog. It reads your bank feed and inbox, finds the waste (duplicate charges, silent price hikes, trials that converted, gym memberships you quit using), and acts. The twist: every action runs through a hard safety protocol — binding, kill switch, scope whitelist, $50 budget cap, approval gate. In-scope cancellations happen on their own. Disputes and outbound emails wait for your one-click yes. Nothing moves without authorization, and every decision is logged.

We built it on Strands because its `@tool` model made policy injection trivial: wrap each tool in the protocol, and there's simply no un-gated path for the agent to call. The result is *bounded autonomy* — the agent works while you sleep, but it can never exceed what you authorized. Demo run: $62.49/month reclaimed, two actions auto-executed, two held for approval, full audit trail.

This is the pattern every money-touching agent needs. Not smarter models. Enforceable authorization. Repo: https://github.com/TheDub-lab/gatekeeper
