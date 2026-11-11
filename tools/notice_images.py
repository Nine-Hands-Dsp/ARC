"""Illustrations de la notice d'apres les captures de la vraie fenetre (tools/render) : python3 tools/notice_images.py <dossier des captures>"""
import os, sys, json
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SH = sys.argv[1]; OUT = os.path.join(ROOT, 'tools', 'manual_assets')
L = json.load(open(os.path.join(ROOT, 'tools', 'layout.json')))
alpha = Image.open(os.path.join(ROOT, 'assets', 'background.png')).getchannel('A')
def cap(n):
    im = Image.open(os.path.join(SH, n + '.png')).convert('RGBA'); im.putalpha(alpha); return im
def crop(im, box_units, name, w=None):
    x0, y0, x1, y1 = [v * 2 for v in box_units]; c = im.crop((int(x0), int(y0), int(x1), int(y1)))
    if w and c.width > w: c = c.resize((w, round(c.height * w / c.width)), Image.LANCZOS)
    c.save(os.path.join(OUT, name)); print(name, c.size)
o, b = cap('arc_exact_orange'), cap('arc_exact_cyan')
o.resize((1400, round(1400 * 1800 / 2350)), Image.LANCZOS).save(os.path.join(OUT, 'cover.png'))
crop(o, (55, 70, 1120, 260), 'knobs_orange.png', 1600); crop(b, (55, 70, 1120, 260), 'knobs_blue.png', 1600)
crop(b, (80, 270, 920, 410), 'voice_selector.png', 1400)
crop(o, (120, 640, 1060, 845), 'footswitches.png', 1600)
crop(o, (280, 640, 900, 700), 'presets_leds.png', 1200)
for n, f in (('arc_play_status', 'status_string.png'), ('arc_play_larsen', 'larsen_display.png')):
    crop(cap(n), (195, 425, 980, 580), f, 1400)
for n, f in (('arc_play_status', 'status_cc.png'), ('arc_play_learn', 'status_learn.png'), ('arc_play_assigned', 'status_assigned.png'), ('arc_play_hold', 'status_hold.png')):
    crop(cap(n), (195, 425, 980, 474), f, 1400)
# vue annotee : numeros des sections 3
a = o.copy(); d = ImageDraw.Draw(a)
fnt = ImageFont.truetype(os.path.join(ROOT, 'assets', 'fonts', 'Poppins-Bold.ttf'), 34)
pts = [(k[0], 92) for k in L['knobs']] + [(L['modeBtn'][0] + 48, 355), (980, 355), (190, 450), (190, 525), (316, 642), (L['foots'][0][0] - 82, 740), (L['foots'][1][0] + 82, 740)]
for i, (x, y) in enumerate(pts):
    x, y = x * 2, y * 2; r = 26
    d.ellipse((x - r, y - r, x + r, y + r), fill=(232, 130, 46, 255), outline=(255, 255, 255, 255), width=3)
    d.text((x, y + 1), str(i + 1), font=fnt, fill='white', anchor='mm')
a.resize((1400, round(1400 * 1800 / 2350)), Image.LANCZOS).save(os.path.join(OUT, 'annotated.png'))
