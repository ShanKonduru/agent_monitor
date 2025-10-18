@echo off
:: Docker Production Deployment Script for Windows
:: This script helps deploy the Agent Monitor Framework in various scenarios

setlocal enabledelayedexpansion

:: Check if Docker is available
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not in PATH
    exit /b 1
)

:: Function definitions (using labels for Windows batch)
goto :main

:print_header
echo ================================
echo   Agent Monitor - Docker Deploy
echo ================================
echo.
goto :eof

:print_success
echo ✅ %~1
goto :eof

:print_warning
echo ⚠️  %~1
goto :eof

:print_error
echo ❌ %~1
goto :eof

:print_info
echo ℹ️  %~1
goto :eof

:show_help
echo Usage: %~nx0 [COMMAND] [OPTIONS]
echo.
echo Commands:
echo     dev             Start development environment (basic setup)
echo     prod            Start production environment (full agent fleet)
echo     stop            Stop all containers
echo     clean           Stop and remove all containers and volumes
echo     logs [service]  Show logs for specific service
echo     status          Show status of all services
echo     dashboard       Open monitoring dashboard
echo     help            Show this help message
echo.
echo Examples:
echo     %~nx0 dev                          # Start development environment
echo     %~nx0 prod                         # Start production with full agent fleet
echo     %~nx0 logs llm-agent-1             # Show logs for LLM agent
echo     %~nx0 status                       # Show all service status
echo     %~nx0 clean                        # Clean everything
echo.
goto :eof

:start_development
call :print_info "Starting development environment..."

docker-compose -f docker/docker-compose.yml up -d --build

call :print_success "Development environment started!"
call :print_info "Services:"
call :print_info "  - Monitor API: http://localhost:8000"
call :print_info "  - Dashboard: http://localhost:8000/dashboard"
call :print_info "  - PostgreSQL: localhost:5432"
call :print_info "  - Redis: localhost:6379"
call :print_info "  - InfluxDB: http://localhost:8086"
call :print_info "  - Grafana: http://localhost:3000 (admin/admin)"
goto :eof

:start_production
call :print_info "Starting production environment with agent fleet..."

:: Check if we need to build images
docker images | findstr "agent_monitor" >nul 2>nul
if %errorlevel% neq 0 (
    call :print_info "Building images..."
    docker-compose -f docker/docker-compose-production.yml build
)

docker-compose -f docker/docker-compose-production.yml up -d

call :print_success "Production environment started!"
call :print_info "Services:"
call :print_info "  - Monitor API: http://localhost:8000"
call :print_info "  - Dashboard: http://localhost:80 (via nginx)"
call :print_info "  - Grafana: http://localhost:80/grafana (admin/admin)"
call :print_info ""
call :print_info "Agents deployed:"
call :print_info "  - 2x LLM Agents (GPT-4, Claude)"
call :print_info "  - 2x API Agents (Gateway, Auth Service)"
call :print_info "  - 2x Data Agents (ETL Pipeline, Analytics)"
call :print_info "  - 1x Monitor Agent (System Monitor)"
call :print_info ""
call :print_warning "Wait 30-60 seconds for all agents to register..."
goto :eof

:stop_all
call :print_info "Stopping all containers..."

docker-compose -f docker/docker-compose.yml down 2>nul
docker-compose -f docker/docker-compose-production.yml down 2>nul

call :print_success "All containers stopped"
goto :eof

:clean_all
call :print_warning "This will remove all containers, networks, and volumes!"
set /p confirm="Are you sure? (y/N): "

if /i "%confirm%"=="y" (
    call :print_info "Cleaning up..."
    
    docker-compose -f docker/docker-compose.yml down -v --remove-orphans 2>nul
    docker-compose -f docker/docker-compose-production.yml down -v --remove-orphans 2>nul
    
    call :print_success "Cleanup complete"
) else (
    call :print_info "Cleanup cancelled"
)
goto :eof

:show_logs
if "%~1"=="" (
    call :print_info "Available services:"
    docker-compose -f docker/docker-compose-production.yml ps --services 2>nul || docker-compose -f docker/docker-compose.yml ps --services 2>nul || call :print_error "No running services found"
) else (
    call :print_info "Showing logs for %~1..."
    
    :: Try production first, then development
    docker-compose -f docker/docker-compose-production.yml ps | findstr "%~1" >nul 2>nul
    if !errorlevel! equ 0 (
        docker-compose -f docker/docker-compose-production.yml logs -f "%~1"
    ) else (
        docker-compose -f docker/docker-compose.yml ps | findstr "%~1" >nul 2>nul
        if !errorlevel! equ 0 (
            docker-compose -f docker/docker-compose.yml logs -f "%~1"
        ) else (
            call :print_error "Service '%~1' not found"
            exit /b 1
        )
    )
)
goto :eof

:show_status
call :print_info "Service Status:"
echo.

:: Check production first
docker-compose -f docker/docker-compose-production.yml ps 2>nul | findstr "Up" >nul 2>nul
if !errorlevel! equ 0 (
    call :print_info "Production Environment:"
    docker-compose -f docker/docker-compose-production.yml ps
) else (
    docker-compose -f docker/docker-compose.yml ps 2>nul | findstr "Up" >nul 2>nul
    if !errorlevel! equ 0 (
        call :print_info "Development Environment:"
        docker-compose -f docker/docker-compose.yml ps
    ) else (
        call :print_warning "No services are currently running"
        call :print_info "Use '%~nx0 dev' or '%~nx0 prod' to start services"
    )
)
goto :eof

:open_dashboard
call :print_info "Opening monitoring dashboard..."

:: Check which environment is running
docker-compose -f docker/docker-compose-production.yml ps 2>nul | findstr "nginx.*Up" >nul 2>nul
if !errorlevel! equ 0 (
    call :print_info "Production dashboard: http://localhost/"
    start http://localhost/
) else (
    docker-compose -f docker/docker-compose.yml ps 2>nul | findstr "monitor.*Up" >nul 2>nul
    if !errorlevel! equ 0 (
        call :print_info "Development dashboard: http://localhost:8000/"
        start http://localhost:8000/
    ) else (
        call :print_warning "No monitoring services are running"
        call :print_info "Start with '%~nx0 dev' or '%~nx0 prod' first"
    )
)
goto :eof

:: Main script logic
:main
call :print_header

if "%~1"=="" set "command=help"
if "%~1"=="dev" set "command=dev"
if "%~1"=="prod" set "command=prod"
if "%~1"=="stop" set "command=stop"
if "%~1"=="clean" set "command=clean"
if "%~1"=="logs" set "command=logs"
if "%~1"=="status" set "command=status"
if "%~1"=="dashboard" set "command=dashboard"
if "%~1"=="help" set "command=help"

if not defined command set "command=help"

if "%command%"=="dev" (
    call :start_development
) else if "%command%"=="prod" (
    call :start_production
) else if "%command%"=="stop" (
    call :stop_all
) else if "%command%"=="clean" (
    call :clean_all
) else if "%command%"=="logs" (
    call :show_logs "%~2"
) else if "%command%"=="status" (
    call :show_status
) else if "%command%"=="dashboard" (
    call :open_dashboard
) else (
    call :show_help
)