# Start Device Mesh coordinator from Windows PowerShell.
# Requires Docker Desktop with Linux containers + WSL2 enabled.
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker Desktop not found. Install Docker Desktop and enable WSL2 Linux containers."
}
docker info *> $null
if ($LASTEXITCODE -ne 0) { throw "Docker daemon not running. Start Docker Desktop." }
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env. Configure EDGE_API_KEY and each NODE_* URL and secret before starting."
    exit 0
}
if ((Get-Content ".env" -Raw) -match "replace_with_") {
    throw "Edit .env with unique strong API keys before starting."
}
docker compose up --build -d
if ($LASTEXITCODE -ne 0) { throw "Docker Compose failed." }
Write-Host "Device Mesh gateway running at http://127.0.0.1:8787/health"
