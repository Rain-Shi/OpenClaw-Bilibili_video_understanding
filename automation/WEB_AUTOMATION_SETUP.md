# OpenClaw Web Automation Setup

## Goal
Use a dedicated Chrome instance for OpenClaw web automation.

## Windows launch
Use either script in this folder:

- `start-openclaw-chrome.ps1`
- `start-openclaw-chrome.bat`

Both launch Chrome with:
- remote debugging port `9333`
- dedicated user data dir `%USERPROFILE%\\openclaw-chrome-automation`
- a clean `about:blank` start page

## Recommended workflow
1. Start the dedicated automation Chrome.
2. Open and log into the target site in that Chrome window.
3. Tell OpenClaw to begin.
4. Let OpenClaw operate only in that browser.

## Notes
- Keep this browser separate from daily browsing.
- Prefer Chrome for automation on this machine; Edge was polluted by a Lenovo Vantage widget in CDP.
- For sensitive actions like sending email or bulk deletion, confirm before execution.
