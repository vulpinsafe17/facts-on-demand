@echo off
cd /d "%~dp0"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
> "%STARTUP%\facts-on-demand-job-runner.bat" echo @start "" /min "%~dp0start-job-runner.bat"
echo Klart! Jobbkon startar nu automatiskt nar Windows startar.
echo (Ta bort: radera %STARTUP%\facts-on-demand-job-runner.bat)
echo.
echo Startar jobbkon nu...
start "" /min "%~dp0start-job-runner.bat"
pause
