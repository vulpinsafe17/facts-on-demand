"""Procedural lip-sync overlays from front-base itself (always perfectly aligned):
the lower half of the beak drops by N px and the gap shows a dark mouth.
Writes cut/overlay-beak-1.png (half open) and cut/overlay-beak-2.png (open)."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage
d = sys.argv[1]
base = np.asarray(Image.open(f'{d}/front-base.png')).astype(float)
H, W = base.shape[:2]
r, g, b, a = (base[..., i] for i in range(4))
orange = (r > 190) & (g > 70) & (g < 175) & (b < 90) & (a > 200)
lab, n = ndimage.label(orange)
sizes = ndimage.sum(orange, lab, range(1, n + 1))
beak = lab == (1 + int(np.argmax(sizes)))
beak = ndimage.binary_fill_holes(ndimage.binary_dilation(beak, iterations=2))
outline = ndimage.binary_dilation(beak, iterations=9) & ~beak       # the black ink around it
ys, xs = np.nonzero(beak)
split = int(ys.min() + 0.55 * (ys.max() - ys.min()))
full = beak | outline
CREAM = np.median(base[(a > 250) & (base[..., :3].mean(-1) > 215)][:, :3], 0)
MOUTH = np.array([70, 22, 14.])
for lvl, drop in ((1, 12), (2, 24)):
    o = np.zeros((H, W, 4))
    yy = np.arange(H)[:, None]
    lower = full & (yy >= split)
    # 1) erase the lower part (face colour) where it will move away from
    o[lower] = [*CREAM, 255]
    # 2) mouth: the beak's width at the split row, stretched over the gap
    row = np.nonzero(full[split])[0]
    x0, x1 = row.min(), row.max()
    for y in range(split, split + drop):
        t = (y - split) / max(drop, 1)
        inset = int(t * (x1 - x0) * 0.12)
        o[y, x0 + inset:x1 - inset + 1] = [0, 0, 0, 255]                  # ink sides
        o[y, x0 + inset + 7:x1 - inset - 6] = [*MOUTH, 255]                # mouth inside
    # 3) the lower beak, moved down
    src = np.zeros_like(base); src[lower] = base[lower]
    moved = np.roll(src, drop, 0)
    mm = moved[..., 3] > 0
    o[mm] = moved[mm]
    Image.fromarray(o.clip(0, 255).astype(np.uint8)).save(f'{d}/overlay-beak-{lvl}.png', optimize=True)
print('beak split', split, 'width', x1 - x0)
