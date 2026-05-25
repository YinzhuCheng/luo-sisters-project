# Browser Automation

This project uses Playwright for browser automation and visual smoke checks.

## Installed Runtime

- Python package: `playwright==1.60.0`
- Installed browser: Chromium
- Runtime used in this workspace:
  `C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

## Install Or Repair

Use the bundled Python runtime:

```bash
C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pip install -r requirements-browser.txt
C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m playwright install chromium
```

## Quick Smoke Check

```bash
C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe tools/browser_smoke_check.py index.html
```

The script accepts a local HTML path or a URL and writes a full-page screenshot to `logs/browser-smoke.png` by default.

## Usage Rules

- Use browser automation after meaningful frontend changes.
- Prefer Chromium for routine local checks.
- Keep the first pass lightweight: load one page, confirm layout, then follow links as needed.
- Use `skills/project-doc-governance/scripts/read_html_doc.py` before browser inspection when the task is document structure rather than visual QA.
