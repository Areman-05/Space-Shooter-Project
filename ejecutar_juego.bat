@echo off
chcp 65001 >nul
echo === Space Shooter ===
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0instalar_y_ejecutar.ps1"
pause

