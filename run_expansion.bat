@echo off
cd /d C:\Users\forrydev\Desktop\IconGameDev
python generate_50_templates.py > templates_gen.log 2>&1
python generate_premium_skins.py >> templates_gen.log 2>&1
echo EXPANSION_DONE >> templates_gen.log
