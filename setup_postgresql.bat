@echo off
:: PostgreSQL Setup Helper
echo ========================================
echo  PostgreSQL Connection Setup
echo ========================================
echo.

if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env >nul
    echo ✅ .env file created
    echo.
    echo ⚠️  IMPORTANT: Please edit .env file and set your PostgreSQL password
    echo    File location: %CD%\.env
    echo    Required: Set POSTGRES_PASSWORD=your_actual_password
    echo.
    echo After setting your password, run:
    echo   docker-compose -f docker-compose.host-db.yml down
    echo   docker-compose -f docker-compose.host-db.yml up -d
    echo.
    pause
    exit /b 0
)

echo Reading PostgreSQL configuration from .env...
for /f "tokens=1,2 delims==" %%a in ('type .env ^| findstr /v "#"') do (
    if "%%a"=="POSTGRES_USER" set PG_USER=%%b
    if "%%a"=="POSTGRES_PASSWORD" set PG_PASSWORD=%%b
    if "%%a"=="POSTGRES_DB" set PG_DB=%%b
)

if "%PG_PASSWORD%"=="your_postgresql_password_here" (
    echo ❌ Please edit .env file and set your actual PostgreSQL password
    echo    File: %CD%\.env
    echo    Change: POSTGRES_PASSWORD=your_postgresql_password_here
    echo    To:     POSTGRES_PASSWORD=your_actual_password
    pause
    exit /b 1
)

echo Testing PostgreSQL connection...
docker exec agent_monitor-monitor-dashboard-1 python -c "import asyncio, asyncpg; asyncio.run(asyncpg.connect('postgresql://%PG_USER%:%PG_PASSWORD%@host.docker.internal:5432/postgres'))" 2>nul
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL connection successful!
) else (
    echo ❌ PostgreSQL connection failed
    echo   Please check your credentials in .env file
    echo   User: %PG_USER%
    echo   Database: %PG_DB%
    pause
    exit /b 1
)

echo.
echo Creating agent_monitor database if it doesn't exist...
docker exec agent_monitor-monitor-dashboard-1 python -c "import asyncio, asyncpg; async def create_db(): conn = await asyncpg.connect('postgresql://%PG_USER%:%PG_PASSWORD%@host.docker.internal:5432/postgres'); await conn.execute('CREATE DATABASE agent_monitor'); await conn.close(); asyncio.run(create_db())" 2>nul

echo.
echo Restarting containers with correct credentials...
docker-compose -f docker-compose.host-db.yml down
timeout /t 2 /nobreak >nul
docker-compose -f docker-compose.host-db.yml up -d

echo.
echo ✅ Setup complete! PostgreSQL should now be connected.
pause