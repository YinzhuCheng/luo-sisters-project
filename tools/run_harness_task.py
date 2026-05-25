#!/usr/bin/env python3
"""Run preflight, verify, bundle, and optional score for one harness task packet."""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS_CLI = ROOT / "tools" / "harness_cli.py"


def read_packet_id(packet_path: Path) -> str:
    import json

    data = json.loads(packet_path.read_text(encoding="utf-8-sig"))
    return str(data["id"])


def run(command: list[str]) -> int:
    result = subprocess.run(command, cwd=ROOT)
    return int(result.returncode)


def write_github_output(path: str | None, run_dir: Path, task_id: str) -> None:
    if not path:
        return
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(f"run_dir={run_dir.as_posix()}\n")
        handle.write(f"task_id={task_id}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a full harness packet flow with one stable run directory.")
    parser.add_argument("packet", help="Path to a harness task packet.")
    parser.add_argument("--score", action="store_true", help="Write score.json into the run directory after bundling.")
    parser.add_argument("--github-output", help="Optional GitHub Actions output file path.")
    args = parser.parse_args()

    packet_path = Path(args.packet)
    if not packet_path.is_absolute():
        packet_path = (ROOT / args.packet).resolve()
    task_id = read_packet_id(packet_path)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = ROOT / "logs" / "harness_runs" / f"{timestamp}-{task_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    write_github_output(args.github_output, run_dir, task_id)

    python_exe = sys.executable
    preflight_code = run([python_exe, str(HARNESS_CLI), "preflight", str(packet_path), "--run-dir", str(run_dir)])
    verify_code = 0
    if preflight_code == 0:
        verify_code = run([python_exe, str(HARNESS_CLI), "verify", str(packet_path), "--run-dir", str(run_dir)])
    bundle_code = run([python_exe, str(HARNESS_CLI), "bundle", str(packet_path), "--run-dir", str(run_dir)])
    score_code = 0
    if args.score:
        score_code = run([python_exe, str(HARNESS_CLI), "score", "--run-dir", str(run_dir)])

    print(run_dir.relative_to(ROOT).as_posix())
    return max(preflight_code, verify_code, bundle_code, score_code)


if __name__ == "__main__":
    raise SystemExit(main())
