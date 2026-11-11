"""
ARC v3 - commandes d'apres les photos (kit NINE HANDS | DSP + LED fournie pour ARC, nov. 2026).
Repris de tools/photo_controls.py de Strong Pickle (potard, footswitch, jack), LED : assets/kit/led_sphere_red.png.
"""
import os
import numpy as np, cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(os.path.dirname(HERE), 'assets', 'kit')

KNOB_C, KNOB_RPX = (437.0, 419.5), 350.0          # centre et rayon exterieur du potard dans la photo (px)
IND_R0, IND_R1, IND_W = 0.45, 0.97, 0.034          # repere de la photo : rayons debut / fin et demi-largeur (x rayon)
FS_C, FS_FLATS_PX, FS_BTN_PX = (625.5, 618.0), 718.0, 272.0
JACK_BOX = (46, 558, 80, 188)
LED_C, LED_RPX = (74.5, 74.5), 47.0                # LED fournie : sphere rouge 150 x 150


def _load(name):
    return np.asarray(Image.open(os.path.join(KIT, name)).convert('RGBA')).astype(np.float32)


def _polar(h, w):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xx - KNOB_C[0], yy - KNOB_C[1]
    return np.hypot(dx, dy), np.arctan2(dx, -dy)


def knob_clean():
    """photo du potard sans son repere blanc (interpolation angulaire a rayon constant)"""
    im = _load('knob_photo.png')
    h, w = im.shape[:2]
    r, th = _polar(h, w)
    R = KNOB_RPX
    half = (IND_W * R + 10.0) / np.maximum(r, 1.0)
    m = (r > IND_R0 * R - 22) & (r < IND_R1 * R + 4) & (np.abs(th) < half)
    out = im.copy()
    ys, xs = np.where(m)
    rr, tt, hh = r[ys, xs], th[ys, xs], half[ys, xs] + 2.0 / np.maximum(r[ys, xs], 1.0)
    def sample(ang):
        sx = KNOB_C[0] + rr * np.sin(ang); sy = KNOB_C[1] - rr * np.cos(ang)
        return np.stack([cv2.remap(im[..., ch], sx.reshape(-1, 1).astype(np.float32), sy.reshape(-1, 1).astype(np.float32),
                                   cv2.INTER_LINEAR).ravel() for ch in range(4)], -1)
    left, right = sample(-hh), sample(hh)
    t = np.clip((tt + hh) / (2 * hh), 0, 1)[:, None]
    fill = left * (1 - t) + right * t
    fill[:, :3] += np.random.default_rng(5).normal(0, 1.6, len(ys))[:, None]
    out[ys, xs] = fill
    return out


def knob_marker():
    """repere blanc seul (RGBA), extrait de la photo par difference avec le potard nettoye"""
    im = _load('knob_photo.png'); cl = knob_clean()
    h, w = im.shape[:2]
    r, th = _polar(h, w)
    R = KNOB_RPX
    zone = (r > IND_R0 * R - 26) & (r < IND_R1 * R + 6) & (np.abs(th) < (IND_W * R + 14.0) / np.maximum(r, 1.0))
    li, lc = im[..., :3].mean(2), cl[..., :3].mean(2)
    a = np.clip((li - lc) / np.maximum(235.0 - lc, 1.0), 0, 1) * zone
    a = cv2.GaussianBlur(a.astype(np.float32), (0, 0), 0.6)
    col = np.where(a[..., None] > 1e-3, (im[..., :3] - (1 - a[..., None]) * cl[..., :3]) / np.maximum(a[..., None], 1e-3), 0)
    col = np.clip(col, 0, 255)
    return np.dstack([col, a * 255]).astype(np.float32)


def _place(src, c, k, n):
    pm = src.copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
    k1 = min(1.0, k * 2.0); f = k1 / k
    n1 = int(round(n * f))
    M1 = np.float32([[k1, 0, n1 / 2 - c[0] * k1], [0, k1, n1 / 2 - c[1] * k1]])
    big = cv2.warpAffine(pm, M1, (n1, n1), flags=cv2.INTER_AREA, borderValue=0)
    small = cv2.resize(big, (n, n), interpolation=cv2.INTER_AREA)
    a = np.clip(small[..., 3] / 255.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-4, small[..., :3] / np.maximum(a, 1e-4)[..., None], 0)
    return rgb, a


ORANGE = np.array([255.0, 146.0, 40.0])
CYAN = np.array([46.0, 226.0, 255.0])

def led_variants(r_px, pad=1.5, scale=1):
    """LED de rayon r_px : {'off', 'orange', 'cyan'} -> (rgb, alpha) dans un carre de 2 r pad px (x scale)"""
    im = _load('led_sphere_red.png')
    rgb = im[..., :3]; a = im[..., 3] / 255.0
    lum = rgb.max(2) / 255.0                                  # intensite (la LED rouge sature R)
    white = np.clip((rgb[..., 1] - 40) / 200.0, 0, 1)         # zones blanchies (reflet / coeur)
    hsv = cv2.cvtColor(np.clip(rgb, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    def tint(col):
        # meme photo, seule la teinte change (structure interne et reflets gardes)
        hue = cv2.cvtColor(np.uint8([[col]]), cv2.COLOR_RGB2HSV)[0, 0, 0].astype(np.float32)
        h2 = hsv.copy()
        h2[..., 0] = (hsv[..., 0] + (hue - 0.0)) % 180
        out = cv2.cvtColor(np.clip(h2, 0, 255).astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
        return out
    # eteinte : lentille fumee sombre, le reflet en haut a gauche reste visible
    g = rgb.mean(2)
    off = np.dstack([g, g, g]) * 0.10 + 14
    yy, xx = np.mgrid[0:im.shape[0], 0:im.shape[1]].astype(np.float32)
    hl = np.exp(-(((xx - LED_C[0] + 0.35 * LED_RPX) / (0.25 * LED_RPX)) ** 2 + ((yy - LED_C[1] + 0.40 * LED_RPX) / (0.18 * LED_RPX)) ** 2))
    off += (hl * 85)[..., None]
    n = int(round(2 * r_px * pad * scale)); k = r_px * scale / LED_RPX
    out = {}
    for key, col in (('off', off), ('orange', tint(ORANGE)), ('cyan', tint(CYAN))):
        out[key] = _place(np.dstack([col, a * 255]).astype(np.float32), LED_C, k, n)
    return out
