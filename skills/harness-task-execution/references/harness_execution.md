# Harness Task Execution Reference

## Use This Skill For

- packet preflight before execution
- verify-stage check routing
- bundle and score stages
- local run-bundle reading
- CI run triage and warn-then-gate interpretation

## Primary Files

- `tools/harness_cli.py`
- `tools/run_harness_task.py`
- `tools/harness_warn_then_gate.py`
- `harness/check_profiles/*.json`
- `harness/tasks/*.json`
- `harness/policies/warn_then_gate.json`
- `docs/harness_ci.md`

## Stage Order

1. `preflight`
2. `verify`
3. `bundle`
4. `score` when the task or maintenance flow needs governance status

Use one explicit run directory when comparing retries or keeping evidence together.

## Reading Run Artifacts

Read in this order:

1. `verify.json` or `report.json`
2. `summary.md`
3. per-check JSON payloads
4. per-check stdout and stderr files

## Packet Categories

- `docs`: documentation and mirror integrity
- `page`: generated HTML, builds, and browser smoke checks
- `asset`: character boundary, registry, and transparent-output validation
- `maintenance`: score and repeated-issue convergence work

## Warn-Then-Gate

- structural corruption should fail immediately
- missing coverage may begin as warnings
- repeated warnings should be promoted through policy and checks over time

Use `docs/harness_ci.md` whenever the task is about GitHub Actions or uploaded run artifacts rather than local-only execution.
