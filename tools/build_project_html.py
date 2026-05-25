#!/usr/bin/env python3
"""Build the Luo sisters static HTML pages.

Usage:
    python tools/build_project_html.py
    python tools/build_project_html.py --locale zh-CN

The builder keeps presentation, character asset structure, and localized copy
separate:
- characters/*.json describes page layout, colors, and asset slots.
- locales/*.json provides user-facing text.
- assets/styles/luo_sisters.css owns the visual system.
"""
from __future__ import annotations

import argparse
import json
import os
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "locales"
CHARACTERS_DIR = ROOT / "characters"
INDEX_PATH = ROOT / "index.html"
SHEETS_DIR = ROOT / "character_sheets"
CHARACTER_IDS = ("qingyou", "arisu")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def e(value: Any) -> str:
    return escape(str(value), quote=True)


def rel(path: str, from_file: Path) -> str:
    if not path:
        return ""
    if path.startswith(("#", "http://", "https://", "mailto:")):
        return path
    target = ROOT / path
    return os.path.relpath(target, from_file.parent).replace("\\", "/")


def label(locale: dict[str, Any], key: str, fallback: str | None = None) -> str:
    labels = locale.get("labels", {})
    return str(labels.get(key, fallback if fallback is not None else key))


def group_name(locale: dict[str, Any], group_id: str) -> str:
    return str(locale.get("asset_groups", {}).get(group_id, group_id))


def tag_row(items: list[str], blue: bool = False) -> str:
    cls = "tag blue" if blue else "tag"
    return "<div class=\"tag-row\">" + "".join(f"<span class=\"{cls}\">{e(item)}</span>" for item in items) + "</div>"


def list_items(items: list[str], class_name: str = "plain-list") -> str:
    return f"<ul class=\"{class_name}\">" + "".join(f"<li>{e(item)}</li>" for item in items) + "</ul>"


def page_head(title: str, stylesheet: str, locale: dict[str, Any]) -> str:
    lang = locale["meta"]["language"]
    direction = locale["meta"].get("dir", "ltr")
    return f"""<!DOCTYPE html>
<html lang="{e(lang)}" dir="{e(direction)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <link rel="stylesheet" href="{e(stylesheet)}">
</head>"""


def topbar(locale: dict[str, Any], page_path: Path, active: str = "") -> str:
    ui = locale["ui"]
    home_href = rel("index.html", page_path)
    qingyou_href = rel("character_sheets/qingyou.html", page_path)
    arisu_href = rel("character_sheets/arisu.html", page_path)
    workflow_href = rel("workflows/asset_generation_workflow.md", page_path)
    return f"""<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="{e(home_href)}">{e(ui["brand"])}</a>
    <nav class="nav-links" aria-label="{e(ui["characters"])}">
      <a href="{e(home_href)}"{" aria-current=\"page\"" if active == "home" else ""}>{e(ui["home"])}</a>
      <a href="{e(qingyou_href)}"{" aria-current=\"page\"" if active == "qingyou" else ""}>洛青悠</a>
      <a href="{e(arisu_href)}"{" aria-current=\"page\"" if active == "arisu" else ""}>洛有栖</a>
      <a href="{e(workflow_href)}">{e(ui["workflow"])}</a>
    </nav>
  </div>
</header>"""


def profile_list(profile: list[dict[str, str]]) -> str:
    rows = "".join(
        f"<div class=\"profile-row\"><b>{e(item['label'])}</b><span>{e(item['value'])}</span></div>"
        for item in profile
    )
    return f"<div class=\"profile-list\">{rows}</div>"


def palette_grid(config: dict[str, Any], locale: dict[str, Any]) -> str:
    swatches = []
    for swatch in config["palette"]:
        name = label(locale, swatch["name_key"])
        hex_value = swatch["hex"]
        swatches.append(
            f"""<div class="swatch">
  <div class="swatch-color" style="background:{e(hex_value)}"></div>
  <span>{e(name)}<br>{e(hex_value)}</span>
</div>"""
        )
    return "<div class=\"palette-grid\">" + "".join(swatches) + "</div>"


def asset_source(item: dict[str, str]) -> tuple[str, str]:
    transparent = item.get("transparent", "")
    crop = item.get("crop", "")
    if transparent and (ROOT / transparent).exists():
        return transparent, "ready"
    if crop and (ROOT / crop).exists():
        return crop, "reference"
    return "", "missing"


def asset_tile(item: dict[str, str], locale: dict[str, Any], page_path: Path) -> str:
    ui = locale["ui"]
    item_label = label(locale, item["label_key"], item["id"])
    image_path, state = asset_source(item)
    if state == "ready":
        state_text = ui["ready"]
        art = f"<img src=\"{e(rel(image_path, page_path))}\" alt=\"{e(item_label)}\">"
    elif state == "reference":
        state_text = ui["reference_crop"]
        art = f"<img src=\"{e(rel(image_path, page_path))}\" alt=\"{e(item_label)} {e(ui['reference_crop'])}\">"
    else:
        state_text = ui["planned"]
        target = item.get("transparent", "")
        art = f"<div class=\"asset-placeholder\"><span>{e(ui['planned'])}<br>{e(target)}</span></div>"

    return f"""<figure class="asset-tile">
  <div class="asset-art">{art}</div>
  <figcaption class="asset-caption"><span>{e(item_label)}</span><span class="asset-state">{e(state_text)}</span></figcaption>
</figure>"""


def group(config: dict[str, Any], group_id: str) -> dict[str, Any]:
    for asset_group in config["asset_groups"]:
        if asset_group["id"] == group_id:
            return asset_group
    return {"id": group_id, "items": []}


def asset_group_html(
    config: dict[str, Any],
    locale: dict[str, Any],
    page_path: Path,
    group_id: str,
    area_class: str = "",
    grid_class: str = "asset-grid",
    heading_level: int = 3,
) -> str:
    asset_group = group(config, group_id)
    items = "".join(asset_tile(item, locale, page_path) for item in asset_group["items"])
    heading = f"h{heading_level}"
    return f"""<section class="board-block {e(area_class)}">
  <{heading}>{e(group_name(locale, group_id))}</{heading}>
  <div class="{e(grid_class)}">{items}</div>
</section>"""


def source_reference(config: dict[str, Any], locale: dict[str, Any], page_path: Path) -> str:
    ui = locale["ui"]
    src = rel(config["source_sheet"], page_path)
    return f"""<section class="board-block area-source">
  <h2>{e(ui["source_reference"])}</h2>
  <figure class="source-reference">
    <img src="{e(src)}" alt="{e(ui["source_reference"])}">
    <figcaption>{e(ui["reference_note"])}</figcaption>
  </figure>
</section>"""


def character_card(
    character_id: str,
    config: dict[str, Any],
    copy: dict[str, Any],
    locale: dict[str, Any],
    page_path: Path,
) -> str:
    ui = locale["ui"]
    href = rel(f"character_sheets/{character_id}.html", page_path)
    source = rel(config["source_sheet"], page_path)
    blue = character_id == "arisu"
    return f"""<a class="character-link" href="{e(href)}">
  <div class="character-thumb"><img src="{e(source)}" alt="{e(copy["name"])}"></div>
  <div class="character-summary">
    <p class="eyebrow">{e(copy["role"])}</p>
    <h3>{e(copy["name"])}<span class="roman">{e(copy["roman"])}</span></h3>
    <p>{e(copy["short"])}</p>
    {tag_row(copy["visual"], blue)}
    <span class="action-link">{e(ui["open_sheet"])}</span>
  </div>
</a>"""


def render_home(locale: dict[str, Any], configs: dict[str, dict[str, Any]]) -> str:
    page_path = INDEX_PATH
    ui = locale["ui"]
    home = locale["home"]
    characters = locale["characters"]
    stylesheet = rel("assets/styles/luo_sisters.css", page_path)
    qingyou = configs["qingyou"]
    arisu = configs["arisu"]

    theme_cards = "".join(
        f"<article class=\"panel\"><h3>{e(layer['name'])}</h3><p>{e(layer['text'])}</p></article>"
        for layer in home["theme_layers"]
    )
    pipeline = list_items(home["pipeline_steps"], "ordered-list")
    character_cards = "".join(
        character_card(character_id, configs[character_id], characters[character_id], locale, page_path)
        for character_id in CHARACTER_IDS
    )
    acts = "".join(
        f"<li class=\"story-item\"><strong>{e(act['title'])}</strong><span>{e(act['text'])}</span></li>"
        for act in home["acts"]
    )

    return f"""{page_head(home["title"], stylesheet, locale)}
<body>
{topbar(locale, page_path, "home")}
<main class="page">
  <section class="hero" id="overview">
    <div>
      <p class="eyebrow">{e(home["eyebrow"])} · {e(locale["meta"]["version"])}</p>
      <h1>{e(home["title"])}</h1>
      <p class="lead">{e(home["subtitle"])}</p>
      <div class="hero-actions">
        <a class="action-link" href="{e(rel("character_sheets/qingyou.html", page_path))}">洛青悠</a>
        <a class="action-link" href="{e(rel("character_sheets/arisu.html", page_path))}">洛有栖</a>
      </div>
    </div>
    <div class="source-duo" aria-label="{e(ui["source_reference"])}">
      <figure class="source-card">
        <img src="{e(rel(qingyou["source_sheet"], page_path))}" alt="洛青悠">
        <figcaption><b>洛青悠</b></figcaption>
      </figure>
      <figure class="source-card">
        <img src="{e(rel(arisu["source_sheet"], page_path))}" alt="洛有栖">
        <figcaption><b>洛有栖</b></figcaption>
      </figure>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <div><p class="eyebrow">Stage 01</p><h2>{e(home["summary_title"])}</h2></div>
      <p>{e(home["summary"])}</p>
    </div>
    <div class="grid">{theme_cards}</div>
  </section>

  <section class="section" id="characters">
    <div class="section-head">
      <div><p class="eyebrow">Character Sheets</p><h2>{e(ui["characters"])}</h2></div>
      <p>{e(ui["reference_note"])}</p>
    </div>
    <div class="grid two">{character_cards}</div>
  </section>

  <section class="section" id="workflow">
    <div class="section-head">
      <div><p class="eyebrow">Pipeline</p><h2>{e(home["pipeline_title"])}</h2></div>
    </div>
    <article class="panel">{pipeline}</article>
  </section>

  <section class="section" id="story">
    <div class="section-head">
      <div><p class="eyebrow">Story</p><h2>{e(home["story_title"])}</h2></div>
      <p><strong>{e(home["story_surface"])}</strong><br>{e(home["story_summary"])}</p>
    </div>
    <ol class="story-list">{acts}</ol>
  </section>

  <p class="footer">HTML / CSS / asset workflow generated from structured JSON. Final public pages are Chinese-first with locale separation for future languages.</p>
</main>
</body>
</html>
"""


def render_journal_board(config: dict[str, Any], copy: dict[str, Any], locale: dict[str, Any], page_path: Path) -> str:
    ui = locale["ui"]
    return f"""<section class="board qingyou journal-layout">
  {source_reference(config, locale, page_path)}
  <section class="board-block area-profile">
    <h2>{e(ui["profile"])}</h2>
    {profile_list(copy["profile"])}
  </section>
  {asset_group_html(config, locale, page_path, "standing", "area-asset", "asset-grid", 2)}
  {asset_group_html(config, locale, page_path, "expressions", "area-expressions", "asset-strip", 2)}
  {asset_group_html(config, locale, page_path, "turnaround", "area-turnaround", "turnaround-grid", 2)}
  <section class="board-block area-palette">
    <h2>{e(ui["palette"])}</h2>
    {palette_grid(config, locale)}
  </section>
  {asset_group_html(config, locale, page_path, "details", "area-details", "asset-grid", 2)}
  <section class="board-block area-notes">
    <h2>{e(ui["quote"])}</h2>
    <blockquote class="quote-box">{e(copy["quote"])}<span>{e(copy["support_quote"])}</span></blockquote>
  </section>
  <section class="board-block area-tags">
    <h2>{e(ui["tags"])}</h2>
    {tag_row(copy["tags"])}
  </section>
</section>"""


def render_alice_board(config: dict[str, Any], copy: dict[str, Any], locale: dict[str, Any], page_path: Path) -> str:
    ui = locale["ui"]
    return f"""<section class="board arisu alice-layout">
  <section class="board-block area-profile">
    <h2>{e(ui["profile"])}</h2>
    {profile_list(copy["profile"])}
  </section>
  {asset_group_html(config, locale, page_path, "turnaround", "area-turnaround", "turnaround-grid", 2)}
  <section class="board-block area-story">
    <h2>{e(ui["conflict"])}</h2>
    <p>{e(copy["conflict"])}</p>
  </section>
  <section class="board-block area-visual">
    <h2>{e(ui["visual_points"])}</h2>
    {tag_row(copy["visual"], True)}
  </section>
  <section class="board-block area-quote">
    <h2>{e(ui["quote"])}</h2>
    <blockquote class="quote-box">{e(copy["quote"])}<span>{e(copy["support_quote"])}</span></blockquote>
  </section>
  {asset_group_html(config, locale, page_path, "props", "area-props", "asset-strip", 2)}
  {asset_group_html(config, locale, page_path, "standing", "area-asset", "asset-grid", 2)}
  {asset_group_html(config, locale, page_path, "expressions", "area-expressions", "asset-strip", 2)}
  <section class="board-block area-palette">
    <h2>{e(ui["palette"])}</h2>
    {palette_grid(config, locale)}
  </section>
  <section class="board-block area-tags">
    <h2>{e(ui["tags"])}</h2>
    {tag_row(copy["tags"], True)}
  </section>
  {asset_group_html(config, locale, page_path, "details", "area-details", "asset-grid", 2)}
</section>"""


def render_character_page(character_id: str, locale: dict[str, Any], config: dict[str, Any]) -> str:
    page_path = SHEETS_DIR / f"{character_id}.html"
    ui = locale["ui"]
    copy = locale["characters"][character_id]
    stylesheet = rel("assets/styles/luo_sisters.css", page_path)
    body_class = f"theme-{character_id}"
    board = (
        render_journal_board(config, copy, locale, page_path)
        if character_id == "qingyou"
        else render_alice_board(config, copy, locale, page_path)
    )
    source_link = rel(config["source_sheet"], page_path)
    clothing = asset_group_html(config, locale, page_path, "clothing", "", "asset-grid", 2)
    accessories = asset_group_html(config, locale, page_path, "accessories", "", "asset-grid", 2)
    props = asset_group_html(config, locale, page_path, "props", "", "asset-grid", 2)
    cg = asset_group_html(config, locale, page_path, "cg", "", "asset-grid", 2)

    return f"""{page_head(f"{copy["name"]} | {copy["board_title"]}", stylesheet, locale)}
<body class="{e(body_class)}">
{topbar(locale, page_path, character_id)}
<main class="page sheet-shell">
  <section class="sheet-hero">
    <div class="sheet-title">
      <p class="eyebrow">{e(copy["board_title"])}</p>
      <h1>{e(copy["name"])}</h1>
      <p class="lead">{e(copy["role"])} · {e(copy["short"])}</p>
    </div>
    <div class="sheet-actions">
      <a class="action-link" href="{e(rel("index.html", page_path))}">{e(ui["back_home"])}</a>
      <a class="action-link" href="{e(source_link)}">{e(ui["open_source"])}</a>
    </div>
  </section>

  {board}

  <section class="section">
    <div class="section-head">
      <div><p class="eyebrow">Asset Expansion</p><h2>{e(ui["asset_slots"])}</h2></div>
      <p>{e(ui["reference_note"])}</p>
    </div>
    <div class="grid two">
      <article class="asset-section">{clothing}</article>
      <article class="asset-section">{accessories}</article>
      <article class="asset-section">{props}</article>
      <article class="asset-section">{cg}</article>
    </div>
  </section>

  <section class="section">
    <div class="grid two">
      <article class="panel">
        <h2>{e(ui["daily"])}</h2>
        {list_items(copy["daily"])}
      </article>
      <article class="panel">
        <h2>{e(ui["growth"])}</h2>
        <p>{e(copy["growth"])}</p>
      </article>
    </div>
  </section>

  <p class="footer">{e(config["asset_root"])} · {e(config["crop_manifest"])}</p>
</main>
</body>
</html>
"""


def build(locale_code: str) -> list[Path]:
    locale_path = LOCALES_DIR / f"{locale_code}.json"
    locale = read_json(locale_path)
    configs = {character_id: read_json(CHARACTERS_DIR / f"{character_id}.json") for character_id in CHARACTER_IDS}
    SHEETS_DIR.mkdir(exist_ok=True)

    outputs = [
        (INDEX_PATH, render_home(locale, configs)),
        (SHEETS_DIR / "qingyou.html", render_character_page("qingyou", locale, configs["qingyou"])),
        (SHEETS_DIR / "arisu.html", render_character_page("arisu", locale, configs["arisu"])),
    ]
    for path, content in outputs:
        path.write_text(content, encoding="utf-8")
    return [path for path, _ in outputs]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Luo sisters static HTML pages.")
    parser.add_argument("--locale", default="zh-CN", help="Locale JSON name in locales/, default zh-CN.")
    args = parser.parse_args()
    outputs = build(args.locale)
    for path in outputs:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
