@echo off
echo ========================================
echo  AeroGuardians - Quick Start
echo ========================================
echo.

echo [1/3] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8+
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

echo [3/3] Starting Flask Backend...
echo.
echo ========================================
echo  Server will start on http://127.0.0.1:5000
echo  Press Ctrl+C to stop
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Keep this window open
echo 2. Open a NEW terminal and run: streamlit run sensor_dashboard.py
echo 3. Configure and power on your ESP32
echo.
echo Your computer's IP addresses:
ipconfig | findstr /i "IPv4"
echo.
echo Use one of these IPs in your ESP32 code!
echo.

python app.py
