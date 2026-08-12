#Requires -Version 5.1
param(
  [switch]$SkipBuild
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$Dist = Join-Path $Root "web\dist\index.html"

if (-not (Test-Path $VenvPython)) {
  Write-Error "Missing .venv. Create it, then: .\.venv\Scripts\python -m pip install -r requirements.txt"
  exit 1
}

Write-Host "Checking Python packages..." -ForegroundColor Cyan
& $VenvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
  Write-Error "pip install failed"
  exit 1
}

$needBuild = -not (Test-Path $Dist)
if (-not $SkipBuild) {
  $needBuild = $true
}

if ($needBuild) {
  Write-Host "Building React app..." -ForegroundColor Cyan
  Push-Location (Join-Path $Root "web")
  npm run build
  $buildCode = $LASTEXITCODE
  Pop-Location
  if ($buildCode -ne 0) {
    Write-Error "Frontend build failed"
    exit 1
  }
}

Write-Host ""
Write-Host "MarketLens: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API docs:   http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

& $VenvPython -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
