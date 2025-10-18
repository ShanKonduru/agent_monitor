@echo off
:: PostgreSQL Production Deployment - For when network connectivity is available
echo ========================================
echo  PostgreSQL Production Deployment  
echo ========================================
echo.

echo Testing Docker Hub connectivity...
docker pull postgres:15-alpine --quiet >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Network connectivity OK - Using PostgreSQL
    docker rmi postgres:15-alpine >nul 2>&1
    goto :postgresql_deployment
) else (
    echo ⚠️  Network issues - Using persistent SQLite
    goto :sqlite_deployment
)

:postgresql_deployment
echo.
echo Enabling PostgreSQL configuration...

:: Create PostgreSQL version of docker-compose
copy docker-compose.production.yml docker-compose.postgresql.yml >nul

:: Enable PostgreSQL services (uncomment)
powershell -Command "(Get-Content docker-compose.postgresql.yml) -replace '#   postgres:', '  postgres:' -replace '#     image:', '    image:' -replace '#     container_name:', '    container_name:' -replace '#     environment:', '    environment:' -replace '#       POSTGRES', '      POSTGRES' -replace '#     volumes:', '    volumes:' -replace '#     networks:', '    networks:' -replace '#     healthcheck:', '    healthcheck:' -replace '#     restart:', '    restart:' | Set-Content docker-compose.postgresql.yml"

:: Update DATABASE_URL for PostgreSQL
powershell -Command "(Get-Content docker-compose.postgresql.yml) -replace 'sqlite\+aiosqlite:///\./data/agent_monitor\.db', 'postgresql+asyncpg://monitor_user:secure_monitor_pass@postgres:5432/agent_monitor' | Set-Content docker-compose.postgresql.yml"

echo Deploying with PostgreSQL...
docker-compose -f docker-compose.postgresql.yml up -d

if %errorlevel% equ 0 (
    echo ✅ PostgreSQL deployment successful!
    goto :show_status
) else (
    echo ❌ PostgreSQL deployment failed, falling back to SQLite
    goto :sqlite_deployment
)

:sqlite_deployment
echo.
echo Deploying with persistent SQLite...
docker-compose -f docker-compose.production.yml up -d

if %errorlevel% equ 0 (
    echo ✅ SQLite deployment successful!
    goto :show_status
) else (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

:show_status
echo.
echo Waiting for services to start...
timeout /t 45 /nobreak >nul

echo.
echo Container status:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ========================================
echo  🐘 DATABASE READY!
echo ========================================
echo.
if exist docker-compose.postgresql.yml (
    echo Database: PostgreSQL (Unified, Persistent)
    echo Location: postgres:5432/agent_monitor
    echo Credentials: monitor_user / secure_monitor_pass
) else (
    echo Database: SQLite (Persistent)
    echo Location: Docker volume 'agent_data'
    echo File: /app/data/agent_monitor.db
)
echo.
echo Services:
echo   📊 Monitor Dashboard: http://localhost:8000
echo   🤖 Container Agents: 5 production agents
echo   🗄️  Database: Persistent storage enabled
echo.
echo Opening dashboard...
start http://localhost:8000/

echo.
echo Management Commands:
if exist docker-compose.postgresql.yml (
    echo   Stop:     docker-compose -f docker-compose.postgresql.yml down
    echo   Logs:     docker-compose -f docker-compose.postgresql.yml logs
    echo   DB Shell: docker exec -it agent_monitor_postgres psql -U monitor_user -d agent_monitor
) else (
    echo   Stop:     docker-compose -f docker-compose.production.yml down
    echo   Logs:     docker-compose -f docker-compose.production.yml logs
    echo   DB Check: docker exec agent_monitor-monitor-dashboard-1 ls -la /app/data/
)
echo.
pause