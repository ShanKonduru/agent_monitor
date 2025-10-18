@echo off
:: Docker Network Diagnostic and Fix Script
:: This script attempts to resolve Docker Hub connectivity issues

echo ========================================
echo  Docker Network Diagnostic Tool
echo ========================================
echo.

:: Test basic connectivity
echo Testing network connectivity...
echo.

echo 1. Testing Docker daemon...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
) else (
    echo ✅ Docker daemon is running
)

echo.
echo 2. Testing internet connectivity...
ping -n 1 8.8.8.8 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ No internet connectivity
    echo Please check your network connection
    pause
    exit /b 1
) else (
    echo ✅ Internet connectivity OK
)

echo.
echo 3. Testing Docker Hub connectivity...
ping -n 1 registry-1.docker.io >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Cannot ping Docker Hub (might be blocked)
) else (
    echo ✅ Docker Hub is reachable
)

echo.
echo 4. Checking Docker configuration...
docker info | findstr "HTTP Proxy" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Proxy detected in Docker configuration
    echo Current proxy settings:
    docker info | findstr "Proxy"
    echo.
    echo Suggestions:
    echo - Try disabling proxy in Docker Desktop Settings
    echo - Or add Docker Hub to proxy bypass list
) else (
    echo ✅ No proxy configuration detected
)

echo.
echo ========================================
echo  Attempting Docker Fixes
echo ========================================
echo.

:: Try to pull a minimal image
echo 5. Testing image pull (this may take a moment)...
echo Attempting to pull busybox (very small image)...

timeout /t 2 /nobreak >nul

:: Try busybox (smaller than hello-world)
docker pull busybox:latest --quiet >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Successfully pulled busybox image!
    echo Docker connectivity is working
    echo.
    echo Now you can try building agent images...
) else (
    echo ❌ Failed to pull image
    echo.
    echo Possible solutions:
    echo 1. Check Docker Desktop proxy settings
    echo 2. Try different DNS settings: 8.8.8.8, 1.1.1.1
    echo 3. Restart Docker Desktop
    echo 4. Contact IT if on corporate network
)

echo.
echo Press any key to continue...
pause >nul