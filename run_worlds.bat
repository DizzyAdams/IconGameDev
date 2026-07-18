@echo off
cd /d C:\Users\forrydev\Desktop\IconGameDev
python generate_150_worlds.py > world_gen.log 2>&1
echo WORLDS_DONE >> world_gen.log
