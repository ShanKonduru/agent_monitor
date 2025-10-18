@echo off
echo Starting Agent Monitor Framework...
echo.
echo Activating virtual environment...
call .\.venv\Scripts\activate.bat

echo.
echo Starting server on http://0.0.0.0:8000...
echo Dashboard will be available at: http://localhost:8000/dashboard
echo API will be available at: http://localhost:8000/api/v1/agents
echo Press Ctrl+C to stop the server
echo.

REM Start the FastAPI server with uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Server stopped.
pause
