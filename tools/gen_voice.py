#!/usr/bin/env python3
"""
gen_voice.py — ElevenLabs TTS voice track for a TSX short, driven by its beats.json.

Shorts-track voice step. Reads a short's beats.json (vo[] lines with estimated
start/end seconds), generates each line with ElevenLabs text-to-speech (per line, so a
single line can be re-rolled without re-billing the rest), time-fits any clip that
overflows its window (gentle atempo, capped), assembles one timed voice track, and
writes the ACTUAL line timings back into beats.json — the TSX captions retime from it.

LIBRARY-FIRST: generated lines are cached by (index, text-hash); unchanged lines are
never re-billed. --force regenerates everything.

Usage:
  python tools/gen_voice.py --beats shorts/short-1-chess/beats.json
  python tools/gen_voice.py --beats ... --mux remotion/out/Short1Chess.mp4   # + voiced preview
  python tools/gen_voice.py --beats ... --dry-run                            # plan only
  python tools/gen_voice.py --beats films/film-1-football/beats.json --blocks  # long-form, one take per chapter

Needs ELEVENLABS_API_KEY in .env. ffmpeg/ffprobe on PATH.
Default voice: ElevenLabs premade "Liam".
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VOICE = "TX3LPaxmHKxFdv7VOQHJ"  # ElevenLabs premade "Liam"
DEFAULT_MODEL = "eleven_multilingual_v2"
MAX_ATEMPO = 1.3  # never speed a line up more than 30%


def load_env():
    env = {}
    p = os.path.join(ROOT, ".env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return {**env, **os.environ}


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if r.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}\n{r.stdout}")
    return r.stdout


def probe_duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", path])
    return float(out.strip())


def tts_line(key, voice, model, text, prev_text, next_text, out_path, speed=None):
    """TTS with character-level timestamps -> writes the mp3 AND <out_path>.words.json
    (per-word start/end seconds in the RAW clip) so captions can sync exactly.

    `text` may contain eleven_v3 audio tags like [excited] — they steer delivery and are
    FILTERED out of the word map (never captioned). If the model rejects /with-timestamps,
    falls back to plain TTS with an empty word map (captions then use estimated timing)."""
    body = {"text": text, "model_id": model}
    if not model.startswith("eleven_v3"):
        # v3 rejects the classic settings block AND previous/next context stitching;
        # server defaults are right for it
        body["voice_settings"] = {"stability": 0.5, "similarity_boost": 0.75, "style": 0.3,
                                  "use_speaker_boost": True}
        if speed:
            body["voice_settings"]["speed"] = speed
        if prev_text:
            body["previous_text"] = prev_text
        if next_text:
            body["next_text"] = next_text

    import base64

    def call(url):
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers={"xi-api-key": key, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:
            ctype = r.headers.get("Content-Type", "")
            raw = r.read()
        return json.loads(raw) if "json" in ctype else raw

    base = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    try:
        resp = call(f"{base}/with-timestamps?output_format=mp3_44100_128")
        audio = base64.b64decode(resp["audio_base64"])
        align = resp.get("alignment") or {}
        words = chars_to_words(align.get("characters", []),
                               align.get("character_start_times_seconds", []),
                               align.get("character_end_times_seconds", []))
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:500]
        if e.code in (400, 404, 422):  # model may not support timestamps — plain fallback
            print(f"    (with-timestamps not available: {e.code}; falling back to plain TTS)")
            try:
                audio = call(f"{base}?output_format=mp3_44100_128")
                words = []
            except urllib.error.HTTPError as e2:
                sys.exit(f"ElevenLabs TTS failed ({e2.code}) for: {text!r}\n{e2.read().decode()[:500]}")
        else:
            sys.exit(f"ElevenLabs TTS failed ({e.code}) for: {text!r}\n{detail}")

    # audio tags ([excited], [pause]…) are delivery directions, not spoken words
    words = [w for w in words if not (w["w"].startswith("[") or w["w"].endswith("]"))]
    with open(out_path, "wb") as f:
        f.write(audio)
    with open(out_path + ".words.json", "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False)


def chars_to_words(chars, starts, ends):
    """Collapse character alignment into [{w, start, end}] (whitespace-delimited)."""
    words, cur, w_start, w_end = [], "", None, None
    for ch, s, e in zip(chars, starts, ends):
        if ch.isspace():
            if cur:
                words.append({"w": cur, "start": round(w_start, 3), "end": round(w_end, 3)})
                cur, w_start = "", None
            continue
        if not cur:
            w_start = s
        cur += ch
        w_end = e
    if cur:
        words.append({"w": cur, "start": round(w_start, 3), "end": round(w_end, 3)})
    return words


def emit_ts(vo, path):
    """Write the generated VO (with exact word times) as a TS module the shot imports."""
    lines = ["// AUTO-GENERATED by tools/gen_voice.py — do not edit.",
             "// Word times are the REAL ElevenLabs alignment; captions sync exactly.",
             "import type { VoLine } from '../../lib/shorts';", "",
             "export const VO: VoLine[] = ["]
    for line in vo:
        esc = line["text"].replace("\\", "\\\\").replace("'", "\\'")
        ws = ", ".join(
            "{ w: '%s', start: %s, end: %s }" % (w["w"].replace("\\", "\\\\").replace("'", "\\'"), w["start"], w["end"])
            for w in line.get("words", []))
        lines.append(f"  {{ text: '{esc}', start: {line['start']}, end: {line['end']}, words: [{ws}] }},")
    lines += ["];", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def run_blocks(args, beats, vo, key, vdir, beats_path):
    """Long-form 'one take per chapter' mode.

    Lines are grouped into blocks (a new block starts at every line marked
    "chapterStart"). Each block is ONE ElevenLabs take, so tempo and intonation flow
    naturally across sentences. Word timestamps are then mapped back onto the lines, so
    every scene still knows exactly when its first word is spoken. Extra silence is
    inserted (inside existing word gaps, never mid-word) before lines marked
    "topicShift", and between blocks. Edges get short fades -> no clicks."""
    blocks, cur = [], []
    for i, line in enumerate(vo):
        if cur and line.get("chapterStart"):
            blocks.append(cur); cur = []
        cur.append(i)
    if cur:
        blocks.append(cur)

    timeline = []   # (wav_path, offset_sec)
    t = 0.4
    for bi, idxs in enumerate(blocks):
        texts = [vo[i].get("tts", vo[i]["text"]) for i in idxs]
        text = " ".join(texts)
        hkey = f"BLOCK|{args.voice}|{args.model}|{text}" + (f"|speed={args.speed}" if args.speed else "")
        h = hashlib.sha1(hkey.encode()).hexdigest()[:8]
        raw = os.path.join(vdir, f"block-{bi:02d}-{h}.mp3")
        if args.dry_run:
            print(f"block {bi:2d}: {len(idxs):2d} lines, {len(text):4d} chars  {texts[0][:50]}")
            continue
        if args.force or not os.path.exists(raw) or not os.path.exists(raw + ".words.json"):
            prev_text = " ".join(vo[i].get("tts", vo[i]["text"]) for i in blocks[bi - 1]) if bi else None
            next_text = " ".join(vo[i].get("tts", vo[i]["text"]) for i in blocks[bi + 1]) if bi + 1 < len(blocks) else None
            tts_line(key, args.voice, args.model, text, prev_text, next_text, raw, args.speed)
        words = json.load(open(raw + ".words.json", encoding="utf-8"))
        n_expected = sum(len(x.split()) for x in texts)
        if len(words) != n_expected:
            sys.exit(f"block {bi}: got {len(words)} words from ElevenLabs, expected {n_expected}. "
                     f"Check punctuation/hyphens in the tts text.")
        dur = probe_duration(raw)

        # split points: before each topicShift line, cut in the middle of the word gap
        cuts, k = [], 0
        line_words = []
        for i, tx in zip(idxs, texts):
            n = len(tx.split())
            line_words.append((i, words[k:k + n]))
            if k > 0 and vo[i].get("topicShift"):
                gap_mid = (words[k - 1]["end"] + words[k]["start"]) / 2
                cuts.append(gap_mid)
            k += n
        edges = [0.0] + cuts + [dur]
        inserted = 0.0
        for si in range(len(edges) - 1):
            a, bnd = edges[si], edges[si + 1]
            seg = os.path.join(vdir, f"block-{bi:02d}-{h}-seg{si}.wav")
            fade_out_at = max(0.0, bnd - a - 0.012)
            if args.force or not os.path.exists(seg):
                run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-ss", f"{a:.3f}", "-to", f"{bnd:.3f}",
                     "-af", f"afade=t=in:d=0.008,afade=t=out:st={fade_out_at:.3f}:d=0.012",
                     "-ar", "44100", "-ac", "2", seg])
            timeline.append((seg, t + a + inserted))
            if si < len(edges) - 2:
                inserted += args.topic_pause - 0.3 if args.topic_pause > 0.3 else 0.0

        # map word times to global time (account for inserted silence)
        def g(tw):
            extra = 0.0
            for c in cuts:
                if tw >= c:
                    extra += args.topic_pause - 0.3 if args.topic_pause > 0.3 else 0.0
            return round(t + tw + extra, 3)
        for i, ws in line_words:
            vo[i]["words"] = [{"w": w["w"], "start": g(w["start"]), "end": g(w["end"])} for w in ws]
            vo[i]["start"] = max(0.0, round(vo[i]["words"][0]["start"] - 0.05, 3))
            vo[i]["end"] = vo[i]["words"][-1]["end"]
        block_end = t + dur + inserted
        print(f"block {bi:2d}: {len(idxs):2d} lines  {t:7.2f}s -> {block_end:7.2f}s  {texts[0][:45]}")
        t = block_end + args.chapter_pause

    if args.dry_run:
        return
    total = round(t - args.chapter_pause + 1.5, 2)
    beats["format"]["durationSec"] = total
    voice_wav = os.path.join(vdir, "voice.wav")
    inputs, parts = [], []
    for j, (path, start) in enumerate(timeline):
        inputs += ["-i", path]
        ms = int(round(start * 1000))
        parts.append(f"[{j}:a]adelay={ms}|{ms}[a{j}]")
    chain = "".join(f"[a{j}]" for j in range(len(timeline)))
    fc = ";".join(parts) + f";{chain}amix=inputs={len(timeline)}:normalize=0,apad,atrim=0:{total}," \
         f"loudnorm=I=-16:TP=-1.5:LRA=11[out]"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc,
         "-map", "[out]", "-ar", "44100", "-ac", "2", voice_wav])
    beats["voiceStatus"] = f"elevenlabs:{args.voice} (blocks)"
    json.dump(beats, open(beats_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"timeline {total:.1f}s ({int(total // 60)}:{total % 60:04.1f})")
    print(f"voice track -> {os.path.relpath(voice_wav, ROOT)}")
    print(f"exact line + word timings written back -> {os.path.relpath(beats_path, ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", required=True, help="path to the short's beats.json")
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--mux", help="optional rendered mp4 to mux the voice onto (-voiced.mp4)")
    ap.add_argument("--emit-ts", help="write the VO (with exact word times) as a TS module, e.g. remotion/src/shots/short-2/vo.gen.ts")
    ap.add_argument("--sequential", action="store_true",
                    help="long-form mode: each line starts right after the previous one ends "
                         "(+ a natural pause), never time-squeezed. Line starts are rewritten; "
                         "format.durationSec is set from the real voice length.")
    ap.add_argument("--pause", type=float, default=0.45, help="sequential: pause after a sentence (s)")
    ap.add_argument("--topic-pause", type=float, default=0.8,
                    help="sequential: pause before a line marked \"topicShift\": true, e.g. a jump in time (s)")
    ap.add_argument("--chapter-pause", type=float, default=1.2,
                    help="sequential: pause before a line marked \"chapterStart\": true (s)")
    ap.add_argument("--blocks", action="store_true",
                    help="long-form: ONE take per chapter (lines marked chapterStart start a new "
                         "chapter) for natural flow; word timings are mapped back to every line")
    ap.add_argument("--speed", type=float, help="ElevenLabs speed (0.7-1.2), e.g. 0.95")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    beats_path = os.path.abspath(args.beats)
    beats = json.load(open(beats_path, encoding="utf-8"))
    vo = beats["vo"]
    total = float(beats["format"]["durationSec"])
    vdir = os.path.join(os.path.dirname(beats_path), "voice")
    os.makedirs(vdir, exist_ok=True)

    key = load_env().get("ELEVENLABS_API_KEY")
    if not key and not args.dry_run:
        sys.exit("ELEVENLABS_API_KEY not found in .env")

    if args.blocks:
        return run_blocks(args, beats, vo, key, vdir, beats_path)

    fitted = []  # (path, start_sec, fitted_dur)
    print(f"{'line':4s} {'start':>6s} {'window':>6s} {'clip':>6s} {'tempo':>5s}  text")
    for i, line in enumerate(vo):
        start = float(line["start"])
        next_start = float(vo[i + 1]["start"]) if i + 1 < len(vo) else total - 0.3
        window = next_start - start - 0.05
        tts_text = line.get("tts", line["text"])  # optional tagged/phonetic variant for TTS
        hkey = f"{args.voice}|{args.model}|{tts_text}" + (f"|speed={args.speed}" if args.speed else "")
        h = hashlib.sha1(hkey.encode()).hexdigest()[:8]
        raw = os.path.join(vdir, f"line-{i:02d}-{h}.mp3")
        fit = os.path.join(vdir, f"line-{i:02d}-{h}-fit.wav")

        if args.dry_run:
            print(f"{i:4d} {start:6.2f} {window:6.2f}      ?     ?  {tts_text}")
            continue

        if args.force or not os.path.exists(raw) or not os.path.exists(raw + ".words.json"):
            prev_text = vo[i - 1].get("tts", vo[i - 1]["text"]) if i > 0 else None
            next_text = vo[i + 1].get("tts", vo[i + 1]["text"]) if i + 1 < len(vo) else None
            tts_line(key, args.voice, args.model, tts_text, prev_text, next_text, raw, args.speed)

        dur = probe_duration(raw)
        tempo = 1.0
        if args.sequential:
            # long-form: the timeline follows the voice, never the other way round
            if fitted:
                _p, prev_start, prev_dur = fitted[-1]
                prev_txt = vo[i - 1]["text"].rstrip()
                gap = args.pause if prev_txt[-1:] in ".?!\"" else 0.12  # mid-sentence split
                if line.get("topicShift"):
                    gap = max(gap, args.topic_pause)
                if line.get("chapterStart"):
                    gap = max(gap, args.chapter_pause)
                start = round(prev_start + prev_dur + gap, 3)
            line["start"] = start
            window = dur + 1.0
        if dur > window:
            tempo = min(MAX_ATEMPO, dur / window)
        if args.force or not os.path.exists(fit):
            run(["ffmpeg", "-y", "-v", "error", "-i", raw,
                 "-filter:a", f"atempo={tempo:.4f}", "-ar", "44100", "-ac", "2", fit])
        fdur = probe_duration(fit)
        overflow = " OVERFLOW" if fdur > window + 0.05 else ""
        print(f"{i:4d} {start:6.2f} {window:6.2f} {fdur:6.2f} {tempo:5.2f}  {line['text']}{overflow}")
        line["end"] = round(start + fdur, 2)
        # exact word times: raw alignment, scaled by the tempo fit, offset to global
        raw_words = json.load(open(raw + ".words.json", encoding="utf-8"))
        line["words"] = [{"w": w["w"],
                          "start": round(start + w["start"] / tempo, 3),
                          "end": round(start + w["end"] / tempo, 3)} for w in raw_words]
        fitted.append((fit, start, fdur))

    if args.dry_run:
        return

    if args.sequential and fitted:
        _p, last_start, last_dur = fitted[-1]
        total = round(last_start + last_dur + 1.5, 2)
        beats["format"]["durationSec"] = total
        print(f"sequential timeline: {total:.1f}s ({int(total // 60)}:{total % 60:04.1f})")

    # assemble: delay each line to its start, sum (lines never overlap), pad to length
    voice_wav = os.path.join(vdir, "voice.wav")
    inputs, parts = [], []
    for j, (path, start, _d) in enumerate(fitted):
        inputs += ["-i", path]
        ms = int(round(start * 1000))
        parts.append(f"[{j}:a]adelay={ms}|{ms}[a{j}]")
    chain = "".join(f"[a{j}]" for j in range(len(fitted)))
    fc = ";".join(parts) + f";{chain}amix=inputs={len(fitted)}:normalize=0,apad,atrim=0:{total}," \
         f"loudnorm=I=-16:TP=-1.5:LRA=11[out]"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc,
         "-map", "[out]", "-ar", "44100", "-ac", "2", voice_wav])
    print(f"voice track -> {os.path.relpath(voice_wav, ROOT)}")

    beats["voiceStatus"] = f"elevenlabs:{args.voice}"
    json.dump(beats, open(beats_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"actual line timings + word maps written back -> {os.path.relpath(beats_path, ROOT)}")

    if args.emit_ts:
        emit_ts(vo, rp := os.path.abspath(args.emit_ts))
        print(f"VO TS module -> {os.path.relpath(rp, ROOT)}")

    if args.mux:
        out = os.path.splitext(args.mux)[0] + "-voiced.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-i", args.mux, "-i", voice_wav,
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-t", str(total), out])
        print(f"voiced preview -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
