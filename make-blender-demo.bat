@echo off
cd /d "%~dp0"
set /p BL=<tools\blender_path.txt
echo Renderar 3D-demo med Blender (EEVEE, GPU)...
"%BL%" -b -P blender\scenes\london_demo.py -- --out blender\out\london_demo_v2.mp4 --engine eevee
