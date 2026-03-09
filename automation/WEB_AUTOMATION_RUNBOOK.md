# OpenClaw Web Automation Runbook

## Start
1. Run `start-openclaw-chrome.ps1` (or `.bat`) on Windows.
2. In that Chrome window, open the target site.
3. Log in if needed.
4. Ask OpenClaw to begin.

## Quick health check on Windows
Run:

```powershell
.\automation\check-openclaw-chrome.ps1
```

Expected result:
- CDP reachable on `127.0.0.1:9333`
- At least one page such as `about:blank`

## If OpenClaw cannot see tabs
1. Close all Chrome windows.
2. Re-run `start-openclaw-chrome.ps1`.
3. Re-run `check-openclaw-chrome.ps1`.
4. Open the target site only in that dedicated Chrome.

## Important rules
- Use the dedicated Chrome only for automation tasks.
- Do not mix daily browsing into that browser.
- For bulk deletion or sending external messages, confirm before execution.
