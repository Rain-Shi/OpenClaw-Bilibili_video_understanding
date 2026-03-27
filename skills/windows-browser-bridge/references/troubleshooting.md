# Troubleshooting

## Symptom map

### `browser status` shows `Remote CDP ... not reachable`
Likely causes:
- Windows Chrome was not launched with remote debugging
- Chrome was launched with the right flags but only listens on Windows loopback
- WSL cannot reach the chosen Windows host IP/port
- Windows firewall is blocking TCP 9333

### Browser Relay says unreachable
Likely causes:
- Relay/loopback confusion between Windows and WSL
- Wrong assumption that gateway token is the main issue
- Extension is pointed at a service Windows can reach but WSL-hosted OpenClaw still cannot use for CDP

## Known-good recovery sequence from this workspace

1. Launch dedicated Chrome from PowerShell with:
   - `--remote-debugging-port=9333`
   - `--remote-debugging-address=0.0.0.0`
   - dedicated user-data-dir
2. Check `chrome://version`
3. On Windows, confirm local DevTools works:
   - `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:9333/json/version`
4. Add `portproxy` rules in admin PowerShell
5. Add firewall allow rule for TCP 9333
6. Point OpenClaw `browser.cdpUrl` to the Windows host IP reachable from WSL
7. Restart gateway
8. Verify with `browser status` and `browser tabs`

## Useful checks

### From WSL/Linux side
- `openclaw gateway status`
- `browser status`
- `browser tabs`
- `curl http://<windows-host-ip>:9333/json/version`

### From Windows side
- `chrome://version`
- `netstat -ano | findstr 9333`
- `netsh interface portproxy show all`
- `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:9333/json/version`

## Interpretation notes

### If Windows local request works but WSL curl fails
This is almost always network bridging or firewall, not login state.

### If Outlook opens but interactive state looks wrong
Inspect all tabs. Microsoft login often finishes in a separate tab while the original tab remains on the marketing page.

### If one login tab is stuck on loading/spinner
Check sibling tabs before retrying. Another tab may already hold the live mailbox session.
