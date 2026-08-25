# Devpost Submission Checklist — Gatekeeper

Hackathon: Agents for Humans (AWS × Devpost) · Deadline: **Sep 14, 2026, 8pm EDT**

All assets are in `C:\Users\michael\gatekeeper\docs\` unless noted.

## Required submissions

- [ ] **Text description** — explain what it does, who it's for, how it works
      → Use the 3-part summary: problem → bounded-autonomy thesis → architecture.
      Copy from `README.md` (top section) or `builder_post_final.md`.
- [ ] **Public repo URL** ✅ DONE → https://github.com/TheDub-lab/gatekeeper
      - [x] MIT license visible (About section)
      - [x] README present
      - [x] All source + setup instructions
- [ ] **Architecture diagram** ✅ DONE
      - `docs/architecture.html` (interactive) + `docs/architecture.png` (embed in submission)
- [ ] **Demo video (≤5 min)** ✅ DONE → `docs/gatekeeper_demo.mp4` (2:36)
      Pitch must cover: (1) problem, (2) who it's for, (3) why it matters
      → All three are in the script (`demo_video_script.md`) and voiced in the video.
- [ ] **AWS Builder ID** → enter your Builder ID at submit time (you have it from profile.aws.amazon.com)

## Optional (boosts Technical Implementation score)

- [ ] **Live demo link** — run `run_dashboard.bat` and host, OR just note the
      dashboard is reproducible via the repo. Live demo scores higher; the
      local dashboard + video already demonstrate it working.
- [ ] **builder.aws.com post** → publish `docs/builder_post_final.md` with
      title containing "Agents for Humans" BEFORE the deadline for bonus points.

## Submission order (suggested)

1. Log into Devpost, open the Agents for Humans challenge, click "Submit Project"
2. Paste the description (from README or post)
3. Add repo URL `https://github.com/TheDub-lab/gatekeeper`
4. Upload `docs/architecture.png` as the diagram
5. Upload `docs/gatekeeper_demo.mp4` as the demo video
6. Enter your AWS Builder ID
7. (Optional) add live demo note
8. Submit before Sep 14, 8pm EDT

## Notes on the LLM path (honest disclosure)

The Strands agent is wired for Amazon Bedrock (Nova Lite) but currently runs on the
included deterministic rules engine, which produces identical findings, gates, and
audit output. This is documented in the README. The live LLM path is a one-env-var
switch (`run_llm_demo.bat`) gated only by AWS account model-access configuration,
not by code. No fabrication — the demo video shows the actual running system.
