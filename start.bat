@echo off
echo ===================================================
echo AI Inventory Management System - Startup Script
echo ===================================================

echo.
echo [1/4] Checking python dependencies...
pip install -r backend/requirements.txt

echo.
echo [2/4] Seeding database...
cd backend
python -m scripts.seed_data
cd ..

echo.
echo [3/4] Starting Backend Server...
start cmd /k "cd backend && uvicorn app.main:app --reload"

echo.
echo [4/4] Starting Frontend Server...
echo NOTE: Requires Node.js installed. If not, install from nodejs.org
cd frontend
if exist node_modules (
    npm run dev
) else (
    echo Installing frontend dependencies...
    call npm install
    npm run dev
)

echo.
echo Application started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo Docs: http://localhost:8000/docs
pause
