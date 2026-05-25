#!/usr/bin/env python3
"""Harness CLI for task packet preflight, verification, bundling, and scoring."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HARNESS_DIR = ROOT / "harness"
LOGS_DIR = ROOT / "logs" / "harness_runs"
TASK_SCHEMA_PATH = HARNESS_DIR / "task_templates" / "task_packet.schema.json"
OWNERSHIP_MAP_PATH = HARNESS_DIR / "ownership_map.json"
QUALITY_SCORE_PATH = HARNESS_DIR / "quality_score.json"
WARN_THEN_GATE_PATH = HARNESS_DIR / "policies" / "warn_then_gate.json"
ISSUE_MEMORY_PATH = ROOT / "logs" / "issue_memory.csv"
EXPECTED_TASK_IDS = (
    "docs-governance-maintenance",
    "knowledge-page-structure",
    "site-smoke-check",
    "qingyou-asset-batch",
    "arisu-asset-batch",
    "asset-registry-sync",
    "harness-maintenance",
)
EXPECTED_WORKFLOWS = (
    ".github/workflows/harness-docs.yml",
    ".github/workflows/harness-pages.yml",
    ".github/workflows/harness-assets.yml",
    ".github/workflows/harness-maintenance.yml",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def normalize_rel(path_text: str) -> str:
    return path_text.replace("\\", "/").lstrip("./")


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def iso_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


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
        "payload": payload,
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
            "--structure-mode",
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
                "target": target,
            }
        )
    return results


def read_issue_rows() -> list[dict[str, str]]:
    if not ISSUE_MEMORY_PATH.exists():
        return []
    with ISSUE_MEMORY_PATH.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def maintenance_issue_scan() -> dict[str, Any]:
    rows = read_issue_rows()
    policy = read_json(WARN_THEN_GATE_PATH)
    trace_fields = list(policy.get("issue_trace_fields", []))
    fieldnames = list(rows[0].keys()) if rows else trace_fields
    missing_trace_fields = [field for field in trace_fields if field not in fieldnames]
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        issue_key = row.get("issue_key", "").strip() or normalize_rel(row.get("issue", "")) or "unkeyed-issue"
        grouped.setdefault(issue_key, []).append(row)

    suggestions: list[str] = []
    tracked_issues: list[dict[str, Any]] = []
    thresholds = policy.get("promotion_policy", {})
    issue_to_policy = int(thresholds.get("issue_to_policy_after_occurrences", 2))
    issue_to_verify = int(thresholds.get("issue_to_verify_after_occurrences", 3))

    for issue_key, entries in sorted(grouped.items()):
        latest = entries[-1]
        occurrences = len(entries)
        policy_ref = latest.get("policy_ref", "").strip()
        check_ref = latest.get("check_ref", "").strip()
        promotion_level = latest.get("promotion_level", "").strip() or "note"
        if occurrences >= issue_to_policy and not policy_ref:
            suggestions.append(f"{issue_key}: add a harness policy reference after {occurrences} occurrences")
        if occurrences >= issue_to_verify and not check_ref:
            suggestions.append(f"{issue_key}: add verify coverage after {occurrences} occurrences")
        if occurrences > issue_to_verify and promotion_level == "verify":
            suggestions.append(f"{issue_key}: repeated verify-level issue should be reviewed for blocking-gate promotion")
        tracked_issues.append(
            {
                "issue_key": issue_key,
                "occurrences": occurrences,
                "policy_ref": policy_ref,
                "check_ref": check_ref,
                "promotion_level": promotion_level,
            }
        )

    rows_with_policy = sum(1 for row in rows if row.get("policy_ref", "").strip())
    rows_with_check = sum(1 for row in rows if row.get("check_ref", "").strip())
    rows_with_level = sum(1 for row in rows if row.get("promotion_level", "").strip())
    return {
        "status": "passed",
        "issue_rows": len(rows),
        "unique_issue_keys": len(grouped),
        "missing_trace_fields": missing_trace_fields,
        "rows_with_policy_ref": rows_with_policy,
        "rows_with_check_ref": rows_with_check,
        "rows_with_promotion_level": rows_with_level,
        "tracked_issues": tracked_issues,
        "suggestions": suggestions,
        "quality_score_file": str(QUALITY_SCORE_PATH.relative_to(ROOT)),
        "promotion_policy": thresholds,
        "warnings": suggestions + ([f"issue_memory.csv missing trace fields: {', '.join(missing_trace_fields)}"] if missing_trace_fields else []),
    }


def latest_run_dir(task_id: str) -> Path | None:
    candidates = sorted(LOGS_DIR.glob(f"*-{task_id}"))
    return candidates[-1] if candidates else None


def latest_task_report(task_id: str) -> tuple[str, Path | None, dict[str, Any] | None]:
    candidates = sorted(LOGS_DIR.glob(f"*-{task_id}"))
    for candidate in reversed(candidates):
        report_path = candidate / "report.json"
        if report_path.exists():
            return str(candidate.relative_to(ROOT)), candidate, read_json(report_path)
    return "", None, None


def verify_docs(packet: dict[str, Any], artifacts_dir: Path) -> list[dict[str, Any]]:
    checks = [
        run_python_check("link-audit", "tools/audit_project_links.py", [], artifacts_dir),
        run_python_check("md-mirror-sync", "tools/build_html_markdown_mirror.py", ["--check"], artifacts_dir),
    ]
    checks.extend(run_reader_targets(packet, artifacts_dir))
    return checks


def verify_page(packet: dict[str, Any], artifacts_dir: Path) -> list[dict[str, Any]]:
    checks = [
        run_python_check("site-build", "tools/build_project_html.py", [], artifacts_dir),
        run_python_check("md-mirror-sync", "tools/build_html_markdown_mirror.py", ["--check"], artifacts_dir),
        run_python_check("link-audit", "tools/audit_project_links.py", [], artifacts_dir),
    ]
    targets = list(packet.get("metadata", {}).get("targets", [])) or ["index.html"]
    for index, target in enumerate(targets, start=1):
        screenshot = artifacts_dir / f"browser-smoke-{index}.png"
        checks.append(
            run_python_check(
                f"browser-smoke-{index}",
                "tools/browser_smoke_check.py",
                [target, "--output", str(screenshot), "--width", "1440", "--height", "2200"],
                artifacts_dir,
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
            "payload": payload,
        }
    )
    return checks


def verify_maintenance(_packet: dict[str, Any], artifacts_dir: Path) -> list[dict[str, Any]]:
    checks = [run_python_check("link-audit", "tools/audit_project_links.py", [], artifacts_dir)]
    payload = maintenance_issue_scan()
    maintenance_json = artifacts_dir / "maintenance-scan.json"
    write_json(maintenance_json, payload)
    checks.append(
        {
            "name": "maintenance-scan",
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "json": str(maintenance_json.relative_to(ROOT)),
            "payload": payload,
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
            "check_profile": str(check_profile_path(packet).relative_to(ROOT)),
        },
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
        "",
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


def status_from_score(score: int) -> str:
    if score >= 16:
        return "strong"
    if score >= 11:
        return "good"
    if score >= 6:
        return "partial"
    return "weak"


def report_points(task_id: str, full_points: int, warning_points: int) -> tuple[int, str]:
    _run_dir_text, _run_dir, report = latest_task_report(task_id)
    if not report:
        return 0, f"{task_id}: no report found"
    status = report.get("status", "missing")
    if status == "passed":
        return full_points, f"{task_id}: passed"
    if status == "passed_with_warnings":
        return warning_points, f"{task_id}: passed with warnings"
    return 0, f"{task_id}: failed"


def all_exist(paths: list[str]) -> bool:
    return all((ROOT / path).exists() for path in paths)


def compute_quality_score(run_dir: Path | None) -> dict[str, Any]:
    defaults = read_json(QUALITY_SCORE_PATH).get("scoring_defaults", {"max_per_dimension": 20, "passing_total": 75, "warning_total": 55})
    catalog = read_json(ROOT / "project_data" / "document_catalog.json")
    catalog_paths = {entry["path"] for entry in catalog.get("documents", [])}
    maintenance_scan = maintenance_issue_scan()
    effective_run_dir = run_dir or latest_task_report("harness-maintenance")[1]

    dimensions: dict[str, dict[str, Any]] = {}

    doc_score = 0
    doc_notes: list[str] = []
    if all_exist(["AGENTS.md", "README.md", "docs/document_governance.md", "docs/content_map.md"]):
        doc_score += 5
        doc_notes.append("Entry documents are present.")
    if all_exist(["docs/harness_ci.md", "skills/project-doc-governance/scripts/read_html_doc.py"]):
        doc_score += 5
        doc_notes.append("HTML reading skill and CI guide are present.")
    if {"knowledge/navigation.html", "knowledge/assets.html", "docs/harness_ci.md"}.issubset(catalog_paths):
        doc_score += 5
        doc_notes.append("Document catalog registers navigation, assets, and CI guide.")
    points, note = report_points("docs-governance-maintenance", 5, 3)
    doc_score += points
    doc_notes.append(note)
    dimensions["doc_legibility"] = {"score": doc_score, "status": status_from_score(doc_score), "notes": doc_notes}

    packet_present = sum(1 for task_id in EXPECTED_TASK_IDS if (ROOT / "harness" / "tasks" / f"{task_id}.json").exists())
    task_score = round((packet_present / len(EXPECTED_TASK_IDS)) * 20)
    task_notes = [f"{packet_present}/{len(EXPECTED_TASK_IDS)} expected task packets are present."]
    dimensions["task_packet_coverage"] = {"score": task_score, "status": status_from_score(task_score), "notes": task_notes}

    page_score = 0
    page_notes: list[str] = []
    if all_exist(["docs/browser_automation.md", "requirements-browser.txt", "tools/browser_smoke_check.py"]):
        page_score += 5
        page_notes.append("Browser automation tooling is present.")
    if all_exist(list(EXPECTED_WORKFLOWS[:2])):
        page_score += 5
        page_notes.append("Docs and page workflows are configured.")
    points, note = report_points("knowledge-page-structure", 5, 3)
    page_score += points
    page_notes.append(note)
    points, note = report_points("site-smoke-check", 5, 3)
    page_score += points
    page_notes.append(note)
    dimensions["page_qa_coverage"] = {"score": page_score, "status": status_from_score(page_score), "notes": page_notes}

    asset_score = 0
    asset_notes: list[str] = []
    if all_exist(
        [
            "characters/qingyou.json",
            "characters/arisu.json",
            "logs/asset_registry.csv",
            "assets/characters/qingyou/workflow/crop_manifest.csv",
            "assets/characters/arisu/workflow/crop_manifest.csv",
        ]
    ):
        asset_score += 5
        asset_notes.append("Character config, registry, and crop manifests are present.")
    if all_exist(
        [
            "harness/tasks/qingyou-asset-batch.json",
            "harness/tasks/arisu-asset-batch.json",
            "harness/tasks/asset-registry-sync.json",
        ]
    ):
        asset_score += 5
        asset_notes.append("Character and shared asset packets are present.")
    points, note = report_points("qingyou-asset-batch", 5, 3)
    asset_score += points
    asset_notes.append(note)
    arisu_points, arisu_note = report_points("arisu-asset-batch", 5, 3)
    asset_score += arisu_points
    asset_notes.append(arisu_note)
    registry_points, registry_note = report_points("asset-registry-sync", 5, 3)
    asset_score += registry_points
    asset_notes.append(registry_note)
    if asset_score > 20:
        asset_score = 20
    dimensions["asset_lineage_completeness"] = {"score": asset_score, "status": status_from_score(asset_score), "notes": asset_notes}

    policy_score = 0
    policy_notes: list[str] = []
    if all_exist(["harness/ownership_map.json", "harness/policies/warn_then_gate.json", "docs/harness_ci.md"]):
        policy_score += 5
        policy_notes.append("Core governance policy files are present.")
    if all_exist(list(EXPECTED_WORKFLOWS)):
        policy_score += 5
        policy_notes.append("All harness delivery-loop workflows are present.")
    if not maintenance_scan["missing_trace_fields"]:
        policy_score += 5
        policy_notes.append("Issue memory exposes trace fields for policy and verify mapping.")
    else:
        policy_notes.append(f"Missing issue trace fields: {', '.join(maintenance_scan['missing_trace_fields'])}")
    points, note = report_points("harness-maintenance", 5, 3)
    policy_score += points
    policy_notes.append(note)
    if maintenance_scan["suggestions"]:
        policy_notes.append(f"{len(maintenance_scan['suggestions'])} maintenance promotion suggestion(s) remain open.")
    else:
        policy_score += 5
        policy_notes.append("No pending promotion suggestions from issue memory.")
    if policy_score > 20:
        policy_score = 20
    dimensions["policy_compliance"] = {"score": policy_score, "status": status_from_score(policy_score), "notes": policy_notes}

    total_score = sum(item["score"] for item in dimensions.values())
    passing_total = int(defaults.get("passing_total", 75))
    warning_total = int(defaults.get("warning_total", 55))
    if total_score >= passing_total:
        status = "passing"
    elif total_score >= warning_total:
        status = "warning"
    else:
        status = "baseline"

    latest_reports: dict[str, dict[str, str]] = {}
    for task_id in EXPECTED_TASK_IDS:
        run_dir_text, _task_dir, report = latest_task_report(task_id)
        latest_reports[task_id] = {
            "run_dir": run_dir_text,
            "status": str(report.get("status", "missing")) if report else "missing",
        }

    payload = {
        "version": "1.1",
        "status": status,
        "last_updated": iso_now(),
        "last_run": str(effective_run_dir.relative_to(ROOT)) if effective_run_dir else None,
        "total_score": total_score,
        "dimensions": dimensions,
        "scoring_defaults": defaults,
        "latest_reports": latest_reports,
        "maintenance_summary": {
            "issue_rows": maintenance_scan["issue_rows"],
            "unique_issue_keys": maintenance_scan["unique_issue_keys"],
            "suggestions": maintenance_scan["suggestions"],
        },
    }
    return payload


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
        "failures": failures,
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
        "check_results": checks,
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
    run_dir: Path | None = None
    if args.run_dir:
        run_dir = Path(args.run_dir)
        if not run_dir.is_absolute():
            run_dir = (ROOT / args.run_dir).resolve()
    payload = compute_quality_score(run_dir)
    write_json(QUALITY_SCORE_PATH, payload)
    if run_dir:
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
