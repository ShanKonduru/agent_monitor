@echo off
echo Testing postgres image detection...

echo Step 1: Attempt pull (expected to fail)
docker pull postgres:15 >nul 2>&1
echo Pull exit code: %errorlevel%

if %errorlevel% neq 0 (
    echo Step 2: Check local image
    docker image inspect postgres:15 >nul 2>&1
    echo Inspect exit code: %errorlevel%
    
    if %errorlevel% neq 0 (
        echo ERROR: Image not found locally
    ) else (
        echo SUCCESS: Image found locally
    )
) else (
    echo SUCCESS: Image pulled from remote
)

pause