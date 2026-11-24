@echo off
cd /d "%~dp0"
echo Skapar 12 epokversioner (ca 40 ore styck, ca 5 kr totalt)...
echo.
echo [main-character] han-soldier
if exist "media\library\characters\main-character\eras\han-soldier.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/main-character/eras/han-soldier.prompt.txt --ref media/library/characters/main-character/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/main-character/eras/han-soldier.png
echo [main-character] greek-athlete
if exist "media\library\characters\main-character\eras\greek-athlete.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/main-character/eras/greek-athlete.prompt.txt --ref media/library/characters/main-character/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/main-character/eras/greek-athlete.png
echo [main-character] heian-noble
if exist "media\library\characters\main-character\eras\heian-noble.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/main-character/eras/heian-noble.prompt.txt --ref media/library/characters/main-character/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/main-character/eras/heian-noble.png
echo [main-character] medieval-peasant
if exist "media\library\characters\main-character\eras\medieval-peasant.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/main-character/eras/medieval-peasant.prompt.txt --ref media/library/characters/main-character/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/main-character/eras/medieval-peasant.png
echo [main-character] victorian-gentleman
if exist "media\library\characters\main-character\eras\victorian-gentleman.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/main-character/eras/victorian-gentleman.prompt.txt --ref media/library/characters/main-character/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/main-character/eras/victorian-gentleman.png
echo [character-2] han-soldier
if exist "media\library\characters\character-2\eras\han-soldier.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/character-2/eras/han-soldier.prompt.txt --ref media/library/characters/character-2/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/character-2/eras/han-soldier.png
echo [character-2] greek-athlete
if exist "media\library\characters\character-2\eras\greek-athlete.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/character-2/eras/greek-athlete.prompt.txt --ref media/library/characters/character-2/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/character-2/eras/greek-athlete.png
echo [character-2] heian-noble
if exist "media\library\characters\character-2\eras\heian-noble.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/character-2/eras/heian-noble.prompt.txt --ref media/library/characters/character-2/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/character-2/eras/heian-noble.png
echo [character-2] medieval-peasant
if exist "media\library\characters\character-2\eras\medieval-peasant.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/character-2/eras/medieval-peasant.prompt.txt --ref media/library/characters/character-2/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/character-2/eras/medieval-peasant.png
echo [character-2] victorian-gentleman
if exist "media\library\characters\character-2\eras\victorian-gentleman.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/character-2/eras/victorian-gentleman.prompt.txt --ref media/library/characters/character-2/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/character-2/eras/victorian-gentleman.png
echo [character-3] ming-hongwu
if exist "media\library\characters\character-3\eras\ming-hongwu.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/character-3/eras/ming-hongwu.prompt.txt --ref media/library/characters/character-3/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/character-3/eras/ming-hongwu.png
echo [character-3] edward-ii
if exist "media\library\characters\character-3\eras\edward-ii.png" (echo   finns redan - hoppar over) else py -3.12 tools/gen_image.py --prompt-file media/library/characters/character-3/eras/edward-ii.prompt.txt --ref media/library/characters/character-3/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/character-3/eras/edward-ii.png
echo.
echo Klart! Alla bilder ligger i media\library\characters\*\eras\
pause
