#!/usr/bin/env python3
"""Crop reference images from the full character sheets.

Examples:
    python tools/crop_from_sheet.py --character all --force
    python tools/crop_from_sheet.py --character qingyou
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CHARACTER_IDS = ("qingyou", "arisu")


def manifest_path(character: str) -> Path:
    return ROOT / "assets" / "characters" / character / "workflow" / "crop_manifest.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def crop_row(row: dict[str, str], force: bool, dry_run: bool) -> str:
    source = ROOT / row["source_sheet"]
    output = ROOT / row["output_path"]
    x = int(row["x"])
    y = int(row["y"])
    width = int(row["width"])
    height = int(row["height"])

    if output.exists() and not force:
        return f"skip existing {output.relative_to(ROOT)}"

    if dry_run:
        return f"would crop {output.relative_to(ROOT)}"

    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        right = x + width
        lower = y + height
        if x < 0 or y < 0 or right > image.width or lower > image.height:
            raise ValueError(
                f"Crop is out of bounds for {source}: "
                f"{x},{y},{width},{height} within {image.width}x{image.height}"
            )
        image.crop((x, y, right, lower)).save(output)
    return f"wrote {output.relative_to(ROOT)}"


def crop_character(character: str, force: bool, dry_run: bool) -> list[str]:
    path = manifest_path(character)
    rows = read_rows(path)
    results = [f"{character}: {len(rows)} crop rows from {path.relative_to(ROOT)}"]
    for row in rows:
        results.append(crop_row(row, force=force, dry_run=dry_run))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Crop reference images from source character sheets.")
    parser.add_argument("--character", choices=(*CHARACTER_IDS, "all"), default="all")
    parser.add_argument("--force", action="store_true", help="Overwrite existing crop files.")
    parser.add_argument("--dry-run", action="store_true", help="Print crop actions without writing files.")
    args = parser.parse_args()

    characters = CHARACTER_IDS if args.character == "all" else (args.character,)
    for character in characters:
        for line in crop_character(character, force=args.force, dry_run=args.dry_run):
            print(line)


if __name__ == "__main__":
    main()
