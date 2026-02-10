@echo off
echo ========================================
echo  PeatSense Backend - Quick Start
echo ========================================
echo.

echo [1/3] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.10+
    pause
    exit /b 1
)
echo.

echo [2/3] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo [3/3] Starting FastAPI Backend...
echo.
echo ========================================
echo  Server will start on http://127.0.0.1:8000
echo  API Docs at http://127.0.0.1:8000/docs
echo  Press Ctrl+C to stop
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Keep this window open
echo 2. Open a NEW terminal and run: streamlit run dashboard.py
echo 3. Configure and power on your ESP32
echo 4. Ensure PostgreSQL and Mosquitto MQTT are running
echo.
echo Your computer's IP addresses:
ipconfig | findstr /i "IPv4"
echo.
echo Use one of these IPs in your ESP32 firmware!
echo.

python backend_api.py
