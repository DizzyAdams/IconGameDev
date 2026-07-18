@echo off
cd /d C:\Users\forrydev\Desktop\IconGameDev
python marketplace-content\scripts\generate-texture-packs.py > texture_gen.log 2>&1
echo DONE >> texture_gen.log
