@echo off
:: Docker Cleanup Script - Clean up build cache and failed builds

echo ========================================
echo  Docker Build Cleanup Tool
echo ========================================
echo.

echo Current Docker usage:
docker system df
echo.

echo ========================================
echo  Cleanup Options
echo ========================================
echo.
echo 1. Clean build cache only (recommended)
echo 2. Clean all unused data (images, containers, networks)
echo 3. Nuclear option - clean everything
echo 4. Just show what would be cleaned
echo 5. Exit
echo.
set /p choice="Choose option (1-5): "

if "%choice%"=="1" goto :clean_cache
if "%choice%"=="2" goto :clean_unused
if "%choice%"=="3" goto :clean_all
if "%choice%"=="4" goto :show_cleanup
if "%choice%"=="5" goto :exit
goto :invalid

:clean_cache
echo.
echo Cleaning build cache...
docker builder prune -f
echo ✅ Build cache cleaned
goto :show_after

:clean_unused
echo.
echo Cleaning unused data (images, containers, networks)...
docker system prune -f
echo ✅ Unused data cleaned
goto :show_after

:clean_all
echo.
echo ⚠️  WARNING: This will remove ALL unused data including volumes!
set /p confirm="Are you sure? (y/N): "
if /i "%confirm%"=="y" (
    docker system prune -a -f --volumes
    echo ✅ Everything cleaned
) else (
    echo Cleanup cancelled
)
goto :show_after

:show_cleanup
echo.
echo What would be cleaned:
echo.
echo Build cache:
docker builder prune --dry-run
echo.
echo System cleanup:
docker system prune --dry-run
goto :end

:show_after
echo.
echo After cleanup:
docker system df
goto :end

:invalid
echo Invalid choice. Please select 1-5.
goto :end

:exit
echo Cleanup cancelled.

:end
echo.
echo Press any key to continue...
pause >nul