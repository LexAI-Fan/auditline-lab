@'
# PowerShell one-click runner from the project root
param(
  [double]$Scale = 1.0
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}
& .\.venv\Scripts\python.exe -V | Write-Host
$py = ".\.venv\Scripts\python.exe"

# Optional: use a stronger signing key for the packet
# $env:INCIDENT_HMAC_KEY = "replace-with-your-secret"

& $py .\src\simulate_egress.py --scale $Scale
& $py .\src\detect_exfil.py
& $py .\src\provenance.py
& $py .\src\build_incident_packet.py
& $py .\src\assess_incident.py
& $py .\src\charts.py

Write-Host "`nAll done. Outputs & charts in: $ROOT\out" -ForegroundColor Green
'@ | Set-Content -Encoding UTF8 -NoNewline .\run_all.ps1
