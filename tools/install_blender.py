"""Install Blender (4.5 LTS, portable zip, no admin rights needed) for the 3D pipeline.
Finds the newest 4.5.x on download.blender.org, downloads with resume (the home connection
drops), unpacks to %LOCALAPPDATA%\\fod-blender and writes its path to tools/blender_path.txt.
Safe to run again: skips what is already done."""
import os, re, sys, time, urllib.request, zipfile

SERIES = "Blender4.5"
BASE = f"https://download.blender.org/release/{SERIES}/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "fod-blender")
os.makedirs(DEST, exist_ok=True)

html = urllib.request.urlopen(BASE, timeout=60).read().decode()
zips = sorted(set(re.findall(r'blender-(4\.5\.(\d+))-windows-x64\.zip"', html)), key=lambda v: int(v[1]))
if not zips:
    sys.exit("FEL: hittar ingen Blender 4.5 for Windows pa " + BASE)
ver = zips[-1][0]
name = f"blender-{ver}-windows-x64"
exe = os.path.join(DEST, name, "blender.exe")
if not os.path.exists(exe):
    url, part = BASE + name + ".zip", os.path.join(DEST, name + ".zip.part")
    print("Laddar ner", url)
    for attempt in range(1, 41):
        have = os.path.getsize(part) if os.path.exists(part) else 0
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={have}-"})
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status == 200 and have:
                    have = 0
                total = have + int(r.headers.get("Content-Length") or 0)
                with open(part, "ab" if have else "wb") as f:
                    last = -1
                    while True:
                        b = r.read(1 << 20)
                        if not b:
                            break
                        f.write(b); have += len(b)
                        pct = int(have * 100 / max(total, 1))
                        if pct // 10 != last:
                            last = pct // 10; print(f"  {pct}%", flush=True)
            if total and have >= total:
                break
        except Exception as e:
            if getattr(e, "code", None) == 416:
                break
            print(f"  avbrott ({e}), fortsatter om 15 s", flush=True); time.sleep(15)
    print("Packar upp...")
    with zipfile.ZipFile(part) as z:
        z.extractall(DEST)
    os.remove(part)
with open(os.path.join(ROOT, "tools", "blender_path.txt"), "w") as f:
    f.write(exe)
print("Blender klar:", exe)
