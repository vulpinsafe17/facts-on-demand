@echo off
cd /d "%~dp0"
py -3.12 -m yt_dlp --skip-download --write-auto-subs --write-subs --sub-langs "en.*" --sub-format vtt -o "media/reference/%%(id)s.%%(ext)s" https://www.youtube.com/shorts/znWzWYHoLOg https://www.youtube.com/shorts/n1ZAiKVl748
