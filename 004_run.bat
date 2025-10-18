@echo off
setlocal enabledelayedexpansion

REM Agent Monitor Framework - Multi-purpose runner
REM Usage: 004_run.bat [command] [options]
REM Commands:
REM   server        - Start the FastAPI server (default)
REM   dashboard     - Open dashboard in browser
REM   register      - Register a new agent
REM   demo          - Run demo agent
REM   test          - Test API endpoints
REM   help          - Show this help

echo Agent Monitor Framework Runner
echo ==============================

REM Parse command line arguments
set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=server

REM Activate virtual environment
echo Activating virtual environment...
call .\.venv\Scripts\activate.bat
echo.

REM Execute based on command
if /i "%COMMAND%"=="server" goto :server
if /i "%COMMAND%"=="dashboard" goto :dashboard
if /i "%COMMAND%"=="register" goto :register
if /i "%COMMAND%"=="demo" goto :demo
if /i "%COMMAND%"=="test" goto :test
if /i "%COMMAND%"=="help" goto :help
if /i "%COMMAND%"=="--help" goto :help
if /i "%COMMAND%"=="-h" goto :help

echo Unknown command: %COMMAND%
echo Use "004_run.bat help" to see available commands
goto :end

:server
echo Starting FastAPI server...
echo Dashboard: http://localhost:8000/dashboard
echo API: http://localhost:8000/api/v1/agents
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
goto :end

:dashboard
echo Opening dashboard in browser...
start chrome http://localhost:8000/dashboard
echo Dashboard opened in Chrome
goto :end

:register
echo Registering new agent...
if [%2]==[] (
    echo Usage: 004_run.bat register [agent_name] [agent_type] [host] [environment]
    echo Example: 004_run.bat register "My Agent" API_AGENT localhost production
    goto :end
)
python scripts\register_agent.py %2 %3 %4 %5
goto :end

:demo
echo Running demo agent...
python demo_agent.py
goto :end

:test
echo Testing API endpoints...
python scripts\test_api.py
goto :end

:help
echo.
echo Agent Monitor Framework - Command Reference
echo ==========================================
echo.
echo Usage: 004_run.bat [command] [options]
echo.
echo Commands:
echo   server                              Start FastAPI server (default)
echo   dashboard                           Open dashboard in browser
echo   register [name] [type] [host] [env] Register new agent
echo   demo                                Run demo agent
echo   test                                Test API endpoints
echo   help                                Show this help
echo.
echo Examples:
echo   004_run.bat                         # Start server
echo   004_run.bat server                  # Start server explicitly
echo   004_run.bat dashboard               # Open dashboard
echo   004_run.bat register "Web API" API_AGENT localhost prod
echo   004_run.bat demo                    # Run demo agent
echo   004_run.bat test                    # Test API
echo.
echo Server URLs:
echo   Dashboard: http://localhost:8000/dashboard
echo   API: http://localhost:8000/api/v1/agents
echo.
goto :end

:end
if /i "%COMMAND%"=="server" (
    echo.
    echo Server stopped.
    pause
)
