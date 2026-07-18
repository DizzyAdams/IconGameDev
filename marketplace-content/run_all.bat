@echo off
cd /d C:\Users\forrydev\Desktop\bedrock_minemods\marketplace-content
echo [%time%] STEP build-all >> run_all.log
python scripts/build-all.py >> run_all.log 2>&1
echo [%time%] STEP generate-mass-skins >> run_all.log
python scripts/generate-mass-skins.py --count 1600 --skins-per-pack 8 --size 64x64 >> run_all.log 2>&1
echo [%time%] STEP repair_dist >> run_all.log
python scripts/repair_dist.py >> run_all.log 2>&1
echo [%time%] STEP certify >> run_all.log
python ..\certify.py >> run_all.log 2>&1
echo ALL_DONE > all.done
echo [%time%] FINISHED >> run_all.log
