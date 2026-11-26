// Long-form film renderer (src/films-index.ts). Used by the job queue (tools/job_runner.py).
//   node scripts/render-film.mjs Film1                         -> out/Film1.mp4 (full film, 1080p)
//   node scripts/render-film.mjs Film1 --frames=0-899          -> only these frames
//   node scripts/render-film.mjs Film1 --stills=22,57,1922     -> out/qa/Film1-f0022.png ... (QA stills)
//   --scale=0.5 for quick previews
import { bundle } from '@remotion/bundler';
import { selectComposition, renderMedia, renderStill, ensureBrowser } from '@remotion/renderer';
import { mkdirSync } from 'fs';
import { fileURLToPath } from 'url';
import path from 'path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const opt = (k) => { const a = args.find((x) => x.startsWith(`--${k}=`)); return a ? a.split('=')[1] : undefined; };
const id = args.find((a) => !a.startsWith('--'));
if (!id) { console.error('usage: render-film.mjs <CompositionId> [--frames=a-b] [--stills=1,2] [--scale=1]'); process.exit(2); }
const scale = Number(opt('scale') ?? 1);

// The render browser is downloaded once (~113 MB). A shaky home connection can cut the
// download, so try a few times before giving up.
for (let i = 1; ; i++) {
  try { await ensureBrowser(); break; } catch (e) {
    if (i >= 6) throw e;
    console.log(`browser download failed (${e.code ?? e.message}), retry ${i}/5 in 20 s...`);
    await new Promise((r) => setTimeout(r, 20000));
  }
}
console.log('bundling...');
const serveUrl = await bundle({ entryPoint: path.join(root, 'src', 'films-index.ts'), publicDir: path.join(root, '..', 'media') });
const composition = await selectComposition({ serveUrl, id });
const outDir = path.join(root, 'out');

if (opt('stills')) {
  mkdirSync(path.join(outDir, 'qa'), { recursive: true });
  for (const f of opt('stills').split(',').map(Number)) {
    const out = path.join(outDir, 'qa', `${id}-f${String(f).padStart(4, '0')}.png`);
    await renderStill({ serveUrl, composition, frame: f, output: out, scale, imageFormat: 'png' });
    console.log('still ->', path.relative(root, out));
  }
} else {
  mkdirSync(outDir, { recursive: true });
  const fr = opt('frames');
  const frameRange = fr ? fr.split('-').map(Number) : undefined;
  const out = path.join(outDir, fr ? `${id}-${fr}.mp4` : `${id}.mp4`);
  let last = -1;
  await renderMedia({
    serveUrl, composition, codec: 'h264', outputLocation: out, scale, frameRange,
    timeoutInMilliseconds: 120000,
    onProgress: ({ progress }) => { const p = Math.floor(progress * 20); if (p !== last) { last = p; console.log(`render ${p * 5}%`); } },
  });
  console.log('video ->', path.relative(root, out));
}
