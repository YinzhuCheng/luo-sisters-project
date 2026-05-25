#!/usr/bin/env python3
"""Summarize one HTML documentation page without loading decorative layers."""
from __future__ import annotations

import argparse
import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag


SKIP_TAGS = {"script", "style", "nav", "header", "footer", "svg", "canvas", "noscript"}
BLOCK_TAGS = {"p", "li", "blockquote", "figcaption", "summary", "td", "th", "pre"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text)).strip()


class DocHTMLParser(HTMLParser):
    def __init__(self, anchor: str | None, include_images: bool, links_only: bool) -> None:
        super().__init__(convert_charrefs=True)
        self.anchor = anchor
        self.include_images = include_images
        self.links_only = links_only
        self.depth = 0
        self.skip_depth = 0
        self.capture_depth: int | None = None
        self.capture_done = False
        self.title_parts: list[str] = []
        self.in_title = False
        self.current_tag: str | None = None
        self.current_parts: list[str] = []
        self.lines: list[str] = []
        self.links: list[tuple[str, str]] = []
        self.anchors: list[str] = []

    def should_capture(self) -> bool:
        if self.skip_depth:
            return False
        if self.capture_done:
            return False
        if not self.anchor:
            return True
        return self.capture_depth is not None and self.depth >= self.capture_depth

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value or "" for key, value in attrs}
        self.depth += 1

        element_id = attrs_dict.get("id") or attrs_dict.get("name")
        if element_id:
            self.anchors.append(element_id)
        if (
            self.anchor
            and self.capture_depth is not None
            and element_id
            and element_id != self.anchor
            and tag == "section"
        ):
            self.flush()
            self.capture_depth = None
            self.capture_done = True
        if self.anchor and element_id == self.anchor and self.capture_depth is None:
            self.capture_depth = self.depth

        if tag in SKIP_TAGS:
            self.skip_depth = self.depth
            return

        if tag == "title":
            self.in_title = True
            self.title_parts = []
            return

        href = attrs_dict.get("href")
        if tag == "a" and href and self.should_capture():
            self.links.append((href, ""))

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
            if self.include_images:
                self.lines.append(f"[image reference: alt=\"{alt}\" src=\"{src}\"]")
            else:
                self.lines.append(f"[image placeholder: alt=\"{alt}\" src=\"{src}\"]")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
            return
        if self.current_tag == tag:
            self.flush()
        if self.skip_depth == self.depth:
            self.skip_depth = 0
        if self.capture_depth == self.depth:
            self.capture_depth = None
        self.depth = max(0, self.depth - 1)

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
            return
        if self.skip_depth or self.links_only:
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
                self.lines.append(f"{'#' * min(level, 6)} {text}")
            elif self.current_tag == "li":
                self.lines.append(f"- {text}")
            else:
                self.lines.append(text)
        self.current_tag = None
        self.current_parts = []

    def output(self, source: str, max_chars: int) -> str:
        self.flush()
        title = clean(" ".join(self.title_parts)) or "(untitled)"
        seen_links: set[tuple[str, str]] = set()
        link_lines = []
        for href, text in self.links:
            item = (href, text)
            if item not in seen_links:
                seen_links.add(item)
                link_lines.append(f"- {href}" + (f" | {text}" if text else ""))

        parts = [
            f"# HTML Document Summary",
            f"Source: {source}",
            f"Title: {title}",
        ]
        if self.anchor:
            parts.append(f"Anchor: {self.anchor}")
        parts.append("")
        if self.links_only:
            parts.append("## Links")
            parts.extend(link_lines or ["(none)"])
        else:
            parts.append("## Content")
            parts.extend(self.lines or ["(no readable content found)"])
            parts.append("")
            parts.append("## Links")
            parts.extend(link_lines or ["(none)"])
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
    args = parser.parse_args()

    path, fragment = parse_target(args.html_path)
    anchor = args.anchor or fragment
    if not path.exists():
        print(f"HTML file not found: {path}", file=sys.stderr)
        return 2
    html = path.read_text(encoding="utf-8", errors="replace")
    doc = DocHTMLParser(anchor=anchor, include_images=args.include_images, links_only=args.list_links_only)
    doc.feed(html)
    print(doc.output(str(path) + (f"#{anchor}" if anchor else ""), args.max_chars), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
