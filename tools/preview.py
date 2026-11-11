"""Apercu ARC v3 : fond + elements dessines en direct par le plugin (textes, logos, LED, anneaux, ecrans, reperes)."""
import os, sys, json, math, re
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from svgraster import raster

L = json.load(open(os.path.join(HERE, 'layout.json')))
PX = 2.0                                  # px par unite
SS = 2                                    # sur-echantillonnage du dessin vectoriel
bg = Image.open(os.path.join(ROOT, 'assets', 'background.png')).convert('RGBA')
W, H = bg.size
FONT = os.path.join(ROOT, 'assets', 'fonts')
def F(sz, w='Medium'): return ImageFont.truetype(os.path.join(FONT, f'Poppins-{w}.ttf'), int(sz * SS))
MONO = lambda sz: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', int(sz * SS))
ORANGE = (255, 146, 40); CYAN = (46, 226, 255); WHITE = (232, 234, 238); NOTE = (255, 138, 31)

def P(x, y): return (x * SS, y * SS)

def render(out, layerB=False, preset=0, voice=0, bow=True, hold=False, status=None, state='BOWING', vals=None, note='A2', hz='110.0 Hz'):
    img = np.asarray(bg).astype(np.float32)
    rgb = img[..., :3].copy(); A = img[..., 3]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    lc = np.array(CYAN if layerB else ORANGE, np.float32)
    # --- halos des LED : la facade recoit la lumiere (tache serree + diffusion large), additif
    def led_glow(cx, cy, r, col, lvl):
        d2 = (xx - cx) ** 2 + (yy - cy) ** 2
        e = 0.9 * np.exp(-d2 / (2 * (r * 1.6) ** 2)) + 0.22 * np.exp(-d2 / (2 * (r * 4.2) ** 2))
        lum = rgb.mean(2, keepdims=True) / 255.0
        rgb[:] = rgb + (e * lvl)[..., None] * np.array(col, np.float32)[None, None, :] * (0.35 + 0.9 * lum)
    leds = []
    leds.append((L['modeLed'], lc, 1.0))
    for i, v in enumerate(L['voiceLeds']): leds.append((v, np.array(ORANGE if i == 0 else CYAN, np.float32), 1.0 if i == voice else 0.0))
    for i, v in enumerate(L['presetLeds']): leds.append((v, np.array(ORANGE if i < 4 else CYAN, np.float32), 1.0 if i == preset else 0.0))
    for (x, y, r), col, lvl in leds:
        if lvl > 0: led_glow(x * PX, y * PX, r * PX, col, lvl)
    base = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), A]).astype(np.uint8), 'RGBA')
    # lentilles allumees
    for (x, y, r), col, lvl in leds:
        if lvl <= 0: continue
        name = 'orange' if col[1] < 200 else 'cyan'
        spr = Image.open(os.path.join(ROOT, 'assets', f'led_{name}_{int(round(r * PX * 10))}.png'))
        base.alpha_composite(spr, (int(round(x * PX - spr.width / 2)), int(round(y * PX - spr.height / 2))))

    big = base.resize((W * SS, H * SS), Image.LANCZOS)
    lay = Image.new('RGBA', big.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    glow = Image.new('RGBA', big.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)

    # --- potards : arcs de valeur (style d'origine) + repere photo qui tourne
    vals = vals or [(.47, .36), (1.0, .5), (.25, 0.0), (.5, .5), (.3, .25), (.8, 0.0), (.25, .67)]
    mk = Image.open(os.path.join(ROOT, 'assets', 'knob_marker.png'))
    for i, (cx, cy, r) in enumerate(L['knobs']):
        cx, cy, r = cx * PX, cy * PX, r * PX
        va, vb = vals[i]; v = va if (i == 3 or not layerB) else vb
        col = WHITE if i == 3 else tuple(int(c) for c in lc)
        R = r + 20
        def arc(a0, a1, n=160): return [P(cx + R * math.sin(math.radians(a0 + (a1 - a0) * k / n)), cy - R * math.cos(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
        d.line(arc(-135, 135), fill=(0, 0, 0, 120), width=9 * SS, joint='curve')
        a = -135 + 270 * v
        if v > 0.003:
            gd.line(arc(-135, a), fill=col + (90,), width=14 * SS, joint='curve')
            d.line(arc(-135, a), fill=col + (255,), width=6 * SS, joint='curve')
            d.line(arc(-135, a), fill=tuple(int(c + (255 - c) * .55) for c in col) + (255,), width=2 * SS, joint='curve')
        m = mk.resize((int(round(2 * r * SS)), int(round(2 * r * SS))), Image.LANCZOS).rotate(-a, resample=Image.BICUBIC)
        lay.alpha_composite(m, (int(round(cx * SS - m.width / 2)), int(round(cy * SS - m.height / 2))))
    # libelles des potards
    names = [('ATTACK', 'RELEASE'), ('SUSTAIN', 'SENS'), ('POSITION', 'BUZZ'), ('TONE', None), ('LIFE', 'GLIDE'), ('BOW LEVEL', 'DRY'), ('SPACE', 'OUTPUT')]
    for i, (cx, cy, r) in enumerate(L['knobs']):
        a_, b_ = names[i]
        cx *= PX
        if b_ is None:
            d.text(P(cx, 466), a_, font=F(31), fill=WHITE + (255,), anchor='mm')
        else:
            d.text(P(cx, 450), a_, font=F(31), fill=ORANGE + (255 if not layerB else 150,), anchor='mm')
            d.text(P(cx, 490), b_, font=F(31), fill=CYAN + (255 if layerB else 150,), anchor='mm')
    # MODE, VOICE
    mx, my, mr = [v * PX for v in L['modeBtn']]
    d.text(P(mx, my + mr + 38), 'MODE', font=F(28), fill=WHITE + (235,), anchor='mm')
    for i, (x, y, w, h) in enumerate(L['voiceBtns']):
        x, y, w, h = x * PX, y * PX, w * PX, h * PX
        lx = L['voiceLeds'][i][0] * PX
        d.text(P((lx + 30 + x + w - 14) / 2, y + h / 2 + 1), ['NORMAL', 'HARM', 'HARM+'][i], font=F(30), fill=WHITE + (240,), anchor='mm')
    # presets
    for i, (x, y, r) in enumerate(L['presetLeds']):
        d.text(P(x * PX, y * PX + 44), str(i + 1), font=F(26), fill=WHITE + (215,), anchor='mm')
    # footswitchs : anneau lumineux dans la gorge (facon Octopus) + libelles
    for i, (fx, fy) in enumerate(L['foots']):
        fx, fy = fx * PX, fy * PX
        footR = L['footBtnR'] * PX
        ringR = footR * 1.0775; ringW = footR * 0.0674
        on = bow if i == 0 else hold
        col = ORANGE if i == 0 else CYAN
        if on:
            sc = ringR / 33.2
            for k in np.arange(20, 3, -1.5):
                wdt = k * sc
                gd.ellipse([P(fx - ringR, fy - ringR), P(fx + ringR, fy + ringR)], outline=col + (int(255 * 0.075),), width=int(wdt * SS))
            d.ellipse([P(fx - ringR, fy - ringR), P(fx + ringR, fy + ringR)], outline=col + (217,), width=max(1, int(ringW * SS)))
            core = tuple(int(c + (255 - c) * 0.6) for c in col)
            d.ellipse([P(fx - ringR, fy - ringR), P(fx + ringR, fy + ringR)], outline=core + (230,), width=max(1, int(ringW * 0.42 * SS)))
        d.text(P(fx, fy + 150), 'BOW' if i == 0 else 'HOLD', font=F(30), fill=WHITE + (235,), anchor='mm')
    # jacks : inscriptions verticales le long des tranches
    for side, y, lbl in L['jacks']:
        t = Image.new('RGBA', (300 * SS, 60 * SS), (0, 0, 0, 0)); td = ImageDraw.Draw(t)
        td.text((150 * SS, 30 * SS), lbl, font=F(22), fill=WHITE + (200,), anchor='mm')
        t = t.rotate(90 if side < 0 else -90, expand=True)
        x = 128 if side < 0 else W - 128
        lay.alpha_composite(t, (int(x * SS - t.width / 2), int(y * PX * SS - t.height / 2)))
    # ecran du haut : barre de presets (ou ligne d'etat)
    x, y, w, h = [v * PX for v in L['screenTop']]
    if status:
        d.text(P(x + w / 2, y + h / 2), status, font=F(40), fill=tuple(int(c) for c in lc) + (255,), anchor='mm')
    else:
        pn = ['CLASSIC BOW', 'VIOLIN SWELL', 'ETHEREAL FLUTE', 'OCTAVE CHOIR', 'FIFTH SHIMMER', 'BUZZ DRONE', 'SLIDE LEAD', 'LARSEN'][preset]
        d.text(P(x + w / 2, y + h / 2), f'{preset + 1}   {pn}', font=F(40), fill=WHITE + (255,), anchor='mm')
        for sgn in (-1, 1):
            ax = x + w / 2 + sgn * (w / 2 - 34); s = 11
            d.polygon([P(ax - sgn * s * 0.7, y + h / 2 - s), P(ax - sgn * s * 0.7, y + h / 2 + s), P(ax + sgn * s * 0.8, y + h / 2)], fill=(200, 200, 205, 160))
    # ecran principal : corde, archet, note
    x, y, w, h = [v * PX for v in L['screenMain']]
    cy = y + h / 2; nut, bridge = x + 46, x + 1130
    for xx_ in (nut, bridge): d.rounded_rectangle([P(xx_ - 7, cy - 44), P(xx_ + 7, cy + 44)], radius=6 * SS, fill=(230, 231, 233, 255))
    pts = [P(nut + 7 + u / 200 * (bridge - nut - 14), cy + 26 * math.sin(math.pi * u / 200)) for u in range(201)]
    gd.line(pts, fill=CYAN + (80,), width=16 * SS); d.line(pts, fill=CYAN + (255,), width=5 * SS)
    bx = bridge - 0.16 * (bridge - nut)
    d.rounded_rectangle([P(bx - 48, cy - 62), P(bx + 48, cy + 62)], radius=12 * SS, fill=(11, 12, 16, 235), outline=NOTE + (255,), width=5 * SS)
    d.text(P(bx, cy), 'BOW', font=F(26), fill=NOTE + (255,), anchor='mm')
    sx = x + 1180
    d.rectangle([P(sx, y + 22), P(sx + 3, y + h - 22)], fill=(44, 47, 54, 255))
    d.text(P(sx + 40, y + 62), note, font=F(70, 'Bold'), fill=NOTE + (255,), anchor='lm')
    d.text(P(sx + 44, y + 118), hz, font=MONO(30), fill=WHITE + (255,), anchor='lm')
    d.text(P(sx + 44, y + 154), state, font=MONO(30), fill=(NOTE if state.startswith('FEED') else CYAN) + (255,), anchor='lm')

    glow = glow.filter(ImageFilter.GaussianBlur(5 * SS))
    big = Image.alpha_composite(Image.alpha_composite(big, glow), lay)
    out_img = big.resize((W, H), Image.LANCZOS)
    # logos vectoriels (SVG officiels, blancs)
    def logo(path, box):
        s = open(path).read()
        s = re.sub(r'<g id="Layer_1" class="st0">.*?</g>', '', s, flags=re.S)
        s = re.sub(r'<g id="Layer_4" class="st0">.*?</g>', '', s, flags=re.S)
        x0, y0, x1, y1, vb = box
        s = re.sub(r'viewBox="[^"]*"', f'viewBox="{vb}" width="{int(x1 - x0)}" height="{int(y1 - y0)}" preserveAspectRatio="xMidYMid meet"', s, count=1)
        a = raster(s, int(x1 - x0), int(y1 - y0), 1.0)
        out_img.alpha_composite(Image.fromarray(a, 'RGBA'), (int(x0), int(y0)))
    logo(os.path.join(ROOT, 'design', 'ARC_LogoPP_v004_White.svg'), (950, 1455, 1400, 1600, '337 125 2326 750'))
    logo(os.path.join(ROOT, 'design', 'NineHands_LogoPP_v003_FullWhite.svg'), (950, 1626, 1400, 1667, '250 387.5 2500 225'))
    out_img.save(out)
    return out_img

if __name__ == '__main__':
    o = os.path.join(ROOT, 'design')
    render(os.path.join(o, 'apercu_v3_orange.png'))
    render(os.path.join(o, 'apercu_v3_bleu.png'), layerB=True, status='MODE  BLUE', hold=True)
    print('ok')
