@echo off
cd /d C:\Users\forrydev\Desktop\bedrock_minemods\marketplace-content
python scripts/build-all.py > build.log 2>&1
echo BUILD_DONE > build.done
