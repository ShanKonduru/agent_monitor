@echo off
echo Testing postgres image detection without output redirection...

echo Step 1: Check if image exists with full output
docker image inspect postgres:15
echo Inspect exit code: %errorlevel%

echo.
echo Step 2: List all postgres images
docker images postgres

pause