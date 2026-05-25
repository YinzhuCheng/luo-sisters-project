#!/usr/bin/env python3
"""Open one local or remote page with Playwright and save a screenshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


def normalize_target(raw: str) -> str:
    parsed = urlparse(raw)
    if parsed.scheme in {"http", "https", "file"}:
        return raw
    return Path(raw).resolve().as_uri()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a quick Playwright smoke check against one page.")
    parser.add_argument("target", help="URL or local HTML path.")
    parser.add_argument("--output", default="logs/browser-smoke.png", help="Screenshot output path.")
    parser.add_argument("--width", type=int, default=1440, help="Viewport width.")
    parser.add_argument("--height", type=int, default=2200, help="Viewport height.")
    parser.add_argument("--wait-ms", type=int, default=1200, help="Extra wait after load.")
    parser.add_argument("--json-out", help="Optional JSON report path.")
    args = parser.parse_args()

    target = normalize_target(args.target)
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": args.width, "height": args.height})
        page.goto(target, wait_until="load")
        page.wait_for_timeout(args.wait_ms)
        title = page.title()
        page.screenshot(path=str(output_path), full_page=True)
        browser.close()

    payload = {
        "target": target,
        "title": title,
        "screenshot": str(output_path),
        "viewport": {"width": args.width, "height": args.height}
    }
    if args.json_out:
        json_path = Path(args.json_out).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"target={payload['target']}")
    print(f"title={payload['title']}")
    print(f"screenshot={payload['screenshot']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
