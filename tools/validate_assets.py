#!/usr/bin/env python3
"""Validate Luo sisters asset structure and generated transparent PNGs."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CHARACTER_IDS = ("qingyou", "arisu")
REQUIRED_DIRS = (
    "source_sheet",
    "crops",
    "generated/chroma/standing",
    "generated/chroma/expressions",
    "generated/chroma/turnaround",
    "generated/chroma/clothing",
    "generated/chroma/accessories",
    "generated/chroma/props",
    "generated/chroma/details",
    "generated/chroma/cg",
    "generated/transparent/standing",
    "generated/transparent/expressions",
    "generated/transparent/turnaround",
    "generated/transparent/clothing",
    "generated/transparent/accessories",
    "generated/transparent/props",
    "generated/transparent/details",
    "generated/transparent/cg",
    "generated/rejected",
    "prompts",
    "workflow",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def transparent_corner_ok(path: Path) -> tuple[bool, str]:
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        corners = [
            rgba.getpixel((0, 0))[3],
            rgba.getpixel((rgba.width - 1, 0))[3],
            rgba.getpixel((0, rgba.height - 1))[3],
            rgba.getpixel((rgba.width - 1, rgba.height - 1))[3],
        ]
        if max(corners) > 8:
            return False, f"corners are not transparent enough: {corners}"
        return True, "transparent corners ok"


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_character(character: str, strict: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    config = read_json(ROOT / "characters" / f"{character}.json")
    asset_root = ROOT / config["asset_root"]

    for rel_dir in REQUIRED_DIRS:
        path = asset_root / rel_dir
        if not path.exists():
            errors.append(f"{character}: missing directory {path.relative_to(ROOT)}")

    source = ROOT / config["source_sheet"]
    if not source.exists():
        errors.append(f"{character}: missing source sheet {source.relative_to(ROOT)}")

    manifest = ROOT / config["crop_manifest"]
    if not manifest.exists():
        errors.append(f"{character}: missing crop manifest {manifest.relative_to(ROOT)}")
    else:
        for row in read_manifest(manifest):
            row_source = ROOT / row["source_sheet"]
            row_output = ROOT / row["output_path"]
            if not row["output_path"].startswith(f"assets/characters/{character}/"):
                errors.append(f"{character}: crop output crosses character boundary: {row['output_path']}")
            if not row_source.exists():
                errors.append(f"{character}: crop source missing {row_source.relative_to(ROOT)}")
            if not row_output.exists():
                warnings.append(f"{character}: crop not generated yet {row_output.relative_to(ROOT)}")

    missing_transparent = 0
    checked_transparent = 0
    for asset_group in config["asset_groups"]:
        for item in asset_group["items"]:
            for key in ("crop", "transparent", "prompt"):
                value = item.get(key, "")
                if value and not value.startswith(f"assets/characters/{character}/"):
                    errors.append(f"{character}: {key} crosses character boundary: {value}")
            transparent = item.get("transparent", "")
            if not transparent:
                continue
            transparent_path = ROOT / transparent
            if not transparent_path.exists():
                missing_transparent += 1
                if strict:
                    errors.append(f"{character}: missing transparent asset {transparent_path.relative_to(ROOT)}")
                continue
            checked_transparent += 1
            ok, message = transparent_corner_ok(transparent_path)
            if not ok:
                errors.append(f"{character}: {transparent_path.relative_to(ROOT)} {message}")

    warnings.append(
        f"{character}: {checked_transparent} transparent assets checked; {missing_transparent} transparent assets still planned"
    )
    return errors, warnings


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate structured assets and transparent PNGs.")
    parser.add_argument("--character", choices=(*CHARACTER_IDS, "all"), default="all")
    parser.add_argument("--strict", action="store_true", help="Treat missing transparent assets as errors.")
    args = parser.parse_args()

    characters = CHARACTER_IDS if args.character == "all" else (args.character,)
    all_errors: list[str] = []
    all_warnings: list[str] = []
    for character in characters:
        errors, warnings = validate_character(character, strict=args.strict)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    for warning in all_warnings:
        print(f"WARN {warning}")
    for error in all_errors:
        print(f"ERROR {error}")

    if all_errors:
        raise SystemExit(1)
    print("Asset validation passed.")


if __name__ == "__main__":
    main()
