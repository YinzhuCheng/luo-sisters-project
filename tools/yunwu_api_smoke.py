#!/usr/bin/env python3
"""Smoke-test Yunwu image API connectivity without exposing the API key."""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://yunwu.ai"
DEFAULT_MODEL = "gpt-image-2"
KEY_RE = re.compile(r"sk-[A-Za-z0-9_-]+")


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


def request_json(
    *,
    method: str,
    url: str,
    key: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 45,
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {key}",
    }
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    started = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            elapsed_ms = int((time.monotonic() - started) * 1000)
            return {
                "ok": True,
                "status": response.status,
                "elapsed_ms": elapsed_ms,
                "json": parse_json(raw),
                "text_preview": raw[:500].decode("utf-8", errors="replace"),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        elapsed_ms = int((time.monotonic() - started) * 1000)
        return {
            "ok": False,
            "status": exc.code,
            "elapsed_ms": elapsed_ms,
            "json": parse_json(raw),
            "text_preview": raw[:500].decode("utf-8", errors="replace"),
        }
    except Exception as exc:  # pragma: no cover - network probe path
        elapsed_ms = int((time.monotonic() - started) * 1000)
        return {
            "ok": False,
            "status": None,
            "elapsed_ms": elapsed_ms,
            "error": type(exc).__name__,
            "text_preview": str(exc)[:500],
        }


def parse_json(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


def summarize_models(payload: Any, target_model: str) -> dict[str, Any]:
    models: list[str] = []
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    models.append(item["id"])
    return {
        "model_count": len(models),
        "target_model_listed": target_model in models,
        "image_related_sample": [m for m in models if "image" in m.lower()][:12],
    }


def summarize_billing(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"has_structured_balance": False}
    text = json.dumps(payload, ensure_ascii=False).lower()
    keys = ("balance", "used", "quota", "credit", "available", "total_available")
    return {
        "has_structured_balance": any(key in text for key in keys),
        "top_level_keys": sorted(payload.keys())[:20],
    }


def write_image_outputs(payload: Any, output_dir: Path) -> list[str]:
    paths: list[str] = []
    if not isinstance(payload, dict):
        return paths
    data = payload.get("data")
    if not isinstance(data, list):
        return paths
    output_dir.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        b64 = item.get("b64_json") or item.get("base64")
        if isinstance(b64, str):
            out = output_dir / f"yunwu-smoke-{index + 1}.png"
            out.write_bytes(base64.b64decode(b64))
            paths.append(str(out.relative_to(ROOT)))
            continue
        url = item.get("url")
        if isinstance(url, str):
            paths.append(url)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-test Yunwu API connectivity.")
    parser.add_argument("--key-file", help="Text file containing an sk-* API key.")
    parser.add_argument("--api-key", help="API key. Prefer --key-file or env injection in normal use.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--json-out", default="logs/yunwu_smoke/latest.json")
    parser.add_argument("--generate-smoke", action="store_true", help="Actually generate one low-quality test image.")
    args = parser.parse_args()

    key = load_api_key(args)
    base = args.base_url.rstrip("/")
    report: dict[str, Any] = {
        "base_url": base,
        "model": args.model,
        "key_present": bool(key),
        "tests": {},
    }

    models = request_json(method="GET", url=f"{base}/v1/models", key=key)
    report["tests"]["models"] = {
        "status": models.get("status"),
        "elapsed_ms": models.get("elapsed_ms"),
        "summary": summarize_models(models.get("json"), args.model),
        "error_preview": None if models.get("ok") else models.get("text_preview"),
    }

    invalid_image_payload = {
        "model": args.model,
        "prompt": "connectivity validation only",
        "n": 0,
        "size": "1024x1024",
        "quality": "low",
        "format": "jpeg",
    }
    image_route = request_json(
        method="POST",
        url=f"{base}/v1/images/generations",
        key=key,
        payload=invalid_image_payload,
    )
    report["tests"]["image_route_no_generation"] = {
        "status": image_route.get("status"),
        "elapsed_ms": image_route.get("elapsed_ms"),
        "connected": image_route.get("status") not in (401, 403, 404, None),
        "error_preview": image_route.get("text_preview"),
    }

    billing_paths = [
        "/v1/billing/usage",
        "/v1/dashboard/billing/credit_grants",
        "/dashboard/billing/credit_grants",
    ]
    billing_results = []
    for path in billing_paths:
        result = request_json(method="GET", url=f"{base}{path}", key=key)
        billing_results.append(
            {
                "path": path,
                "status": result.get("status"),
                "elapsed_ms": result.get("elapsed_ms"),
                "summary": summarize_billing(result.get("json")),
                "error_preview": None if result.get("ok") else result.get("text_preview"),
            }
        )
    report["tests"]["billing_candidates"] = billing_results

    if args.generate_smoke:
        output_dir = ROOT / "logs" / "yunwu_smoke" / "artifacts"
        payload = {
            "model": args.model,
            "prompt": "A tiny blue teacup icon on a flat #ff00ff background, connectivity smoke test only.",
            "n": 1,
            "size": "1024x1024",
            "quality": "low",
            "format": "png",
        }
        generated = request_json(
            method="POST",
            url=f"{base}/v1/images/generations",
            key=key,
            payload=payload,
            timeout=180,
        )
        report["tests"]["generate_smoke"] = {
            "status": generated.get("status"),
            "elapsed_ms": generated.get("elapsed_ms"),
            "output_refs": write_image_outputs(generated.get("json"), output_dir),
            "error_preview": None if generated.get("ok") else generated.get("text_preview"),
        }

    json_out = ROOT / args.json_out
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
