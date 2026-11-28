@echo off
cd /d "%~dp0"
set /p BL=<tools\blender_path.txt
set OUT=media\projects\film-1-football-full\3d-kit
"%BL%" -b -P blender\film1_3d\render.py -- --plan full --engine eevee --samples 64 --scenes 30-36 --force --out %OUT%
if errorlevel 1 exit /b 1
(for %%i in (030 031 032 033 034 035 036) do @echo file 'scene%%i.mp4') > %OUT%\list.txt
ffmpeg -y -f concat -safe 0 -i %OUT%\list.txt -ss 195.266 -t 44.978 -i films\film-1-football-full\voice\voice.wav -map 0:v -map 1:a -c:v libx264 -crf 20 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 160k -shortest remotion\out\London-kit-test.mp4
echo klar
