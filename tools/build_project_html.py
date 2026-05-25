#!/usr/bin/env python3
"""Build the Luo sisters static HTML pages.

Usage:
    python tools/build_project_html.py
    python tools/build_project_html.py --locale zh-CN
    python tools/build_project_html.py --locale en

The default build writes the Chinese site at the repository root and the
English mirror under en/. Generated HTML is not the long-term editing source.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "locales"
CHARACTERS_DIR = ROOT / "characters"
PROJECT_DATA_DIR = ROOT / "project_data"
CHARACTER_IDS = ("qingyou", "arisu")
DEFAULT_LOCALES = ("zh-CN", "en")
ASSET_GROUP_ORDER = ("standing", "expressions", "poses", "turnaround", "clothing", "accessories", "props", "details", "cg")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def e(value: Any) -> str:
    return escape(str(value), quote=True)


def rel(path: str, from_file: Path) -> str:
    if not path:
        return ""
    if path.startswith(("#", "http://", "https://", "mailto:")):
        return path
    target = ROOT / path
    return os.path.relpath(target, from_file.parent).replace("\\", "/")


def site_dir(locale: dict[str, Any]) -> str:
    return str(locale.get("meta", {}).get("site_dir", "")).strip("/")


def localized_path(path: str, locale: dict[str, Any]) -> str:
    directory = site_dir(locale)
    return f"{directory}/{path}" if directory else path


def output_path(path: str, locale: dict[str, Any]) -> Path:
    return ROOT / localized_path(path, locale)


def page_rel(path: str, page_path: Path, locale: dict[str, Any]) -> str:
    return rel(localized_path(path, locale), page_path)


def is_generated_page(path: str) -> bool:
    return (
        path == "index.html"
        or path.startswith("character_sheets/")
        or path.startswith("knowledge/")
    )


def doc_href(path: str, page_path: Path, locale: dict[str, Any], root_link: bool = False) -> str:
    if path.startswith(("#", "http://", "https://", "mailto:")):
        return path
    if root_link or not is_generated_page(path):
        return rel(path, page_path)
    return page_rel(path, page_path, locale)


def canonical_generated_path(page_path: Path, locale: dict[str, Any]) -> str:
    root_relative = os.path.relpath(page_path, ROOT).replace("\\", "/")
    directory = site_dir(locale)
    if directory and root_relative.startswith(f"{directory}/"):
        return root_relative[len(directory) + 1 :]
    return root_relative


def site_dir_for_locale(locale_code: str) -> str:
    if locale_code == "zh-CN":
        return ""
    if locale_code == "en":
        return "en"
    return locale_code


def language_href(page_path: Path, locale: dict[str, Any]) -> str:
    alternate = str(locale.get("meta", {}).get("alternate_locale", "en"))
    current = canonical_generated_path(page_path, locale)
    alternate_dir = site_dir_for_locale(alternate)
    target = f"{alternate_dir}/{current}" if alternate_dir else current
    return rel(target, page_path)


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
    characters = locale.get("characters", {})
    qingyou_name = characters.get("qingyou", {}).get("name", "Luo Qingyou")
    arisu_name = characters.get("arisu", {}).get("name", "Luo Arisu")
    home_href = page_rel("index.html", page_path, locale)
    qingyou_href = page_rel("character_sheets/qingyou.html", page_path, locale)
    arisu_href = page_rel("character_sheets/arisu.html", page_path, locale)
    knowledge_href = page_rel("knowledge/index.html", page_path, locale)
    assets_href = page_rel("knowledge/assets.html", page_path, locale)
    content_map_href = rel("docs/content_map.md", page_path)
    workflow_href = rel("workflows/asset_generation_workflow.md", page_path)
    home_current = ' aria-current="page"' if active == "home" else ""
    qingyou_current = ' aria-current="page"' if active == "qingyou" else ""
    arisu_current = ' aria-current="page"' if active == "arisu" else ""
    knowledge_current = ' aria-current="page"' if active == "knowledge" else ""
    assets_current = ' aria-current="page"' if active == "assets" else ""
    return f"""<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="{e(home_href)}">{e(ui["brand"])}</a>
    <nav class="nav-links" aria-label="{e(ui["characters"])}">
      <a href="{e(home_href)}"{home_current}>{e(ui["home"])}</a>
      <a href="{e(qingyou_href)}"{qingyou_current}>{e(qingyou_name)}</a>
      <a href="{e(arisu_href)}"{arisu_current}>{e(arisu_name)}</a>
      <a href="{e(knowledge_href)}"{knowledge_current}>{e(ui["knowledge"])}</a>
      <a href="{e(assets_href)}"{assets_current}>{e(ui["assets"])}</a>
      <a href="{e(content_map_href)}">{e(ui["content_map"])}</a>
      <a href="{e(workflow_href)}">{e(ui["workflow"])}</a>
      <a href="{e(language_href(page_path, locale))}">{e(ui["language_switch"])}</a>
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
    href = page_rel(f"character_sheets/{character_id}.html", page_path, locale)
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


def content_map_html(locale: dict[str, Any], page_path: Path) -> str:
    home = locale["home"]
    groups = []
    for group_data in home["content_map_groups"]:
        links = "".join(
            f"""<li>
  <a href="{e(doc_href(item["href"], page_path, locale, bool(item.get("root_link"))))}">{e(item["label"])}</a>
  <span>{e(item["note"])}</span>
</li>"""
            for item in group_data["links"]
        )
        groups.append(
            f"""<article class="link-group">
  <h3>{e(group_data["title"])}</h3>
  <p>{e(group_data["text"])}</p>
  <ul class="link-list">{links}</ul>
</article>"""
        )
    return "<div class=\"link-tree\">" + "".join(groups) + "</div>"


def render_home(locale: dict[str, Any], configs: dict[str, dict[str, Any]]) -> tuple[Path, str]:
    page_path = output_path("index.html", locale)
    ui = locale["ui"]
    home = locale["home"]
    characters = locale["characters"]
    stylesheet = rel("assets/styles/luo_sisters.css", page_path)
    qingyou = configs["qingyou"]
    arisu = configs["arisu"]
    qingyou_copy = characters["qingyou"]
    arisu_copy = characters["arisu"]

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
    content_map = content_map_html(locale, page_path)

    content = f"""{page_head(home["title"], stylesheet, locale)}
<body>
{topbar(locale, page_path, "home")}
<main class="page">
  <section class="hero" id="overview">
    <div>
      <p class="eyebrow">{e(home["eyebrow"])} | {e(locale["meta"]["version"])}</p>
      <h1>{e(home["title"])}</h1>
      <p class="lead">{e(home["subtitle"])}</p>
      <div class="hero-actions">
        <a class="action-link" href="{e(page_rel("character_sheets/qingyou.html", page_path, locale))}">{e(qingyou_copy["name"])}</a>
        <a class="action-link" href="{e(page_rel("character_sheets/arisu.html", page_path, locale))}">{e(arisu_copy["name"])}</a>
        <a class="action-link" href="{e(page_rel("knowledge/index.html", page_path, locale))}">{e(ui["knowledge"])}</a>
        <a class="action-link" href="{e(page_rel("knowledge/assets.html", page_path, locale))}">{e(ui["assets"])}</a>
      </div>
    </div>
    <div class="source-duo" aria-label="{e(ui["source_reference"])}">
      <figure class="source-card">
        <img src="{e(rel(qingyou["source_sheet"], page_path))}" alt="{e(qingyou_copy["name"])}">
        <figcaption><b>{e(qingyou_copy["name"])}</b></figcaption>
      </figure>
      <figure class="source-card">
        <img src="{e(rel(arisu["source_sheet"], page_path))}" alt="{e(arisu_copy["name"])}">
        <figcaption><b>{e(arisu_copy["name"])}</b></figcaption>
      </figure>
    </div>
  </section>

  <section class="section">
    <div class="section-head">
      <div><p class="eyebrow">{e(home["summary_eyebrow"])}</p><h2>{e(home["summary_title"])}</h2></div>
      <p>{e(home["summary"])}</p>
    </div>
    <div class="grid">{theme_cards}</div>
  </section>

  <section class="section" id="characters">
    <div class="section-head">
      <div><p class="eyebrow">{e(ui["characters"])}</p><h2>{e(ui["characters"])}</h2></div>
      <p>{e(ui["reference_note"])}</p>
    </div>
    <div class="grid two">{character_cards}</div>
  </section>

  <section class="section" id="workflow">
    <div class="section-head">
      <div><p class="eyebrow">{e(ui["workflow"])}</p><h2>{e(home["pipeline_title"])}</h2></div>
    </div>
    <article class="panel">{pipeline}</article>
  </section>

  <section class="section" id="content-map">
    <div class="section-head">
      <div><p class="eyebrow">{e(ui["content_map"])}</p><h2>{e(home["content_map_title"])}</h2></div>
      <p>{e(home["content_map_summary"])}</p>
    </div>
    {content_map}
  </section>

  <section class="section" id="story">
    <div class="section-head">
      <div><p class="eyebrow">{e(ui["story"])}</p><h2>{e(home["story_title"])}</h2></div>
      <p><strong>{e(home["story_surface"])}</strong><br>{e(home["story_summary"])}</p>
    </div>
    <ol class="story-list">{acts}</ol>
  </section>

  <p class="footer">{e(ui["site_footer"])}</p>
</main>
</body>
</html>
"""
    return page_path, content


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
  {asset_group_html(config, locale, page_path, "poses", "area-poses", "asset-strip", 2)}
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
  {asset_group_html(config, locale, page_path, "poses", "area-poses", "asset-strip", 2)}
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


def render_character_page(character_id: str, locale: dict[str, Any], config: dict[str, Any]) -> tuple[Path, str]:
    page_path = output_path(f"character_sheets/{character_id}.html", locale)
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
    config_link = rel(f"characters/{character_id}.json", page_path)
    crop_manifest_link = rel(config["crop_manifest"], page_path)
    prompt_link = rel(f"assets/characters/{character_id}/prompts/asset_prompts.md", page_path)
    workflow_link = rel("workflows/asset_generation_workflow.md", page_path)
    registry_link = rel("logs/asset_registry.csv", page_path)
    task_packet_link = rel(f"harness/tasks/{character_id}-asset-batch.json", page_path)
    clothing = asset_group_html(config, locale, page_path, "clothing", "", "asset-grid", 2)
    accessories = asset_group_html(config, locale, page_path, "accessories", "", "asset-grid", 2)
    props = asset_group_html(config, locale, page_path, "props", "", "asset-grid", 2)
    poses = asset_group_html(config, locale, page_path, "poses", "", "asset-grid", 2)
    cg = asset_group_html(config, locale, page_path, "cg", "", "asset-grid", 2)
    title = f"{copy['name']} | {copy['board_title']}"

    content = f"""{page_head(title, stylesheet, locale)}
<body class="{e(body_class)}">
{topbar(locale, page_path, character_id)}
<main class="page sheet-shell">
  <section class="sheet-hero" id="overview">
    <div class="sheet-title">
      <p class="eyebrow">{e(copy["board_title"])}</p>
      <h1>{e(copy["name"])}</h1>
      <p class="lead">{e(copy["role"])} | {e(copy["short"])}</p>
    </div>
    <div class="sheet-actions">
      <a class="action-link" href="{e(page_rel("index.html", page_path, locale))}">{e(ui["back_home"])}</a>
      <a class="action-link" href="{e(source_link)}">{e(ui["open_source"])}</a>
      <a class="action-link" href="{e(page_rel("knowledge/assets.html", page_path, locale))}">{e(ui["assets"])}</a>
    </div>
    <div class="source-links">
      <a href="{e(config_link)}">{e(character_id)}.json</a>
      <a href="{e(task_packet_link)}">{e(character_id)}-asset-batch.json</a>
      <a href="{e(crop_manifest_link)}">crop_manifest</a>
      <a href="{e(prompt_link)}">asset_prompts.md</a>
      <a href="{e(registry_link)}">asset_registry.csv</a>
      <a href="{e(workflow_link)}">asset_generation_workflow.md</a>
    </div>
  </section>

  {board}

  <section class="section" id="assets">
    <div class="section-head">
      <div><p class="eyebrow">{e(ui["asset_expansion"])}</p><h2>{e(ui["asset_slots"])}</h2></div>
      <p>{e(ui["reference_note"])}</p>
    </div>
    <div class="grid two">
      <article class="asset-section">{clothing}</article>
      <article class="asset-section">{accessories}</article>
      <article class="asset-section">{props}</article>
      <article class="asset-section">{poses}</article>
      <article class="asset-section">{cg}</article>
    </div>
  </section>

  <section class="section" id="workflow">
    <div class="section-head">
      <div><p class="eyebrow">{e(ui["workflow"])}</p><h2>{e(ui["workflow"])}</h2></div>
      <p>{e(config["asset_root"])}</p>
    </div>
    <div class="source-links">
      <a href="{e(page_rel("knowledge/navigation.html", page_path, locale))}">knowledge/navigation.html</a>
      <a href="{e(page_rel("knowledge/assets.html", page_path, locale))}">knowledge/assets.html</a>
      <a href="{e(config_link)}">{e(character_id)}.json</a>
      <a href="{e(task_packet_link)}">{e(character_id)}-asset-batch.json</a>
      <a href="{e(crop_manifest_link)}">crop_manifest</a>
      <a href="{e(prompt_link)}">asset_prompts.md</a>
      <a href="{e(registry_link)}">asset_registry.csv</a>
      <a href="{e(workflow_link)}">asset_generation_workflow.md</a>
    </div>
  </section>

  <section class="section" id="notes">
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

  <p class="footer">{e(config["asset_root"])} | {e(config["crop_manifest"])}</p>
</main>
</body>
</html>
"""
    return page_path, content


def asset_registry_map() -> dict[tuple[str, str, str], dict[str, str]]:
    path = ROOT / "logs" / "asset_registry.csv"
    rows = read_csv_rows(path)
    return {(row["character"], row["asset_type"], row["asset_name"]): row for row in rows}


def registry_status(row: dict[str, str] | None) -> str:
    return row["status"] if row else "untracked"


def path_cell(path: str, page_path: Path, label_text: str | None = None) -> str:
    if not path:
        return "<span class=\"asset-state\">planned</span>"
    href = rel(path, page_path)
    text = label_text or path
    return f"<a href=\"{e(href)}\">{e(text)}</a>"


def asset_aliases(item: dict[str, Any]) -> str:
    aliases = item.get("aliases", [])
    if not aliases:
        return ""
    return " / ".join(str(alias) for alias in aliases)


def asset_index_table(
    character_id: str,
    config: dict[str, Any],
    locale: dict[str, Any],
    page_path: Path,
    registry: dict[tuple[str, str, str], dict[str, str]],
) -> str:
    sections: list[str] = []
    for group_id in ASSET_GROUP_ORDER:
        asset_group = group(config, group_id)
        if not asset_group["items"]:
            continue
        rows: list[str] = []
        for item in asset_group["items"]:
            row = registry.get((character_id, group_id, item["id"]))
            label_text = label(locale, item["label_key"], item["id"])
            aliases = asset_aliases(item)
            label_block = f"<b>{e(label_text)}</b>"
            if aliases:
                label_block += f"<span class=\"asset-state\">{e(aliases)}</span>"
            rows.append(
                "<tr>"
                f"<td>{label_block}</td>"
                f"<td>{path_cell(item.get('crop', ''), page_path, item.get('crop', '') or None)}</td>"
                f"<td>{path_cell(item.get('prompt', ''), page_path, item.get('prompt', '') or None)}</td>"
                f"<td>{path_cell(item.get('transparent', ''), page_path, item.get('transparent', '') or None)}</td>"
                f"<td><span class=\"status-pill\">{e(registry_status(row))}</span></td>"
                f"<td>{path_cell('logs/asset_registry.csv', page_path, row['asset_name'] if row else 'asset_registry.csv')}</td>"
                "</tr>"
            )
        sections.append(
            f"""<section class="knowledge-section" id="{e(group_id)}">
  <div class="section-head">
    <div><p class="eyebrow">{e(config['id'])}</p><h2>{e(group_name(locale, group_id))}</h2></div>
    <p>{e(config['asset_root'])}</p>
  </div>
  <div class="knowledge-table-wrap">
    <table class="knowledge-table">
      <thead><tr><th>{e(locale['ui']['assets'])}</th><th>{e(locale['ui'].get('asset_crop_header', 'crop'))}</th><th>{e(locale['ui'].get('asset_prompt_header', 'prompt'))}</th><th>{e(locale['ui'].get('asset_output_header', 'output'))}</th><th>{e(locale['ui'].get('asset_status_header', 'status'))}</th><th>{e(locale['ui'].get('asset_registry_header', 'registry'))}</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
</section>"""
        )
    return "".join(sections)


def render_assets_index(locale: dict[str, Any], configs: dict[str, dict[str, Any]]) -> tuple[Path, str]:
    page_path = output_path("knowledge/assets.html", locale)
    stylesheet = rel("assets/styles/luo_sisters.css", page_path)
    registry = asset_registry_map()
    ui = locale["ui"]
    characters = locale["characters"]
    cards: list[str] = []
    sections: list[str] = []
    for character_id in CHARACTER_IDS:
        config = configs[character_id]
        copy = characters[character_id]
        cards.append(
            f"""<article class="knowledge-card">
  <p class="eyebrow">{e(copy['roman'])}</p>
  <h3><a href="{e(page_rel(f'character_sheets/{character_id}.html', page_path, locale))}">{e(copy['name'])}</a></h3>
  <p>{e(copy['short'])}</p>
  <div class="source-links">
    <a href="{e(rel(f'characters/{character_id}.json', page_path))}">{e(character_id)}.json</a>
    <a href="{e(rel(f'harness/tasks/{character_id}-asset-batch.json', page_path))}">{e(character_id)}-asset-batch.json</a>
    <a href="{e(rel(config['source_sheet'], page_path))}">source_sheet</a>
    <a href="{e(rel(config['crop_manifest'], page_path))}">crop_manifest</a>
    <a href="{e(rel(f'assets/characters/{character_id}/prompts/asset_prompts.md', page_path))}">asset_prompts.md</a>
  </div>
</article>"""
        )
        sections.append(asset_index_table(character_id, config, locale, page_path, registry))

    content = f"""{page_head(f"{ui['assets']} | {ui['knowledge']}", stylesheet, locale)}
<body class="theme-knowledge">
{topbar(locale, page_path, "assets")}
<main class="page knowledge-shell">
  <section class="knowledge-hero">
    <div>
      <p class="eyebrow">{e(ui.get("asset_index_eyebrow", "Asset Index"))}</p>
      <h1>{e(ui["assets"])}</h1>
      <p class="lead">{e(ui.get("asset_index_summary", "Use one page to find character source sheets, crop handles, prompt notes, planned transparent outputs, and registry status."))}</p>
      <div class="source-links">
        <a href="{e(rel('logs/asset_registry.csv', page_path))}">asset_registry.csv</a>
        <a href="{e(rel('harness/tasks/qingyou-asset-batch.json', page_path))}">qingyou-asset-batch.json</a>
        <a href="{e(rel('harness/tasks/arisu-asset-batch.json', page_path))}">arisu-asset-batch.json</a>
        <a href="{e(rel('harness/tasks/asset-registry-sync.json', page_path))}">asset-registry-sync.json</a>
      </div>
    </div>
    <ol class="hierarchy-chain"><li>AGENTS.md</li><li>knowledge/navigation.html</li><li>knowledge/assets.html</li><li>character_sheets/*.html</li></ol>
  </section>

  <section class="knowledge-section">
    <div class="section-head">
      <div><p class="eyebrow">{e(ui["assets"])}</p><h2>{e(ui["asset_slots"])}</h2></div>
      <p>{e(ui.get("asset_index_locator", "Every asset path stays inside its character root and links to prompts, crops, planned outputs, and the shared CSV registry."))}</p>
    </div>
    <div class="knowledge-card-grid">{''.join(cards)}</div>
  </section>

  {''.join(sections)}
</main>
</body>
</html>
"""
    return page_path, content


def paragraphs(value: str | list[str]) -> str:
    values = value if isinstance(value, list) else [value]
    return "".join(f"<p>{e(item)}</p>" for item in values)


def render_cards(section: dict[str, Any]) -> str:
    cards = []
    for item in section.get("items", []):
        points = item.get("points", [])
        point_list = list_items(points) if points else ""
        cards.append(
            f"""<article class="knowledge-card {e(item.get("tone", ""))}">
  <h3>{e(item["title"])}</h3>
  {paragraphs(item.get("text", ""))}
  {point_list}
</article>"""
        )
    return f"<div class=\"knowledge-card-grid\">{''.join(cards)}</div>"


def render_detail_groups(section: dict[str, Any]) -> str:
    groups = []
    for group_data in section.get("groups", []):
        details = []
        for item in group_data.get("items", []):
            details.append(
                f"""<details{" open" if item.get("open") else ""}>
  <summary>{e(item["title"])}</summary>
  <div class="detail-body">{paragraphs(item.get("text", ""))}</div>
</details>"""
            )
        groups.append(
            f"""<article class="detail-set {e(group_data.get("tone", ""))}">
  <h3>{e(group_data["title"])}</h3>
  {paragraphs(group_data.get("intro", ""))}
  {''.join(details)}
</article>"""
        )
    return f"<div class=\"knowledge-detail-grid\">{''.join(groups)}</div>"


def render_table(section: dict[str, Any]) -> str:
    headers = "".join(f"<th>{e(header)}</th>" for header in section.get("headers", []))
    rows = []
    for row in section.get("rows", []):
        rows.append("<tr>" + "".join(f"<td>{e(cell)}</td>" for cell in row) + "</tr>")
    return f"""<div class="knowledge-table-wrap">
  <table class="knowledge-table">
    <thead><tr>{headers}</tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</div>"""


def render_checklist(section: dict[str, Any]) -> str:
    return list_items(section.get("items", []), "checklist")


def render_prompt_grid(section: dict[str, Any]) -> str:
    prompts = []
    for item in section.get("items", []):
        source = item.get("source_id", "")
        source_tag = f"<span>{e(source)}</span>" if source else ""
        prompts.append(
            f"""<article class="prompt-card">
  <div class="prompt-head"><b>{e(item["title"])}</b>{source_tag}</div>
  <pre><code>{e(item.get("code", ""))}</code></pre>
</article>"""
        )
    return f"<div class=\"prompt-grid\">{''.join(prompts)}</div>"


def render_link_list(section: dict[str, Any], page_path: Path, locale: dict[str, Any]) -> str:
    items = "".join(
        f"""<li>
  <a href="{e(doc_href(item["href"], page_path, locale, bool(item.get("root_link"))))}">{e(item["label"])}</a>
  <span>{e(item.get("note", ""))}</span>
</li>"""
        for item in section.get("items", [])
    )
    return f"<ul class=\"link-list knowledge-links\">{items}</ul>"


def render_knowledge_section(section: dict[str, Any], page_path: Path, locale: dict[str, Any]) -> str:
    section_type = section.get("type", "cards")
    if section_type == "details":
        body = render_detail_groups(section)
    elif section_type == "table":
        body = render_table(section)
    elif section_type == "checklist":
        body = render_checklist(section)
    elif section_type == "prompts":
        body = render_prompt_grid(section)
    elif section_type == "links":
        body = render_link_list(section, page_path, locale)
    else:
        body = render_cards(section)

    return f"""<section class="knowledge-section" id="{e(section.get("id", ""))}">
  <div class="section-head">
    <div><p class="eyebrow">{e(section.get("eyebrow", ""))}</p><h2>{e(section["title"])}</h2></div>
    <p>{e(section.get("summary", ""))}</p>
  </div>
  {body}
</section>"""


def render_knowledge_index(locale: dict[str, Any], knowledge: dict[str, Any]) -> tuple[Path, str]:
    page_path = output_path("knowledge/index.html", locale)
    ui = locale["ui"]
    stylesheet = rel("assets/styles/luo_sisters.css", page_path)
    cards = []
    cards.append(
        f"""<article class="knowledge-card">
  <p class="eyebrow">Knowledge 01</p>
  <h3><a href="{e(page_rel('knowledge/assets.html', page_path, locale))}">{e(ui['assets'])}</a></h3>
  <p>{e(ui.get('asset_index_card_summary', 'Character roots, source sheets, crop handles, prompt notes, planned transparent outputs, and registry status.'))}</p>
  <span class="status-pill">active</span>
</article>"""
    )
    for page in knowledge["pages"]:
        href = page_rel(page["href"], page_path, locale)
        cards.append(
            f"""<article class="knowledge-card">
  <p class="eyebrow">{e(page["eyebrow"])}</p>
  <h3><a href="{e(href)}">{e(page["title"])}</a></h3>
  <p>{e(page["summary"])}</p>
</article>"""
        )
    chain = "".join(f"<li>{e(item)}</li>" for item in knowledge.get("hierarchy", []))
    intro_cards = render_cards({"items": knowledge.get("intro_cards", [])})
    content = f"""{page_head(knowledge["title"], stylesheet, locale)}
<body class="theme-knowledge">
{topbar(locale, page_path, "knowledge")}
<main class="page knowledge-shell">
  <section class="knowledge-hero">
    <div>
      <p class="eyebrow">{e(knowledge["eyebrow"])}</p>
      <h1>{e(knowledge["title"])}</h1>
      <p class="lead">{e(knowledge["summary"])}</p>
    </div>
    <ol class="hierarchy-chain">{chain}</ol>
  </section>

  <section class="knowledge-section">
    <div class="section-head">
      <div><p class="eyebrow">{e(ui["knowledge_pages_eyebrow"])}</p><h2>{e(ui["knowledge_pages_title"])}</h2></div>
      <p>{e(ui["knowledge_pages_summary"])}</p>
    </div>
    <div class="knowledge-card-grid">{''.join(cards)}</div>
  </section>

  <section class="knowledge-section">
    <div class="section-head">
      <div><p class="eyebrow">{e(ui["structure_rule_eyebrow"])}</p><h2>{e(ui["structure_rule_title"])}</h2></div>
    </div>
    {intro_cards}
  </section>
</main>
</body>
</html>
"""
    return page_path, content


def render_knowledge_page(locale: dict[str, Any], knowledge: dict[str, Any], page: dict[str, Any]) -> tuple[Path, str]:
    page_path = output_path(page["href"], locale)
    ui = locale["ui"]
    stylesheet = rel("assets/styles/luo_sisters.css", page_path)
    sections = "".join(render_knowledge_section(section, page_path, locale) for section in page.get("sections", []))
    title = f"{page['title']} | {knowledge['title']}"
    content = f"""{page_head(title, stylesheet, locale)}
<body class="theme-knowledge">
{topbar(locale, page_path, "knowledge")}
<main class="page knowledge-shell">
  <section class="knowledge-hero">
    <div>
      <p class="eyebrow">{e(page["eyebrow"])}</p>
      <h1>{e(page["title"])}</h1>
      <p class="lead">{e(page["summary"])}</p>
    </div>
    <div class="knowledge-meta">
      <div><b>{e(ui["structured_content"])}</b><span>{e(page["structured_content"])}</span></div>
    </div>
  </section>

  {sections}
</main>
</body>
</html>
"""
    return page_path, content


def load_knowledge(locale_code: str) -> dict[str, Any]:
    localized = PROJECT_DATA_DIR / f"knowledge_base.{locale_code}.json"
    if localized.exists():
        return read_json(localized)
    return read_json(PROJECT_DATA_DIR / "knowledge_base.json")


def build(locale_code: str) -> list[Path]:
    locale_path = LOCALES_DIR / f"{locale_code}.json"
    locale = read_json(locale_path)
    configs = {character_id: read_json(CHARACTERS_DIR / f"{character_id}.json") for character_id in CHARACTER_IDS}
    knowledge = load_knowledge(locale_code)

    outputs = [
        render_home(locale, configs),
        render_character_page("qingyou", locale, configs["qingyou"]),
        render_character_page("arisu", locale, configs["arisu"]),
        render_knowledge_index(locale, knowledge),
        render_assets_index(locale, configs),
    ]
    outputs.extend(render_knowledge_page(locale, knowledge, page) for page in knowledge["pages"])
    for path, content in outputs:
        path.parent.mkdir(exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return [path for path, _ in outputs]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Luo sisters static HTML pages.")
    parser.add_argument("--locale", help="Locale JSON name in locales/. Omit to build all public locales.")
    parser.add_argument("--json-out", help="Optional JSON report path.")
    args = parser.parse_args()
    locales = (args.locale,) if args.locale else DEFAULT_LOCALES
    outputs: list[Path] = []
    for locale_code in locales:
        outputs.extend(build(locale_code))
    for path in outputs:
        print(f"Wrote {path}")
    if args.json_out:
        payload = {
            "status": "passed",
            "locales": list(locales),
            "outputs": [str(path) for path in outputs]
        }
        json_path = Path(args.json_out).resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
