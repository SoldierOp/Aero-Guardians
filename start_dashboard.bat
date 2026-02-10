@echo off
echo ========================================
echo  PeatSense Dashboard
echo ========================================
echo.

echo Starting Streamlit dashboard...
echo.
echo Dashboard will open in your browser at:
echo http://localhost:8501
echo.
echo Make sure backend is running on:
echo http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo.

python -m streamlit run dashboard.py
