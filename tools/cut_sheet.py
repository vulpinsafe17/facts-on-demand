#!/usr/bin/env python3
"""Cut one full-body view out of a character sheet into a transparent PNG.

The sheets have a plain off-white background and a dark ground line under the
four body views. Background = regions of background colour that touch the crop
border (plus enclosed holes whose colour matches the background; the pure-white heads and hands are kept). The ground line is
removed except directly under the boots, so the soles stay whole.

  py -3.12 tools/cut_sheet.py SHEET.png --x0 0.05 --x1 0.22 --out cutout.png
  (x0/x1 = left/right edge of the view as a fraction of sheet width;
   front view ~0.05-0.22, three-quarter ~0.28-0.45, side ~0.52-0.66, back ~0.76-0.94)
"""
import argparse
import numpy as np
from PIL import Image
from scipy import ndimage

def cut(path, x0, x1, tol=60):
    a = np.array(Image.open(path).convert("RGB")).astype(int)
    H, W, _ = a.shape
    dark = a.sum(2) < 200
    rows = [r for r in range(int(H * .4), int(H * .65)) if dark[r, int(W * .1):int(W * .9)].mean() > .6]
    if not rows:
        raise SystemExit("ground line not found")
    gt, gb = min(rows) - 3, max(rows) + 3
    X0, X1 = int(x0 * W), int(x1 * W)
    s, dk = a[:gb + 1, X0:X1], dark[:gb + 1, X0:X1]
    bg = np.median(s[:20, :20].reshape(-1, 3), 0)
    d = np.abs(s - bg).sum(2) < tol
    boot = ndimage.binary_dilation(~d[gt - 2], iterations=3)
    d[gt:] = True
    lab, _ = ndimage.label(d)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    bgm = np.isin(lab, list(border))
    # enclosed holes (e.g. between arm and body): remove a hole if its colour is
    # closer to the sheet background than to the pure white of the heads/hands
    white = np.array([255, 255, 255])
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if i in border or sl is None:
            continue
        m = lab[sl] == i
        mean = s[sl][m].mean(0)
        if np.abs(mean - bg).sum() < np.abs(mean - white).sum():
            bgm[sl] |= m
    fg = ~bgm
    for r in range(gt, gb + 1):
        fg[r] = boot & dk[r]
    alpha = (fg * 255).astype(np.uint8)
    im = Image.fromarray(np.dstack([s, alpha]).astype(np.uint8), "RGBA")
    ys, xs = np.where(alpha > 0)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("sheet"); p.add_argument("--x0", type=float, required=True)
    p.add_argument("--x1", type=float, required=True); p.add_argument("--out", required=True)
    p.add_argument("--tol", type=int, default=60)
    a = p.parse_args()
    cut(a.sheet, a.x0, a.x1, a.tol).save(a.out)
    print("wrote", a.out)
