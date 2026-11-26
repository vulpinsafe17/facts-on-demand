@echo off
cd /d "%~dp0"
echo Installerar ComfyUI-GGUF (behovs for bildmodellen). ComfyUI maste vara igang.
py -3.12 tools\comfy_install_gguf.py
