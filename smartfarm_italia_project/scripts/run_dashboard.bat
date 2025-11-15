@echo off
REM Avvia SmartFarm Italia - Dashboard 

cd /d "%~dp0"
cd ..

python -m src.dashboard

pause