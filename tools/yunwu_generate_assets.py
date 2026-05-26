#!/usr/bin/env python3
"""Generate Luo Sisters asset chroma images with Yunwu gpt-image-2."""
from __future__ import annotations

import argparse
import base64
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import mimetypes
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://yunwu.ai"
DEFAULT_MODEL = "gpt-image-2"
DEFAULT_PYTHON = sys.executable
KEY_RE = re.compile(r"sk-[A-Za-z0-9_-]+")
CHROMA_HELPER = Path.home() / ".codex" / "skills" / ".system" / "imagegen" / "scripts" / "remove_chroma_key.py"

CHARACTER_STYLE = {
    "qingyou": (
        "Luo Qingyou: sage/celadon/ivory/antique-gold Chinese classic Lolita older sister; "
        "long dark hair; plum or gold-green hair ornament; cloud collar, frog buttons, lace cuffs, "
        "fine embroidery; calm tea-and-planner mood."
    ),
    "arisu": (
        "Luo Arisu: blue-white JK Lolita Alice motif; long dark hair; daisy hairpin; blue ribbons, "
        "key necklace, rabbit and pocket-watch motifs, lace socks; curious younger sister; soft youthful proportions."
    ),
}

ASSET_HINTS = {
    ("qingyou", "props", "camera"): "vintage compact camera prop with sage strap, ivory body, antique brass details, planner-recording mood.",
    ("qingyou", "props", "journal"): "sage project journal notebook prop, paper texture, ribbon bookmark, subtle gold floral motif, tidy planner feeling.",
    ("qingyou", "props", "bookmark"): "delicate dry-flower bookmark prop, pressed flower, slim paper tag, antique gold cord.",
    ("arisu", "props", "pocket-watch"): "antique gold pocket watch prop with blue ribbon, simple unnumbered clock face, Alice motif, small daisy/key detail.",
    ("arisu", "props", "storybook"): "old storybook prop with blue-white Alice mood, worn cream pages, small daisy and key ornament on the cover.",
    ("arisu", "props", "notebook"): "small school notebook prop with blue ribbon and subtle daisy motif, tidy soft paper texture.",
}

GLOBAL_STYLE = (
    "Polished 2D Japanese anime character-design asset; clean confident lineart; delicate hand-painted watercolor texture; "
    "soft cel shading; warm diffuse highlights; crisp readable silhouette; source-sheet-consistent proportions; "
    "gentle storybook-lolita mood; refined textile and metal details; not photorealistic, not 3D, not chibi."
)

OUTPUT_RULES = (
    "Single complete object only, centered, generous padding, complete silhouette. "
    "No text, no labels, no watermark, no border, no frame, no card, no unrelated objects, no cast shadow. "
    "Perfectly flat solid #ff00ff chroma-key background only, no gradient, no texture, no floor plane."
)


def read_text_lossy(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gbk", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def load_api_key(args: argparse.Namespace) -> str:
    if args.api_key:
        return args.api_key.strip()
    if args.key_file:
        text = read_text_lossy(Path(args.key_file))
        match = KEY_RE.search(text)
        if match:
            return match.group(0)
        raise SystemExit(f"No sk-* API key found in {args.key_file}")
    raise SystemExit("Provide --api-key or --key-file.")


def read_registry() -> list[dict[str, str]]:
    with (ROOT / "logs" / "asset_registry.csv").open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_registry(rows: list[dict[str, str]]) -> None:
    path = ROOT / "logs" / "asset_registry.csv"
    fieldnames = ["character", "asset_type", "asset_name", "version", "source_crop", "prompt_path", "output_path", "status"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_asset(value: str) -> tuple[str, str, str]:
    parts = value.split(":")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("asset must look like character:asset_type:asset_name")
    return parts[0], parts[1], parts[2]


def registry_row(rows: list[dict[str, str]], key: tuple[str, str, str]) -> dict[str, str]:
    for row in rows:
        if (row["character"], row["asset_type"], row["asset_name"]) == key:
            return row
    raise KeyError(f"No registry row for {':'.join(key)}")


def extract_section(path: Path, heading: str) -> str:
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = None
    marker = f"## {heading}".lower()
    for index, line in enumerate(lines):
        if line.strip().lower() == marker:
            start = index + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def section_from_prompt_path(prompt_path: str) -> str:
    if "#" not in prompt_path:
        return ""
    rel_path, anchor = prompt_path.split("#", 1)
    heading = anchor.replace("-", " ")
    path = ROOT / rel_path
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    start = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## "):
            title = stripped[3:].strip().lower()
            if title == anchor.lower() or title == heading.lower():
                start = index + 1
                break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            end = index
            break
    return "\n".join(lines[start:end]).strip()


def chroma_path_for(row: dict[str, str]) -> Path:
    transparent = Path(row["output_path"])
    parts = list(transparent.parts)
    try:
        index = parts.index("transparent")
    except ValueError as exc:
        raise ValueError(f"Unexpected transparent output path: {transparent}") from exc
    parts[index] = "chroma"
    return ROOT.joinpath(*parts)


def prompt_for(row: dict[str, str], attempt: int = 1) -> str:
    key = (row["character"], row["asset_type"], row["asset_name"])
    hint = ASSET_HINTS.get(key)
    if not hint:
        hint = f"{row['asset_name'].replace('-', ' ')} {row['asset_type']} asset, matching the registered Luo Sisters character design."
    global_anchor = extract_section(ROOT / "prompts" / "character_sheet_prompt_notes.md", "Global Style Anchor")
    prompt_file = ROOT / row["prompt_path"].split("#", 1)[0]
    shared_rules = extract_section(prompt_file, "Shared Rules")
    shared_style = extract_section(prompt_file, "Shared Style Anchor")
    character_heading = "Qingyou Character Style Anchor" if row["character"] == "qingyou" else "Arisu Character Style Anchor"
    character_style = extract_section(prompt_file, character_heading)
    asset_section = section_from_prompt_path(row["prompt_path"])
    retry_note = ""
    if attempt > 1:
        retry_note = (
            "\nRetry safety note: depict only a harmless still-life costume accessory or stationery prop. "
            "Avoid any real-world brand, surveillance, weapon, medical, military, political, or adult context."
        )
    return "\n\n".join(
        part
        for part in [
            "Use the uploaded reference crop as the primary visual guide. Regenerate the referenced subject as a cleaner reusable asset, not as a full sheet crop.",
            global_anchor or GLOBAL_STYLE,
            shared_rules,
            shared_style,
            character_style or CHARACTER_STYLE[row["character"]],
            asset_section,
            f"Registered asset target: {row['character']} / {row['asset_type']} / {row['asset_name']} v{row['version'].lstrip('v')}.",
            f"Asset-specific interpretation for this run: {hint}",
            OUTPUT_RULES,
            "The generated image must use a uniform flat #ff00ff chroma-key background. Do not use yellow, green, blue, white, gray, shadows, gradients, paper texture, or lighting variation in the background. Keep #ff00ff out of the subject itself.",
            retry_note,
        ]
        if part
    )


def request_image(
    *,
    base_url: str,
    key: str,
    model: str,
    prompt: str,
    size: str,
    quality: str,
    image_format: str,
    timeout: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": quality,
        "format": image_format,
        "moderation": "low",
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/images/generations",
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            return {
                "ok": True,
                "status": response.status,
                "elapsed_ms": int((time.monotonic() - started) * 1000),
                "headers": dict(response.headers.items()),
                "json": parse_json(raw),
                "text_preview": raw[:500].decode("utf-8", errors="replace"),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return {
            "ok": False,
            "status": exc.code,
            "elapsed_ms": int((time.monotonic() - started) * 1000),
            "headers": dict(exc.headers.items()),
            "json": parse_json(raw),
            "text_preview": raw[:500].decode("utf-8", errors="replace"),
        }
    except Exception as exc:
        return {
            "ok": False,
            "status": None,
            "elapsed_ms": int((time.monotonic() - started) * 1000),
            "headers": {},
            "json": None,
            "text_preview": f"{type(exc).__name__}: {exc}",
        }


def encode_multipart(fields: dict[str, str], files: list[tuple[str, Path]]) -> tuple[bytes, str]:
    boundary = f"----luo-sisters-yunwu-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"),
                str(value).encode("utf-8"),
                b"\r\n",
            ]
        )
    for name, path in files:
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                (
                    f'Content-Disposition: form-data; name="{name}"; '
                    f'filename="{path.name}"\r\n'
                ).encode("utf-8"),
                f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
                path.read_bytes(),
                b"\r\n",
            ]
        )
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def request_image_edit(
    *,
    base_url: str,
    key: str,
    model: str,
    prompt: str,
    size: str,
    quality: str,
    image_paths: list[Path],
    image_field: str,
    timeout: int,
) -> dict[str, Any]:
    fields = {
        "model": model,
        "prompt": prompt,
        "n": "1",
        "size": size,
        "quality": quality,
        "moderation": "low",
    }
    files = [(image_field, path) for path in image_paths]
    body, content_type = encode_multipart(fields, files)
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/images/edits",
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": content_type,
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            return {
                "ok": True,
                "status": response.status,
                "elapsed_ms": int((time.monotonic() - started) * 1000),
                "headers": dict(response.headers.items()),
                "json": parse_json(raw),
                "text_preview": raw[:500].decode("utf-8", errors="replace"),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return {
            "ok": False,
            "status": exc.code,
            "elapsed_ms": int((time.monotonic() - started) * 1000),
            "headers": dict(exc.headers.items()),
            "json": parse_json(raw),
            "text_preview": raw[:500].decode("utf-8", errors="replace"),
        }
    except Exception as exc:
        return {
            "ok": False,
            "status": None,
            "elapsed_ms": int((time.monotonic() - started) * 1000),
            "headers": {},
            "json": None,
            "text_preview": f"{type(exc).__name__}: {exc}",
        }


def parse_json(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


def save_image(payload: Any, out: Path) -> str:
    if not isinstance(payload, dict):
        raise ValueError("Response was not JSON object")
    data = payload.get("data")
    if isinstance(data, dict):
        item = data
    elif isinstance(data, list) and data:
        item = data[0]
    else:
        raise ValueError("Response JSON did not contain data")
    if not isinstance(item, dict):
        raise ValueError("Response data item was not an object")
    b64 = item.get("b64_json") or item.get("base64")
    out.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(b64, str) and b64:
        out.write_bytes(base64.b64decode(b64))
        return "b64_json"
    url = item.get("url")
    if isinstance(url, str) and url:
        with urllib.request.urlopen(url, timeout=120) as response:
            out.write_bytes(response.read())
        return "url"
    raise ValueError("Response data[0] contained neither b64_json nor url")


def remove_chroma(chroma: Path, transparent: Path) -> dict[str, Any]:
    cmd = [
        DEFAULT_PYTHON,
        str(CHROMA_HELPER),
        "--input",
        str(chroma),
        "--out",
        str(transparent),
        "--auto-key",
        "border",
        "--soft-matte",
        "--transparent-threshold",
        "42",
        "--opaque-threshold",
        "132",
        "--despill",
        "--force",
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=180)
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def alpha_report(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        width, height = rgba.size
        corners = [
            rgba.getpixel((0, 0))[3],
            rgba.getpixel((width - 1, 0))[3],
            rgba.getpixel((0, height - 1))[3],
            rgba.getpixel((width - 1, height - 1))[3],
        ]
        alpha = rgba.getchannel("A")
        bbox = alpha.getbbox()
        bad = 0
        for red, green, blue, alpha_value in rgba.getdata():
            if alpha_value > 200 and red > 230 and blue > 230 and green < 60:
                bad += 1
        return {
            "size": [width, height],
            "corners_alpha": corners,
            "alpha_bbox": list(bbox) if bbox else None,
            "opaque_magenta_pixels": bad,
            "passed": max(corners) <= 8 and bad == 0 and bbox is not None,
        }


def generate_one(row: dict[str, str], args: argparse.Namespace, key: str) -> dict[str, Any]:
    chroma = chroma_path_for(row)
    transparent = ROOT / row["output_path"]
    if (chroma.exists() or transparent.exists()) and not args.force:
        return {
            "asset": asset_id(row),
            "status": "skipped-existing",
            "chroma_path": str(chroma.relative_to(ROOT)),
            "transparent_path": str(transparent.relative_to(ROOT)),
        }
    attempts: list[dict[str, Any]] = []
    final_report: dict[str, Any] | None = None
    for attempt in range(1, args.max_attempts + 1):
        prompt = prompt_for(row, attempt=attempt)
        reference_paths: list[Path] = []
        if args.reference_mode == "edit":
            if not row.get("source_crop"):
                final_report = {
                    "asset": asset_id(row),
                    "status": "missing-reference-crop",
                    "chroma_path": str(chroma.relative_to(ROOT)),
                    "transparent_path": str(transparent.relative_to(ROOT)),
                    "attempts": attempts,
                }
                break
            crop_path = ROOT / row["source_crop"]
            if not crop_path.exists():
                final_report = {
                    "asset": asset_id(row),
                    "status": "missing-reference-crop",
                    "source_crop": row["source_crop"],
                    "chroma_path": str(chroma.relative_to(ROOT)),
                    "transparent_path": str(transparent.relative_to(ROOT)),
                    "attempts": attempts,
                }
                break
            reference_paths.append(crop_path)
            response = request_image_edit(
                base_url=args.base_url,
                key=key,
                model=args.model,
                prompt=prompt,
                size=args.size,
                quality=args.quality,
                image_paths=reference_paths,
                image_field=args.image_field,
                timeout=args.timeout,
            )
        else:
            response = request_image(
                base_url=args.base_url,
                key=key,
                model=args.model,
                prompt=prompt,
                size=args.size,
                quality=args.quality,
                image_format=args.format,
                timeout=args.timeout,
            )
        item_report: dict[str, Any] = {
            "asset": asset_id(row),
            "source_crop": row["source_crop"],
            "attempt": attempt,
            "prompt": prompt,
            "prompt_chars": len(prompt),
            "request": {
                "base_url": args.base_url,
                "model": args.model,
                "size": args.size,
                "quality": args.quality,
                "format": args.format,
                "moderation": "low",
                "reference_mode": (
                    "edit; uploaded source_crop as multipart image"
                    if args.reference_mode == "edit"
                    else "generation; text-only; crop path recorded but not uploaded"
                ),
                "reference_images": [str(path.relative_to(ROOT)) for path in reference_paths],
            },
            "response": {
                "ok": response["ok"],
                "status": response["status"],
                "elapsed_ms": response["elapsed_ms"],
                "headers": filtered_headers(response.get("headers", {})),
                "usage": response["json"].get("usage") if isinstance(response.get("json"), dict) else None,
                "text_preview": None if response["ok"] else response["text_preview"],
            },
            "chroma_path": str(chroma.relative_to(ROOT)),
            "transparent_path": str(transparent.relative_to(ROOT)),
        }
        if not response["ok"]:
            item_report["status"] = "request-failed"
            attempts.append(item_report)
            final_report = item_report
            continue
        try:
            item_report["response_source"] = save_image(response["json"], chroma)
            item_report["remove_chroma"] = remove_chroma(chroma, transparent)
            if item_report["remove_chroma"]["returncode"] != 0:
                item_report["status"] = "chroma-generated"
                attempts.append(item_report)
                final_report = item_report
                continue
            item_report["alpha"] = alpha_report(transparent)
            item_report["status"] = "transparent-ready" if item_report["alpha"]["passed"] else "needs-redraw"
            attempts.append(item_report)
            final_report = item_report
            if item_report["status"] == "transparent-ready":
                break
        except Exception as exc:
            item_report["status"] = "postprocess-failed"
            item_report["postprocess_error"] = f"{type(exc).__name__}: {exc}"
            attempts.append(item_report)
            final_report = item_report
    assert final_report is not None
    report = dict(final_report)
    report["attempts"] = [dict(attempt) for attempt in attempts]
    return report


def filtered_headers(headers: dict[str, str]) -> dict[str, str]:
    interesting = {}
    for key, value in headers.items():
        lower = key.lower()
        if any(token in lower for token in ("cost", "usage", "quota", "balance", "credit", "request", "ratelimit")):
            interesting[key] = value
    return interesting


def asset_id(row: dict[str, str]) -> str:
    return f"{row['character']}:{row['asset_type']}:{row['asset_name']}:{row['version']}"


def append_progress(results: list[dict[str, Any]]) -> None:
    path = ROOT / "logs" / "progress_updates.csv"
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for result in results:
            character, asset_type, asset_name, _version = result["asset"].split(":")
            writer.writerow(
                [
                    datetime.now().strftime("%Y-%m-%d"),
                    "Codex",
                    character,
                    asset_type,
                    "generated external Yunwu asset batch",
                    result["status"],
                    result.get("transparent_path") or result.get("chroma_path", ""),
                    f"{asset_name}; elapsed_ms={result.get('response', {}).get('elapsed_ms', '')}; usage={result.get('response', {}).get('usage')}",
                ]
            )


def update_registry_status(rows: list[dict[str, str]], results: list[dict[str, Any]]) -> None:
    status_by_key = {}
    for result in results:
        character, asset_type, asset_name, _version = result["asset"].split(":")
        if result["status"] in {"transparent-ready", "chroma-generated", "needs-redraw"}:
            status_by_key[(character, asset_type, asset_name)] = result["status"]
        elif result["status"] in {"request-failed", "postprocess-failed", "missing-reference-crop"}:
            status_by_key[(character, asset_type, asset_name)] = "needs-redraw"
    for row in rows:
        key = (row["character"], row["asset_type"], row["asset_name"])
        if key in status_by_key:
            row["status"] = status_by_key[key]
    write_registry(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate registered Luo Sisters assets via Yunwu.")
    parser.add_argument("--key-file", required=True)
    parser.add_argument("--api-key")
    parser.add_argument("--asset", action="append", type=parse_asset, required=True, help="character:asset_type:asset_name")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="low", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--format", default="png", choices=["png", "jpeg", "webp"])
    parser.add_argument("--reference-mode", choices=["edit", "generation"], default="edit")
    parser.add_argument("--image-field", default="image", help="Multipart field name for reference images.")
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json-out", help="Report path. Defaults to logs/yunwu_batches/<timestamp>/report.json.")
    args = parser.parse_args()

    key = load_api_key(args)
    rows = read_registry()
    selected = [registry_row(rows, asset) for asset in args.asset]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = ROOT / (args.json_out or f"logs/yunwu_batches/{timestamp}/report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [executor.submit(generate_one, row, args, key) for row in selected]
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda item: item["asset"])
    update_registry_status(rows, results)
    append_progress(results)

    report = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "base_url": args.base_url,
        "model": args.model,
        "concurrency": args.concurrency,
        "quality": args.quality,
        "size": args.size,
        "format": args.format,
        "results": results,
        "cost_summary": {
            "usage_fields_present": any(result.get("response", {}).get("usage") for result in results),
            "header_cost_fields": [
                result.get("response", {}).get("headers", {}) for result in results if result.get("response", {}).get("headers")
            ],
        },
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
