#!/usr/bin/env python3
"""Shared HTML parsing and link utilities for doc summaries and Markdown mirrors."""
from __future__ import annotations

import json
import os
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag


SKIP_TAGS = {"script", "style", "nav", "header", "footer", "svg", "canvas", "noscript", "aside"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
TEXT_BLOCK_TAGS = {"p", "li", "blockquote", "figcaption", "summary", "pre"}
MEANINGFUL_DIV_CLASSES = {"profile-row", "source-links", "swatch", "sheet-actions", "asset-placeholder", "tag-row"}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text)).strip()


def parse_target(raw: str) -> tuple[Path, str | None]:
    path_text, fragment = urldefrag(raw)
    return Path(path_text), fragment or None


def strip_fragment(path: str) -> str:
    return urldefrag(path)[0]


def find_repo_root(start: Path) -> Path | None:
    for candidate in [start, *start.parents]:
        if (candidate / "project_data" / "document_catalog.json").exists():
            return candidate
    return None


def load_catalog(repo_root: Path | None) -> dict[str, Any]:
    if not repo_root:
        return {}
    path = repo_root / "project_data" / "document_catalog.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_catalog_roles(repo_root: Path | None) -> dict[str, str]:
    data = load_catalog(repo_root)
    return {entry["path"]: entry.get("role", "") for entry in data.get("documents", [])}


def is_planned_output(relative: str) -> bool:
    normalized = strip_fragment(relative).replace("\\", "/")
    return (
        normalized.startswith("assets/characters/")
        and "/generated/transparent/" in normalized
        and normalized.endswith(".png")
    )


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
    relative = ""
    if repo_root:
        try:
            relative = target.relative_to(repo_root).as_posix()
        except ValueError:
            relative = ""
    if exists == "missing" and relative and is_planned_output(relative):
        exists = "planned"
    role = catalog_roles.get(relative, "") if relative else ""
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


def default_mirror_markdown_path(html_path: str) -> str:
    normalized = html_path.replace("\\", "/")
    stem = normalized[:-5] if normalized.endswith(".html") else normalized
    return f"docs_mirror/{stem}.md"


def mirror_mapping(repo_root: Path) -> dict[str, str]:
    data = load_catalog(repo_root)
    mapping: dict[str, str] = {}
    for entry in data.get("documents", []):
        path = str(entry.get("path", ""))
        if path.endswith(".html"):
            mapping[path] = str(entry.get("mirror_markdown") or default_mirror_markdown_path(path))
    return mapping


def resolve_local_href(href: str, source_path: Path, output_path: Path, repo_root: Path, html_to_mirror: dict[str, str]) -> str:
    if not href or href.startswith(("http://", "https://", "mailto:", "#")):
        return href
    path_text, fragment = urldefrag(href)
    target = (source_path.parent / path_text).resolve()
    try:
        relative = target.relative_to(repo_root).as_posix()
    except ValueError:
        return href
    mapped = html_to_mirror.get(relative, relative)
    new_target = repo_root / mapped
    rendered = os.path.relpath(new_target, output_path.parent).replace("\\", "/")
    return f"{rendered}#{fragment}" if fragment else rendered


def rewrite_markdown_links(markdown: str, source_path: Path, output_path: Path, repo_root: Path, html_to_mirror: dict[str, str]) -> str:
    pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

    def replace(match: re.Match[str]) -> str:
        label = match.group(1)
        href = match.group(2)
        rewritten = resolve_local_href(href, source_path, output_path, repo_root, html_to_mirror)
        return f"[{label}]({rewritten})"

    return pattern.sub(replace, markdown)


def rewrite_image_placeholders(markdown: str, source_path: Path, output_path: Path, repo_root: Path, html_to_mirror: dict[str, str]) -> str:
    pattern = re.compile(r'(\[image placeholder:\s+alt="[^"]*"\s+src=")([^"]+)("\])')

    def replace(match: re.Match[str]) -> str:
        prefix = match.group(1)
        src = match.group(2)
        suffix = match.group(3)
        rewritten = resolve_local_href(src, source_path, output_path, repo_root, html_to_mirror)
        return f"{prefix}{rewritten}{suffix}"

    return pattern.sub(replace, markdown)


def render_table(rows: list[list[str]]) -> list[str]:
    if not rows:
        return []
    width = max(len(row) for row in rows)
    normalized_rows = [row + [""] * (width - len(row)) for row in rows]
    header = normalized_rows[0]
    separator = ["---"] * width
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    for row in normalized_rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def normalize_lines(lines: list[str]) -> list[str]:
    normalized: list[str] = []
    last_blank = True
    for line in lines:
        value = line.rstrip()
        if not value:
            if not last_blank:
                normalized.append("")
            last_blank = True
            continue
        normalized.append(value)
        last_blank = False
    if normalized and normalized[-1] != "":
        normalized.append("")
    return normalized


class RepositoryHTMLParser(HTMLParser):
    def __init__(self, anchor: str | None = None, include_images: bool = False) -> None:
        super().__init__(convert_charrefs=True)
        self.anchor = anchor
        self.include_images = include_images
        self.depth = 0
        self.skip_depth = 0
        self.capture_depth: int | None = None
        self.capture_done = False
        self.anchor_found = False
        self.title_parts: list[str] = []
        self.in_title = False
        self.anchors: list[str] = []
        self.links: list[dict[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.body_lines: list[str] = []
        self.headings: list[str] = []
        self.list_stack: list[str] = []
        self.current_tag: str | None = None
        self.current_tag_end: str | None = None
        self.current_tag_depth: int | None = None
        self.current_parts: list[str] = []
        self.current_link_href: str | None = None
        self.current_link_parts: list[str] = []
        self.current_table: list[list[str]] | None = None
        self.current_row: list[str] | None = None
        self.current_cell_parts: list[str] | None = None
        self.current_cell_tag: str | None = None

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

    def start_text_block(self, tag: str, end_tag: str) -> None:
        if not self.should_capture():
            return
        self.flush()
        self.current_tag = tag
        self.current_tag_end = end_tag
        self.current_tag_depth = self.depth
        self.current_parts = []

    def append_text_line(self, line: str) -> None:
        if line:
            self.body_lines.append(line)

    def flush(self) -> None:
        if not self.current_tag:
            return
        tag = self.current_tag
        text = ""
        if tag == "pre":
            text = "".join(self.current_parts).strip("\n")
        else:
            text = clean("".join(self.current_parts))
        if text:
            if tag in HEADING_TAGS:
                level = int(tag[1])
                heading = f"{'#' * min(level, 6)} {text}"
                self.append_text_line(heading)
                self.append_text_line("")
                self.headings.append(heading)
            elif tag == "summary":
                heading = f"#### {text}"
                self.append_text_line(heading)
                self.append_text_line("")
                self.headings.append(heading)
            elif tag == "li":
                prefix = "1." if self.list_stack and self.list_stack[-1] == "ol" else "-"
                indent = "  " * max(0, len(self.list_stack) - 1)
                self.append_text_line(f"{indent}{prefix} {text}")
            elif tag == "pre":
                self.append_text_line("```text")
                for line in text.splitlines():
                    self.append_text_line(line.rstrip())
                self.append_text_line("```")
                self.append_text_line("")
            else:
                self.append_text_line(text)
                self.append_text_line("")
        self.current_tag = None
        self.current_tag_end = None
        self.current_tag_depth = None
        self.current_parts = []

    def flush_table(self) -> None:
        if self.current_table:
            for line in render_table(self.current_table):
                self.append_text_line(line)
            self.append_text_line("")
        self.current_table = None
        self.current_row = None
        self.current_cell_parts = None
        self.current_cell_tag = None

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
            return

        if tag in {"ul", "ol"} and self.should_capture():
            self.list_stack.append(tag)
            return

        if tag == "table" and self.should_capture():
            self.flush()
            self.current_table = []
            return
        if tag == "tr" and self.current_table is not None:
            self.current_row = []
            return
        if tag in {"td", "th"} and self.current_row is not None:
            self.current_cell_tag = tag
            self.current_cell_parts = []
            return

        if tag == "img" and self.should_capture():
            alt = clean(attrs_dict.get("alt", ""))
            src = attrs_dict.get("src", "")
            self.images.append({"alt": alt, "src": src})
            placeholder = f"[image reference: alt=\"{alt}\" src=\"{src}\"]" if self.include_images else f"[image placeholder: alt=\"{alt}\" src=\"{src}\"]"
            self.append_text_line(placeholder)
            self.append_text_line("")
            return

        if tag in HEADING_TAGS:
            self.start_text_block(tag, tag)
            return
        if tag in TEXT_BLOCK_TAGS:
            self.start_text_block(tag, tag)
            return
        if tag == "div":
            classes = set(attrs_dict.get("class", "").split())
            if classes.intersection(MEANINGFUL_DIV_CLASSES):
                self.start_text_block("div", "div")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
            return

        if tag == "a" and self.current_link_href is not None:
            href = self.current_link_href
            text = clean("".join(self.current_link_parts))
            if href:
                self.links.append({"href": href, "text": text})
                rendered = f"[{text}]({href})" if text else href
                if self.current_cell_parts is not None:
                    self.current_cell_parts.append(rendered)
                elif self.current_tag and self.should_capture():
                    self.current_parts.append(rendered)
            self.current_link_href = None
            self.current_link_parts = []

        if tag in {"td", "th"} and self.current_cell_tag == tag:
            cell_text = clean("".join(self.current_cell_parts or []))
            if self.current_row is not None:
                self.current_row.append(cell_text)
            self.current_cell_tag = None
            self.current_cell_parts = None
        elif tag == "tr" and self.current_row is not None:
            if any(cell for cell in self.current_row):
                self.current_table = self.current_table or []
                self.current_table.append(self.current_row)
            self.current_row = None
        elif tag == "table" and self.current_table is not None:
            self.flush_table()

        if tag in {"ul", "ol"} and self.list_stack:
            self.list_stack.pop()

        if self.current_tag_end == tag and self.current_tag_depth == self.depth:
            self.flush()

        if self.skip_depth == self.depth:
            self.skip_depth = 0
        self.depth = max(0, self.depth - 1)

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
            return
        if self.skip_depth or not self.should_capture():
            return
        if self.current_link_href is not None:
            self.current_link_parts.append(data)
            return
        if self.current_cell_parts is not None:
            self.current_cell_parts.append(data)
            return
        if self.current_tag:
            self.current_parts.append(data)

    def output_title(self) -> str:
        return clean(" ".join(self.title_parts)) or "(untitled)"


def parse_html_document(path: Path, anchor: str | None = None, include_images: bool = False) -> RepositoryHTMLParser:
    parser = RepositoryHTMLParser(anchor=anchor, include_images=include_images)
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    parser.flush()
    parser.flush_table()
    parser.body_lines = normalize_lines(parser.body_lines)
    return parser
