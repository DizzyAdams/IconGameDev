@echo off
cd /d C:\Users\forrydev\Desktop\IconGameDev
python submit\auto_submit_mc.py --dry-run 2>&1
echo.
echo --- exit code: %ERRORLEVEL% ---
pause
