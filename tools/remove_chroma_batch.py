#!/usr/bin/env python3
"""Convert solid chroma-key generated images into transparent PNG assets.

Generated chroma sources are expected under:
    assets/characters/<character>/generated/chroma/<asset_type>/

Transparent outputs are mirrored under:
    assets/characters/<character>/generated/transparent/<asset_type>/
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CHARACTER_IDS = ("qingyou", "arisu")
ASSET_TYPES = ("standing", "expressions", "turnaround", "clothing", "accessories", "props", "details", "cg")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def parse_hex_color(value: str) -> tuple[int, int, int]:
    raw = value.strip().lstrip("#")
    if len(raw) != 6:
        raise ValueError(f"Expected 6-digit hex color, got {value}")
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def alpha_for_pixel(rgb: tuple[int, int, int], key: tuple[int, int, int], transparent_threshold: float, opaque_threshold: float) -> int:
    dist = distance(rgb, key)
    if dist <= transparent_threshold:
        return 0
    if dist >= opaque_threshold:
        return 255
    return int(255 * ((dist - transparent_threshold) / (opaque_threshold - transparent_threshold)))


def remove_chroma(input_path: Path, output_path: Path, key: tuple[int, int, int], transparent_threshold: float, opaque_threshold: float) -> None:
    with Image.open(input_path) as image:
        rgba = image.convert("RGBA")
        pixels = rgba.load()
        for y in range(rgba.height):
            for x in range(rgba.width):
                r, g, b, a = pixels[x, y]
                alpha = min(a, alpha_for_pixel((r, g, b), key, transparent_threshold, opaque_threshold))
                pixels[x, y] = (r, g, b, alpha)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        rgba.save(output_path)


def source_dir(character: str, asset_type: str) -> Path:
    return ROOT / "assets" / "characters" / character / "generated" / "chroma" / asset_type


def output_for(character: str, asset_type: str, source: Path) -> Path:
    return ROOT / "assets" / "characters" / character / "generated" / "transparent" / asset_type / f"{source.stem}.png"


def iter_sources(character: str, asset_type: str) -> list[Path]:
    base = source_dir(character, asset_type)
    if not base.exists():
        return []
    return sorted(path for path in base.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES and path.is_file())


def process(character: str, asset_type: str, args: argparse.Namespace) -> list[str]:
    key = parse_hex_color(args.key)
    results: list[str] = []
    for source in iter_sources(character, asset_type):
        output = output_for(character, asset_type, source)
        if output.exists() and not args.force:
            results.append(f"skip existing {output.relative_to(ROOT)}")
            continue
        if args.dry_run:
            results.append(f"would remove chroma {source.relative_to(ROOT)} -> {output.relative_to(ROOT)}")
            continue
        remove_chroma(
            source,
            output,
            key=key,
            transparent_threshold=args.transparent_threshold,
            opaque_threshold=args.opaque_threshold,
        )
        results.append(f"wrote {output.relative_to(ROOT)}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch remove chroma-key backgrounds from generated assets.")
    parser.add_argument("--character", choices=(*CHARACTER_IDS, "all"), default="all")
    parser.add_argument("--asset-type", choices=(*ASSET_TYPES, "all"), default="all")
    parser.add_argument("--key", default="#ff00ff", help="Chroma key color. Default #ff00ff.")
    parser.add_argument("--transparent-threshold", type=float, default=18.0)
    parser.add_argument("--opaque-threshold", type=float, default=92.0)
    parser.add_argument("--force", action="store_true", help="Overwrite existing transparent files.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    characters = CHARACTER_IDS if args.character == "all" else (args.character,)
    asset_types = ASSET_TYPES if args.asset_type == "all" else (args.asset_type,)
    total = 0
    for character in characters:
        for asset_type in asset_types:
            results = process(character, asset_type, args)
            total += len(results)
            for line in results:
                print(line)
    if total == 0:
        print("No chroma source images found.")


if __name__ == "__main__":
    main()
