@echo off
rem Grant read/write permissions to all .mcpack files for upload
set "TARGET_DIR=%~dp0..\output"
icacls "%TARGET_DIR%" /grant Everyone:(F) /T
echo Permissions set for %TARGET_DIR%
