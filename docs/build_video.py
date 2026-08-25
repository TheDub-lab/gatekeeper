#!/usr/bin/env python
"""Render the Gatekeeper demo video.

Captions come from the demo_video_script.md VO text; audio via edge-tts.
Images: terminal run + dashboard. Assembled with moviepy.
"""
from __future__ import annotations
import json, os, subprocess, asyncio, textwrap
from pathlib import Path

import edge_tts

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "docs" / "video_assets"
OUT.mkdir(exist_ok=True)
FINAL = ROOT / "docs" / "gatekeeper_demo.mp4"

# ---- narration: (segment, text, seconds) ----
NARRATION = [
    ("problem",
     "Every month, the average person loses sixty to a hundred dollars to subscription waste: "
     "duplicate charges they never notice, price hikes buried in email, free trials that silently "
     "convert. Budgeting apps show you dashboards. But a dashboard is just more homework. "
     "What if an agent did the work instead, and you could trust it with your money?", 23),
    ("run",
     "Here is Gatekeeper running live. Built on the Strands Agents SDK, the scanner agent reads "
     "my bank feed and inbox and finds four problems: Netflix charged me twice in ten days. "
     "Comcast raised my rate from twelve dollars to twenty one fifty. I have a gym membership I "
     "have not used since March. And a news trial just converted to paid.", 23),
    ("gate",
     "Now watch what happens. Two cancellations execute immediately, because they are in scope. "
     "But the Netflix dispute and the Comcast negotiation email are held, not blocked, for me. "
     "Every action this agent takes passes through a six stage safety protocol: binding check, "
     "kill switch, scope whitelist, budget limit, approval gate. Only then does it execute. "
     "There is no bypass path. The agent's tools are the protocol.", 27),
    ("decision",
     "This is the part that makes it trustworthy rather than terrifying. The agent pings me only "
     "when there is a real decision. Here is the dashboard: what it found, why, what it did on its "
     "own, and what is waiting for me. I can see the Comcast hike would cost nine fifty more per "
     "month, so I approve the negotiation email. One click, and it is logged.", 24),
    ("audit",
     "And here is the receipt. Every single event is logged: when the protocol was initialized and "
     "with what limits, every approval request, my decision, every execution. If anyone ever asks "
     "why an agent cancelled my gym membership, there is a tamper evident answer. This is what "
     "deploying agents into money domains actually requires. Not smarter models, enforceable "
     "authorization.", 27),
    ("why",
     "Gatekeeper found sixty two dollars of monthly waste and resolved most of it autonomously, "
     "while guaranteeing it could not move a dollar outside its authorization. The same safety "
     "protocol layer generalizes to any high stakes agent domain: health, legal, procurement. "
     "Bounded autonomy is not a constraint on what agents can do. It is what makes them deployable.",
     24),
]

TITLE = "GATEKEEPER — bounded autonomy for agents that touch your money"
OUTRO = "github.com/TheDub-lab/gatekeeper  ·  built with Strands Agents SDK + safety-protocol"


def run(cmd):
    subprocess.run(cmd, shell=True, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


async def tts(seg: str, text: str, path: Path):
    voice = "en-US-AndrewNeural"  # clear male
    comm = edge_tts.Communicate(text, voice)
    await comm.save(str(path))


def build_title_img(path: Path):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        run(f'"{ROOT}/.venv/Scripts/python" -m pip install pillow --quiet')
        from PIL import Image, ImageDraw, ImageFont
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), (13, 17, 23))
    d = ImageDraw.Draw(img)
    # grid
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(30, 41, 59), width=1)
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(30, 41, 59), width=1)
    font = ImageFont.load_default()
    d.text((640, 320), TITLE, fill=(88, 166, 255), anchor="mm", font=font)
    img.save(path)


def main():
    # 1. audio
    audio_paths = []
    for i, (seg, text, secs) in enumerate(NARRATION):
        ap = OUT / f"vo_{i}.mp3"
        asyncio.run(tts(seg, text, ap))
        audio_paths.append(ap)
        print(f"audio {i}: {ap.stat().st_size} bytes")

    # 2. title image
    build_title_img(OUT / "title.png")

    # 3. assemble with moviepy
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ColorClip

    clips = []
    # title card
    title = ImageClip(str(OUT / "title.png")).with_duration(4)
    clips.append(title)

    # each narration segment pairs real footage with its audio + a caption lower-third
    backdrops = {
        "problem": str(OUT / "dash.png"),
        "run": str(OUT / "term.png"),
        "gate": str(OUT / "term.png"),
        "decision": str(OUT / "dash.png"),
        "audit": str(OUT / "dash.png"),
        "why": str(OUT / "arch.png"),
    }
    for i, (seg, text, secs) in enumerate(NARRATION):
        ap = audio_paths[i]
        adur = AudioFileClip(str(ap)).duration
        dur = max(secs, adur + 0.3)
        bdpath = backdrops.get(seg, str(OUT / "title.png"))
        bg = ImageClip(bdpath).with_duration(dur).with_position("center").resized(lambda t: (1280, 720))
        # caption sits in a dedicated band at the bottom, clear of the footage
        cap = TextClip(text=text, font_size=24, color=(230, 237, 243),
                       size=(1240, 130), method="caption",
                       bg_color=(13, 17, 23)).with_duration(dur).with_position(("center", 560))
        segclip = CompositeVideoClip([bg, cap]).with_audio(AudioFileClip(str(ap)))
        clips.append(segclip)

    # outro
    outro = ColorClip((1280, 720), color=(13, 17, 23)).with_duration(4)
    oc = TextClip(text=OUTRO, font_size=40, color=(88, 166, 255),
                  size=(1180, 660)).with_position("center").with_duration(4)
    outro = CompositeVideoClip([outro, oc])
    clips.append(outro)

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(str(FINAL), fps=24, codec="libx264", audio_codec="aac")
    print("WROTE", FINAL)


if __name__ == "__main__":
    main()
