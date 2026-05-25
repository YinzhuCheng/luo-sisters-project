#!/usr/bin/env python3
"""Build Markdown mirrors from project HTML pages."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from html_doc_utils import (
    classify_link,
    default_mirror_markdown_path,
    find_repo_root,
    load_catalog,
    load_catalog_roles,
    mirror_mapping,
    normalize_lines,
    parse_html_document,
    resolve_local_href,
    rewrite_image_placeholders,
    rewrite_markdown_links,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS_MIRROR_DIR = ROOT / "docs_mirror"
DEFAULT_LOCALES = ("zh-CN", "en")
FORBIDDEN_HTML_TAGS = ("<img", "<style", "<script", "<div", "<span", "<section", "<table")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def selected_html_entries(locales: tuple[str, ...]) -> list[dict[str, Any]]:
    catalog = load_catalog(ROOT)
    entries: list[dict[str, Any]] = []
    for entry in catalog.get("documents", []):
        if entry.get("type") != "html":
            continue
        if entry.get("language") not in locales:
            continue
        entries.append(entry)
    return entries


def ensure_mirror_path(entry: dict[str, Any]) -> str:
    return str(entry.get("mirror_markdown") or default_mirror_markdown_path(str(entry["path"])))


def link_appendix(source_path: Path, output_path: Path, links: list[dict[str, str]], repo_root: Path, html_to_mirror: dict[str, str], catalog_roles: dict[str, str]) -> list[str]:
    seen: set[tuple[str, str]] = set()
    lines: list[str] = []
    for item in links:
        href = item["href"]
        text = item["text"]
        key = (href, text)
        if key in seen:
            continue
        seen.add(key)
        category, exists, role = classify_link(href, source_path, repo_root, catalog_roles)
        rewritten = resolve_local_href(href, source_path, output_path, repo_root, html_to_mirror)
        role_text = f" | {role}" if role else ""
        label = text or rewritten
        lines.append(f"- `{category} | {exists}{role_text}` {label}: [{rewritten}]({rewritten})")
    return lines or ["(none)"]


def resource_appendix(source_path: Path, output_path: Path, images: list[dict[str, str]], repo_root: Path, html_to_mirror: dict[str, str], catalog_roles: dict[str, str]) -> list[str]:
    seen: set[str] = set()
    lines: list[str] = []
    for image in images:
        src = image["src"]
        if src in seen:
            continue
        seen.add(src)
        category, exists, role = classify_link(src, source_path, repo_root, catalog_roles)
        rewritten = resolve_local_href(src, source_path, output_path, repo_root, html_to_mirror)
        role_text = f" | {role}" if role else ""
        alt_text = f' alt="{image["alt"]}"' if image["alt"] else ""
        lines.append(f"- `{category} | {exists}{role_text}` {rewritten}{alt_text}")
    return lines or ["(none)"]


def render_markdown_mirror(source_path: Path, output_path: Path, html_to_mirror: dict[str, str]) -> str:
    repo_root = find_repo_root(source_path.resolve()) or ROOT
    catalog_roles = load_catalog_roles(repo_root)
    parser = parse_html_document(source_path)
    body = "\n".join(parser.body_lines).strip()
    if body:
        body = rewrite_markdown_links(body, source_path, output_path, repo_root, html_to_mirror)
        body = rewrite_image_placeholders(body, source_path, output_path, repo_root, html_to_mirror)
    link_lines = link_appendix(source_path, output_path, parser.links, repo_root, html_to_mirror, catalog_roles)
    resource_lines = resource_appendix(source_path, output_path, parser.images, repo_root, html_to_mirror, catalog_roles)
    anchors = [f"- `{item}`" for item in parser.anchors] or ["(none)"]
    lines = [
        f"# {parser.output_title()}",
        "",
        f"Source HTML: `{source_path.relative_to(ROOT).as_posix()}`",
        "",
        "## Content",
    ]
    if body:
        lines.extend(body.splitlines())
    else:
        lines.append("(no readable content found)")
    lines.extend(
        [
            "",
            "## Page Links",
            *link_lines,
            "",
            "## Page Anchors",
            *anchors,
            "",
            "## Resource References",
            *resource_lines,
            "",
        ]
    )
    return "\n".join(normalize_lines(lines))


def stale_candidates(locales: tuple[str, ...]) -> list[Path]:
    candidates = list(DOCS_MIRROR_DIR.rglob("*.md")) if DOCS_MIRROR_DIR.exists() else []
    if locales == DEFAULT_LOCALES:
        return candidates
    filtered: list[Path] = []
    for path in candidates:
        relative = path.relative_to(DOCS_MIRROR_DIR).as_posix()
        if locales == ("en",):
            if relative.startswith("en/"):
                filtered.append(path)
        elif locales == ("zh-CN",):
            if not relative.startswith("en/"):
                filtered.append(path)
    return filtered


def validate_markdown_text(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    for snippet in FORBIDDEN_HTML_TAGS:
        if snippet in text.lower():
            errors.append(f"{path.relative_to(ROOT)} contains forbidden HTML residue: {snippet}")
    return errors


def build_markdown_mirrors(locales: tuple[str, ...], check: bool = False) -> dict[str, Any]:
    entries = selected_html_entries(locales)
    html_to_mirror = {str(entry["path"]): ensure_mirror_path(entry) for entry in selected_html_entries(DEFAULT_LOCALES)}
    expected_paths: set[Path] = set()
    outputs: list[str] = []
    stale: list[str] = []
    errors: list[str] = []

    for entry in entries:
        source_path = ROOT / str(entry["path"])
        mirror_path = ROOT / ensure_mirror_path(entry)
        expected_paths.add(mirror_path)
        if not source_path.exists():
            errors.append(f"missing source HTML for mirror generation: {entry['path']}")
            continue
        rendered = render_markdown_mirror(source_path, mirror_path, html_to_mirror)
        errors.extend(validate_markdown_text(mirror_path, rendered))
        if check:
            if not mirror_path.exists():
                errors.append(f"missing Markdown mirror: {mirror_path.relative_to(ROOT).as_posix()}")
            else:
                existing = mirror_path.read_text(encoding="utf-8")
                if existing != rendered:
                    errors.append(f"stale Markdown mirror: {mirror_path.relative_to(ROOT).as_posix()}")
        else:
            mirror_path.parent.mkdir(parents=True, exist_ok=True)
            mirror_path.write_text(rendered, encoding="utf-8")
            outputs.append(mirror_path.relative_to(ROOT).as_posix())

    for candidate in stale_candidates(locales):
        if candidate not in expected_paths:
            relative = candidate.relative_to(ROOT).as_posix()
            stale.append(relative)
            if check:
                errors.append(f"stale Markdown mirror present: {relative}")
            else:
                candidate.unlink()

    if not check and DOCS_MIRROR_DIR.exists():
        for directory in sorted(DOCS_MIRROR_DIR.rglob("*"), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()

    return {
        "status": "failed" if errors else "passed",
        "locales": list(locales),
        "generated": outputs,
        "stale": stale,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Markdown mirrors from project HTML pages.")
    parser.add_argument("--locale", choices=DEFAULT_LOCALES, help="Only build one locale mirror subtree.")
    parser.add_argument("--check", action="store_true", help="Verify mirrors are present and synchronized without writing.")
    parser.add_argument("--json-out", help="Optional JSON report path.")
    args = parser.parse_args()

    locales = (args.locale,) if args.locale else DEFAULT_LOCALES
    payload = build_markdown_mirrors(locales, check=args.check)
    if args.json_out:
        write_json(Path(args.json_out).resolve(), payload)
    if payload["status"] == "failed":
        for error in payload["errors"]:
            print(f"ERROR {error}")
        return 1
    for item in payload["generated"]:
        print(f"Wrote {ROOT / item}")
    if args.check:
        print("Markdown mirror check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
