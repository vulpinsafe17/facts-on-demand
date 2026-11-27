// Long-form film renderer (src/films-index.ts). Used by the job queue (tools/job_runner.py).
//   node scripts/render-film.mjs Film1                         -> out/Film1.mp4 (full film, 1080p)
//   node scripts/render-film.mjs Film1 --frames=0-899          -> only these frames
//   node scripts/render-film.mjs Film1 --stills=22,57,1922     -> out/qa/Film1-f0022.png ... (QA stills)
//   --scale=0.5 for quick previews
import { bundle } from '@remotion/bundler';
import { selectComposition, renderMedia, renderStill, ensureBrowser } from '@remotion/renderer';
import { mkdirSync, existsSync } from 'fs';
import os from 'os';
import { fileURLToPath } from 'url';
import path from 'path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const opt = (k) => { const a = args.find((x) => x.startsWith(`--${k}=`)); return a ? a.split('=')[1] : undefined; };
const id = args.find((a) => !a.startsWith('--'));
if (!id) { console.error('usage: render-film.mjs <CompositionId> [--frames=a-b] [--stills=1,2] [--scale=1]'); process.exit(2); }
const scale = Number(opt('scale') ?? 1);

// Render browser: Remotion's own (downloaded once, ~113 MB) if it is already here; otherwise
// the Chrome/Edge installed on this PC (a shaky home connection kept cutting the download, and
// a cut download crashes node outright). Only if neither exists, download with retries.
const LOCAL = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
].find((p) => existsSync(p));
const haveShell = existsSync(path.join(root, 'node_modules', '.remotion', 'chrome-headless-shell', 'VERSION'));
let browser = {};
if (!haveShell) {
  // Remotion's own headless browser renders fastest and most reliably: try to fetch it first
  // (a cut download used to crash node, so guard the whole process while it runs).
  let cut = null;
  const guard = (e) => { cut = e; };
  process.on('uncaughtException', guard);
  process.on('unhandledRejection', guard);
  for (let i = 1; i <= 3 && !existsSync(path.join(root, 'node_modules', '.remotion', 'chrome-headless-shell', 'VERSION')); i++) {
    cut = null;
    try {
      await Promise.race([ensureBrowser(), new Promise((_, rej) => {
        const iv = setInterval(() => { if (cut) { clearInterval(iv); rej(cut); } }, 500);
        setTimeout(() => { clearInterval(iv); rej(new Error('download took over 5 min')); }, 300000).unref();
      })]);
    } catch (e) { cut = e; }
    if (cut) { console.log(`browser download try ${i} failed (${cut.code ?? cut.message})`); await new Promise((r) => setTimeout(r, 15000)); }
  }
  process.off('uncaughtException', guard);
  process.off('unhandledRejection', guard);
  if (!existsSync(path.join(root, 'node_modules', '.remotion', 'chrome-headless-shell', 'VERSION'))) {
    if (!LOCAL) throw new Error('no render browser');
    console.log(`using the browser installed on this PC: ${LOCAL}`);
    browser = { browserExecutable: LOCAL, chromeMode: 'chrome-for-testing' };
  }
}
// 16 GB RAM: a loaded ComfyUI model (~10 GB) starves the render tabs (fonts/images time out,
// ffmpeg pipe dies). Ask ComfyUI to unload its models first; harmless if it isn't running.
for (const port of [8188, 8000]) {
  try {
    await fetch(`http://127.0.0.1:${port}/free`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ unload_models: true, free_memory: true }), signal: AbortSignal.timeout(5000) });
    console.log(`asked ComfyUI (port ${port}) to free its memory`);
    await new Promise((r) => setTimeout(r, 5000));
  } catch { /* not running */ }
}
console.log(`free RAM: ${(os.freemem() / 1e9).toFixed(1)} of ${(os.totalmem() / 1e9).toFixed(1)} GB`);
console.log('bundling...');
const serveUrl = await bundle({ entryPoint: path.join(root, 'src', 'films-index.ts'), publicDir: path.join(root, '..', 'media') });
const composition = await selectComposition({ serveUrl, id, ...browser });
const outDir = path.join(root, 'out');

if (opt('stills')) {
  mkdirSync(path.join(outDir, 'qa'), { recursive: true });
  for (const f of opt('stills').split(',').map(Number)) {
    const out = path.join(outDir, 'qa', `${id}-f${String(f).padStart(4, '0')}.png`);
    await renderStill({ serveUrl, composition, frame: f, output: out, scale, imageFormat: 'png', ...browser });
    console.log('still ->', path.relative(root, out));
  }
} else {
  // Rendered in parts of PART frames, each with a fresh browser (a long single render on the
  // 16 GB PC froze/crashed tabs at 25-60 %). Each part is retried, then the picture parts are
  // joined and the sound (rendered once, whole) is laid under them: no clicks at the joins.
  mkdirSync(outDir, { recursive: true });
  const { execFileSync } = await import('child_process');
  const fr = opt('frames');
  const [a0, a1] = fr ? fr.split('-').map(Number) : [0, composition.durationInFrames - 1];
  const name = fr ? `${id}-${fr}` : id;
  const partsDir = path.join(outDir, 'parts', name);
  mkdirSync(partsDir, { recursive: true });
  const PART = Number(opt('part') ?? 900);
  const parts = [];
  for (let s0 = a0; s0 <= a1; s0 += PART) {
    const s1 = Math.min(s0 + PART - 1, a1);
    const out = path.join(partsDir, `v-${String(s0).padStart(6, '0')}.mp4`);
    parts.push(out);
    if (existsSync(out) && !args.includes('--fresh')) { console.log(`part ${s0}-${s1}: already rendered`); continue; }
    for (let attempt = 1; ; attempt++) {
      try {
        await renderMedia({ serveUrl, composition, codec: 'h264', muted: true, outputLocation: out + '.tmp.mp4', scale,
          frameRange: [s0, s1], timeoutInMilliseconds: 120000, ...browser, concurrency: browser.browserExecutable ? 1 : 3 });
        (await import('fs')).renameSync(out + '.tmp.mp4', out);
        console.log(`part ${s0}-${s1} done (${Math.round(((s1 - a0 + 1) / (a1 - a0 + 1)) * 100)}% of the film)`);
        break;
      } catch (e) {
        console.log(`part ${s0}-${s1} failed (try ${attempt}): ${String(e.message ?? e).split('\n')[0]}`);
        if (attempt >= 3) throw e;
        await new Promise((r) => setTimeout(r, 10000));
      }
    }
  }
  console.log('rendering the sound...');
  const audio = path.join(partsDir, 'audio.wav');
  await renderMedia({ serveUrl, composition, codec: 'wav', outputLocation: audio, frameRange: [a0, a1], timeoutInMilliseconds: 120000, ...browser });
  const list = path.join(partsDir, 'list.txt');
  (await import('fs')).writeFileSync(list, parts.map((p) => `file '${p.replace(/\\/g, '/')}'`).join('\n'));
  const out = path.join(outDir, `${name}.mp4`);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-i', audio,
    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', out], { stdio: 'inherit' });
  console.log('video ->', path.relative(root, out));
}
