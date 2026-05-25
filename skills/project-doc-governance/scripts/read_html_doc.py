#!/usr/bin/env python3
"""Summarize one HTML documentation page without loading decorative layers."""
from __future__ import annotations

import argparse
import json
import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag


SKIP_TAGS = {"script", "style", "nav", "header", "footer", "svg", "canvas", "noscript", "aside"}
BLOCK_TAGS = {"p", "li", "blockquote", "figcaption", "summary", "td", "th", "pre"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text)).strip()


def find_repo_root(start: Path) -> Path | None:
    for candidate in [start, *start.parents]:
        if (candidate / "project_data" / "document_catalog.json").exists():
            return candidate
    return None


def load_catalog_roles(repo_root: Path | None) -> dict[str, str]:
    if not repo_root:
        return {}
    path = repo_root / "project_data" / "document_catalog.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return {entry["path"]: entry.get("role", "") for entry in data.get("documents", [])}


def classify_link(href: str, base_path: Path, repo_root: Path | None, catalog_roles: dict[str, str]) -> tuple[str, str, str]:
    if href.startswith(("http://", "https://", "mailto:")):
        return "external", "n/a", ""
    if href.startswith("#"):
        return "anchor", "n/a", ""
    link_path, _fragment = urldefrag(href)
    if not link_path:
        return "anchor", "n/a", ""
    target = (base_path.parent / link_path).resolve()
    exists = "ok" if target.exists() else "missing"
    try:
        relative = target.relative_to(repo_root).as_posix() if repo_root else ""
    except ValueError:
        relative = ""
    if (
        exists == "missing"
        and relative.startswith("assets/characters/")
        and "/generated/transparent/" in relative
        and relative.endswith(".png")
    ):
        exists = "planned"
    role = ""
    if repo_root:
        role = catalog_roles.get(relative, "")
        if relative.startswith("assets/"):
            return "asset", exists, role
        if relative.endswith(".html"):
            return "html", exists, role
        if relative.endswith(".md"):
            return "markdown", exists, role
        if relative.endswith(".json"):
            return "json", exists, role
        if relative.endswith(".csv"):
            return "csv", exists, role
    return "file", exists, role


class DocHTMLParser(HTMLParser):
    def __init__(
        self,
        anchor: str | None,
        include_images: bool,
        links_only: bool,
        structure_mode: bool,
    ) -> None:
        super().__init__(convert_charrefs=True)
        self.anchor = anchor
        self.include_images = include_images
        self.links_only = links_only
        self.structure_mode = structure_mode
        self.depth = 0
        self.skip_depth = 0
        self.capture_depth: int | None = None
        self.capture_done = False
        self.anchor_found = False
        self.title_parts: list[str] = []
        self.in_title = False
        self.current_tag: str | None = None
        self.current_parts: list[str] = []
        self.lines: list[str] = []
        self.headings: list[str] = []
        self.links: list[dict[str, str]] = []
        self.anchors: list[str] = []
        self.images: list[dict[str, str]] = []
        self.current_link_href: str | None = None
        self.current_link_parts: list[str] = []

    def should_capture(self) -> bool:
        if self.skip_depth or self.capture_done:
            return False
        if not self.anchor:
            return True
        return self.capture_depth is not None and self.depth >= self.capture_depth

    def start_capture_if_needed(self, element_id: str | None) -> None:
        if self.anchor and element_id == self.anchor and self.capture_depth is None:
            self.capture_depth = self.depth
            self.capture_done = False
            self.anchor_found = True

    def stop_capture_if_needed(self, element_id: str | None) -> None:
        if not self.anchor or self.capture_depth is None or not element_id or element_id == self.anchor:
            return
        if self.depth <= self.capture_depth:
            self.flush()
            self.capture_depth = None
            self.capture_done = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value or "" for key, value in attrs}
        self.depth += 1

        element_id = attrs_dict.get("id") or attrs_dict.get("name")
        if element_id:
            self.anchors.append(element_id)
        self.stop_capture_if_needed(element_id)
        self.start_capture_if_needed(element_id)

        if tag in SKIP_TAGS:
            self.skip_depth = self.depth
            return

        if tag == "title":
            self.in_title = True
            self.title_parts = []
            return

        if tag == "a" and self.should_capture():
            self.current_link_href = attrs_dict.get("href", "")
            self.current_link_parts = []

        if self.links_only:
            return

        if tag in HEADING_TAGS and self.should_capture():
            self.flush()
            self.current_tag = tag
            self.current_parts = []
        elif tag in BLOCK_TAGS and self.should_capture():
            self.flush()
            self.current_tag = tag
            self.current_parts = []
        elif tag == "img" and self.should_capture():
            alt = clean(attrs_dict.get("alt", ""))
            src = attrs_dict.get("src", "")
            self.images.append({"alt": alt, "src": src})
            if self.structure_mode:
                return
            if self.include_images:
                self.lines.append(f"[image reference: alt=\"{alt}\" src=\"{src}\"]")
            else:
                self.lines.append(f"[image placeholder: alt=\"{alt}\" src=\"{src}\"]")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
            return
        if tag == "a" and self.current_link_href is not None:
            href = self.current_link_href
            if href:
                self.links.append({"href": href, "text": clean(" ".join(self.current_link_parts))})
            self.current_link_href = None
            self.current_link_parts = []
        if self.current_tag == tag:
            self.flush()
        if self.skip_depth == self.depth:
            self.skip_depth = 0
        self.depth = max(0, self.depth - 1)

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
            return
        if self.skip_depth:
            return
        if self.current_link_href is not None and self.should_capture():
            self.current_link_parts.append(data)
        if self.links_only or self.structure_mode and not self.current_tag:
            return
        if self.current_tag and self.should_capture():
            self.current_parts.append(data)

    def flush(self) -> None:
        if not self.current_tag:
            return
        text = clean(" ".join(self.current_parts))
        if text:
            if self.current_tag in HEADING_TAGS:
                level = int(self.current_tag[1])
                heading = f"{'#' * min(level, 6)} {text}"
                self.lines.append(heading)
                self.headings.append(heading)
            elif self.current_tag == "li":
                self.lines.append(f"- {text}")
            else:
                self.lines.append(text)
        self.current_tag = None
        self.current_parts = []

    def output(self, source: Path, max_chars: int) -> str:
        self.flush()
        repo_root = find_repo_root(source.resolve())
        catalog_roles = load_catalog_roles(repo_root)
        title = clean(" ".join(self.title_parts)) or "(untitled)"
        seen_links: set[tuple[str, str]] = set()
        link_lines = []
        grouped_links: dict[str, list[str]] = {}
        for item in self.links:
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

        asset_lines = []
        seen_assets: set[str] = set()
        for image in self.images:
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
        if self.anchor:
            parts.append(f"Anchor: {self.anchor}")
            if not self.anchor_found:
                parts.append("Anchor status: not found")
        parts.append("")
        if self.links_only:
            parts.append("## Links")
            parts.extend(link_lines or ["(none)"])
        else:
            if self.structure_mode:
                parts.append("## Structure")
                parts.extend(self.headings or ["(no headings found)"])
                parts.append("")
            parts.append("## Content")
            parts.extend(self.lines or ["(no readable content found)"])
            parts.append("")
            parts.append("## Link Map")
            parts.extend(link_lines or ["(none)"])
            if self.structure_mode:
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
            parts.extend(f"- {anchor}" for anchor in self.anchors[:120])
            if len(self.anchors) > 120:
                parts.append(f"- ... {len(self.anchors) - 120} more")

        text = "\n".join(parts).strip() + "\n"
        if max_chars > 0 and len(text) > max_chars:
            return text[:max_chars].rstrip() + f"\n\n[truncated to {max_chars} characters]\n"
        return text


def parse_target(raw: str) -> tuple[Path, str | None]:
    path_text, fragment = urldefrag(raw)
    return Path(path_text), fragment or None


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
    html = path.read_text(encoding="utf-8", errors="replace")
    doc = DocHTMLParser(
        anchor=anchor,
        include_images=args.include_images,
        links_only=args.list_links_only,
        structure_mode=args.structure_mode,
    )
    doc.feed(html)
    print(doc.output(path, args.max_chars), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
