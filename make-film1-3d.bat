@echo off
cd /d "%~dp0"
set /p BL=<tools\blender_path.txt
echo Renderar film 1 i 3D (Blender EEVEE). Kan avbrytas och startas om - fardiga scener hoppas over.
"%BL%" -b -P blender\film1_3d\render.py -- --engine eevee --samples 64
