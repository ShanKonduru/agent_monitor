@echo off
:: Deploy Agent Monitor Framework in Docker Desktop
:: This script handles network connectivity issues gracefully

echo ========================================
echo  Agent Monitor - Docker Deployment
echo ========================================
echo.

:: Create data directory
if not exist "data" mkdir data

echo Step 1: Testing Docker connectivity...
echo.

:: Test if we can pull any image
echo Testing Docker Hub connectivity with minimal image...
docker pull hello-world:latest >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Hub connectivity works!
    goto :build_with_registry
) else (
    echo ⚠️  Docker Hub connectivity issues detected
    echo Trying alternative approaches...
    goto :build_local
)

:: Function definitions
goto :main

:print_header
echo ================================
echo   Agent Monitor - Docker Deploy
echo ================================
echo Project Root: %PROJECT_ROOT%
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
echo     test            Test the deployment
echo     help            Show this help message
echo.
echo Examples:
echo     %~nx0 dev                          # Start development environment
echo     %~nx0 prod                         # Start production with full agent fleet
echo     %~nx0 test                         # Test current deployment
echo     %~nx0 logs monitor                 # Show logs for monitor service
echo     %~nx0 status                       # Show all service status
echo     %~nx0 clean                        # Clean everything
echo.
goto :eof

:test_deployment
call :print_info "Testing deployment..."

:: Test if monitor service is running
curl -s http://localhost:8000/api/v1/system/status >nul 2>nul
if %errorlevel% equ 0 (
    call :print_success "Monitor service is running on port 8000"
    call :print_info "Testing API endpoints..."
    
    :: Test agents endpoint
    curl -s http://localhost:8000/api/v1/agents >nul 2>nul
    if %errorlevel% equ 0 (
        call :print_success "Agents API is responding"
    ) else (
        call :print_warning "Agents API not responding"
    )
    
    call :print_info "Access points:"
    call :print_info "  - Dashboard: http://localhost:8000/"
    call :print_info "  - API Docs: http://localhost:8000/docs"
    call :print_info "  - Health: http://localhost:8000/api/v1/system/status"
) else (
    call :print_warning "Monitor service not responding on port 8000"
    call :print_info "Try starting with: %~nx0 dev"
)

:: Check for production setup (nginx)
curl -s http://localhost/ >nul 2>nul
if %errorlevel% equ 0 (
    call :print_success "Production nginx is running on port 80"
    call :print_info "Production access: http://localhost/"
)

goto :eof

:start_development
call :print_info "Starting development environment..."

:: Create a simple docker-compose.yml for development
call :create_dev_compose

docker-compose up -d --build

if %errorlevel% equ 0 (
    call :print_success "Development environment started!"
    call :print_info "Services:"
    call :print_info "  - Monitor API: http://localhost:8000"
    call :print_info "  - Dashboard: http://localhost:8000/"
    call :print_info ""
    call :print_warning "Wait 30 seconds for services to initialize..."
    timeout /t 30 /nobreak >nul
    call :test_deployment
) else (
    call :print_error "Failed to start development environment"
)
goto :eof

:create_dev_compose
call :print_info "Creating development compose file..."

(
echo version: '3.8'
echo.
echo services:
echo   # Main monitoring service
echo   monitor:
echo     build:
echo       context: .
echo       dockerfile: docker/Dockerfile
echo     ports:
echo       - "8000:8000"
echo     environment:
echo       - DATABASE_URL=postgresql://monitor:password@postgres:5432/agent_monitor
echo       - LOG_LEVEL=INFO
echo     depends_on:
echo       postgres:
echo         condition: service_healthy
echo     restart: unless-stopped
echo     healthcheck:
echo       test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/system/status"]
echo       interval: 30s
echo       timeout: 10s
echo       retries: 3
echo       start_period: 40s
echo.
echo   # PostgreSQL database
echo   postgres:
echo     image: postgres:15-alpine
echo     environment:
echo       POSTGRES_DB: agent_monitor
echo       POSTGRES_USER: monitor
echo       POSTGRES_PASSWORD: password
echo     volumes:
echo       - postgres_data:/var/lib/postgresql/data
echo     ports:
echo       - "5432:5432"
echo     restart: unless-stopped
echo     healthcheck:
echo       test: ["CMD-SHELL", "pg_isready -U monitor -d agent_monitor"]
echo       interval: 10s
echo       timeout: 5s
echo       retries: 5
echo.
echo   # Example agent
echo   example-agent:
echo     build:
echo       context: .
echo       dockerfile: docker/agent.Dockerfile
echo     environment:
echo       - MONITOR_URL=http://monitor:8000
echo       - AGENT_NAME=Development Agent
echo       - AGENT_TYPE=llm_agent
echo       - WORKLOAD_TYPE=standard
echo       - AGENT_VERSION=1.0.0
echo       - AGENT_ENVIRONMENT=development
echo       - LOG_LEVEL=INFO
echo     command: ["python", "example_agent.py"]
echo     depends_on:
echo       - monitor
echo     restart: unless-stopped
echo.
echo volumes:
echo   postgres_data:
echo     driver: local
) > docker-compose.yml

call :print_success "Development compose file created"
goto :eof

:start_production
call :print_info "Starting production environment with agent fleet..."

if not exist "docker\docker-compose-production.yml" (
    call :print_error "Production compose file not found: docker\docker-compose-production.yml"
    exit /b 1
)

docker-compose -f docker\docker-compose-production.yml up -d --build

if %errorlevel% equ 0 (
    call :print_success "Production environment started!"
    call :print_info "Services:"
    call :print_info "  - Monitor Dashboard: http://localhost/ (via nginx)"
    call :print_info "  - Direct API: http://localhost:8000"
    call :print_info "  - Grafana: http://localhost:3000 (admin/admin)"
    call :print_info ""
    call :print_info "Agents deployed:"
    call :print_info "  - 2x LLM Agents (GPT-4, Claude)"
    call :print_info "  - 2x API Agents (Gateway, Auth Service)"
    call :print_info "  - 2x Data Agents (ETL Pipeline, Analytics)"
    call :print_info "  - 1x Monitor Agent (System Monitor)"
    call :print_info ""
    call :print_warning "Wait 60 seconds for all agents to register..."
    timeout /t 60 /nobreak >nul
    call :test_deployment
) else (
    call :print_error "Failed to start production environment"
)
goto :eof

:stop_all
call :print_info "Stopping all containers..."

docker-compose down 2>nul
docker-compose -f docker\docker-compose-production.yml down 2>nul

call :print_success "All containers stopped"
goto :eof

:clean_all
call :print_warning "This will remove all containers, networks, and volumes!"
set /p confirm="Are you sure? (y/N): "

if /i "%confirm%"=="y" (
    call :print_info "Cleaning up..."
    
    docker-compose down -v --remove-orphans 2>nul
    docker-compose -f docker\docker-compose-production.yml down -v --remove-orphans 2>nul
    
    :: Clean up development compose file
    if exist "docker-compose.yml" del docker-compose.yml
    
    call :print_success "Cleanup complete"
) else (
    call :print_info "Cleanup cancelled"
)
goto :eof

:show_logs
if "%~1"=="" (
    call :print_info "Available services:"
    docker-compose ps --services 2>nul || docker-compose -f docker\docker-compose-production.yml ps --services 2>nul || call :print_error "No running services found"
) else (
    call :print_info "Showing logs for %~1..."
    
    :: Try development first, then production
    docker-compose ps | findstr "%~1" >nul 2>nul
    if !errorlevel! equ 0 (
        docker-compose logs -f "%~1"
    ) else (
        docker-compose -f docker\docker-compose-production.yml ps | findstr "%~1" >nul 2>nul
        if !errorlevel! equ 0 (
            docker-compose -f docker\docker-compose-production.yml logs -f "%~1"
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

:: Check development first
if exist "docker-compose.yml" (
    docker-compose ps 2>nul | findstr "Up" >nul 2>nul
    if !errorlevel! equ 0 (
        call :print_info "Development Environment:"
        docker-compose ps
        echo.
    )
)

:: Check production
if exist "docker\docker-compose-production.yml" (
    docker-compose -f docker\docker-compose-production.yml ps 2>nul | findstr "Up" >nul 2>nul
    if !errorlevel! equ 0 (
        call :print_info "Production Environment:"
        docker-compose -f docker\docker-compose-production.yml ps
        echo.
    )
)

:: If nothing is running
docker ps | findstr "agent_monitor\|postgres\|redis\|influxdb\|grafana\|nginx" >nul 2>nul
if !errorlevel! neq 0 (
    call :print_warning "No agent monitor services are currently running"
    call :print_info "Use '%~nx0 dev' or '%~nx0 prod' to start services"
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
if "%~1"=="test" set "command=test"
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
) else if "%command%"=="test" (
    call :test_deployment
) else (
    call :show_help
)