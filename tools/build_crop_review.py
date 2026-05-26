#!/usr/bin/env python3
"""Build a lightweight HTML review board for crop QA."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CHARACTERS = ("qingyou", "arisu")
TYPE_ORDER = ("standing", "turnaround", "expressions", "clothing", "accessories", "props", "details")
TYPE_PRIORITY = {"standing", "turnaround", "expressions", "clothing", "accessories", "props"}


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def rel(path: str | Path, base: Path) -> str:
    absolute = path if isinstance(path, Path) and path.is_absolute() else (ROOT / path)
    return os.path.relpath(absolute, base.parent).replace("\\", "/")


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def percent(value: float) -> str:
    return f"{value:.3f}%"


def build_character_payload(character: str, output_path: Path) -> dict[str, Any]:
    manifest_path = ROOT / "assets" / "characters" / character / "workflow" / "crop_manifest.csv"
    rows = read_manifest(manifest_path)
    if not rows:
        raise ValueError(f"empty crop manifest: {manifest_path}")
    source_sheet = ROOT / rows[0]["source_sheet"]
    with Image.open(source_sheet) as image:
        source_width, source_height = image.size

    grouped: dict[str, list[dict[str, Any]]] = {asset_type: [] for asset_type in TYPE_ORDER}
    for row in rows:
        asset_type = row["asset_type"]
        x = int(row["x"])
        y = int(row["y"])
        width = int(row["width"])
        height = int(row["height"])
        grouped.setdefault(asset_type, []).append(
            {
                "asset_name": row["asset_name"],
                "version": row["version"],
                "purpose": row["purpose"],
                "source_sheet": rel(row["source_sheet"], output_path),
                "crop_path": rel(row["output_path"], output_path),
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "left_pct": percent((x / source_width) * 100),
                "top_pct": percent((y / source_height) * 100),
                "width_pct": percent((width / source_width) * 100),
                "height_pct": percent((height / source_height) * 100),
            }
        )

    return {
        "character": character,
        "manifest_path": rel(manifest_path, output_path),
        "source_sheet": rel(source_sheet, output_path),
        "source_width": source_width,
        "source_height": source_height,
        "groups": grouped,
    }


def render_group(character: str, asset_type: str, items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    cards = []
    for item in items:
        cards.append(
            f"""
      <article class="crop-card" data-asset-type="{html_escape(asset_type)}">
        <div class="crop-card-head">
          <div>
            <p class="crop-type">{html_escape(asset_type)}</p>
            <h4>{html_escape(item["asset_name"])} <span>{html_escape(item["version"])}</span></h4>
          </div>
          <p class="coords">x={item["x"]}, y={item["y"]}, w={item["width"]}, h={item["height"]}</p>
        </div>
        <div class="crop-card-body">
          <figure class="source-preview">
            <img src="{html_escape(item["source_sheet"])}" alt="{html_escape(character)} source sheet">
            <div class="crop-box" style="left:{item["left_pct"]}; top:{item["top_pct"]}; width:{item["width_pct"]}; height:{item["height_pct"]};"></div>
          </figure>
          <figure class="crop-preview">
            <img src="{html_escape(item["crop_path"])}" alt="{html_escape(item["asset_name"])} crop">
          </figure>
        </div>
        <p class="purpose">{html_escape(item["purpose"])}</p>
        <p class="paths"><a href="{html_escape(item["crop_path"])}">crop</a> · <a href="{html_escape(item["source_sheet"])}">source</a></p>
      </article>"""
        )
    priority = " priority" if asset_type in TYPE_PRIORITY else ""
    return f"""
    <section class="asset-group{priority}" id="{html_escape(character)}-{html_escape(asset_type)}">
      <div class="group-head">
        <h3>{html_escape(asset_type.title())}</h3>
        <p>{len(items)} crops</p>
      </div>
      <div class="crop-grid">
        {''.join(cards)}
      </div>
    </section>"""


def render_board(payloads: list[dict[str, Any]]) -> str:
    character_sections = []
    for payload in payloads:
        groups = "".join(
            render_group(payload["character"], asset_type, payload["groups"].get(asset_type, []))
            for asset_type in TYPE_ORDER
        )
        character_sections.append(
            f"""
  <section class="character-section" id="{html_escape(payload["character"])}">
    <div class="character-head">
      <div>
        <p class="eyebrow">Crop QA</p>
        <h2>{html_escape(payload["character"].title())}</h2>
      </div>
      <p class="meta"><a href="{html_escape(payload["manifest_path"])}">crop_manifest.csv</a> · {payload["source_width"]}×{payload["source_height"]}</p>
    </div>
    {groups}
  </section>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Luo Sisters Crop Review Board</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f3ef;
      --panel: #fffdfa;
      --ink: #1f2430;
      --muted: #6c7280;
      --line: #d7d0c4;
      --accent: #3e7b6b;
      --priority: #8f5b3a;
      --box: rgba(215, 72, 45, 0.86);
      --box-fill: rgba(215, 72, 45, 0.14);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.45;
    }}
    a {{ color: #275da8; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .page {{
      max-width: 1440px;
      margin: 0 auto;
      padding: 24px;
    }}
    .hero {{
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 20px 24px;
      border-radius: 8px;
      margin-bottom: 20px;
    }}
    .hero h1 {{ margin: 0 0 8px; font-size: 28px; }}
    .hero p, .hero li {{ color: var(--muted); }}
    .hero ul {{ margin: 8px 0 0 20px; padding: 0; }}
    .character-section {{
      margin-bottom: 24px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    .character-head, .group-head {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: baseline;
    }}
    .character-head h2, .group-head h3 {{ margin: 0; }}
    .eyebrow, .crop-type {{
      margin: 0 0 4px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      font-size: 12px;
      color: var(--muted);
    }}
    .meta, .coords, .purpose, .paths {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
    }}
    .asset-group {{
      margin-top: 18px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
    }}
    .asset-group.priority .group-head h3 {{ color: var(--priority); }}
    .crop-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 14px;
      margin-top: 12px;
    }}
    .crop-card {{
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
    }}
    .crop-card-head h4 {{
      margin: 0;
      font-size: 18px;
    }}
    .crop-card-head h4 span {{
      color: var(--muted);
      font-size: 13px;
      font-weight: 500;
      margin-left: 6px;
    }}
    .crop-card-body {{
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 10px;
      margin: 10px 0;
      align-items: start;
    }}
    figure {{
      margin: 0;
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
      background: #f8f7f4;
    }}
    .source-preview {{
      position: relative;
      aspect-ratio: 4 / 3;
    }}
    .source-preview img, .crop-preview img {{
      display: block;
      width: 100%;
      height: 100%;
      object-fit: contain;
      background: #ffffff;
    }}
    .crop-preview {{
      min-height: 180px;
    }}
    .crop-box {{
      position: absolute;
      border: 2px solid var(--box);
      background: var(--box-fill);
      box-shadow: 0 0 0 1px rgba(255,255,255,0.9) inset;
    }}
    @media (max-width: 900px) {{
      .page {{ padding: 14px; }}
      .crop-grid {{ grid-template-columns: 1fr; }}
      .crop-card-body {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <h1>Luo Sisters Crop Review Board</h1>
      <p>Lightweight QA pass before asset generation. Prioritize obvious fixes only: clipped heads, cropped-out props, missing silhouette context, off-target boxes, or strong neighbor bleed.</p>
      <ul>
        <li>Fix only clearly bad crops before generation starts.</li>
        <li>Keep the full source sheet as fallback when a crop is usable but imperfect.</li>
        <li>Priority sections are standing, turnaround, expressions, clothing, accessories, and props.</li>
      </ul>
    </section>
    {''.join(character_sections)}
  </main>
</body>
</html>
"""


def build_review(output_path: Path) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payloads = [build_character_payload(character, output_path) for character in CHARACTERS]
    output_path.write_text(render_board(payloads), encoding="utf-8")
    return {
        "status": "passed",
        "output": str(output_path.relative_to(ROOT).as_posix()),
        "characters": list(CHARACTERS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a lightweight crop review board.")
    parser.add_argument("--output", default="logs/crop_review/index.html", help="Repo-relative HTML output path.")
    parser.add_argument("--json-out", help="Optional JSON report path.")
    args = parser.parse_args()

    output_path = (ROOT / args.output).resolve()
    payload = build_review(output_path)
    if args.json_out:
        json_path = Path(args.json_out).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
