"""Record a demo GIF of the chat page: a real browser (Playwright) drives the page against a running server.

The model's waiting time is shortened in the GIF (one "Thinking..." frame); everything else,
including the replies, is captured as it happens.

Example (server running on localhost:8000):
    python scripts/make_demo_gif.py
    python scripts/make_demo_gif.py --url https://nordwind-support-agent.onrender.com
"""
from __future__ import annotations

import argparse
import io
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

MESSAGES = [
    "Can I return the boots from NW-100008? I'm hannah@example.com, they don't fit.",
    "How long does a PayPal refund take?",
    "Do you offer gift wrapping?",
]
VIEWPORT = {"width": 1120, "height": 760}
SCALE = 0.75  # GIF size vs. viewport, keeps the file small


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--out", default="docs/demo.gif")
    ap.add_argument("--channel", default="msedge", help="installed browser to drive (msedge, chrome) or '' for Playwright's Chromium")
    args = ap.parse_args()

    frames: list[Image.Image] = []
    durations: list[int] = []

    def snap(page, ms: int) -> None:
        img = Image.open(io.BytesIO(page.screenshot())).convert("RGB")
        frames.append(img.resize((int(img.width * SCALE), int(img.height * SCALE)), Image.LANCZOS))
        durations.append(ms)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel=args.channel or None)
        page = browser.new_page(viewport=VIEWPORT, color_scheme="light")
        page.goto(args.url)
        page.wait_for_selector("#examples button")
        snap(page, 1800)

        replies = page.locator(".msg.agent:not(.typing)")
        for message in MESSAGES:
            box = page.locator("#input")
            box.click()
            for i in range(0, len(message), 5):  # typing animation, one frame per 5 characters
                box.press_sequentially(message[i : i + 5])
                snap(page, 70)
            snap(page, 500)
            before = replies.count()
            page.click("#send")
            page.wait_for_selector(".msg.typing")
            snap(page, 1200)  # "Thinking...": the real wait is shortened
            deadline = time.time() + 180
            while replies.count() <= before:
                if time.time() > deadline:
                    raise SystemExit("No reply within 180 s")
                time.sleep(0.5)
            time.sleep(0.3)
            snap(page, 4500)
        browser.close()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    print(f"{out}: {len(frames)} frames, {out.stat().st_size / 1e6:.1f} MB, {sum(durations) / 1000:.0f} s")


if __name__ == "__main__":
    main()
