#!/usr/bin/env python3
"""Emit GitHub-friendly warnings and gating errors from a harness run bundle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "harness" / "policies" / "warn_then_gate.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def latest_run_dir(task_id: str) -> Path:
    candidates = sorted((ROOT / "logs" / "harness_runs").glob(f"*-{task_id}"))
    if not candidates:
        raise FileNotFoundError(f"No harness run directory found for task {task_id}")
    return candidates[-1]


def check_coverage(report: dict, packet: dict, check_profile: dict) -> list[str]:
    checks_run = list(report.get("checks_run", []))
    warnings: list[str] = []
    expectations = list(check_profile.get("stages", {}).get("verify", []))

    def has(prefix: str) -> bool:
        return any(item == prefix or item.startswith(prefix) for item in checks_run)

    coverage_map = {
        "document-catalog-reachability": has("link-audit"),
        "link-audit": has("link-audit"),
        "md-mirror-sync": has("md-mirror-sync"),
        "html-reader-structure-check": has("html-reader-"),
        "site-build": has("site-build"),
        "browser-smoke-check": has("browser-smoke-"),
        "asset-structure-validation": has("asset-validate"),
        "asset-registry-consistency": has("asset-validate"),
        "planned-output-boundary-check": has("planned-output-boundary"),
        "issue-memory-scan": has("maintenance-scan"),
        "score-input-scan": has("maintenance-scan"),
    }
    for item in expectations:
        if not coverage_map.get(item, False):
            warnings.append(f"coverage gap: expected verify check `{item}` was not observed in checks_run")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply warn-then-gate policy to a harness run bundle.")
    parser.add_argument("packet", help="Path to a harness task packet.")
    parser.add_argument("--run-dir", help="Explicit harness run directory. Defaults to the latest run for the packet id.")
    args = parser.parse_args()

    packet_path = Path(args.packet)
    if not packet_path.is_absolute():
        packet_path = (ROOT / args.packet).resolve()
    packet = read_json(packet_path)
    run_dir = Path(args.run_dir).resolve() if args.run_dir else latest_run_dir(str(packet["id"]))
    report = read_json(run_dir / "report.json")
    policy = read_json(POLICY_PATH)
    check_profile = read_json(ROOT / packet["metadata"]["check_profile"])

    warnings = list(report.get("warnings", []))
    warnings.extend(check_coverage(report, packet, check_profile))

    expected_files = set(packet.get("evidence_bundle", {}).get("artifact_expectations", []))
    missing = [name for name in expected_files if not (run_dir / name).exists()]
    if missing:
        warnings.append(f"missing evidence artifacts: {', '.join(sorted(missing))}")

    score_path = run_dir / "score.json"
    if score_path.exists():
        score = read_json(score_path)
        total = int(score.get("total_score", 0))
        thresholds = score.get("scoring_defaults", {})
        warning_total = int(thresholds.get("warning_total", 0))
        if total < warning_total:
            warnings.append(
                f"quality score below warning threshold: total={total}, warning_total={warning_total}"
            )

    for warning in warnings:
        print(f"::warning::{warning}")

    failures = list(report.get("failures", []))
    if report.get("status") == "failed":
        for failure in failures:
            print(f"::error::{failure}")
        return 1

    if report.get("status") == "passed_with_warnings" and not policy.get("warning_rules"):
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
