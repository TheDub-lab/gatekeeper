# Gatekeeper — Demo Video Script (4:00 target, max 5:00)

Format: screen recording + voiceover. No face on camera. Slides only for intro/outro.

---

## [0:00–0:25] — The problem (slide + bank feed b-roll)

**VO:** "Every month, the average person loses sixty to a hundred dollars to subscription
waste — duplicate charges they never notice, price hikes buried in email, free trials
that silently convert. Budgeting apps show you dashboards. But a dashboard is just
more homework. What if an agent did the work instead — and you could trust it with
your money?"

**On screen:** Title card "Gatekeeper — bounded autonomy for agents that touch your money."
Then scroll the seeded bank.json feed.

---

## [0:25–1:10] — The run

**VO:** "Here's Gatekeeper running live. It's built on the Strands Agents SDK — the
scanner agent reads my bank feed and inbox, and finds four problems: Netflix charged
me twice in ten days. Comcast raised my rate from twelve dollars to twenty-one fifty.
I have a gym membership I haven't used since March. And a news trial just converted
to paid."

**On screen:** terminal running `python -m gatekeeper.run_gate`, output appearing.

---

## [1:10–1:50] — The gate

**VO:** "Now watch what happens. Two cancellations execute immediately — they're in
scope. But the Netflix dispute and the Comcast negotiation email are HELD. Not blocked
— held, for me. Every action this agent takes passes through a six-stage safety
protocol: binding check, kill switch, scope whitelist, budget limit, approval gate.
Only then does it execute. There is no bypass path — the agent's tools ARE the
protocol."

**On screen:** highlight the two `[PENDING_APPROVAL]` lines; cut to protocol_layer.py
showing ScopeRule definitions.

---

## [1:50–2:40] — Human decision point

**VO:** "This is the part that makes it trustworthy rather than terrifying. The agent
pings me only when there's a real decision. Here's the dashboard: what it found, why,
what it did on its own, and what's waiting for me. I can see the Comcast hike would
cost nine-fifty more per month — so I approve the negotiation email. One click, logged."

**On screen:** dashboard_live.html — stats, findings with explanations, then clicking
approve; decision message appears.

---

## [2:40–3:20] — Audit trail

**VO:** "And here's the receipt. Every single event is logged: when the protocol was
initialized and with what limits, every approval request, my decision, every execution.
If anyone ever asks 'why did an agent cancel my gym membership' — there's a
tamper-evident answer. This is what deploying agents into money domains actually
requires. Not smarter models — enforceable authorization."

**On screen:** audit.jsonl contents / dashboard audit section scrolling.

---

## [3:20–3:50] — Why it matters (slide)

**VO:** "Gatekeeper found sixty-two dollars of monthly waste and resolved most of it
autonomously — while guaranteeing it could not move a dollar outside its authorization.
The same safety-protocol layer generalizes to any high-stakes agent domain: health,
legal, procurement. Bounded autonomy isn't a constraint on what agents can do.
It's what makes them deployable."

**On screen:** architecture diagram; closing card with repo URL.

---

## Production notes
- Record at 1920×1080, dark terminal/dashboard theme
- Voiceover: any TTS or your own read — script above is ~430 words ≈ 3.5 min at natural pace
- Free tools: OBS Studio (screen), Audacity (audio), DaVinci Resolve (edit)
- Music: none or very low ambient (judges skip through)
