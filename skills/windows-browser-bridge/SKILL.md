---
name: windows-browser-bridge
description: Recover and use OpenClaw browser automation when the agent runs in WSL/Linux but must control a Windows Chrome/Edge window. Use when browser status shows Remote CDP unreachable, Browser Relay repeatedly fails, the user says the browser/plugin used to work before, or the task requires reconnecting OpenClaw to a Windows browser for real web actions like Outlook/GitHub/account pages.
---

# Windows Browser Bridge

Use this skill to reconnect OpenClaw running in WSL/Linux to a Windows browser instance.

## Goal

Create a browser window on Windows that OpenClaw can actually control from WSL, then verify control with the `browser` tool.

## Preferred path

Prefer direct remote-debugging CDP over the Browser Relay extension when WSL↔Windows networking is the problem.

Why:
- Relay often fails because loopback on Windows is not reachable from WSL.
- Direct CDP is easier to reason about and easier to re-check.

## Files used by this skill

- Launcher script: `scripts/start-openclaw-chrome.ps1`
- Troubleshooting notes: `references/troubleshooting.md`

Read the troubleshooting reference if any step below fails or if the browser still reports `cdpReady: false`.

## Workflow

1. Confirm current browser config/status.
   - Check `browser status`.
   - If it already shows `running: true` and `cdpReady: true`, stop and use the browser.

2. Make OpenClaw point at the Windows-host-reachable CDP URL.
   - Prefer the Windows host IP visible from WSL, not `127.0.0.1`.
   - In this environment, the working pattern was a Windows host address like `10.x.x.x:9333`.

3. Launch a dedicated Windows Chrome window with remote debugging.
   - Use `scripts/start-openclaw-chrome.ps1`.
   - The script must include:
     - `--remote-debugging-port=9333`
     - `--remote-debugging-address=0.0.0.0`
     - a dedicated `--user-data-dir`
   - Have the user keep that special window open.

4. Verify on Windows that Chrome was really launched with the expected flags.
   - Ask the user to open `chrome://version` in that special window.
   - Confirm the command line contains the remote debugging flags.

5. Bridge Windows loopback to an address WSL can reach.
   - If Chrome still only listens on `127.0.0.1:9333`, instruct the user to create `netsh interface portproxy` rules from an admin PowerShell.
   - Also add a Windows firewall allow rule for TCP 9333 when needed.

6. Update OpenClaw config to the reachable CDP URL and restart the gateway.
   - Re-check `browser status` until it shows `cdpReady: true`.

7. Prove control.
   - Use `browser tabs`.
   - Open or focus the target page.
   - Only then begin the actual user task.

## Minimal success criteria

Treat the bridge as working only when all are true:
- `browser status` shows `running: true`
- `browser status` shows `cdpReady: true`
- `browser tabs` returns real tabs from the Windows browser

## User instructions to give verbatim when needed

### Launch the dedicated browser

Tell the user to run the PowerShell script on Windows and keep the opened window alive.

### Verify Chrome flags

Tell the user to check `chrome://version` and confirm:
- `--remote-debugging-port=9333`
- `--remote-debugging-address=0.0.0.0`

### Add portproxy rules

If WSL still cannot reach the browser, tell the user to run these from **Administrator PowerShell**:

```powershell
netsh interface portproxy delete v4tov4 listenaddress=10.255.255.254 listenport=9333
netsh interface portproxy add v4tov4 listenaddress=10.255.255.254 listenport=9333 connectaddress=127.0.0.1 connectport=9333
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=9333 connectaddress=127.0.0.1 connectport=9333
netsh advfirewall firewall add rule name="OpenClaw Chrome DevTools 9333" dir=in action=allow protocol=TCP localport=9333
```

Adjust the listen address if the Windows-side reachable host IP differs.

## Important cautions

- Do not assume Browser Relay token issues are the real problem. First verify network reachability.
- Do not keep retrying `browser` blindly after a timeout. Inspect status and transport first.
- Use a dedicated browser profile/window for automation; avoid the user’s normal browser profile when possible.
- If a page login completes in a second tab/pop-up, inspect all tabs again before assuming failure.

## After recovery

If this workflow required changes to scripts or config, document the working combination in memory and keep the launcher script in sync with the proven flags.
