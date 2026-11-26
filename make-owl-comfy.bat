@echo off
cd /d "%~dp0"
echo Skapar ugglans poser i ComfyUI (gratis, pa din dator).
echo ComfyUI maste vara igang. Stang garna andra program forst (16 GB RAM ar snalt).
echo Bilder som redan finns hoppas over.
echo.
py -3.12 tools/comfy_run.py comfy/jobs/owl-parts.json
echo.
pause
