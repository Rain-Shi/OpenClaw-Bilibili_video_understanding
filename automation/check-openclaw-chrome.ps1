$Port = 9333

Write-Host "Checking Chrome CDP on port $Port..."

try {
  $json = Invoke-WebRequest "http://127.0.0.1:$Port/json/list" -UseBasicParsing | Select-Object -ExpandProperty Content
  Write-Host "CDP reachable on 127.0.0.1:$Port"
  Write-Host $json
} catch {
  Write-Error "CDP not reachable on 127.0.0.1:$Port"
  exit 1
}
