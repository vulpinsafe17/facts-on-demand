#!/usr/bin/env python3
"""Cut a character-sheet front view into PUPPET PARTS that are all AI pixels:
body (head+torso), armL, armR, legL, legR (each leg incl. its boot).
Code only rotates these parts around their joints (shoulder / hip): the arms and
legs on screen are always the drawn ones (owner's rule: no code-drawn arms).

  py -3.12 tools/puppet_parts.py SHEET.png --x0 0.04 --x1 0.23 --out-dir <dir>
"""
import argparse, json, os
import numpy as np
from PIL import Image
from scipy import ndimage
from cut_sheet import cut

def build(sheet, x0, x1, out):
    a = np.array(cut(sheet, x0, x1)); al = a[..., 3] > 0; H, W = al.shape
    r = max(3, int(W * .035))
    opened = ndimage.binary_opening(al, ndimage.generate_binary_structure(2, 1), iterations=r)
    lab, n = ndimage.label(opened); sizes = ndimage.sum(opened, lab, range(1, n + 1))
    core = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > .06 * opened.sum()])
    core = ndimage.binary_dilation(core, iterations=r) & al
    def runs(row):
        xs = np.where(row)[0]
        return [] if xs.size == 0 else np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)
    bottom = np.where(core.any(1))[0].max(); hem = bottom
    for y in range(bottom, int(H * .45), -1):
        if len(runs(core[y])) >= 2: hem = y
        else: break
    legs_visible = bottom - hem >= H * .06
    body = core.copy()
    if legs_visible: body[hem + 1:] = False
    lab2, n2 = ndimage.label(body); s2 = ndimage.sum(body, lab2, range(1, n2 + 1))
    body = np.isin(lab2, [i + 1 for i, s in enumerate(s2) if s > .06 * body.sum()])
    # arms: each drawn mitten hand survives the opening as a small round blob; the arm
    # is that hand plus the thin line pieces touching it (not the body outline)
    cx = int(np.median(np.where(body)[1]))
    hands = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if .002 * opened.sum() < s <= .06 * opened.sum()])
    if legs_visible: hands[hem - 2:] &= False
    thin = al & ~ndimage.binary_dilation(opened, iterations=2)
    if legs_visible: thin[hem + 1:] = False
    labT, nT = ndimage.label(thin)
    labH, nH = ndimage.label(hands)
    parts = {}
    os.makedirs(out, exist_ok=True)
    def save(mask, name):
        ys, xs = np.where(mask)
        if ys.size < 150: return
        x0b, y0b, x1b, y1b = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        rgba = a.copy(); rgba[..., 3] = np.where(mask, a[..., 3], 0)
        Image.fromarray(rgba).crop((x0b, y0b, x1b, y1b)).save(f"{out}/{name}.png")
        top = xs[ys <= y0b + 3]
        parts[name] = {"file": f"{name}.png", "x": int(x0b), "y": int(y0b), "w": int(x1b - x0b), "h": int(y1b - y0b),
                       "pivot": [int(top.mean()) - int(x0b), 2]}
    arms = {}
    for i in range(1, nH + 1):
        hm = labH == i
        hm = ndimage.binary_dilation(hm, iterations=2) & al
        touch = np.unique(labT[ndimage.binary_dilation(hm, iterations=4)]); touch = touch[touch > 0]
        m = hm | np.isin(labT, touch)
        side = 'armL' if np.where(hm)[1].mean() < cx else 'armR'
        arms[side] = arms.get(side, np.zeros_like(al)) | m
    for nm, m in arms.items():
        save(m, nm)
        body &= ~m
    comps = []
    if legs_visible:
        low = al.copy(); low[:hem + 1] = False
        labL, nL = ndimage.label(low)
        comps = sorted([(np.where(labL == i)[1].mean(), i) for i in range(1, nL + 1) if (labL == i).sum() > 150])
        if len(comps) >= 2:
            save(labL == comps[0][1], "legL"); save(labL == comps[-1][1], "legR")
        else:
            body = body | low
    # body = everything that is not a limb (keeps the full outline of the clothes)
    body = al.copy()
    for p in parts.values():
        pass
    for nm, m in arms.items(): body &= ~m
    if legs_visible and len(comps) >= 2: body[hem + 1:] = False
    lab3, n3 = ndimage.label(body); s3 = ndimage.sum(body, lab3, range(1, n3 + 1))
    body = np.isin(lab3, [i + 1 for i, s in enumerate(s3) if s > .02 * body.sum()])
    ys, xs = np.where(body)
    rgba = a.copy(); rgba[..., 3] = np.where(body, a[..., 3], 0)
    Image.fromarray(rgba).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)).save(f"{out}/pbody.png")
    parts["body"] = {"file": "pbody.png", "x": int(xs.min()), "y": int(ys.min()), "w": int(xs.max() + 1 - xs.min()), "h": int(ys.max() + 1 - ys.min())}
    meta = {"W": W, "H": H, "parts": parts}
    json.dump(meta, open(f"{out}/puppet.json", "w"), indent=2)
    return meta

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("sheet")
    p.add_argument("--x0", type=float, required=True); p.add_argument("--x1", type=float, required=True)
    p.add_argument("--out-dir", required=True); a = p.parse_args()
    print(json.dumps(build(a.sheet, a.x0, a.x1, a.out_dir)))
