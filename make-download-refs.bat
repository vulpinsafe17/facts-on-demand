@echo off
cd /d "%~dp0"
echo Laddar ner referensvideor (bara for analys, laddas aldrig upp igen).
py -3.12 -m pip install --user -U yt-dlp
if not exist media\reference mkdir media\reference
py -3.12 -m yt_dlp -f "bv*[height<=1920]+ba/b" --merge-output-format mp4 -o "media/reference/%%(id)s.%%(ext)s" https://www.youtube.com/shorts/znWzWYHoLOg https://www.youtube.com/shorts/n1ZAiKVl748
