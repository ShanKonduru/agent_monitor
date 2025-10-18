@echo off
:: Deploy using manually created Alpine image
echo ========================================
echo  Alpine Container Deployment
echo ========================================
echo.

echo Checking Docker and Alpine image...
docker images alpine:latest
if %errorlevel% neq 0 (
    echo ❌ Alpine image not found
    echo Please make sure you have the alpine:latest image
    pause
    exit /b 1
) else (
    echo ✅ Alpine image found
)

echo.
echo Deploying containers using Alpine image...
docker-compose -f docker-compose.alpine.yml up -d

if %errorlevel% equ 0 (
    echo ✅ Containers deployed successfully!
) else (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

echo.
echo Waiting for containers to start...
timeout /t 30 /nobreak >nul

echo.
echo Container status:
docker-compose -f docker-compose.alpine.yml ps

echo.
echo Services:
echo   📊 Dashboard: http://localhost:8000
echo   🐳 Containers: 3 Alpine agent containers
echo.
echo Opening dashboard...
start http://localhost:8000/

echo.
echo ========================================
echo  Deployment Complete!
echo ========================================
echo.
echo Your containerized agents are running!
echo.
echo To stop: docker-compose -f docker-compose.alpine.yml down
echo To view logs: docker-compose -f docker-compose.alpine.yml logs
echo.
pause