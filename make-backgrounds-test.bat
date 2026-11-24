@echo off
cd /d "%~dp0"
echo Skapar 2 bakgrunder (ca 1 kr styck)...
echo.
echo med-london-street
if exist "media\projects\film-1-football\bg\med-london-street.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/med-london-street.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/med-london-street.png
echo heian-garden
if exist "media\projects\film-1-football\bg\heian-garden.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/heian-garden.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/heian-garden.png
echo.
echo Klart!
pause
