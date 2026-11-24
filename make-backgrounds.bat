@echo off
cd /d "%~dp0"
echo Skapar 22 bakgrunder (ca 1 kr styck)...
echo.
echo med-throne-hall
if exist "media\projects\film-1-football\bg\med-throne-hall.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/med-throne-hall.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/med-throne-hall.png
echo decree-table
if exist "media\projects\film-1-football\bg\decree-table.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/decree-table.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/decree-table.png
echo modern-stadium
if exist "media\projects\film-1-football\bg\modern-stadium.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/modern-stadium.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/modern-stadium.png
echo scholar-study
if exist "media\projects\film-1-football\bg\scholar-study.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/scholar-study.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/scholar-study.png
echo han-city-dusk
if exist "media\projects\film-1-football\bg\han-city-dusk.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/han-city-dusk.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/han-city-dusk.png
echo han-palace-court
if exist "media\projects\film-1-football\bg\han-palace-court.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/han-palace-court.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/han-palace-court.png
echo han-training-field
if exist "media\projects\film-1-football\bg\han-training-field.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/han-training-field.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/han-training-field.png
echo song-street
if exist "media\projects\film-1-football\bg\song-street.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/song-street.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/song-street.png
echo greek-field
if exist "media\projects\film-1-football\bg\greek-field.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/greek-field.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/greek-field.png
echo heian-garden
if exist "media\projects\film-1-football\bg\heian-garden.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/heian-garden.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/heian-garden.png
echo med-muddy-field
if exist "media\projects\film-1-football\bg\med-muddy-field.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/med-muddy-field.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/med-muddy-field.png
echo med-london-street
if exist "media\projects\film-1-football\bg\med-london-street.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/med-london-street.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/med-london-street.png
echo med-archery-field
if exist "media\projects\film-1-football\bg\med-archery-field.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/med-archery-field.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/med-archery-field.png
echo school-field-1840s
if exist "media\projects\film-1-football\bg\school-field-1840s.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/school-field-1840s.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/school-field-1840s.png
echo cambridge-room
if exist "media\projects\film-1-football\bg\cambridge-room.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/cambridge-room.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/cambridge-room.png
echo frosty-field
if exist "media\projects\film-1-football\bg\frosty-field.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/frosty-field.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/frosty-field.png
echo victorian-street-night
if exist "media\projects\film-1-football\bg\victorian-street-night.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/victorian-street-night.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/victorian-street-night.png
echo solicitor-office
if exist "media\projects\film-1-football\bg\solicitor-office.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/solicitor-office.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/solicitor-office.png
echo tavern-interior
if exist "media\projects\film-1-football\bg\tavern-interior.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/tavern-interior.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/tavern-interior.png
echo cricket-ground-1872
if exist "media\projects\film-1-football\bg\cricket-ground-1872.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/cricket-ground-1872.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/cricket-ground-1872.png
echo montevideo-1930
if exist "media\projects\film-1-football\bg\montevideo-1930.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/montevideo-1930.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/montevideo-1930.png
echo props-sheet
if exist "media\projects\film-1-football\bg\props-sheet.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/projects/film-1-football/bg/props-sheet.prompt.txt --model fast --aspect 16:9 --out media/projects/film-1-football/bg/props-sheet.png
echo.
echo Klart!
pause
