$ChromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$UserDataDir = Join-Path $env:USERPROFILE "openclaw-chrome-automation"
$Port = 9333

if (-not (Test-Path $ChromePath)) {
  Write-Error "Chrome not found at $ChromePath"
  exit 1
}

New-Item -ItemType Directory -Force -Path $UserDataDir | Out-Null

Start-Process -FilePath $ChromePath -ArgumentList @(
  "--remote-debugging-port=$Port",
  "--remote-debugging-address=0.0.0.0",
  "--user-data-dir=$UserDataDir",
  "--no-first-run",
  "--no-default-browser-check",
  "about:blank"
)

Write-Host "Started OpenClaw automation Chrome on port $Port"
Write-Host "User data dir: $UserDataDir"
Write-Host "Next: open the target site in that Chrome window and keep it open."
