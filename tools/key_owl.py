"""Green-screen key for the ComfyUI owl poses -> transparent PNGs, tightly cropped to a
shared canvas so all poses line up (feet on the same baseline, owl centred)."""
import sys, os, numpy as np
from PIL import Image
from scipy import ndimage

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
CREAM = np.array([247, 241, 226], float)
out = {}
for fn in sorted(os.listdir(src)):
    if not fn.endswith('.png'): continue
    a = np.asarray(Image.open(os.path.join(src, fn)).convert('RGB')).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = g - np.maximum(r, b)                 # how "green-screen" a pixel is
    alpha = np.clip(1 - (green - 25) / 60, 0, 1)  # soft edge between 25 and 85
    # despill: no green cast on the ink edges
    g2 = np.minimum(g, np.maximum(r, b) + 8)
    rgb = np.stack([r, g2, b], -1)
    # lens / closed holes: fill enclosed transparent regions that are round (the glass);
    # other enclosed gaps (between wing and body) stay transparent: rule "gaps show the background"
    hole = alpha < 0.5
    lab, n = ndimage.label(hole)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    for k in range(1, n + 1):
        if k in border: continue
        m = lab == k
        ys, xs = np.nonzero(m)
        h, w = np.ptp(ys) + 1, np.ptp(xs) + 1
        fill = m.sum() / (h * w)
        if m.sum() > 1500 and 0.6 < h / w < 1.6 and fill > 0.6:   # round and big = lens
            mm = ndimage.binary_dilation(m, iterations=3) & (alpha < 1)
            rgb[mm] = CREAM; alpha[mm] = 1
            print(f'{fn}: lens filled ({m.sum()} px)')
    rgba = np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8)
    out[fn] = rgba

# shared crop: union bbox of all poses, so swapping poses never jumps
bb = None
for rgba in out.values():
    ys, xs = np.nonzero(rgba[..., 3] > 20)
    b = [ys.min(), ys.max(), xs.min(), xs.max()]
    bb = b if bb is None else [min(bb[0], b[0]), max(bb[1], b[1]), min(bb[2], b[2]), max(bb[3], b[3])]
pad = 12
y0, y1, x0, x1 = max(bb[0] - pad, 0), bb[1] + pad, max(bb[2] - pad, 0), bb[3] + pad
for fn, rgba in out.items():
    Image.fromarray(rgba[y0:y1, x0:x1]).save(os.path.join(dst, fn), optimize=True)
print('canvas', x1 - x0, 'x', y1 - y0)
