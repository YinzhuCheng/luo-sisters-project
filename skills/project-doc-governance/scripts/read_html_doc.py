#!/usr/bin/env python3
"""Summarize one HTML documentation page without loading decorative layers."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.html_doc_utils import (  # noqa: E402
    classify_link,
    find_repo_root,
    load_catalog_roles,
    parse_html_document,
    parse_target,
)


def render_summary(source: Path, anchor: str | None, max_chars: int, links_only: bool, structure_mode: bool, include_images: bool) -> str:
    parser = parse_html_document(source, anchor=anchor, include_images=include_images)
    repo_root = find_repo_root(source.resolve())
    catalog_roles = load_catalog_roles(repo_root)
    title = parser.output_title()
    seen_links: set[tuple[str, str]] = set()
    link_lines: list[str] = []
    grouped_links: dict[str, list[str]] = {}
    for item in parser.links:
        href = item["href"]
        text = item["text"]
        key = (href, text)
        if key in seen_links:
            continue
        seen_links.add(key)
        category, exists, role = classify_link(href, source, repo_root, catalog_roles)
        role_text = f" | {role}" if role else ""
        text_part = f" | {text}" if text else ""
        line = f"- [{category} | {exists}]{role_text} {href}{text_part}"
        link_lines.append(line)
        grouped_links.setdefault(category, []).append(line)

    asset_lines: list[str] = []
    seen_assets: set[str] = set()
    for image in parser.images:
        src = image["src"]
        if src in seen_assets:
            continue
        seen_assets.add(src)
        category, exists, role = classify_link(src, source, repo_root, catalog_roles)
        role_text = f" | {role}" if role else ""
        asset_lines.append(f"- [{category} | {exists}]{role_text} {src}" + (f" | {image['alt']}" if image["alt"] else ""))

    parts = [
        "# HTML Document Summary",
        f"Source: {source}",
        f"Title: {title}",
    ]
    if anchor:
        parts.append(f"Anchor: {anchor}")
        if not parser.anchor_found:
            parts.append("Anchor status: not found")
    parts.append("")

    if links_only:
        parts.append("## Links")
        parts.extend(link_lines or ["(none)"])
    else:
        if structure_mode:
            parts.append("## Structure")
            parts.extend(parser.headings or ["(no headings found)"])
            parts.append("")
        parts.append("## Content")
        if structure_mode:
            parts.extend(parser.headings or ["(no readable content found)"])
        else:
            parts.extend(parser.body_lines or ["(no readable content found)"])
        parts.append("")
        parts.append("## Link Map")
        parts.extend(link_lines or ["(none)"])
        if structure_mode:
            parts.append("")
            parts.append("## Link Groups")
            for category in ("html", "asset", "markdown", "json", "csv", "anchor", "external", "file"):
                items = grouped_links.get(category)
                if not items:
                    continue
                parts.append(f"### {category}")
                parts.extend(items)
        parts.append("")
        parts.append("## Asset References")
        parts.extend(asset_lines or ["(none)"])
        parts.append("")
        parts.append("## Anchors")
        parts.extend(f"- {item}" for item in parser.anchors[:120])
        if len(parser.anchors) > 120:
            parts.append(f"- ... {len(parser.anchors) - 120} more")

    text = "\n".join(parts).strip() + "\n"
    if max_chars > 0 and len(text) > max_chars:
        return text[:max_chars].rstrip() + f"\n\n[truncated to {max_chars} characters]\n"
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize one HTML documentation page.")
    parser.add_argument("html_path", help="HTML path, optionally with #anchor.")
    parser.add_argument("--anchor", help="Anchor id to read. Overrides #fragment in html_path.")
    parser.add_argument("--max-chars", type=int, default=8000, help="Maximum output characters; 0 disables truncation.")
    parser.add_argument("--include-images", action="store_true", help="Show image references instead of placeholders.")
    parser.add_argument("--list-links-only", action="store_true", help="Only list links from the selected page or anchor.")
    parser.add_argument("--structure-mode", action="store_true", help="Focus on headings, links, and asset references.")
    args = parser.parse_args()

    path, fragment = parse_target(args.html_path)
    anchor = args.anchor or fragment
    if not path.exists():
        print(f"HTML file not found: {path}", file=sys.stderr)
        return 2
    print(render_summary(path, anchor, args.max_chars, args.list_links_only, args.structure_mode, args.include_images), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
