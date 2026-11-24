@echo off
cd /d "%~dp0"
set E=media\library\characters\character-3\eras
if exist "%E%\ming-hongwu.png" ren "%E%\ming-hongwu.png" ming-hongwu-v1-rejected.png
echo Gor om Ming-kejsaren (ca 1 kr)...
py -3.12 tools/gen_image.py --prompt-file media/library/characters/character-3/eras/ming-hongwu.prompt.txt --ref media/library/characters/character-3/master-sheet.jpg --model fast --aspect 16:9 --out media/library/characters/character-3/eras/ming-hongwu.png
echo Klart!
pause
