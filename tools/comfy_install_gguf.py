"""Install the ComfyUI-GGUF custom node (city96) into the running ComfyUI Desktop.
Needed for the GGUF image-edit model. Run via make-comfy-gguf.bat, then restart ComfyUI.
Finds ComfyUI's folders through its own API, clones the node, installs its requirements into
ComfyUI's own Python environment. Safe to run twice (skips what is already there)."""
import glob, json, os, subprocess, sys, urllib.request

REPO = "https://github.com/city96/ComfyUI-GGUF"


def api(path):
    for port in (8000, 8188):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as r:
                return json.loads(r.read())
        except Exception:
            pass
    sys.exit("FEL: ComfyUI ar inte igang. Starta ComfyUI och kor igen.")


paths = api("/internal/folder_paths")
cn = paths.get("custom_nodes") or []
cn = [c if isinstance(c, str) else c[0] for c in cn]
if not cn:
    sys.exit("FEL: hittar ingen custom_nodes-mapp i ComfyUI")
node_dir = os.path.join(cn[0], "ComfyUI-GGUF")
print("custom_nodes:", cn[0])
if os.path.isdir(node_dir):
    print("ComfyUI-GGUF finns redan:", node_dir)
else:
    subprocess.run(["git", "clone", "--depth", "1", REPO, node_dir], check=True)

# ComfyUI's own python: look for a .venv next to / above the custom_nodes folder, then anywhere
# under the Comfy Desktop data folder.
cands = []
d = os.path.abspath(cn[0])
for _ in range(4):
    d = os.path.dirname(d)
    cands += glob.glob(os.path.join(d, ".venv", "Scripts", "python.exe"))
local = os.environ.get("LOCALAPPDATA", "")
for pat in ("Comfy-Desktop/**/.venv/Scripts/python.exe", "Programs/Comfy Desktop/**/.venv/Scripts/python.exe",
            "Programs/@comfyorgcomfyui-electron/**/python.exe"):
    cands += glob.glob(os.path.join(local, pat), recursive=True)
cands = list(dict.fromkeys(cands))
print("ComfyUI python candidates:", cands)
if not cands:
    sys.exit("FEL: hittar inte ComfyUI:s Python. Installera ComfyUI-GGUF via ComfyUI Manager i stallet.")
for py in cands:
    print("\npip install i", py)
    subprocess.run([py, "-m", "pip", "install", "-r", os.path.join(node_dir, "requirements.txt")], check=False)
print("\nKlart. Starta om ComfyUI sa att noden laddas.")
