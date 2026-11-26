@echo off
title Facts on Demand - job runner
cd /d "%~dp0"
echo Startar jobbkon. Lat fonstret vara oppet (minimerat gar bra).
py -3.12 tools\job_runner.py
echo.
echo Jobbkon stoppades.
pause
