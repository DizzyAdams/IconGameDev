@echo off
echo ===== Checking PIL =====
python3 -c "from PIL import Image; print('PIL OK:', Image.__version__)"
if errorlevel 1 (
    echo PIL not available - installing Pillow
    pip install Pillow
)
echo ===== Checking PIL again =====
python3 -c "from PIL import Image; print('PIL OK:', Image.__version__)"
echo ===== Running skin pack generator =====
cd /d C:\Users\forrydev\Desktop\IconGameDev
python3 marketplace-content/scripts/generate-all-skin-packs.py
echo ===== Script finished =====
echo Checking output...
dir /s /b marketplace-content\skin-packs\* 2>nul | find /c ":"
echo Done.
pause
