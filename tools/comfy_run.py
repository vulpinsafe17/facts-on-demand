"""Run a batch of image jobs on the LOCAL ComfyUI (free, on the owner's RTX 5070).

    py -3.12 tools/comfy_run.py comfy/jobs/owl-parts.json            # all jobs, skips finished ones
    py -3.12 tools/comfy_run.py comfy/jobs/owl-parts.json --only front-talk --force

How it works: talks to ComfyUI's API on localhost (ComfyUI Desktop = port 8000, portable =
8188), uploads the job's reference picture, fills the workflow template ({{UNET}}, {{PROMPT}},
{{SEED}}, {{REF_IMAGE}}, {{PREFIX}}), queues one picture at a time and saves the result into
the job's out_dir. Fixed seeds + fixed workflow = the same picture every run.
Stdlib only (no pip installs). Run from the repo root.
"""
import argparse, json, os, sys, time, uuid, urllib.request, urllib.parse, urllib.error

PORTS = [8000, 8188]
# Largest first. Q4_0 (11.9 GB) looks best; Q3_K_M (9.9 GB) is the safe pick for 12 GB VRAM + 16 GB RAM.
UNET_PREF = ["qwen-image-edit-2511-Q4_0.gguf", "qwen-image-edit-2511-Q4_K_S.gguf",
             "qwen-image-edit-2511-Q3_K_M.gguf", "qwen-image-edit-2511-Q3_K_S.gguf"]
NEEDS = {
    ("CLIPLoader", "clip_name"): ("qwen_2.5_vl_7b_fp8_scaled.safetensors", "models/text_encoders",
        "https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors"),
    ("VAELoader", "vae_name"): ("qwen_image_vae.safetensors", "models/vae",
        "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors"),
    ("LoraLoaderModelOnly", "lora_name"): ("Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors", "models/loras",
        "https://huggingface.co/lightx2v/Qwen-Image-Edit-2511-Lightning/resolve/main/Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors"),
}
GGUF_URL = "https://huggingface.co/unsloth/Qwen-Image-Edit-2511-GGUF/resolve/main/qwen-image-edit-2511-Q3_K_M.gguf"


def die(msg):
    print("\nFEL: " + msg)
    sys.exit(1)


def http(base, path, data=None, headers=None, timeout=30):
    req = urllib.request.Request(base + path, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def find_server():
    for p in PORTS:
        base = f"http://127.0.0.1:{p}"
        try:
            http(base, "/system_stats", timeout=3)
            return base
        except Exception:
            pass
    die("Hittar inte ComfyUI. Starta ComfyUI och vanta tills det ar klart, kor sedan igen.")


def options(base, node, field):
    try:
        info = json.loads(http(base, f"/object_info/{node}"))
    except urllib.error.HTTPError:
        return None  # node not installed
    spec = info.get(node, {}).get("input", {})
    for group in ("required", "optional"):
        if field in spec.get(group, {}):
            opts = spec[group][field][0]
            return opts if isinstance(opts, list) else []
    return []


def check_models(base):
    unets = options(base, "UnetLoaderGGUF", "unet_name")
    if unets is None:
        die("Tillagget ComfyUI-GGUF saknas. Installera det i ComfyUI Manager (sok 'ComfyUI-GGUF' av city96) och starta om ComfyUI.")
    unet = next((u for u in UNET_PREF if u in unets), None)
    missing = []
    if not unet:
        missing.append(("qwen-image-edit-2511-Q3_K_M.gguf", "models/unet", GGUF_URL))
    for (node, field), (name, folder, url) in NEEDS.items():
        if name not in (options(base, node, field) or []):
            missing.append((name, folder, url))
    if missing:
        print("\nDessa modellfiler saknas i ComfyUI (ladda ner, lagg i mappen, starta om ComfyUI):")
        for name, folder, url in missing:
            print(f"  - {name}\n      mapp: ComfyUI/{folder}\n      lank: {url}")
        sys.exit(1)
    return unet


def upload(base, path):
    boundary = uuid.uuid4().hex
    name = os.path.basename(path)
    with open(path, "rb") as f:
        img = f.read()
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
            f"Content-Type: image/png\r\n\r\n").encode() + img + \
           f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    res = json.loads(http(base, "/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={boundary}"}, 120))
    return (res.get("subfolder") + "/" if res.get("subfolder") else "") + res["name"]


def fill(node, slots):
    if isinstance(node, dict):
        return {k: fill(v, slots) for k, v in node.items()}
    if isinstance(node, list):
        return [fill(v, slots) for v in node]
    if isinstance(node, str) and node in slots:
        return slots[node]
    return node


def run_one(base, wf, slots, client):
    prompt = {k: v for k, v in fill(wf, slots).items() if not k.startswith("_")}
    body = json.dumps({"prompt": prompt, "client_id": client}).encode()
    try:
        pid = json.loads(http(base, "/prompt", body, {"Content-Type": "application/json"}))["prompt_id"]
    except urllib.error.HTTPError as e:
        die("ComfyUI vagrade jobbet:\n" + e.read().decode(errors="replace")[:1500])
    while True:
        time.sleep(2)
        hist = json.loads(http(base, f"/history/{pid}"))
        if pid not in hist:
            continue
        h = hist[pid]
        st = h.get("status", {})
        if st.get("status_str") == "error":
            msgs = [m for m in st.get("messages", []) if m[0] == "execution_error"]
            die("ComfyUI-fel: " + json.dumps(msgs[-1][1] if msgs else st)[:1500])
        for out in h.get("outputs", {}).values():
            for im in out.get("images", []):
                q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im["subfolder"], "type": im["type"]})
                return http(base, "/view?" + q, timeout=120)
        if st.get("completed"):
            die("ComfyUI blev klart men gav ingen bild.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jobfile")
    ap.add_argument("--only", help="comma-separated job names")
    ap.add_argument("--force", action="store_true", help="redo pictures that already exist")
    a = ap.parse_args()
    spec = json.load(open(a.jobfile, encoding="utf-8"))
    wf = json.load(open(spec["workflow"], encoding="utf-8"))
    ref = spec["reference"]
    if not os.path.exists(ref):
        die(f"Referensbilden saknas: {ref}\nLagg profilbilden dar (PNG) och kor igen.")
    os.makedirs(spec["out_dir"], exist_ok=True)
    jobs = spec["jobs"]
    if a.only:
        want = set(a.only.split(","))
        jobs = [j for j in jobs if j["name"] in want]
    todo = [j for j in jobs if a.force or not os.path.exists(os.path.join(spec["out_dir"], j["name"] + ".png"))]
    for j in jobs:
        if j not in todo:
            print(f"{j['name']}: finns redan - hoppar over")
    if not todo:
        print("Inget att gora.")
        return
    base = find_server()
    print(f"ComfyUI hittat pa {base}")
    unet = check_models(base)
    print(f"Modell: {unet}")
    ref_name = upload(base, ref)
    client = uuid.uuid4().hex
    for i, j in enumerate(todo, 1):
        t0 = time.time()
        print(f"[{i}/{len(todo)}] {j['name']} ...", end="", flush=True)
        slots = {"{{UNET}}": unet, "{{REF_IMAGE}}": ref_name, "{{SEED}}": int(j["seed"]),
                 "{{PROMPT}}": j["prompt"] + " " + spec.get("style_lock", ""),
                 "{{PREFIX}}": f"fod/{os.path.basename(spec['out_dir'])}/{j['name']}"}
        png = run_one(base, wf, slots, client)
        out = os.path.join(spec["out_dir"], j["name"] + ".png")
        with open(out, "wb") as f:
            f.write(png)
        with open(out[:-4] + ".json", "w", encoding="utf-8") as f:  # sidecar: exactly how it was made
            json.dump({"job": j, "unet": unet, "workflow": spec["workflow"], "reference": ref}, f, indent=1)
        print(f" klar ({time.time() - t0:.0f} s) -> {out}")
    print("\nKlart!")


if __name__ == "__main__":
    main()
