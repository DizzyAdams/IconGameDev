@echo off
rem ------------------------------------------------
rem Prepare final submission bundle for Microsoft Marketplace
rem ------------------------------------------------
set "OUTPUT_DIR=%~dp0..\output"
set "BUNDLE=submission_bundle.zip"
rem Create zip of all .mcpack files
powershell -Command "Compress-Archive -Path \"%OUTPUT_DIR%\*.mcpack\" -DestinationPath \"%OUTPUT_DIR%\\%BUNDLE%\" -Force"
rem Grant Everyone full control on the bundle (Windows ACL)
icacls "%OUTPUT_DIR%\\%BUNDLE%" /grant Everyone:(F) /T
echo Submission bundle created at %OUTPUT_DIR%\\%BUNDLE%
