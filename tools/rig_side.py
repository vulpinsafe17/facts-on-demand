#!/usr/bin/env python3
"""Side-view rig for walking: from a character sheet's SIDE view, produce
  body.png  head+torso with the drawn arm painted out (arms/legs come from code)
  boot.png  the AI-drawn boot, used as a sprite at the end of each code-drawn leg
  rig.json  anchor points in body.png pixels + leg/arm sizes and colours

  py -3.12 tools/rig_side.py SHEET.png --x0 0.52 --x1 0.68 --out-dir <dir>
"""
import argparse, json, os
import cv2
import numpy as np
from PIL import Image
from scipy import ndimage
from cut_sheet import cut

def runs(row):
    xs = np.where(row)[0]
    return [] if xs.size == 0 else np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)

def build(sheet, x0, x1, out):
    rgba = np.array(cut(sheet, x0, x1)); al = rgba[..., 3] > 0; H, W = al.shape
    rgb = rgba[..., :3].astype(int)
    widths = al.sum(1); torso_w = np.percentile(widths[widths > 0], 80)
    # hem: lowest row that is still one wide run
    hem = next(y for y in range(H - 1, 0, -1) if (lambda rr: len(rr) == 1 and rr[0].size > torso_w * .6)(runs(al[y])))
    # leg + boot below the hem
    legrows = [(y, max(runs(al[y]), key=len)) for y in range(hem + 1, H) if runs(al[y])]
    mid = [r for y, r in legrows if hem + 0.3 * (H - hem) < y < hem + 0.6 * (H - hem)]
    leg_w = int(np.median([r.size for r in mid]))
    lx = int(np.median([r.mean() for r in mid]))
    # boot starts where the leg's inner colour turns from (light) hose to (dark) leather
    def inner(y):
        r = max(runs(al[y]), key=len); c = rgb[y, r.min() + 8:r.max() - 8]
        c = c[c.sum(1) > 90]
        return c.sum(1).mean() if len(c) else 0
    hose_b = np.median([inner(y) for y in range(int(hem + .3 * (H - hem)), int(hem + .5 * (H - hem)))])
    boot_top = next(y for y in range(int(hem + .4 * (H - hem)), H) if inner(y) < hose_b * .8) - 3
    # leg colour = median of non-dark pixels in the leg band
    band = rgb[hem + 8:boot_top - 8, lx - leg_w // 4:lx + leg_w // 4].reshape(-1, 3)
    hose = np.median(band[band.sum(1) > 150], 0).astype(int)
    bootrgb = rgb[boot_top + 10:H - 6, lx - 5:lx + 25].reshape(-1, 3)
    bootc = np.median(bootrgb[bootrgb.sum(1) > 120], 0).astype(int)
    # boot sprite
    bys, bxs = np.where(al[boot_top:])
    boot = Image.fromarray(rgba[boot_top:, :]).crop((bxs.min(), 0, bxs.max() + 1, H - boot_top))
    boot_pivot = [int(lx - bxs.min()), 6]
    # paint out the drawn arm: white hand blob in the torso + the thin dark line above it
    body = rgba[:hem + 3].copy(); b = body[..., :3].astype(int); a = body[..., 3] > 0
    white = (b.min(2) > 232) & a
    lab, n = ndimage.label(white)
    cands = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if ys.mean() > hem * .62 and 200 < ys.size < 0.05 * a.sum():
            cands.append((ys.size, i, int(xs.mean()), int(ys.mean())))
    mask = np.zeros(a.shape, np.uint8)
    hand_xy = None
    if cands:
        _, i, hx, hy = max(cands)
        hand_xy = (hx, hy)
        hm = ndimage.binary_dilation(lab == i, iterations=9)
        mask[hm] = 1
        dark = b.sum(2) < 170
        top = int(hem * .5)
        for y in range(top, hy):
            for r in runs(dark[y, max(0, hx - 30):hx + 30]):
                if r.size <= 22:
                    x = r.mean() + max(0, hx - 30)
                    mask[y, int(x - r.size / 2 - 6):int(x + r.size / 2 + 7)] = 1
    # fill the painted-out arm row by row by mirroring the cloth just beside it,
    # so texture and the rope belt continue across; inpaint whatever is left
    src = body[..., :3].copy(); left = mask.astype(bool).copy()
    for y in range(mask.shape[0]):
        for r in runs(left[y]):
            x0r, x1r = r.min(), r.max(); n = x1r - x0r + 1
            for side in (-1, 1):
                ok = True
                for k in range(n):
                    sx = x0r - 1 - k if side < 0 else x1r + 1 + k
                    if not (0 <= sx < W) or not a[y, sx] or mask[y, sx]:
                        ok = False; break
                if ok:
                    for k in range(n):
                        tx = x0r + k if side < 0 else x1r - k
                        sx = x0r - 1 - k if side < 0 else x1r + 1 + k
                        src[y, tx] = body[y, sx, :3]
                    left[y, x0r:x1r + 1] = False
                    break
    bgr = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)
    fixed = cv2.inpaint(bgr, left.astype(np.uint8) * 255, 5, cv2.INPAINT_TELEA)
    body[..., :3] = cv2.cvtColor(fixed, cv2.COLOR_BGR2RGB)
    # hand area that hung below the hem: make transparent
    body[hem - 2:, :, 3] = np.where(mask[hem - 2:] > 0, 0, body[hem - 2:, :, 3])
    ys, xs = np.where(body[..., 3] > 0)
    x0b, y0b = xs.min(), ys.min()
    part = Image.fromarray(body).crop((x0b, y0b, xs.max() + 1, ys.max() + 1))
    sh_y = int(hem * .58)
    rig = {
        "view": "side", "body": "body.png", "boot": "boot.png", "w": part.size[0], "h": part.size[1],
        "hip": [int(lx - x0b), int(hem - y0b - 10)],
        "shoulder": [int((hand_xy[0] if hand_xy else lx) - x0b), int(sh_y - y0b)],
        "legLen": int(boot_top - hem + 14), "legW": leg_w, "armLen": int((hand_xy[1] if hand_xy else hem) - sh_y),
        "hand": max(10, int(W * .085)), "line": max(4, int(W * .022)),
        "bootPivot": boot_pivot, "bootW": boot.size[0], "bootH": boot.size[1],
        "hose": "#%02x%02x%02x" % tuple(hose), "bootColor": "#%02x%02x%02x" % tuple(bootc), "outline": "#141010",
        "source": os.path.basename(sheet),
    }
    os.makedirs(out, exist_ok=True)
    part.save(f"{out}/body.png"); boot.save(f"{out}/boot.png")
    json.dump(rig, open(f"{out}/rig.json", "w"), indent=2)
    return rig

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("sheet")
    p.add_argument("--x0", type=float, required=True); p.add_argument("--x1", type=float, required=True)
    p.add_argument("--out-dir", required=True); a = p.parse_args()
    print(json.dumps(build(a.sheet, a.x0, a.x1, a.out_dir)))
