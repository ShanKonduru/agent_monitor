@echo off
:: Start Agent Monitor in Docker Demo Mode
echo Starting Agent Monitor in Docker Demo Mode...

:: Copy docker env file
copy .env.docker .env.temp

:: Activate virtual environment
call .venv\Scripts\activate

:: Set environment
set PYTHONPATH=%CD%
set DATABASE_URL=sqlite:///./agent_monitor.db

:: Start server
echo Starting server on http://localhost:8000
python main.py

:: Cleanup
if exist .env.temp del .env.temp