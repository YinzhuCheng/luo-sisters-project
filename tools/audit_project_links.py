#!/usr/bin/env python3
"""Audit project links, asset references, and forbidden legacy entrypoints."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import urldefrag

from build_html_markdown_mirror import build_markdown_mirrors
from html_doc_utils import default_mirror_markdown_path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SNIPPETS = (
    "docs/luo_sisters_project_guide_v2.html",
    "assets/images/luo_qingyou_character_sheet_v2.png",
    "assets/images/luo_arisu_character_sheet_v1.png",
)
TEXT_EXTENSIONS = {".md", ".html", ".json"}


def strip_fragment(path: str) -> str:
    return urldefrag(path)[0]


def is_planned_output(rel_path: str) -> bool:
    normalized = strip_fragment(rel_path).replace("\\", "/")
    return (
        normalized.startswith("assets/characters/")
        and "/generated/transparent/" in normalized
        and normalized.endswith(".png")
    )


def is_planned_target(target: Path) -> bool:
    try:
        relative = target.relative_to(ROOT).as_posix()
    except ValueError:
        return False
    return is_planned_output(relative)


def local_target(path: str, base_path: Path) -> Path | None:
    if not path or path.startswith(("#", "http://", "https://", "mailto:")):
        return None
    target_path = strip_fragment(path)
    if not target_path:
        return None
    return (base_path.parent / target_path).resolve()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def scan_text_links(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for snippet in FORBIDDEN_SNIPPETS:
        if snippet in text:
            errors.append(f"{path.relative_to(ROOT)} contains forbidden legacy reference: {snippet}")
    matches = re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
    matches.extend(re.findall(r"""(?:href|src)=["']([^"']+)["']""", text))
    seen: set[str] = set()
    for match in matches:
        if match in seen:
            continue
        seen.add(match)
        target = local_target(match, path)
        if target and not target.exists() and not is_planned_target(target):
            errors.append(f"{path.relative_to(ROOT)} -> missing local target {match}")
    return errors


def audit_manifest() -> list[str]:
    errors: list[str] = []
    data = read_json(ROOT / "manifest.json")
    for rel_path in data.get("included_files", []):
        if not (ROOT / rel_path).exists():
            errors.append(f"manifest.json references missing file {rel_path}")
    return errors


def audit_document_catalog() -> list[str]:
    errors: list[str] = []
    data = read_json(ROOT / "project_data" / "document_catalog.json")
    for entry in data.get("documents", []):
        path = ROOT / entry["path"]
        if not path.exists():
            errors.append(f"document_catalog.json references missing file {entry['path']}")
        if entry.get("type") == "html":
            mirror = str(entry.get("mirror_markdown") or default_mirror_markdown_path(entry["path"]))
            if not (ROOT / mirror).exists():
                errors.append(f"document_catalog.json mirror missing: {entry['path']} -> {mirror}")
        for child in entry.get("children", []):
            child_path = strip_fragment(child)
            if not child_path or child_path.startswith("#"):
                continue
            if not (ROOT / child_path).exists() and not is_planned_output(child):
                errors.append(f"document_catalog.json child missing: {entry['path']} -> {child}")
    return errors


def audit_character_configs() -> list[str]:
    errors: list[str] = []
    for character in ("qingyou", "arisu"):
        data = read_json(ROOT / "characters" / f"{character}.json")
        for key in ("asset_root", "source_sheet", "crop_manifest"):
            if not (ROOT / data[key]).exists():
                errors.append(f"{character}.json missing {key}: {data[key]}")
        for group in data["asset_groups"]:
            for item in group["items"]:
                for key in ("crop", "prompt"):
                    value = item.get(key, "")
                    target = strip_fragment(value)
                    if target and not (ROOT / target).exists():
                        errors.append(f"{character}.json missing {key}: {value}")
                transparent = item.get("transparent", "")
                if transparent and not transparent.startswith(f"assets/characters/{character}/"):
                    errors.append(f"{character}.json output crosses boundary: {transparent}")
    return errors


def audit_registry() -> list[str]:
    errors: list[str] = []
    path = ROOT / "logs" / "asset_registry.csv"
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for field in ("prompt_path",):
            target = strip_fragment(row[field])
            if target and not (ROOT / target).exists():
                errors.append(f"asset_registry.csv missing {field}: {row[field]}")
        crop_target = strip_fragment(row["source_crop"])
        if crop_target and not (ROOT / crop_target).exists():
            errors.append(f"asset_registry.csv missing source_crop: {row['source_crop']}")
        if row["output_path"] and not row["output_path"].startswith(f"assets/characters/{row['character']}/"):
            errors.append(f"asset_registry.csv output crosses boundary: {row['output_path']}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit repository links and structured asset references.")
    parser.add_argument("--json-out", help="Optional JSON report path.")
    args = parser.parse_args()
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in TEXT_EXTENSIONS:
            if path.name == "luo_sisters_project_guide_v2.html":
                continue
            errors.extend(scan_text_links(path))
    errors.extend(audit_manifest())
    errors.extend(audit_document_catalog())
    errors.extend(audit_character_configs())
    errors.extend(audit_registry())
    mirror_payload = build_markdown_mirrors(("zh-CN", "en"), check=True)
    errors.extend(mirror_payload.get("errors", []))

    payload = {
        "status": "failed" if errors else "passed",
        "errors": errors
    }
    if args.json_out:
        json_path = Path(args.json_out).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        raise SystemExit(1)
    print("Project link audit passed.")


if __name__ == "__main__":
    main()
