# PowerShell wrapper for Makefile commands
# Usage: .\make.ps1 <command> [args]

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Command,
    
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

switch ($Command) {
    "help" {
        Write-Host "Available commands:" -ForegroundColor Cyan
        Write-Host "  up              - Start all services in background" -ForegroundColor Green
        Write-Host "  down            - Stop all services" -ForegroundColor Green
        Write-Host "  restart         - Restart all services" -ForegroundColor Green
        Write-Host "  logs            - View logs for all services (follow)" -ForegroundColor Green
        Write-Host "  logs-backend    - View logs for backend only" -ForegroundColor Green
        Write-Host "  logs-worker     - View logs for celery worker" -ForegroundColor Green
        Write-Host "  test            - Run backend tests" -ForegroundColor Green
        Write-Host "  shell-backend   - Open bash shell in backend container" -ForegroundColor Green
        Write-Host "  shell-db        - Open PostgreSQL shell" -ForegroundColor Green
        Write-Host "  migrate         - Apply database migrations" -ForegroundColor Green
        Write-Host "  makemigrations  - Create new migration (usage: .\make.ps1 makemigrations 'message')" -ForegroundColor Green
        Write-Host "  seed            - Trigger odds fetch task to seed mock data" -ForegroundColor Green
        Write-Host "  sim             - Run a simulation manually (usage: .\make.ps1 sim <match_id> <n_sims>)" -ForegroundColor Green
    }
    "up" {
        docker compose up -d
    }
    "down" {
        docker compose down
    }
    "restart" {
        docker compose restart
    }
    "logs" {
        docker compose logs -f
    }
    "logs-backend" {
        docker compose logs -f backend
    }
    "logs-worker" {
        docker compose logs -f celeryworker
    }
    "test" {
        docker compose exec backend pytest
    }
    "shell-backend" {
        docker compose exec backend bash
    }
    "shell-db" {
        docker compose exec db psql -U postgres -d app
    }
    "migrate" {
        docker compose exec backend alembic upgrade head
    }
    "makemigrations" {
        if ($Args.Count -eq 0) {
            Write-Host "Error: Please provide a migration message" -ForegroundColor Red
            Write-Host "Usage: .\make.ps1 makemigrations 'your message here'" -ForegroundColor Yellow
            exit 1
        }
        $msg = $Args -join " "
        docker compose exec backend alembic revision --autogenerate -m "$msg"
    }
    "seed" {
        docker compose exec celeryworker celery -A app.worker call app.worker.run_odds_fetch
    }
    "sim" {
        if ($Args.Count -lt 2) {
            Write-Host "Error: Please provide match ID and number of simulations" -ForegroundColor Red
            Write-Host "Usage: .\make.ps1 sim <match_id> <n_sims>" -ForegroundColor Yellow
            exit 1
        }
        $id = $Args[0]
        $sims = $Args[1]
        docker compose exec celeryworker python -c "from app.worker import run_tennis_simulation; import structlog; run_tennis_simulation('$id', n_sims=$sims)"
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\make.ps1 help' to see available commands" -ForegroundColor Yellow
        exit 1
    }
}
