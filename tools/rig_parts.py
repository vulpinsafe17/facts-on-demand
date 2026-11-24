#!/usr/bin/env python3
"""Split a character-sheet body view into a rig: head+torso PNG (arms/legs removed)
plus anchor points (shoulders, hips) and limb style, for code-drawn stick limbs.

  py -3.12 tools/rig_parts.py SHEET.png --x0 0.05 --x1 0.22 --out-dir media/library/characters/<c>/rigs/<era>
Writes body.png and rig.json (pixel coords inside body.png).
"""
import argparse, json, os
import numpy as np
from PIL import Image
from scipy import ndimage
from cut_sheet import cut

def build(sheet, x0, x1, out_dir):
    im = cut(sheet, x0, x1)
    a = np.array(im); al = a[..., 3] > 0
    H, W = al.shape
    # 1) remove thin stick lines (arms) with an opening, keep the biggest blob
    r = max(3, int(W * 0.035))
    st = ndimage.generate_binary_structure(2, 1)
    opened = ndimage.binary_opening(al, structure=st, iterations=r)
    lab, n = ndimage.label(opened)
    sizes = ndimage.sum(opened, lab, range(1, n + 1))
    main = lab == (1 + int(np.argmax(sizes)))
    # 2) tunic hem = lowest row where the blob is ONE wide run (legs/boots are two runs)
    def runs(row):
        xs = np.where(row)[0]
        if xs.size == 0: return []
        cuts = np.where(np.diff(xs) > 1)[0]
        return np.split(xs, cuts + 1)
    widths = main.sum(1)
    torso_w = np.percentile(widths[widths > 0], 75)
    hem = None
    for y in range(H - 1, 0, -1):
        rr = runs(main[y])
        if len(rr) == 1 and rr[0].size > torso_w * 0.6:
            hem = y; break
    body = ndimage.binary_dilation(main, iterations=r) & al
    body[hem + 1:] = False
    # keep only the component that holds the torso centre
    lab, n = ndimage.label(body)
    cy = int(hem * 0.85); cx = int(np.median(np.where(body[cy])[0]))
    body = lab == lab[cy, cx]
    # legs start under the hem; measure their length from the original cut-out
    leg_len = H - hem
    out = a.copy(); out[..., 3] = np.where(body, a[..., 3], 0)
    ys, xs = np.where(body)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    part = Image.fromarray(out).crop(box)
    bw, bh = part.size
    bodyc = body[box[1]:box[3], box[0]:box[2]]
    # shoulders: where the torso first becomes wide (below the head/scarf)
    wid = bodyc.sum(1)
    neck = int(np.argmin(wid[int(bh*0.35):int(bh*0.6)])) + int(bh*0.35)
    sh_y = neck + int(bh * 0.07)
    row = np.where(bodyc[sh_y])[0]
    hip_row = np.where(bodyc[bh - 3])[0]
    rig = {
        "body": "body.png", "w": bw, "h": bh,
        "shoulderL": [int(row.min()) + 4, sh_y], "shoulderR": [int(row.max()) - 4, sh_y],
        "hipL": [int(hip_row.min() + np.ptp(hip_row) * 0.3), bh - 6], "hipR": [int(hip_row.min() + np.ptp(hip_row) * 0.7), bh - 6],
        "armLen": int(bh * 0.42), "legLen": leg_len, "line": max(4, int(W * 0.018)), "hand": int(W * 0.075),
        "source": os.path.basename(sheet),
    }
    os.makedirs(out_dir, exist_ok=True)
    part.save(os.path.join(out_dir, "body.png"))
    json.dump(rig, open(os.path.join(out_dir, "rig.json"), "w"), indent=2)
    return rig

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("sheet")
    p.add_argument("--x0", type=float, required=True); p.add_argument("--x1", type=float, required=True)
    p.add_argument("--out-dir", required=True); a = p.parse_args()
    print(json.dumps(build(a.sheet, a.x0, a.x1, a.out_dir), indent=1))
