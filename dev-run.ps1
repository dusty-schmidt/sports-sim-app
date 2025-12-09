# PowerShell Dev Run Script

Write-Host "Starting Development Environment (No Docker)..." -ForegroundColor Green

# 1. Setup Backend Environment Variables
$env:USE_SQLITE = "True"
$env:POSTGRES_SERVER = "none" # Dummy value to satisfy validation if unused
$env:POSTGRES_USER = "none"
$env:SECRET_KEY = "dev_secret_key_unsafe"
$env:FIRST_SUPERUSER = "admin@example.com"
$env:FIRST_SUPERUSER_PASSWORD = "admin12345"

Set-Location "backend"

# 2. Install Backend Dependencies
Write-Host "Syncing Backend (uv)..." -ForegroundColor Cyan
uv sync

# 3. Initialize Database (Seeds)
Write-Host "Initializing Database..." -ForegroundColor Cyan
uv run python -m app.initial_data

# 4. Start Backend (New Window)
Write-Host "Starting Backend Server..." -ForegroundColor Cyan
Start-Process -FilePath "uv" -ArgumentList "run", "fastapi", "dev", "app/main.py" -NoNewWindow:$false -WorkingDirectory "$PWD"

Set-Location ".."

# 5. Start Frontend (Current Window or New Window)
Set-Location "frontend"
Write-Host "Starting Frontend..." -ForegroundColor Cyan
Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev" -NoNewWindow:$false -WorkingDirectory "$PWD"

Write-Host "Backend and Frontend launched in separate windows." -ForegroundColor Green
Set-Location ".."
