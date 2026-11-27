@echo off
cd /d "%~dp0"
set /p BL=<tools\blender_path.txt
"%BL%" -b -P blender\film1_3d\render.py -- --engine eevee --samples 64 --scenes 21,41 --force --out media\projects\film-1-football\3d-test
