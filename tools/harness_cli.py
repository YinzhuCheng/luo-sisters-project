#!/usr/bin/env python3
"""Harness CLI for task packet preflight, verification, bundling, and scoring."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS_DIR = ROOT / "harness"
LOGS_DIR = ROOT / "logs" / "harness_runs"
TASK_SCHEMA_PATH = HARNESS_DIR / "task_templates" / "task_packet.schema.json"
OWNERSHIP_MAP_PATH = HARNESS_DIR / "ownership_map.json"
QUALITY_SCORE_PATH = HARNESS_DIR / "quality_score.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def normalize_rel(path_text: str) -> str:
    return path_text.replace("\\", "/").lstrip("./")


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def load_packet(packet_ref: str) -> tuple[Path, dict[str, Any]]:
    candidate = Path(packet_ref)
    if not candidate.is_absolute():
        candidate = (ROOT / packet_ref).resolve()
    return candidate, read_json(candidate)


def packet_run_dir(packet: dict[str, Any], explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            path = (ROOT / explicit).resolve()
        return path
    return (LOGS_DIR / f"{now_stamp()}-{packet['id']}").resolve()


def owner_domain(packet: dict[str, Any]) -> str:
    return str(packet.get("metadata", {}).get("owner_domain", "")).strip()


def check_profile_path(packet: dict[str, Any]) -> Path:
    override = str(packet.get("metadata", {}).get("check_profile", "")).strip()
    if override:
        return (ROOT / override).resolve()
    return (HARNESS_DIR / "check_profiles" / f"{packet['kind']}.json").resolve()


def path_in_domain(path_text: str, prefixes: list[str]) -> bool:
    target = normalize_rel(path_text)
    for prefix in prefixes:
        normalized_prefix = normalize_rel(prefix)
        if normalized_prefix.endswith("/"):
            if target.startswith(normalized_prefix):
                return True
        elif target == normalized_prefix or target.startswith(f"{normalized_prefix}/"):
            return True
    return False


def find_domain(domain_id: str) -> dict[str, Any] | None:
    data = read_json(OWNERSHIP_MAP_PATH)
    for domain in data.get("domains", []):
        if domain["id"] == domain_id:
            return domain
    return None


def packet_conflicts(packet: dict[str, Any]) -> list[str]:
    conflicts: list[str] = []
    allowed = [normalize_rel(item) for item in packet.get("allowed_paths", [])]
    forbidden = [normalize_rel(item) for item in packet.get("forbidden_paths", [])]
    for allow in allowed:
        for deny in forbidden:
            if allow == deny or allow.startswith(f"{deny}/") or deny.startswith(f"{allow}/"):
                conflicts.append(f"allowed and forbidden paths conflict: {allow} <-> {deny}")
    return conflicts


def validate_packet_shape(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = read_json(TASK_SCHEMA_PATH).get("required", [])
    for key in required:
        if key not in packet:
            errors.append(f"missing required task packet field: {key}")
    if packet.get("kind") not in {"docs", "page", "asset", "maintenance"}:
        errors.append(f"invalid task kind: {packet.get('kind')}")
    if not packet.get("allowed_paths"):
        errors.append("allowed_paths must not be empty")
    if not packet.get("required_checks"):
        errors.append("required_checks must not be empty")
    if owner_domain(packet) == "":
        errors.append("metadata.owner_domain is required")
    if not check_profile_path(packet).exists():
        errors.append(f"check profile missing: {check_profile_path(packet).relative_to(ROOT)}")
    return errors


def validate_ownership(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    domain_id = owner_domain(packet)
    domain = find_domain(domain_id)
    if not domain:
        return [f"unknown ownership domain: {domain_id}"]
    prefixes = domain.get("path_prefixes", [])
    for path_text in packet.get("allowed_paths", []):
        if not path_in_domain(path_text, prefixes):
            errors.append(f"allowed path outside ownership domain {domain_id}: {path_text}")
    return errors


def validate_inputs(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for item in packet.get("inputs", []):
        if not item.get("required", True):
            continue
        path_text = str(item.get("path", ""))
        if not path_text:
            errors.append("input is missing path")
            continue
        if not (ROOT / path_text).resolve().exists():
            errors.append(f"required input missing: {path_text}")
    return errors


def preflight_packet(packet: dict[str, Any]) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    failures.extend(validate_packet_shape(packet))
    failures.extend(packet_conflicts(packet))
    failures.extend(validate_ownership(packet))
    failures.extend(validate_inputs(packet))
    return failures, warnings


def python_exe() -> str:
    return sys.executable


def run_python_check(name: str, script_rel: str, args: list[str], artifacts_dir: Path) -> dict[str, Any]:
    stdout_path = artifacts_dir / f"{name}.stdout.txt"
    stderr_path = artifacts_dir / f"{name}.stderr.txt"
    json_path = artifacts_dir / f"{name}.json"
    command = [python_exe(), str((ROOT / script_rel).resolve()), *args, "--json-out", str(json_path)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    payload = read_json(json_path) if json_path.exists() else {}
    return {
        "name": name,
        "returncode": result.returncode,
        "stdout": str(stdout_path.relative_to(ROOT)),
        "stderr": str(stderr_path.relative_to(ROOT)),
        "json": str(json_path.relative_to(ROOT)) if json_path.exists() else "",
        "payload": payload
    }


def run_reader_targets(packet: dict[str, Any], artifacts_dir: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    targets = list(packet.get("metadata", {}).get("reader_targets", []))
    if not targets:
        targets = [item["path"] for item in packet.get("inputs", []) if str(item.get("path", "")).endswith(".html")]
    for index, target in enumerate(targets[:3], start=1):
        out_path = artifacts_dir / f"reader-{index}.txt"
        err_path = artifacts_dir / f"reader-{index}.stderr.txt"
        command = [
            python_exe(),
            str((ROOT / "skills" / "project-doc-governance" / "scripts" / "read_html_doc.py").resolve()),
            target,
            "--structure-mode"
        ]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        out_path.write_text(result.stdout, encoding="utf-8")
        err_path.write_text(result.stderr, encoding="utf-8")
        results.append(
            {
                "name": f"html-reader-{index}",
                "returncode": result.returncode,
                "stdout": str(out_path.relative_to(ROOT)),
                "stderr": str(err_path.relative_to(ROOT)),
                "target": target
            }
        )
    return results


def verify_docs(packet: dict[str, Any], artifacts_dir: Path) -> list[dict[str, Any]]:
    checks = [run_python_check("link-audit", "tools/audit_project_links.py", [], artifacts_dir)]
    checks.extend(run_reader_targets(packet, artifacts_dir))
    return checks


def verify_page(packet: dict[str, Any], artifacts_dir: Path) -> list[dict[str, Any]]:
    checks = [
        run_python_check("site-build", "tools/build_project_html.py", [], artifacts_dir),
        run_python_check("link-audit", "tools/audit_project_links.py", [], artifacts_dir)
    ]
    targets = list(packet.get("metadata", {}).get("targets", [])) or ["index.html"]
    for index, target in enumerate(targets, start=1):
        screenshot = artifacts_dir / f"browser-smoke-{index}.png"
        checks.append(
            run_python_check(
                f"browser-smoke-{index}",
                "tools/browser_smoke_check.py",
                [target, "--output", str(screenshot), "--width", "1440", "--height", "2200"],
                artifacts_dir
            )
        )
    return checks


def verify_asset(packet: dict[str, Any], artifacts_dir: Path) -> list[dict[str, Any]]:
    args: list[str] = []
    character = str(packet.get("metadata", {}).get("character", "")).strip()
    if character:
        args.extend(["--character", character])
    checks = [run_python_check("asset-validate", "tools/validate_assets.py", args, artifacts_dir)]
    boundary_errors: list[str] = []
    if character:
        for output_path in packet.get("expected_outputs", []):
            normalized = normalize_rel(output_path)
            if normalized.startswith("assets/characters/") and not normalized.startswith(f"assets/characters/{character}/"):
                boundary_errors.append(f"expected output crosses declared character boundary: {normalized}")
    payload = {"status": "failed" if boundary_errors else "passed", "errors": boundary_errors}
    boundary_json = artifacts_dir / "planned-output-boundary.json"
    write_json(boundary_json, payload)
    checks.append(
        {
            "name": "planned-output-boundary",
            "returncode": 1 if boundary_errors else 0,
            "stdout": "",
            "stderr": "",
            "json": str(boundary_json.relative_to(ROOT)),
            "payload": payload
        }
    )
    return checks


def verify_maintenance(_packet: dict[str, Any], artifacts_dir: Path) -> list[dict[str, Any]]:
    checks = [run_python_check("link-audit", "tools/audit_project_links.py", [], artifacts_dir)]
    issue_rows = 0
    issue_path = ROOT / "logs" / "issue_memory.csv"
    if issue_path.exists():
        with issue_path.open("r", encoding="utf-8", newline="") as handle:
            issue_rows = sum(1 for _ in csv.DictReader(handle))
    payload = {
        "status": "passed",
        "issue_rows": issue_rows,
        "quality_score_file": str(QUALITY_SCORE_PATH.relative_to(ROOT))
    }
    maintenance_json = artifacts_dir / "maintenance-scan.json"
    write_json(maintenance_json, payload)
    checks.append(
        {
            "name": "maintenance-scan",
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "json": str(maintenance_json.relative_to(ROOT)),
            "payload": payload
        }
    )
    return checks


def verify_packet(packet: dict[str, Any], artifacts_dir: Path) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    if packet["kind"] == "docs":
        checks = verify_docs(packet, artifacts_dir)
    elif packet["kind"] == "page":
        checks = verify_page(packet, artifacts_dir)
    elif packet["kind"] == "asset":
        checks = verify_asset(packet, artifacts_dir)
    else:
        checks = verify_maintenance(packet, artifacts_dir)

    warnings: list[str] = []
    failures: list[str] = []
    for check in checks:
        payload = check.get("payload", {})
        warnings.extend(payload.get("warnings", []))
        failures.extend(payload.get("errors", []))
        if check["returncode"] != 0 and not payload.get("errors"):
            failures.append(f"{check['name']} failed with return code {check['returncode']}")
    return checks, warnings, failures


def bundle_report(packet: dict[str, Any], run_dir: Path) -> tuple[dict[str, Any], Path, Path]:
    preflight = read_json(run_dir / "preflight.json") if (run_dir / "preflight.json").exists() else {"warnings": [], "failures": []}
    verify = read_json(run_dir / "verify.json") if (run_dir / "verify.json").exists() else {"warnings": [], "failures": [], "checks_run": []}
    warnings = list(preflight.get("warnings", [])) + list(verify.get("warnings", []))
    failures = list(preflight.get("failures", [])) + list(verify.get("failures", []))
    artifacts_dir = run_dir / "artifacts"
    artifacts = [str(path.relative_to(ROOT)) for path in artifacts_dir.rglob("*") if path.is_file()] if artifacts_dir.exists() else []
    status = "failed" if failures else ("passed_with_warnings" if warnings else "passed")
    report = {
        "task_id": packet["id"],
        "task_kind": packet["kind"],
        "status": status,
        "checks_run": verify.get("checks_run", []),
        "warnings": warnings,
        "failures": failures,
        "artifacts": artifacts,
        "touched_paths": packet.get("allowed_paths", []),
        "metadata": {
            "owner_domain": owner_domain(packet),
            "check_profile": str(check_profile_path(packet).relative_to(ROOT))
        }
    }
    report_path = run_dir / "report.json"
    summary_path = run_dir / "summary.md"
    write_json(report_path, report)
    summary_lines = [
        "# Harness Run Summary",
        "",
        f"- Task ID: `{packet['id']}`",
        f"- Kind: `{packet['kind']}`",
        f"- Status: `{status}`",
        f"- Owner Domain: `{owner_domain(packet)}`",
        f"- Checks Run: {', '.join(report['checks_run']) if report['checks_run'] else '(none)'}",
        f"- Warnings: {len(warnings)}",
        f"- Failures: {len(failures)}",
        ""
    ]
    if warnings:
        summary_lines.append("## Warnings")
        summary_lines.extend(f"- {item}" for item in warnings)
        summary_lines.append("")
    if failures:
        summary_lines.append("## Failures")
        summary_lines.extend(f"- {item}" for item in failures)
        summary_lines.append("")
    if artifacts:
        summary_lines.append("## Artifacts")
        summary_lines.extend(f"- `{item}`" for item in artifacts)
        summary_lines.append("")
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    return report, report_path, summary_path


def command_preflight(args: argparse.Namespace) -> int:
    packet_path, packet = load_packet(args.packet)
    run_dir = packet_run_dir(packet, args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    failures, warnings = preflight_packet(packet)
    payload = {
        "task_id": packet["id"],
        "task_path": str(packet_path.relative_to(ROOT)),
        "status": "failed" if failures else "passed",
        "warnings": warnings,
        "failures": failures
    }
    write_json(run_dir / "preflight.json", payload)
    print(str((run_dir / "preflight.json").relative_to(ROOT)))
    return 1 if failures else 0


def command_verify(args: argparse.Namespace) -> int:
    _packet_path, packet = load_packet(args.packet)
    run_dir = packet_run_dir(packet, args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = run_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    checks, warnings, failures = verify_packet(packet, artifacts_dir)
    payload = {
        "task_id": packet["id"],
        "status": "failed" if failures else "passed",
        "checks_run": [check["name"] for check in checks],
        "warnings": warnings,
        "failures": failures,
        "check_results": checks
    }
    write_json(run_dir / "verify.json", payload)
    print(str((run_dir / "verify.json").relative_to(ROOT)))
    return 1 if failures else 0


def command_bundle(args: argparse.Namespace) -> int:
    _packet_path, packet = load_packet(args.packet)
    run_dir = packet_run_dir(packet, args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    report, report_path, summary_path = bundle_report(packet, run_dir)
    print(str(report_path.relative_to(ROOT)))
    print(str(summary_path.relative_to(ROOT)))
    return 1 if report["status"] == "failed" else 0


def command_score(args: argparse.Namespace) -> int:
    payload = read_json(QUALITY_SCORE_PATH)
    if args.run_dir:
        run_dir = Path(args.run_dir)
        if not run_dir.is_absolute():
            run_dir = (ROOT / args.run_dir).resolve()
        write_json(run_dir / "score.json", payload)
        print(str((run_dir / "score.json").relative_to(ROOT)))
    else:
        print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run harness task packet stages.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight", help="Validate packet shape and boundaries.")
    preflight.add_argument("packet", help="Task packet path.")
    preflight.add_argument("--run-dir", help="Existing or target run directory.")
    preflight.set_defaults(func=command_preflight)

    verify = subparsers.add_parser("verify", help="Run task-type verification checks.")
    verify.add_argument("packet", help="Task packet path.")
    verify.add_argument("--run-dir", help="Existing or target run directory.")
    verify.set_defaults(func=command_verify)

    bundle = subparsers.add_parser("bundle", help="Assemble the final evidence bundle report.")
    bundle.add_argument("packet", help="Task packet path.")
    bundle.add_argument("--run-dir", help="Existing or target run directory.")
    bundle.set_defaults(func=command_bundle)

    score = subparsers.add_parser("score", help="Write or print the current harness quality score snapshot.")
    score.add_argument("--run-dir", help="Run directory for score.json output.")
    score.set_defaults(func=command_score)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
