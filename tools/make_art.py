"""
ARC v3 (NINE HANDS | DSP) - fond du plugin d'apres design/Arc_Mockup_v003.svg (2350 x 1800, format double).

Repere : 1 px de l'image = 0,5 unite du plugin (repere 1175 x 900).
Tout est calcule a la resolution finale ou reduit depuis une source plus grande (jamais d'agrandissement) :
  - coque, bevel rond de 64 px (metal), plaque grise lisse, ecrans, boutons : rendus procedurals a 2350 x 1800 ;
  - potards, footswitchs, jacks : photos du kit (assets/kit) reduites ;
  - LED : photo de l'utilisateur (assets/kit/led_sphere_red.png, 150 px) reduite et recoloree.
Lumiere : en haut a gauche, a 45 deg ; ombres portees a 45 deg vers le bas a droite + occlusion de contact.

Sorties (assets/) : background.png (RGBA), knob_marker.png, led_*.png, glow_*.png ; tools/layout.json.
"""
import os, sys, json, re
import numpy as np, cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KIT = os.path.join(ROOT, 'assets', 'kit')
OUT = os.path.join(ROOT, 'assets')
sys.path.insert(0, HERE)

W, H = 2350, 1800
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(3)

# ------------------------------------------------------------------ geometrie (maquette v003, pixels de l'image)
BODY = (40.0, 0.0, 2310.0, 1800.0, 98.8)                 # x0, y0, x1, y1, rayon des coins
BEVEL = 64.0
KNOBS = [(274.36 + 300 * i, 300.0) for i in range(7)]
KNOB_R = 105.0
MODE_BTN = (274.36, 710.0, 45.0)
MODE_LED = (274.36, 583.01, 16.0)
VOICE_BTNS = [(543.11, 670.0, 330.0, 80.0), (1009.36, 670.0, 330.0, 80.0), (1475.57, 670.0, 330.0, 80.0)]
VOICE_LEDS = [(586.11, 710.0, 18.5), (1052.36, 710.0, 18.5), (1518.57, 710.0, 18.5)]
BTN_R = 21.6
SCREEN_TOP = (406.86, 864.0, 1535.0, 72.0, 18.32)
SCREEN_MAIN = (406.86, 955.0, 1535.0, 190.0, 18.32)
PRESET_LEDS = [(631.86 + 155 * i, 1335.0, 16.0) for i in range(8)]
FOOTS = [(406.86, 1480.0), (1941.86, 1480.0)]
FS_FLATS = 216.42                                         # hexagone : distance entre plats
FS_BTN_R = 80.6
SCREWS = [(129.94, 90.0), (2220.0, 90.0), (2220.0, 1710.0), (129.94, 1710.0)]   # (maquette : 94,31 en bas a gauche -> recentre sur l'encoche)
SCREW_R = 30.0
JACKS = [(-1, 808.5, 'OUT L'), (-1, 1145.0, 'OUT R'), (1, 808.5, 'IN L'), (1, 1145.0, 'IN R')]
JACK_LEN, JACK_DEPTH = 204.75, 40.0
LIGHT = np.array([-1.0, -1.0, 1.25]); LIGHT /= np.linalg.norm(LIGHT)

# ------------------------------------------------------------------ outils
def rrect_alpha(x0, y0, x1, y1, r, ss=4):
    """masque anti-crenele d'un rectangle arrondi"""
    hw, hh = (x1 - x0) / 2, (y1 - y0) / 2
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    qx = np.abs(xx - cx) - (hw - r); qy = np.abs(yy - cy) - (hh - r)
    d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
    return np.clip(0.5 - d, 0, 1), d

def circle_alpha(cx, cy, r):
    d = np.hypot(xx - cx, yy - cy) - r
    return np.clip(0.5 - d, 0, 1), d

def shift(a, dx, dy):
    return cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (a.shape[1], a.shape[0]), borderValue=0)

def over(dst, rgb, a, x0=0, y0=0):
    """compose rgb/alpha (float) sur dst (float HxWx3) a la position x0, y0"""
    h, w = a.shape[:2]
    X0, Y0 = max(0, x0), max(0, y0); X1, Y1 = min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0: return
    sa = a[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0][..., None]
    dst[Y0:Y1, X0:X1] = dst[Y0:Y1, X0:X1] * (1 - sa) + rgb[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * sa

def darken(dst, amt):
    dst *= (1 - np.clip(amt, 0, 0.95))[..., None]

def cast_shadow(mask, size, amount=0.55, contact=0.5):
    """ombre portee a 45 deg vers le bas a droite + occlusion de contact, d'apres un masque plein cadre"""
    o = 0.045 * size
    cast = cv2.GaussianBlur(shift(mask, o, o), (0, 0), 0.05 * size) * amount
    cont = cv2.GaussianBlur(shift(mask, 0.008 * size, 0.008 * size), (0, 0), 0.014 * size) * contact
    return np.clip(cast + cont, 0, 0.88) * (1 - mask)

def load(name):
    return np.asarray(Image.open(os.path.join(KIT, name)).convert('RGBA')).astype(np.float32)

def place(src, c, k, n_w, n_h=None):
    """reduit (alpha premultiplie) la photo src : point c au centre d'un cadre n_w x n_h ; k = echelle (< 1)"""
    n_h = n_h or n_w
    pm = src.copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
    k1 = min(1.0, k * 2.0); f = k1 / k
    w1, h1 = int(round(n_w * f)), int(round(n_h * f))
    M1 = np.float32([[k1, 0, w1 / 2 - c[0] * k1], [0, k1, h1 / 2 - c[1] * k1]])
    big = cv2.warpAffine(pm, M1, (w1, h1), flags=cv2.INTER_AREA, borderValue=0)
    small = cv2.resize(big, (n_w, n_h), interpolation=cv2.INTER_AREA)
    a = np.clip(small[..., 3] / 255.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-4, small[..., :3] / np.maximum(a, 1e-4)[..., None], 0)
    return rgb, a

def put_sprite(dst, shadow_acc, rgb, a, cx, cy, size, amount=0.55, contact=0.5):
    n_h, n_w = a.shape
    x0, y0 = int(round(cx - n_w / 2)), int(round(cy - n_h / 2))
    full = np.zeros((H, W), np.float32)
    X0, Y0 = max(0, x0), max(0, y0); X1, Y1 = min(W, x0 + n_w), min(H, y0 + n_h)
    full[Y0:Y1, X0:X1] = a[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    darken(dst, cast_shadow(full, size, amount, contact))
    over(dst, rgb, a, x0, y0)
    return full

# ------------------------------------------------------------------ 1. coque, bevel metal, plaque
body_a, body_d = rrect_alpha(*BODY)
from svgraster import raster
svg = open(os.path.join(ROOT, 'design', 'Arc_Mockup_v003.svg')).read()
svg = svg.replace('viewBox="0 0 2350 1800">', 'viewBox="0 0 2350 1800" width="2350" height="1800">')
red_only = re.sub(r'<g id="Layer_9".*?</svg>', '</svg>', svg, flags=re.S)
red2 = raster(red_only, W, H, 2.0)[..., 3].astype(np.float32) / 255.0
metal = cv2.resize(red2, (W, H), interpolation=cv2.INTER_AREA)
metal = np.clip(metal, 0, 1) * body_a
plate = np.clip(body_a - metal, 0, 1)

# ---- contour : aluminium microbille (texture fournie) + leger bevel
dout = cv2.distanceTransform((body_a > 0.5).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE).astype(np.float32)
dout = dout + (body_a - 0.5)                                   # sous-pixel au bord exterieur
din = cv2.distanceTransform((metal > 0.5).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE).astype(np.float32)
# leger bevel : arrondi de 20 px sur l'arete exterieure + petit chanfrein de 5 px contre la plaque
h_out = np.sqrt(np.clip(1 - (1 - np.clip(dout / 20.0, 0, 1)) ** 2, 0, 1)) * 9.0
h_in = np.clip(din / 5.0, 0, 1) * 2.0
hgt = cv2.GaussianBlur(np.minimum(h_out, 7.0 + h_in), (0, 0), 0.8)
gy, gx = np.gradient(hgt)
nrm = np.dstack([-gx, -gy, np.ones_like(gx)]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
LB = np.array([-1.0, -1.0, 1.15]); LB /= np.linalg.norm(LB)
ndl = np.clip((nrm * LB).sum(2), 0, 1)
half = LB + np.array([0, 0, 1.0]); half /= np.linalg.norm(half)
spec = np.clip((nrm * half).sum(2), 0, 1) ** 30
grain = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.6)
# texture du contour : alu microbille (assets/kit/sandblasted_alu_1024.png), sans direction -> pavage en miroir
# (raccords invisibles, aucune mise a l'echelle : 1 px de texture = 1 px de l'image)
tex = np.asarray(Image.open(os.path.join(KIT, 'sandblasted_alu_1024.png')).convert('RGB')).astype(np.float32)
TS = tex.shape[0]
def refl(i):
    i = i % (2 * TS)
    return np.where(i < TS, i, 2 * TS - 1 - i)
alu = tex[refl(yy.astype(np.int32)), refl(xx.astype(np.int32))]
alu = alu * (np.array([0.985, 0.99, 1.02]) * (196.0 / 171.0) * 0.86)        # teinte du contour d'origine
flat = LB[2]
shade = 0.30 + 0.70 * ndl / flat
metal_rgb = alu * shade[..., None] + (spec * 70)[..., None]
metal_rgb *= (0.78 + 0.22 * np.clip(dout / 3.0, 0, 1))[..., None]          # arete exterieure

# ---- plaque : acier peint en poudre (epoxy), meme teinte grise : peau d'orange fine + grains
top = np.array([88.0, 92.0, 97.0]); bot = np.array([66.0, 69.0, 74.0])
diag = np.clip(((xx - 40) / 2270 * 0.35 + yy / 1800 * 0.65), 0, 1)[..., None]
plate_rgb = top * (1 - diag) + bot * diag
vig = np.hypot((xx - W * 0.45) / W, (yy - H * 0.35) / H)
plate_rgb *= (1.05 - 0.20 * np.clip(vig, 0, 1))[..., None]
n0 = rng.normal(0, 1, (H, W)).astype(np.float32)
peel = cv2.GaussianBlur(n0, (0, 0), 1.0) * 0.9 + cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 2.4) * 1.1
pgy, pgx = np.gradient(peel)
plate_rgb *= (1.0 + 0.8 * (pgx + pgy) / np.sqrt(2.0))[..., None]            # relief eclaire en haut a gauche
speck = (rng.random((H, W)) < 0.05).astype(np.float32) * rng.normal(0, 1, (H, W)).astype(np.float32)
speck = cv2.GaussianBlur(speck, (0, 0), 0.4) * 8.0
plate_rgb += (speck + cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.6) * 1.6)[..., None]
plate_rgb *= (1.0 + 0.035 * np.clip(cv2.GaussianBlur(n0, (0, 0), 40.0) * 6, -1, 1))[..., None]   # legere irregularite du lustre
# occlusion contre le metal (la plaque est un peu en retrait du bevel)
dmet = cv2.distanceTransform((metal < 0.5).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE).astype(np.float32)
occ = 0.40 * np.exp(-dmet / 5.0) + 0.12 * np.exp(-dmet / 22.0)
# l'ombre est plus marquee sous le bord haut / gauche (lumiere en haut a gauche)
sh_metal = cast_shadow(np.clip(metal, 0, 1), 60, 0.35, 0.0)
plate_rgb *= (1 - np.clip(occ * 0.9 + sh_metal, 0, 0.8))[..., None]

img = np.zeros((H, W, 3), np.float32)
img = plate_rgb * plate[..., None] + metal_rgb * metal[..., None]
alpha = body_a.copy()

# ------------------------------------------------------------------ 2. ecrans (vitre noire encastree, cadre sombre, reflet sur toute la longueur)
def screen(x, y, w, h, r):
    a_out, d_out = rrect_alpha(x, y, x + w, y + h, r)
    a_in, d_in = rrect_alpha(x + 7, y + 7, x + w - 7, y + h - 7, max(2, r - 7))
    # cadre : leger relief, arete haute eclairee, arete basse sombre
    ring = np.clip(a_out - a_in, 0, 1)
    v = (yy - y) / h
    frame = 34 + 20 * (1 - v)
    frame_rgb = np.dstack([frame, frame + 1, frame + 4])
    edge_top = np.exp(-((yy - (y + 1.2)) / 1.0) ** 2) * (xx > x + r * 0.4) * (xx < x + w - r * 0.4) * 70
    frame_rgb += edge_top[..., None]
    # vitre : noire, tres legere montee vers le haut, ombre interne en haut a gauche
    g = 7 + 6 * (1 - (yy - y) / h)
    glass = np.dstack([g * 0.9, g * 0.95, g * 1.1])
    inner = np.clip(-d_in, 0, 30)
    glass *= (0.55 + 0.45 * np.clip(inner / 9.0, 0, 1))[..., None]
    # reflet : fine ligne claire sous l'arete haute, sur toute la largeur
    refl = np.exp(-((yy - (y + 10.5)) / 1.3) ** 2) * np.clip((xx - (x + 9)) / 6, 0, 1) * np.clip((x + w - 9 - xx) / 6, 0, 1) * 30
    glass += refl[..., None]
    out = frame_rgb * ring[..., None] + glass * a_in[..., None]
    return out, a_out
for sc in (SCREEN_TOP, SCREEN_MAIN):
    rgb, a = screen(*sc)
    darken(img, cast_shadow(a, 120, 0.25, 0.35) * 0.8)
    img = img * (1 - a[..., None]) + rgb

# ------------------------------------------------------------------ 3. boutons de fonction (VOICE) : coussin satine sombre
def cushion(a_soft, d, bev):
    h = np.clip(-d / bev, 0, 1); h = np.sin(h * np.pi / 2)
    h = cv2.GaussianBlur(h.astype(np.float32), (0, 0), 0.8) * bev * 0.9
    gy, gx = np.gradient(h)
    n = np.dstack([-gx, -gy, np.ones_like(gx)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    return n
for (x, y, w, h_) in VOICE_BTNS:
    a, d = rrect_alpha(x, y, x + w, y + h_, BTN_R)
    darken(img, cast_shadow(a, 160, 0.55, 0.6))
    n = cushion(a, d, 11.0)
    ndl_ = np.clip((n * LIGHT).sum(2), 0, 1); sp = np.clip((n * half).sum(2), 0, 1) ** 28
    face = 30 + 14 * (1 - (yy - y) / h_)                       # face satinee, plus claire en haut
    lum = face * (0.55 + 0.6 * ndl_) + 120 * sp + 1.6 * grain
    rgb = np.dstack([lum, lum * 1.01, lum * 1.05])
    img = img * (1 - a[..., None]) + rgb * a[..., None]

# ------------------------------------------------------------------ 4. potards (photo du kit, repere efface : seul le repere dessine tourne)
from photo_controls_arc import knob_clean, KNOB_C, KNOB_RPX, knob_marker, FS_C, FS_FLATS_PX, FS_BTN_PX, JACK_BOX
kc = knob_clean()
for (cx, cy) in KNOBS:
    k = KNOB_R / KNOB_RPX
    n = int(np.ceil(KNOB_R * 2 + 6))
    rgb, a = place(kc, KNOB_C, k, n)
    put_sprite(img, None, rgb, a, cx, cy, 2 * KNOB_R, 0.62, 0.6)
# bouton MODE : meme metal noir tourne, sans repere
k = MODE_BTN[2] / KNOB_RPX; n = int(np.ceil(MODE_BTN[2] * 2 + 6))
rgb, a = place(kc, KNOB_C, k, n)
put_sprite(img, None, rgb, a, MODE_BTN[0], MODE_BTN[1], 2 * MODE_BTN[2], 0.62, 0.6)

# ------------------------------------------------------------------ 5. footswitchs (photo du kit)
fsp = load('footswitch_photo.png')
for (cx, cy) in FOOTS:
    k = FS_FLATS / FS_FLATS_PX; n = int(np.ceil(FS_FLATS * 1.25))
    rgb, a = place(fsp, FS_C, k, n)
    put_sprite(img, None, rgb, a, cx, cy, FS_FLATS, 0.62, 0.6)

# ------------------------------------------------------------------ 6. vis (rendu procedural : tete bombee, empreinte six pans, inox)
SCREW_C, SCREW_RPX = (137.0, 135.0), 89.0                 # photo de vis fournie (tete cruciforme), 275 x 271
def screw_sprite(R):
    im = np.asarray(Image.open(os.path.join(KIT, 'screw_photo.png')).convert('RGB')).astype(np.float32)
    h, w = im.shape[:2]
    sy, sx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.clip(SCREW_RPX - np.hypot(sx - SCREW_C[0], sy - SCREW_C[1]) + 0.5, 0, 1)
    n = int(np.ceil(R * 2 + 4))
    return place(np.dstack([im, a * 255]).astype(np.float32), SCREW_C, R / SCREW_RPX, n)
for (cx, cy) in SCREWS:
    rgb, a = screw_sprite(SCREW_R)
    put_sprite(img, None, rgb, a, cx, cy, 2 * SCREW_R, 0.55, 0.65)

# ------------------------------------------------------------------ 7. LED : siege sombre + lentille eteinte (la lentille allumee est dessinee par le plugin)
from photo_controls_arc import led_variants
LED_SPR = {}
for (cx, cy, r) in [MODE_LED] + VOICE_LEDS + PRESET_LEDS:
    key = round(r, 1)
    if key not in LED_SPR: LED_SPR[key] = led_variants(r)
    off_rgb, off_a = LED_SPR[key]['off']
    n = off_a.shape[0]
    # siege : petit creux sombre (occlusion)
    seat_a, _ = circle_alpha(cx, cy, r * 1.16)
    darken(img, cv2.GaussianBlur(seat_a, (0, 0), 1.5) * 0.75)
    over(img, off_rgb, off_a, int(round(cx - n / 2)), int(round(cy - n / 2)))

# ------------------------------------------------------------------ 8. jacks (photo du kit, sur les tranches ; IN a droite, OUT a gauche)
jp = load('jack_photo.png')
jx0, jx1, jy0, jy1 = JACK_BOX
for side, cy, _ in JACKS:
    crop = jp[jy0:jy1, jx0:jx1]
    rot = np.rot90(crop, k=-1 if side > 0 else 1).copy()
    h0, w0 = rot.shape[:2]
    k = JACK_LEN / h0
    n_w, n_h = int(round(w0 * k)), int(round(h0 * k))
    pm = rot.copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
    sm = cv2.resize(pm, (n_w, n_h), interpolation=cv2.INTER_AREA)
    a = np.clip(sm[..., 3] / 255.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-4, sm[..., :3] / np.maximum(a, 1e-4)[..., None], 0)
    rgb = np.clip(rgb * np.linspace(1.08, 0.86, n_h)[:, None, None], 0, 255)
    x0 = int(round(BODY[2] - 2)) if side > 0 else int(round(BODY[0] + 2 - n_w))
    y0 = int(round(cy - n_h / 2))
    # occlusion (moindre) sur la tranche du boitier au contact
    contact = np.zeros((H, W), np.float32)
    ex = BODY[2] if side > 0 else BODY[0]
    band = np.exp(-np.abs(xx - ex) / 7.0) * np.clip(1 - np.abs(yy - cy) / (n_h / 2 + 6), 0, 1)
    darken(img, band * 0.22 * body_a)
    over(img, rgb, a, x0, y0)
    full = np.zeros((H, W), np.float32)
    X0, X1 = max(0, x0), min(W, x0 + n_w)
    full[y0:y0 + n_h, X0:X1] = a[:, X0 - x0:X1 - x0]
    alpha = np.maximum(alpha, full)

# ------------------------------------------------------------------ sorties
os.makedirs(OUT, exist_ok=True)
bg = np.dstack([np.clip(img, 0, 255), np.clip(alpha, 0, 1) * 255]).astype(np.uint8)
Image.fromarray(bg, 'RGBA').save(os.path.join(OUT, 'background.png'), optimize=True)

# repere du potard (seul calque qui tourne), cadre carre centre sur le potard
mk = knob_marker()
for key, (cx, cy) in [('knob', KNOBS[0])]:
    pass
n = int(round(KNOB_R * 2 * 2)); k = (n / 2) / KNOB_RPX           # rendu 2x (net en HiDPI), cadre = diametre du potard
rgb, a = place(mk, KNOB_C, k, n)
Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(OUT, 'knob_marker.png'))
for key, spr in LED_SPR.items():
    for col in ('orange', 'cyan'):
        rgb, a = spr[col]
        Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(OUT, f'led_{col}_{int(round(key * 10))}.png'))

U = 0.5
layout = {
    'image': [W, H], 'unitsPerPx': U,
    'knobs': [[cx * U, cy * U, KNOB_R * U] for cx, cy in KNOBS],
    'modeBtn': [MODE_BTN[0] * U, MODE_BTN[1] * U, MODE_BTN[2] * U],
    'modeLed': [MODE_LED[0] * U, MODE_LED[1] * U, MODE_LED[2] * U],
    'voiceBtns': [[x * U, y * U, w * U, h * U] for x, y, w, h in VOICE_BTNS],
    'voiceLeds': [[x * U, y * U, r * U] for x, y, r in VOICE_LEDS],
    'presetLeds': [[x * U, y * U, r * U] for x, y, r in PRESET_LEDS],
    'screenTop': [v * U for v in SCREEN_TOP[:4]], 'screenMain': [v * U for v in SCREEN_MAIN[:4]],
    'foots': [[x * U, y * U] for x, y in FOOTS], 'footBtnR': FS_BTN_R * U, 'fsFlats': FS_FLATS * U,
    'jacks': [[s, y * U, lbl] for s, y, lbl in JACKS],
}
json.dump(layout, open(os.path.join(HERE, 'layout.json'), 'w'), indent=1)
print('ok')
