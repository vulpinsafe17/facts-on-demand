@echo off
cd /d "%~dp0"
echo Gor en mindre delningsversion av Film1Full.mp4 (for mobilen).
ffmpeg -y -loglevel error -i remotion\out\Film1Full.mp4 -c:v libx264 -preset veryfast -crf 25 -pix_fmt yuv420p -c:a copy -movflags +faststart remotion\out\Film1Full-share.mp4
echo klar
