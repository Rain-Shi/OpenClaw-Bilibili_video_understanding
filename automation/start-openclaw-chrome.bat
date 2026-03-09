@echo off
set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
set USER_DATA_DIR=%USERPROFILE%\openclaw-chrome-automation
set PORT=9333

if not exist "%CHROME_PATH%" (
  echo Chrome not found at %CHROME_PATH%
  exit /b 1
)

if not exist "%USER_DATA_DIR%" mkdir "%USER_DATA_DIR%"

start "" "%CHROME_PATH%" --remote-debugging-port=%PORT% --user-data-dir="%USER_DATA_DIR%" --no-first-run --no-default-browser-check about:blank

echo Started OpenClaw automation Chrome on port %PORT%
echo User data dir: %USER_DATA_DIR%
