"""Facts on Demand job queue: lets Claude run work on this PC from the owner's phone.

Start:  start-job-runner.bat   (or install-job-runner-autostart.bat to start it with Windows)

How it works
- Claude drops a small job file into queue/inbox/<id>.json, e.g.
      {"action": "comfy", "args": {"job": "owl-parts"}}
- This runner picks jobs up one at a time (oldest first), runs them, and writes
      queue/logs/<id>.log      everything the job printed
      queue/done/<id>.json     status (ok / failed / rejected), times, exit code
  and keeps queue/heartbeat.json fresh every few seconds, so Claude can see it is alive.

SAFETY: only the actions in ACTIONS below can run, with checked arguments. A job file can
never run an arbitrary command. Anything else is rejected and logged.
Stdlib only. Run from the repo root.
"""
import datetime, json, os, re, shutil, socket, subprocess, sys, time, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = os.path.join(ROOT, "queue")
INBOX, RUNNING, DONE, LOGS = (os.path.join(Q, d) for d in ("inbox", "running", "done", "logs"))
POLL_S = 5
EDDIE = "VsQmyFHffusQDewmHB5v"  # PRODUCTION-RULES: narrator ElevenLabs "Eddie Starling"
WIN = os.name == "nt"
PY = sys.executable

RE_FILM = re.compile(r"^film-\d+-[a-z0-9-]+$")
RE_COMP = re.compile(r"^[A-Za-z][A-Za-z0-9]{1,40}$")
RE_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")
RE_BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,80}$")
RE_FRAMES = re.compile(r"^\d{1,6}-\d{1,6}$")
RE_STILLS = re.compile(r"^\d{1,6}(,\d{1,6}){0,39}$")
RE_BAT = re.compile(r"^make-[a-z0-9-]+\.bat$")


class Reject(Exception):
    pass


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def tool(name):
    """Full path of a program on PATH (npm/npx are .cmd files on Windows)."""
    for cand in ([name + ".cmd", name + ".exe", name] if WIN else [name]):
        p = shutil.which(cand)
        if p:
            return p
    raise Reject(f"{name} is not installed / not on PATH")


def need(args, key, rx, optional=False):
    v = args.get(key)
    if v is None and optional:
        return None
    if not isinstance(v, str) or not rx.match(v):
        raise Reject(f"bad or missing argument '{key}': {v!r}")
    return v


def run(cmd, log, cwd=ROOT, timeout=3 * 3600):
    log.write(f"\n$ {' '.join(cmd)}\n")
    log.flush()
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace",
                         env={**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8"})
    t0 = time.time()
    for line in p.stdout:
        log.write(line)
        log.flush()
        if time.time() - t0 > timeout:
            p.kill()
            raise RuntimeError(f"timed out after {timeout} s")
    rc = p.wait()
    if rc != 0:
        raise RuntimeError(f"command failed (exit {rc})")


# ---------------------------------------------------------------- actions
def a_ping(args, log):
    """Health check: tools, GPU, disk, ComfyUI reachable, current git branch."""
    for name in ("git", "node", "ffmpeg"):
        log.write(f"{name}: {shutil.which(name) or shutil.which(name + '.exe') or 'MISSING'}\n")
    log.write(f"python: {PY}\n")
    try:
        run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total,temperature.gpu", "--format=csv"], log, timeout=30)
    except Exception as e:
        log.write(f"nvidia-smi: {e}\n")
    total, used, free = shutil.disk_usage(ROOT)
    log.write(f"disk free: {free / 1e9:.1f} GB of {total / 1e9:.0f} GB\n")
    up = None
    for port in (8000, 8188):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=2).close()
            up = port
            break
        except OSError:
            pass
    log.write(f"ComfyUI: {'running on port %d' % up if up else 'NOT running'}\n")
    if os.path.isdir(os.path.join(ROOT, ".git")):
        run([tool("git"), "status", "-sb"], log, timeout=60)
    else:
        log.write("folder is not a git clone (update downloads from GitHub instead)\n")
    for k in ("ELEVENLABS_API_KEY", "GEMINI_API_KEY"):
        env = _read(os.path.join(ROOT, ".env")) or b""
        log.write(f"{k}: {'set' if (k + '=').encode() in env else 'missing'} in .env\n")


REPO = "vulpinsafe17/facts-on-demand"


def _update_from_zip(branch, log):
    """For a folder that is not a git clone: download the branch as a zip from GitHub and copy
    its files in. Local-only files (.env, voice, outputs, new pictures) are never touched, and
    pictures/sounds under media/ that already exist here are kept as they are."""
    import io, urllib.request, zipfile
    url = f"https://codeload.github.com/{REPO}/zip/refs/heads/{branch}"
    log.write(f"downloading {url}\n")
    log.flush()
    with urllib.request.urlopen(url, timeout=600) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    new = changed = kept = 0
    for info in z.infolist():
        if info.is_dir():
            continue
        rel = info.filename.split("/", 1)[1] if "/" in info.filename else ""
        if not rel or rel.startswith(("queue/", ".env")) or ".." in rel.split("/"):
            continue
        dst = os.path.normpath(os.path.join(ROOT, rel))
        if not dst.startswith(ROOT + os.sep):
            continue
        data = z.read(info)
        old = _read(dst)
        if old == data:
            continue
        if old is not None and rel.startswith("media/"):
            kept += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(data)
        if old is None:
            new += 1
        else:
            changed += 1
        log.write(f"  {'new    ' if old is None else 'updated'} {rel}\n")
    log.write(f"\n{new} new, {changed} updated, {kept} existing media files kept as they are\n")


def a_update(args, log):
    """Get the newest code from GitHub. Never throws away local work."""
    branch = need(args, "branch", RE_BRANCH, optional=True) or "film-1-football"
    lock_before = _read(os.path.join(ROOT, "remotion", "package-lock.json"))
    me_before = _read(os.path.abspath(__file__))
    if os.path.isdir(os.path.join(ROOT, ".git")):
        git = tool("git")  # git clone: fast-forward only
        run([git, "fetch", "origin", branch], log, timeout=600)
        run([git, "checkout", branch], log, timeout=120)
        run([git, "merge", "--ff-only", f"origin/{branch}"], log, timeout=120)
    else:
        _update_from_zip(branch, log)
    if lock_before != _read(os.path.join(ROOT, "remotion", "package-lock.json")) or \
            not os.path.isdir(os.path.join(ROOT, "remotion", "node_modules")):
        log.write("\nremotion packages changed -> npm ci\n")
        run([tool("npm"), "ci", "--no-audit", "--no-fund"], log, cwd=os.path.join(ROOT, "remotion"), timeout=1800)
    if me_before != _read(os.path.abspath(__file__)):
        log.write("\njob runner itself was updated -> restarting after this job\n")
        return "restart"


def a_comfy(args, log):
    """Pictures on the local ComfyUI: a job file in comfy/jobs/ (e.g. owl-parts)."""
    job = need(args, "job", RE_NAME)
    path = os.path.join("comfy", "jobs", job + ".json")
    if not os.path.exists(os.path.join(ROOT, path)):
        raise Reject(f"no such ComfyUI job: {path}")
    cmd = [PY, "tools/comfy_run.py", path]
    only = args.get("only")
    if only is not None:
        if not isinstance(only, list) or not all(isinstance(x, str) and RE_NAME.match(x) for x in only):
            raise Reject("'only' must be a list of picture names")
        cmd += ["--only", ",".join(only)]
    if args.get("force") is True:
        cmd.append("--force")
    run(cmd, log, timeout=4 * 3600)


def a_voice(args, log):
    """ElevenLabs voice for a film (COSTS CREDITS; Claude states the cost before queueing).
    Cached lines are never re-billed. Copies the track to media/projects/<film>/audio/voice.wav."""
    film = need(args, "film", RE_FILM)
    beats = os.path.join("films", film, "beats.json")
    if not os.path.exists(os.path.join(ROOT, beats)):
        raise Reject(f"{beats} does not exist yet")
    cmd = [PY, "tools/gen_voice.py", "--beats", beats, "--blocks", "--voice", EDDIE]
    if args.get("dry_run") is True:
        cmd.append("--dry-run")
    run(cmd, log, timeout=2 * 3600)
    src = os.path.join(ROOT, "films", film, "voice", "voice.wav")
    if os.path.exists(src) and args.get("dry_run") is not True:
        dst = os.path.join(ROOT, "media", "projects", film, "audio", "voice.wav")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        log.write(f"\nvoice track copied -> {os.path.relpath(dst, ROOT)}\n")


def a_render(args, log):
    """Render a film (or part of it) to remotion/out/."""
    comp = need(args, "composition", RE_COMP)
    cmd = [tool("node"), "scripts/render-film.mjs", comp]
    fr = need(args, "frames", RE_FRAMES, optional=True)
    if fr:
        cmd.append(f"--frames={fr}")
    cmd.append(f"--scale={_scale(args)}")
    run(cmd, log, cwd=os.path.join(ROOT, "remotion"), timeout=6 * 3600)


def a_stills(args, log):
    """QA stills of chosen frames -> remotion/out/qa/ (Claude reads these before any full render)."""
    comp = need(args, "composition", RE_COMP)
    frames = need(args, "frames", RE_STILLS)
    run([tool("node"), "scripts/render-film.mjs", comp, f"--stills={frames}", f"--scale={_scale(args)}"],
        log, cwd=os.path.join(ROOT, "remotion"), timeout=1800)


def a_bat(args, log):
    """One of the repo's own make-*.bat files (e.g. make-owl-comfy.bat)."""
    name = need(args, "name", RE_BAT)
    if not os.path.exists(os.path.join(ROOT, name)):
        raise Reject(f"no such file: {name}")
    if not WIN:
        raise Reject(".bat files only run on Windows")
    run([os.environ.get("COMSPEC", "cmd.exe"), "/c", name], log, timeout=6 * 3600)


ACTIONS = {"ping": a_ping, "update": a_update, "comfy": a_comfy, "voice": a_voice,
           "render": a_render, "stills": a_stills, "bat": a_bat}


def _scale(args):
    s = args.get("scale", 1)
    if not isinstance(s, (int, float)) or not 0.25 <= s <= 2:
        raise Reject("scale must be between 0.25 and 2")
    return s


def _read(p):
    try:
        with open(p, "rb") as f:
            return f.read()
    except OSError:
        return None


# ---------------------------------------------------------------- loop
def heartbeat(state, job=None):
    tmp = os.path.join(Q, "heartbeat.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"time": now(), "state": state, "job": job, "pid": os.getpid(),
                   "actions": sorted(ACTIONS)}, f, indent=1)
    os.replace(tmp, os.path.join(Q, "heartbeat.json"))


def handle(name):
    jid = name[:-5]
    src = os.path.join(INBOX, name)
    cur = os.path.join(RUNNING, name)
    try:
        os.replace(src, cur)
    except OSError:
        return None  # still being written / gone
    result = {"id": jid, "received": now()}
    ret = None
    with open(os.path.join(LOGS, jid + ".log"), "w", encoding="utf-8") as log:
        try:
            with open(cur, encoding="utf-8") as f:
                job = json.load(f)
            action = job.get("action")
            result["action"] = action
            if action not in ACTIONS:
                raise Reject(f"unknown action {action!r}; allowed: {sorted(ACTIONS)}")
            args = job.get("args") or {}
            if not isinstance(args, dict):
                raise Reject("'args' must be an object")
            print(f"[{now()}] {jid}: {action} {json.dumps(args)}")
            heartbeat("running", jid)
            log.write(f"job {jid}: {action} {json.dumps(args)}\nstarted {now()}\n")
            ret = ACTIONS[action](args, log)
            result["status"] = "ok"
        except Reject as e:
            result["status"], result["error"] = "rejected", str(e)
            log.write(f"\nREJECTED: {e}\n")
        except Exception as e:
            result["status"], result["error"] = "failed", str(e)
            log.write("\nFAILED:\n" + traceback.format_exc())
        result["finished"] = now()
        log.write(f"\n{result['status'].upper()} {result['finished']}\n")
    print(f"[{now()}] {jid}: {result['status']}" + (f" - {result.get('error')}" if result.get("error") else ""))
    with open(os.path.join(DONE, jid + ".json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1)
    os.replace(cur, os.path.join(DONE, jid + ".job.json"))
    return ret


def main():
    os.chdir(ROOT)
    for d in (INBOX, RUNNING, DONE, LOGS):
        os.makedirs(d, exist_ok=True)
    try:  # one runner at a time
        guard = socket.socket()
        guard.bind(("127.0.0.1", 48765))
    except OSError:
        print("The job runner is already running.")
        return
    for left in os.listdir(RUNNING):  # a job cut off by a crash/reboot goes back in line
        os.replace(os.path.join(RUNNING, left), os.path.join(INBOX, left))
    print(f"Facts on Demand job runner - watching {INBOX}\nLeave this window open (minimised is fine). Ctrl+C stops it.")
    while True:
        heartbeat("idle")
        jobs = sorted((f for f in os.listdir(INBOX) if f.endswith(".json")
                       and time.time() - os.path.getmtime(os.path.join(INBOX, f)) > 2),  # fully written
                      key=lambda f: os.path.getmtime(os.path.join(INBOX, f)))
        for name in jobs:
            if handle(name) == "restart":
                guard.close()
                print("Restarting with the updated runner...")
                flags = subprocess.CREATE_NEW_CONSOLE if WIN else 0
                subprocess.Popen([PY, os.path.abspath(__file__)], cwd=ROOT, creationflags=flags)
                sys.exit(0)
        time.sleep(POLL_S)


if __name__ == "__main__":
    main()
