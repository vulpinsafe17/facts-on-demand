"""Make the owl puppet's lip-sync and blink overlays: patches cut from front-talk / front-blink,
aligned onto front-base (phase correlation), colour-matched, with a feathered mask.
Output: cut/overlay-beak-open.png, cut/overlay-eyes-closed.png (same canvas as front-base)."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage
d = sys.argv[1]
L = lambda n: np.asarray(Image.open(f'{d}/{n}.png')).astype(float)
base = L('front-base')
H, W = base.shape[:2]

def gray(a):  # ink map: dark & opaque
    return (255 - a[..., :3].mean(-1)) * (a[..., 3] / 255)

def shift_between(a, b, box):
    y0, y1, x0, x1 = box
    A, B = gray(a)[y0:y1, x0:x1], gray(b)[y0:y1, x0:x1]
    A, B = A - A.mean(), B - B.mean()
    R = np.fft.fft2(A) * np.conj(np.fft.fft2(B)); R /= np.abs(R) + 1e-9
    c = np.real(np.fft.ifft2(R)); dy, dx = np.unravel_index(np.argmax(c), c.shape)
    if dy > c.shape[0] // 2: dy -= c.shape[0]
    if dx > c.shape[1] // 2: dx -= c.shape[1]
    return dy, dx  # move b by (dy,dx) to match a

def bright_median(a, mask):
    sel = mask & (a[..., :3].mean(-1) > 200) & (a[..., 3] > 250)
    return np.median(a[sel][:, :3], 0)

def make(name, box_face, patch_ellipses, out):
    p = L(name)
    dy, dx = shift_between(base, p, box_face)
    p = np.roll(p, (dy, dx), (0, 1))
    m = np.zeros((H, W), bool)
    yy, xx = np.mgrid[:H, :W]
    for cx, cy, rx, ry in patch_ellipses:
        m |= ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    face = np.zeros((H, W), bool); face[box_face[0]:box_face[1], box_face[2]:box_face[3]] = True
    gain = bright_median(base, face) / bright_median(p, face)   # match cream vs white
    p[..., :3] = np.clip(p[..., :3] * gain, 0, 255)
    feather = ndimage.gaussian_filter(m.astype(float), 3)
    a = feather * (p[..., 3] / 255)
    o = np.dstack([p[..., :3], a * 255]).astype(np.uint8)
    Image.fromarray(o).save(f'{d}/{out}.png', optimize=True)
    print(out, 'shift', dy, dx, 'gain', gain.round(3))

# locate pupils on base: two biggest dark blobs in the face area
ink = (base[..., :3].mean(-1) < 60) & (base[..., 3] > 200)
lab, n = ndimage.label(ink)
cands = []
for k in range(1, n + 1):
    ys, xs = np.nonzero(lab == k); s = len(ys)
    h, w = np.ptp(ys) + 1, np.ptp(xs) + 1
    if 1500 < s < 12000 and 0.7 < h / w < 1.4 and s / (h * w) > 0.6:
        cands.append((s, xs.mean(), ys.mean(), w, h))
cands = sorted(cands, reverse=True)[:2]
cands = sorted(cands, key=lambda c: c[1])
print('pupils', [(round(c[1]), round(c[2]), c[3]) for c in cands])
(_, lx, ly, lw, _), (_, rx_, ry, rw, _) = cands
eye_r = max(lw, rw) * 1.25                   # white of the eye ~2.5x the pupil
beak = (base[..., 0] > 200) & (base[..., 1] > 80) & (base[..., 1] < 170) & (base[..., 2] < 80) & (base[..., 3] > 200)
by, bx = np.nonzero(beak); bcx, bcy = bx.mean(), by.mean(); bh = np.ptp(by)
face_box = (int(min(ly, ry) - 2.4 * eye_r), int(bcy + 2.5 * bh), int(lx - 2.2 * eye_r), int(rx_ + 2.2 * eye_r))
face_box = (max(face_box[0], 0), min(face_box[1], H), max(face_box[2], 0), min(face_box[3], W))
make('front-blink', face_box, [(lx, ly, eye_r * 1.02, eye_r * 1.02), (rx_, ry, eye_r * 1.02, eye_r * 1.02)], 'overlay-eyes-closed')

import json
json.dump({'eyes': [[round(lx), round(ly)], [round(rx_), round(ry)]], 'eye_r': round(eye_r), 'beak': [round(bcx), round(bcy)],
           'canvas': [W, H]}, open(f'{d}/rig.json', 'w'), indent=1)
