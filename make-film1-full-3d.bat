@echo off
cd /d "%~dp0"
set /p BL=<tools\blender_path.txt
echo Renderar hela film 1 i 3D (10 min, ca 4 timmar). Kan startas om - fardiga scener hoppas over.
"%BL%" -b -P blender\film1_3d\render.py -- --plan full --engine eevee --samples 64
