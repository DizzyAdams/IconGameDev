@echo off
cd /d C:\Users\forrydev\Desktop\\bedrock_minemods\marketplace-content
python scripts/generate-mass-skins.py --count 1600 --skins-per-pack 8 --size 64x64 > gen.log 2>&1
echo GEN_DONE > gen.done
