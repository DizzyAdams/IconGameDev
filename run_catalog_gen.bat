@echo off
cd /d "C:\Users\forrydev\Desktop\IconGameDev"
python catalog\generate_catalog.py
if errorlevel 1 (
    echo Script failed with error code %errorlevel%
    pause
    exit /b %errorlevel%
)
echo Done! Catalog generated successfully.
pause
