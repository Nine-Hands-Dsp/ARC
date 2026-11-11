# ARC (NINE HANDS | DSP) - notice PDF, en francais uniquement.
# Usage : python3 tools/manual.py [fichier PDF de sortie]   (defaut : docs/ARC_Manual_EN-FR_v<VERSION>.pdf)
# Illustrations : tools/manual_assets/ (rendus reels du plugin et courbes mesurees sur le moteur, repris de la notice 2.6.0 ;
# aucune ne montre le menu clic droit). Polices : assets/fonts (Poppins, DejaVu Sans pour les symboles).
# Pas d'historique des versions dans la notice (demande de l'utilisateur).
import re as _re, os as _os
VERSION = _re.search(r"project\(\w+ VERSION ([0-9.]+)", open(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "CMakeLists.txt")).read()).group(1)   # version du plugin
NAME = "ARC"
TITLE = "ARC"
FOOTER = {"en": "ARC (NINE HANDS | DSP) · v" + VERSION, "fr": "ARC (NINE HANDS | DSP) · v" + VERSION}
from reportlab.lib import colors
ACC = colors.HexColor("#E8822E")
H1COL = ACC; H2COL = colors.HexColor("#1B1D22")
HCELLBG = colors.HexColor("#F4F1EC"); HCELLTXT = colors.HexColor("#1B1D22")
# ---------- mise en page commune (style maison NINE HANDS | DSP) ----------
import os, sys
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, CondPageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "tools", "manual_assets")
FONTS = os.path.join(ROOT, "assets", "fonts")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", NAME + "_Notice_v" + VERSION + ".pdf")

for n, f in (("Pop", "Poppins-Regular"), ("PopL", "Poppins-Light"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold"),
             ("Dej", "DejaVuSans")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f + ".ttf")))
addMapping("PopL", 0, 0, "PopL"); addMapping("PopL", 1, 0, "PopM"); addMapping("PopL", 0, 1, "PopL"); addMapping("PopL", 1, 1, "PopM")
addMapping("Pop", 0, 0, "Pop"); addMapping("Pop", 1, 0, "PopB"); addMapping("Pop", 0, 1, "Pop"); addMapping("Pop", 1, 1, "PopB")

DARK = colors.HexColor("#1B1D22"); GREY = colors.HexColor("#6B6F78"); LIGHT = colors.HexColor("#F4F1EC"); RULE = colors.HexColor("#DDD8D0")
SYMBOLS = "★✎◄►↔→⇄"   # absents de Poppins : DejaVu Sans

def sym(t):
    for c in SYMBOLS: t = t.replace(c, '<font name="Dej">' + c + '</font>')
    return t

st = {
    "h1": ParagraphStyle("h1", fontName="PopB", fontSize=17, leading=21, textColor=H1COL, spaceAfter=6, spaceBefore=8, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="PopM", fontSize=11.5, leading=15, textColor=H2COL, spaceAfter=3, spaceBefore=7, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="PopL", fontSize=9, leading=13, textColor=DARK, spaceAfter=4),
    "li": ParagraphStyle("li", fontName="PopL", fontSize=9, leading=13, textColor=DARK, spaceAfter=2, leftIndent=9, bulletIndent=0),
    "note": ParagraphStyle("note", fontName="PopL", fontSize=8.4, leading=12, textColor=DARK, backColor=LIGHT, borderPadding=5, spaceBefore=4, spaceAfter=8),
    "small": ParagraphStyle("small", fontName="PopL", fontSize=7.6, leading=10.5, textColor=GREY, alignment=TA_CENTER, spaceBefore=2, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontName="PopL", fontSize=7.9, leading=10.2, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="PopM", fontSize=7.9, leading=10.2, textColor=DARK),
    "hcell": ParagraphStyle("hcell", fontName="PopM", fontSize=7.9, leading=10.2, textColor=HCELLTXT),
    "cover": ParagraphStyle("cover", fontName="PopM", fontSize=30, leading=36, textColor=colors.white, alignment=TA_CENTER),
    "coversub": ParagraphStyle("coversub", fontName="PopL", fontSize=10, leading=14, textColor=colors.HexColor("#B9B9B9"), alignment=TA_CENTER),
    "coverver": ParagraphStyle("coverver", fontName="PopL", fontSize=10, leading=14, textColor=colors.HexColor("#DADADA"), alignment=TA_CENTER),
    "coverlang": ParagraphStyle("coverlang", fontName="PopM", fontSize=7.5, leading=10, textColor=ACC),
}
def P(t, s="p"): return Paragraph(sym(t), st[s])
def bullets(items): return [Paragraph(sym(i), st["li"], bulletText="•") for i in items]
def table(rows, widths, header=True, first_bold=False):
    data = []
    for r, row in enumerate(rows):
        data.append([P(c, "hcell" if (header and r == 0) else ("cellb" if (first_bold and k == 0) else "cell")) for k, c in enumerate(row)])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, RULE),
             ("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
             ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    if header: style += [("BACKGROUND", (0, 0), (-1, 0), HCELLBG), ("LINEBELOW", (0, 0), (-1, 0), 0.9, ACC)]
    t.setStyle(TableStyle(style)); return t
def img(name, width=None, height=None):
    path = name if os.path.isabs(name) else os.path.join(ASSETS, name)
    im = Image.open(path)
    if width is None: width = height * im.width / im.height
    if height is None: height = width * im.height / im.width
    return RLImage(path, width=width, height=height)
def side(left, right, wl):
    t = Table([[left, right]], colWidths=[wl, W - wl])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (-1, 0), (-1, 0), 0),
                           ("LEFTPADDING", (1, 0), (1, 0), 10)]))
    return t

W = A4[0] - 36 * mm
def cover(t, cover_img, cover_w):
    return [Spacer(1, 38 * mm), img(cover_img, cover_w), Spacer(1, 12 * mm),
            P(" ".join(TITLE), "cover"), Spacer(1, 3 * mm), P(t["ver"], "coverver"),
            Spacer(1, 16 * mm), img("logo_white.png", 46 * mm), NextPageTemplate("p"), PageBreak()]

def build(sections, title):
    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=17 * mm, bottomMargin=18 * mm,
                          title=title, author="NINE HANDS | DSP")
    lang = {"v": "fr"}
    def deco(c, d):
        c.saveState()
        c.setFillColor(ACC); c.rect(0, A4[1] - 2.2 * mm, A4[0], 2.2 * mm, stroke=0, fill=1)
        c.setFont("PopL", 7); c.setFillColor(GREY)
        c.drawString(18 * mm, 10 * mm, FOOTER[lang["v"]])
        c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(d.page))
        c.restoreState()
    def cover_bg(c, d):
        c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
        c.setFillColor(ACC); c.rect(0, A4[1] - 2.2 * mm, A4[0], 2.2 * mm, stroke=0, fill=1); c.restoreState()
    class SetLang(Spacer):
        def __init__(self, l): Spacer.__init__(self, 0, 0); self.l = l
        def draw(self): lang["v"] = self.l
    fr = lambda: Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([PageTemplate(id="cover", frames=[fr()], onPage=cover_bg), PageTemplate(id="p", frames=[fr()], onPage=deco)])
    story = []
    for i, (l, flow) in enumerate(sections):
        if i: story += [NextPageTemplate("cover"), PageBreak()]
        story += [SetLang(l)] + flow
    doc.build(story)
    print(OUT)
# ---------- contenu de la notice ARC (vérifié contre PluginEditor.cpp / PluginProcessor.cpp / README) ----------
PRESET_VALUES = [  # Attack, Release, Voice, Position, Tone, Life, Glide, Buzz, Dry, Bow, Space, Feedback (presets d'usine)
    ("1", "600 ms", "400 ms", "Normal", "25 %", "50 %", "30 %", "40 ms", "0 %", "0 %", "80 %", "25 %", "0 %"),
    ("2", "1.2 s", "600 ms", "Normal", "12 %", "68 %", "55 %", "60 ms", "0 %", "0 %", "80 %", "35 %", "0 %"),
    ("3", "900 ms", "1.2 s", "Harm", "50 %", "22 %", "40 %", "80 ms", "0 %", "0 %", "75 %", "60 %", "0 %"),
    ("4", "800 ms", "1.5 s", "Harm", "30 %", "45 %", "50 %", "50 ms", "0 %", "15 %", "70 %", "70 %", "0 %"),
    ("5", "700 ms", "1 s", "Harm+", "35 %", "55 %", "35 %", "40 ms", "0 %", "0 %", "70 %", "55 %", "0 %"),
    ("6", "300 ms", "800 ms", "Normal", "4 %", "90 %", "20 %", "20 ms", "70 %", "0 %", "75 %", "20 %", "0 %"),
    ("7", "150 ms", "300 ms", "Normal", "20 %", "72 %", "40 %", "250 ms", "10 %", "25 %", "80 %", "20 %", "0 %"),
    ("8", "1.2 s", "1.2 s", "Normal", "15 %", "75 %", "45 %", "30 ms", "15 %", "40 %", "85 %", "30 %", "85 %")]
PV_HDR = ["#", "Attack", "Release", "Voice", "Position", "Tone", "Life", "Glide", "Buzz", "Dry", "Bow", "Space", "Feedb."]

T = {
"fr": dict(
 lang="FRANÇAIS", sub="Simulateur d'archet électromagnétique<br/>VST3 pour Windows et macOS &nbsp;·&nbsp; AU pour macOS", ver="Notice d'utilisation &nbsp;·&nbsp; version " + VERSION,
 in_t="1. Présentation",
 intro=["<b>ARC</b> transforme votre guitare en instrument à archet. Inspiré de l'<b>EBow</b>, l'archet électronique que l'on tient à la main, il en recrée le son : des notes qui montent sans attaque de médiator, qui tiennent aussi longtemps que vous le voulez, et qui peuvent s'épanouir en harmoniques ou en un larsen maîtrisé, enregistrable sans risque.",
        "Un archet électronique est un petit appareil tenu au-dessus de la corde : une bobine capte la corde, un ampli renforce le signal et une seconde bobine repousse la corde par un champ magnétique, si bien que la corde vibre indéfiniment. ARC fait la même chose sur une <b>corde virtuelle</b> : il détecte la note jouée, accorde une corde modélisée sur cette note, l'excite avec votre vraie corde, puis l'entretient avec la même boucle « capteur &gt; ampli &gt; excitateur », avec un contrôle automatique de gain qui l'empêche de s'emballer.",
        "<b>Trajet du signal.</b> Entrée guitare (mono ou stéréo) &gt; suivi (hauteur par YIN, attaques et étouffements) &gt; corde virtuelle (guide d'onde accordé, sustain infini) &gt; VOICE et POSITION (harmoniques, placement de l'archet, larsen) &gt; SPACE (réverbération du son d'archet) &gt; mélange DRY et BOW LEVEL &gt; OUTPUT.",
        "ARC est <b>monophonique</b>, comme un vrai archet électronique : jouez une note à la fois et il vous suit. Repincer la même note garde le son d'archet continu (la corde virtuelle est resynchronisée en douceur, plus de « poc » ni de décrochage) ; une nouvelle note change de hauteur sans aucun silence."],
 pluck_cap="Une note pincée s'éteint ; à travers ARC, elle monte, tient, suit le hammer-on et s'arrête quand on étouffe la corde (mesuré sur le moteur d'ARC).",
 qs_t="Prise en main rapide",
 qs=["Placez ARC <b>en premier</b> sur la piste guitare, avant toute distorsion, modulation ou delay.",
     "Le preset 1 <b>Classic Bow</b> est chargé par défaut. Jouez une seule note et laissez-la sonner : le son monte puis tient. L'affichage de la note (par exemple A2 / 110.0 Hz) et l'état BOWING confirment qu'ARC vous suit.",
     "Pour arrêter la note, étouffez la corde avec la paume, ou appuyez sur le footswitch BOW pour mettre ARC en bypass.",
     "Appuyez sur <b>MODE</b> : la LED devient bleue et les potards règlent les réglages bleus. Appuyez de nouveau pour revenir à l'orange."],
 ins_t="2. Installation",
 ins=[("Windows", "Copiez <b>Arc.vst3</b> (artefact <b>Arc-Windows-VST3</b>) dans <b>C:\\Program Files\\Common Files\\VST3\\</b>, puis relancez le scan des plugins du DAW."),
      ("macOS", "Depuis l'artefact <b>Arc-macOS-VST3-AU</b> (binaire universel, Apple Silicon et Intel), copiez <b>Arc.vst3</b> dans <b>~/Library/Audio/Plug-Ins/VST3/</b> et <b>Arc.component</b> (Audio Unit) dans <b>~/Library/Audio/Plug-Ins/Components/</b>. Le plugin n'est pas notarié : si macOS le bloque, lancez dans le Terminal <b>xattr -cr</b> suivi du chemin du plugin."),
      ("Reaper", "Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. ARC apparaît sous le nom <b>Arc</b>, fabricant <b>NINE HANDS | DSP</b>. Pour le piloter depuis un pédalier MIDI, armez la piste avec votre entrée MIDI (ou utilisez un envoi MIDI) afin que le plugin reçoive le MIDI.")],
 ov_t="3. Vue d'ensemble de l'interface",
 ov=[["#", "Commande", "#", "Commande"], ["1", "ATTACK / RELEASE", "8", "Bouton MODE et sa LED"], ["2", "SUSTAIN / SENS", "9", "Sélecteur VOICE (NORMAL, HARM, HARM+)"],
     ["3", "POSITION / BUZZ", "10", "Écran du haut : presets et ligne d'état"], ["4", "TONE", "11", "Écran de corde"], ["5", "LIFE / GLIDE", "12", "Presets 1 à 8"],
     ["6", "BOW LEVEL / DRY", "13", "Footswitch BOW (effet / bypass)"], ["7", "SPACE / OUTPUT", "14", "Footswitch HOLD"]],
 ov_note="Tirez un potard pour le régler, double-cliquez pour remettre le réglage actif à sa valeur par défaut. <b>Clic droit sur une commande</b> : son menu MIDI Learn (section 6) ; clic droit ailleurs : <b>Plugin size</b>, <b>Glow</b> et menu <b>MIDI</b>. Les menus s'ouvrent là où vous cliquez. Les jacks des tranches (OUT L / OUT R à gauche, IN L / IN R à droite) sont décoratifs : l'audio et le MIDI passent par le DAW.",
 c_t="4. Les commandes une par une",
 mode_t="Le bouton MODE et les potards doubles",
 mode=["ARC a 7 potards mais 13 réglages. Sous chaque potard, deux réglages sont écrits : le réglage <b>orange</b> en haut, le réglage <b>bleu</b> en dessous. Le bouton MODE choisit lequel des deux les potards pilotent.",
       "LED MODE orange : les potards règlent les réglages orange, leurs arcs et la ligne d'état sont orange. LED MODE bleue : ils règlent les réglages bleus, arcs et ligne d'état passent au bleu.",
       "Chaque réglage garde sa propre valeur : en changeant de mode, chaque potard se place sur la valeur de l'autre réglage, rien n'est écrasé. TONE est un potard simple à arc blanc : il règle le timbre dans les deux modes."],
 ko_cap="MODE orange : arcs orange, réglages orange.", kb_cap="MODE bleu : arcs bleus, réglages bleus.",
 set_t="Réglages",
 sets=[["Potard", "Réglage", "Plage", "Rôle", "Défaut"],
       ["1", "ATTACK", "10 ms – 4 s", "Durée de montée de la note. Court = immédiat, long = montée lente façon violon.", "600 ms"],
       ["1", "RELEASE", "20 ms – 5 s", "Durée d'extinction quand vous étouffez la corde.", "400 ms"],
       ["2", "SUSTAIN", "0–100 %", "Au maximum (« Infinite ») la note tient indéfiniment ; plus bas elle s'éteint 0,3 à 20 s après que la vraie corde s'est tue.", "Infinite"],
       ["2", "SENS", "−70 à −20 dB", "Seuil de détection. Baissez-le si des notes douces sont ratées, montez-le si le bruit des cordes déclenche des notes.", "−45 dB"],
       ["3", "POSITION", "0–100 %", "Emplacement de l'archet : près du chevalet (0 %) brillant et nasal, au milieu de la corde (100 %) creux, façon clarinette.", "25 %"],
       ["3", "BUZZ", "0–100 %", "La corde frise contre l'archet, pour des sons granuleux.", "0 %"],
       ["4", "TONE", "0–100 %", "Brillance de la corde virtuelle ; elle suit la note, le timbre reste homogène sur tout le manche.", "50 %"],
       ["5", "LIFE", "0–100 %", "Léger vibrato (environ 5 Hz) et petites instabilités naturelles de hauteur et de niveau.", "30 %"],
       ["5", "GLIDE", "1–600 ms", "Portamento quand la note saute (hammer-on, pull-off, slide). Les bends et le vibrato des doigts ne sont jamais ralentis.", "40 ms"],
       ["6", "BOW LEVEL", "0–100 %", "Niveau du son d'archet.", "80 %"],
       ["6", "DRY", "0–100 %", "Niveau du son direct. À 0 %, son d'archet pur, sans attaque de médiator.", "0 %"],
       ["7", "SPACE", "0–100 %", "Réverbération appliquée au seul son d'archet.", "25 %"],
       ["7", "OUTPUT", "−24 à +12 dB", "Volume de sortie final.", "0 dB"]],
 voice_t="VOICE",
 voice=["<b>NORMAL</b> : la corde est frottée sur sa fondamentale.", "<b>HARM</b> : la corde vibre sur son 2e harmonique, une octave au-dessus.",
        "<b>HARM+</b> : la corde vibre sur son 3e harmonique, une octave et une quinte au-dessus."],
 bend_t="Bends, vibrato, glide et réattaques",
 bend=["Les bends et le vibrato des doigts sont suivis en 15 ms environ, quel que soit GLIDE. Les sauts de note (hammer-on, pull-off, slide vers une autre frette) utilisent GLIDE. ARC fait la différence tout seul : une hauteur qui glisse en continu est un bend, une hauteur qui saute est une nouvelle note.",
       "Les bends sont suivis tant que la vraie corde s'entend au-dessus du seuil SENS. Si la corde s'est éteinte alors qu'ARC tient encore la note, bendez pendant que la corde sonne, ou baissez SENS.",
       "Repincer ne coupe plus la corde virtuelle : la même note reste continue (resynchronisation douce), une autre note change sans silence, sans double déclenchement après l'attaque. Un étouffement est confirmé sur 20 ms avant l'arrêt de la note, et le clic du médiator n'entre jamais dans la boucle de l'archet."],
 bend_cap="Même avec GLIDE à 250 ms, ARC suit de près un bend d'un ton et son relâchement (mesuré sur le moteur d'ARC).",
 fs_t="5. Footswitches, LED et écran",
 fs=["<b>BOW</b> : effet actif (LED allumée) ou bypass (LED éteinte). En bypass la guitare passe telle quelle, à son niveau d'origine quels que soient DRY, BOW LEVEL et OUTPUT ; l'écran affiche BYPASS. Le passage se fait par un court fondu, sans clic ni coupure.",
     "<b>HOLD</b> : maintien infini qui ignore l'étouffement, pour les nappes et bourdons. Une commande MIDI apprise sur HOLD (par exemple la pédale de sustain d'un clavier MIDI) active HOLD tant qu'elle est enfoncée (section 6)."],
 led=[["LED", "Comportement"], ["MODE", "Orange ou bleue : quels réglages les potards pilotent."], ["NORMAL / HARM / HARM+", "Seule la voix choisie est allumée."],
      ["PRESETS 1–8", "Seul le preset chargé est allumé : orange pour 1 à 4, cyan pour 5 à 8."], ["BOW", "Allumée quand l'effet est actif ; sa luminosité respire avec la corde."],
      ["HOLD", "Allumée quand HOLD est actif, par le footswitch ou par le MIDI."]],
 sl_t="Les deux écrans",
 sl=["L'<b>écran du haut</b> montre au repos la <b>barre de presets</b> : ◄ numéro et nom du preset ►. Les flèches passent au preset précédent ou suivant, un clic sur le nom ouvre la liste des presets.",
     "Dès qu'un réglage bouge (souris, molette, automation, MIDI), la <b>ligne d'état</b> prend la place de la barre de presets : dernier réglage touché, sa valeur et son équivalent MIDI (0–127), par exemple <b>ATTACK 600 ms (MIDI 59)</b>, puis le dernier CC reçu (<b>CC20=59</b>) et <b>HOLD</b> quand HOLD est tenu par le MIDI. Sa couleur suit MODE. Elle reste 2,5 s après le dernier mouvement puis la barre de presets revient en fondu ; un clic la fait revenir tout de suite. Pendant un MIDI Learn, elle affiche les messages d'apprentissage.",
     "L'<b>écran de corde</b> montre le <b>flux d'archet</b> : des particules de lumière partent du point de contact de l'archet (placé selon POSITION, couleur du MODE) et voyagent vers le sillet et le chevalet, où elles rebondissent. Leur densité suit le niveau, leur vitesse suit ATTACK, leur durée suit RELEASE, BUZZ les fait trembler, et elles se regroupent sur 1, 2 ou 3 ventres de vibration selon VOICE. La corde et les particules s'effacent en fondu aux deux bouts. À droite : note détectée, fréquence et état : IDLE, LISTENING, BOWING, RELEASE, BYPASS, ou FEEDBACK x5 quand le larsen a pris le dessus."],
 sl_cap="Écran du haut (ici la ligne d'état) et écran de corde : La2 détecté, archet en jeu.",
 mi_t="6. MIDI",
 mi="Toutes les commandes de la pédale se pilotent par des messages MIDI Control Change, sur n'importe quel canal. <b>Aucun CC n'est assigné par défaut</b> : chaque commande s'assigne avec le <b>MIDI Learn</b>. Les assignations sont <b>sauvegardées avec le projet</b>.",
 ml_t="MIDI Learn",
 ml=["<b>Clic droit sur une commande</b> : un potard (c'est le réglage visible, orange ou bleu, qui est appris), MODE, un bouton VOICE, une LED de preset, BOW ou HOLD. Le haut du menu affiche le nom de la commande et son assignation (<b>MIDI: CC n</b> ou <b>not assigned</b>), puis <b>MIDI Learn: &lt;Nom&gt;</b>.",
     "Choisissez-le, puis bougez une pédale, un potard ou un footswitch de votre contrôleur. L'écran du haut affiche <b>MIDI LEARN · &lt;NOM&gt;</b>, puis <b>&lt;NOM&gt; = CC n</b> pendant deux secondes. Le CC d'apprentissage ne modifie pas le son.",
     "<b>Clear MIDI: &lt;Nom&gt;</b> efface l'assignation ; <b>Cancel MIDI learn</b> (ou choisir de nouveau le même Learn) arrête l'attente.",
     "Clic droit sur une zone vide : le sous-menu <b>MIDI</b> liste <b>Learn</b> pour les 18 commandes avec leur CC, <b>Cancel MIDI learn</b>, <b>Clear all MIDI assignments</b>, et le comportement des footswitches : <b>MIDI footswitches latching (127 = on / 0 = off)</b> (par défaut) ou <b>MIDI footswitches momentary (toggle each press)</b>.",
     "Un CC ne pilote qu'une commande : apprendre un CC déjà utilisé le retire de l'autre commande. Les CC 120 à 127 ne sont jamais appris.",
     "Un projet enregistré avec une version précédente qui avait encore l'ancienne assignation d'usine (Hold sur le CC 64, rien d'autre) s'ouvre sans aucune assignation ; un projet où vous aviez changé une assignation garde ses assignations."],
 lc_t="Commandes apprenables",
 lc=[["Commande", "Type"],
     ["Attack, Release, Sustain, Sensitivity, Position, Buzz, Tone, Life, Glide, Bow Level, Dry, Space, Output", "Continu (0–127 sur toute la plage)"],
     ["Mode button", "Bascule : ≥ 64 = réglages bleus, &lt; 64 = orange"], ["Voice", "Sélecteur 3 positions : 0–42 Normal, 43–85 Harm, 86–127 Harm+"],
     ["Preset", "Sélecteur 8 positions : 0–127 découpé en 8 zones égales (presets 1 à 8)"],
     ["Bow footswitch", "Footswitch : à accrochage (≥ 64 = actif, &lt; 64 = bypass) ou momentané (chaque appui bascule)"],
     ["Hold footswitch", "Footswitch : à accrochage (tenu tant que ≥ 64, comme une pédale de sustain) ou momentané (chaque appui bascule)"]],
 mb=["Le HOLD MIDI s'ajoute au footswitch HOLD de l'écran. Effacer l'assignation de Hold relâche aussi un HOLD MIDI.",
     "ARC n'utilise pas le Program Change : choisissez les presets avec un CC appris, ou avec le menu de programmes du DAW (les 8 presets y sont listés avec leur nom).",
     "Chaque réglage est aussi un paramètre distinct du DAW, automatisable, y compris ceux qui partagent un potard : les 13 réglages, Voice, Knob Mode (Orange / Cyan), Bow, Hold et le paramètre caché Feedback (voir le preset Larsen).",
     "Les valeurs reçues en MIDI sont transmises à l'hôte par un timer, jamais depuis le thread audio (anti-gel)."],
 sc=[("status_cc.png", "Un réglage et le dernier CC reçu"), ("status_learn.png", "MIDI Learn en attente d'un CC"),
     ("status_assigned.png", "Assignation confirmée (2 s)"), ("status_hold.png", "HOLD tenu par le MIDI (ici une pédale de sustain apprise sur Hold)")],
 w_t="7. Fenêtre",
 w=["ARC s'ouvre à sa taille par défaut, <b>60 %</b> au départ, la même taille par défaut que Ring Think et les autres pédales NINE HANDS | DSP, et la fenêtre ne peut jamais être plus petite que 60 %, même si le DAW tente de la réduire.",
    "Clic droit &gt; <b>Glow</b> : intensité du halo des LED, des arcs des potards et des anneaux des footswitches, à 25, 50, 75 ou 100 %. Ce réglage est commun à toutes les fenêtres d'ARC et enregistré sur l'ordinateur.",
    "Clic droit sur la pédale &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b> ou <b>100 %</b> (la taille actuelle est cochée) ; <i>(default)</i> est indiqué à côté de la taille par défaut. Vous pouvez aussi tirer le bord de la fenêtre entre 60 % et 100 % ; la pédale garde ses proportions.",
    "<b>Plugin size &gt; Default size (new windows)</b> choisit la taille d'ouverture de toutes les nouvelles fenêtres d'ARC. Ce réglage est commun à toutes les instances et enregistré sur l'ordinateur (<i>settings.xml</i> dans le dossier NINE HANDS | DSP\\Arc des données utilisateur : %APPDATA% sous Windows, ~/Library sous macOS) ; la fenêtre ouverte prend aussi cette taille tout de suite.",
    "Une taille choisie pour une instance (par le menu ou en tirant le bord) est mémorisée avec son projet et reste prioritaire pour cette instance à la réouverture du projet. Une instance dont la taille n'a jamais été changée n'est liée à aucune taille : elle s'ouvre toujours à la taille par défaut du moment."],
 pr_t="8. Presets",
 pr="Cliquez sur une LED de preset (ou son numéro) pour le charger. Le DAW voit aussi les 8 presets comme des programmes, avec leur nom. Pour garder vos réglages, enregistrez l'état du plugin dans le DAW. Tous les presets utilisent SUSTAIN Infinite, SENS −45 dB et OUTPUT 0 dB.",
 pl=[["N°", "Preset", "Caractère"], ["1", "Classic Bow", "Le son d'archet de référence : montée moyenne, sustain infini, un peu d'espace."],
     ["2", "Violin Swell", "Montée lente près du chevalet, vibrato vivant : des lignes lyriques, façon violon."],
     ["3", "Ethereal Flute", "Voix HARM, position creuse au milieu de la corde, timbre sombre et beaucoup d'espace."],
     ["4", "Octave Choir", "Voix HARM avec un peu de son direct et une longue réverb : un chœur doux à l'octave."],
     ["5", "Fifth Shimmer", "Voix HARM+ : un halo à l'octave et à la quinte au-dessus de chaque note."],
     ["6", "Buzz Drone", "Attaque rapide tout contre le chevalet, BUZZ prononcé : bourdons granuleux, façon sitar."],
     ["7", "Slide Lead", "Archet rapide, long GLIDE entre les notes, un peu de son direct : des solos chantants."],
     ["8", "Larsen", "Larsen de guitare simulé : chaque note tenue s'épanouit vers sa propre harmonique."]],
 pv_t="Valeurs des presets",
 la_t="Le preset Larsen (larsen simulé)",
 la=["Jouez et tenez une note : pendant environ une seconde on entend la note à l'archet (et un peu de guitare directe), puis elle <b>s'épanouit</b> : le son d'archet s'efface pendant qu'une harmonique monte, avec la lente respiration d'un vrai larsen.",
     "L'harmonique est celle qui tombe le plus près des résonances d'un ampli et d'une pièce virtuels : elle dépend donc de la note jouée. Deux notes différentes à la suite ne prennent jamais la même harmonique, et les résonances dérivent lentement.",
     "Changez de note, repincez ou glissez : le larsen retombe, puis repart sur l'harmonique de la nouvelle note.",
     "Bendez pendant le larsen : il vacille, puis saute sur l'harmonique qui accroche mieux (parfois plusieurs fois sur un long bend) ; un vibrato large entre deux zones le fait papillonner. Ramenez la corde à sa hauteur de départ : l'harmonique d'origine revient, sans réattaquer.",
     "Les bends restent suivis jusqu'à environ 30 dB sous SENS (ronflement ignoré), et une attaque forte accroche plus vite (environ 1,2 s contre 2,4 s). L'écran affiche <b>FEEDBACK x5</b> (par exemple) quand l'harmonique a pris le dessus.",
     "<b>Sans danger</b> : rien n'est renvoyé vers l'ampli, aucune vraie boucle de larsen ne peut se former ; le niveau du larsen est aligné sur le son d'archet normal et un limiteur doux plafonne les crêtes. La quantité est le paramètre caché <b>Feedback</b> (0–100 %, 85 % dans le preset), automatisable dans le DAW et combinable avec tous les autres réglages."],
 ld_cap="Preset 8 Larsen : l'écran affiche FEEDBACK x5 quand le 5e harmonique a pris le dessus.",
 lb_cap="Mesuré sur le moteur d'ARC : la note à l'archet s'efface pendant que l'harmonique du larsen monte, puis se stabilise.",
 lv_cap="Mesuré sur le moteur d'ARC : pendant un bend lent, le larsen saute d'harmonique ; un vibrato large le fait papillonner.",
 ten_t="Dix notes jouées à la suite avec le preset Larsen",
 ten=[["Note jouée", "Larsen sur", "Fréquence"], ["Mi2 (82 Hz)", "6e harmonique", "494 Hz"], ["La2 (110 Hz)", "4e harmonique", "440 Hz"],
      ["Ré3 (147 Hz)", "3e harmonique", "440 Hz"], ["Sol3 (196 Hz)", "4e harmonique", "784 Hz"], ["Si3 (247 Hz)", "2e harmonique", "494 Hz"],
      ["Mi4 (330 Hz)", "4e harmonique", "1319 Hz"], ["La3 (220 Hz)", "6e harmonique", "1320 Hz"], ["Mi3 (165 Hz)", "3e harmonique", "494 Hz"],
      ["Si2 (123 Hz)", "4e harmonique", "494 Hz"], ["Do4 (262 Hz)", "2e harmonique", "523 Hz"]],
 ten_note="Chaque note bascule sur sa propre harmonique et deux notes consécutives n'en partagent jamais. Les résonances dérivant lentement, une autre prise peut légèrement différer.",
 tp_t="9. Conseils d'utilisation",
 tp=["Dans Reaper, placez ARC <b>en premier</b> dans la chaîne d'effets, avant votre simulateur d'ampli et tout drive, modulation ou delay : le suivi de note a besoin d'un signal de guitare direct et propre. Distorsion et delay sonnent très bien <b>après</b> ARC.",
     "Micro manche, son clair, volume de la guitare ouvert, une note à la fois : le suivi le plus fiable.",
     "Les accordages graves sont suivis jusqu'au Sol#1 (52 Hz) : baryton, <b>7 cordes</b> et accordages drop. Sur une corde grave de si ou de la, gardez POSITION vers 25–40 % et TONE un peu plus haut pour la définition ; HARM donne une octave façon violoncelle au-dessus de la corde grave.",
     "Construisez des accords note par note avec HOLD, puis superposez-les avec SPACE. Glissez lentement sur une corde avec un long GLIDE pour des phrases façon violoncelle.",
     "Affectez BOW et HOLD à un pédalier MIDI par MIDI Learn, et une pédale d'expression à BOW LEVEL ou SPACE pour des swells.",
     "Enregistrez le preset Larsen à faible volume et glissez-le sous une partie saturée."],
 ts_t="Dépannage",
 ts=[["Problème", "Solution"],
     ["Pas de son d'archet", "LED BOW allumée et BOW LEVEL monté ? Jouez une note nette ; l'état doit passer de LISTENING à BOWING."],
     ["Les notes douces ne sont pas détectées", "Baissez SENS (réglage bleu du potard 2)."], ["Des notes partent toutes seules", "Montez SENS, ou étouffez les cordes que vous ne jouez pas."],
     ["Notes fausses ou qui sautent", "Une note à la fois, micro manche, son clair, ARC en premier dans la chaîne."],
     ["La note ne s'arrête jamais", "SUSTAIN sur Infinite : étouffez la corde, appuyez sur BOW, ou coupez HOLD (vérifiez une commande MIDI apprise sur Hold, comme une pédale de sustain)."],
     ["Les potards ne règlent pas ce que j'attends", "Regardez la LED MODE : orange pour les réglages orange, bleue pour les réglages bleus."],
     ["Ma pédale MIDI ne fait rien", "Aucun CC n'est assigné par défaut : apprenez-le (clic droit sur la commande &gt; MIDI Learn). Vérifiez que le DAW envoie le MIDI au plugin et regardez la ligne d'état (dernier CC reçu)."],
     ["Un footswitch MIDI demande deux appuis", "Choisissez « MIDI footswitches momentary (toggle each press) » dans le sous-menu MIDI."]],
 sp_t="10. Caractéristiques techniques",
 sp=[["Formats", "VST3 (Windows 64 bits, macOS), AU (macOS), universel Apple Silicon + Intel ; listé « Arc », fabricant « NINE HANDS | DSP »"],
     ["Canaux", "Entrée mono ou stéréo, sortie mono ou stéréo ; entrée MIDI"], ["Fréquences", "44,1 à 192 kHz"], ["Latence", "0 échantillon"],
     ["Suivi de note", "Monophonique, d'environ 48 Hz (Sol#1) à 1,4 kHz"], ["Processeur", "Environ 3 % d'un cœur pour le moteur d'archet (mesuré hors DAW)"],
     ["Paramètres", "18, tous automatisables (13 réglages, Voice, Knob Mode, Bow, Hold, Feedback)"],
     ["MIDI", "MIDI Learn sur 18 commandes (CC), aucun CC assigné par défaut, footswitches à accrochage ou momentanés, assignations sauvegardées avec le projet"],
     ["Presets", "8 presets d'usine"],
     ["Fenêtre", "Format double, Plugin size 60 % / 75 % / 100 %, taille par défaut des nouvelles fenêtres au choix (60 % au départ), jamais plus petite que 60 % ; proportions conservées"],
     ["Stabilité", "Anti-gel v2 sous Windows : rendu logiciel, caches refaits par le timer, chien de garde du redessin, aucun appel à l'hôte depuis le thread audio"],
     ["Version", VERSION]]),
}

def section(lang):
    t = T[lang]; f = cover(t, "cover.png", 130 * mm)
    f += [P(t["in_t"], "h1")] + [P(x) for x in t["intro"]]
    f += [KeepTogether([img("chart_pluck.png", W * 0.68), P(t["pluck_cap"], "small")])]
    f += [P(t["qs_t"], "h2")] + bullets(t["qs"]) + [PageBreak()]
    f += [P(t["ins_t"], "h1")]
    for h, x in t["ins"]: f += [P(h, "h2"), P(x)]
    f += [Spacer(1, 4 * mm), P(t["ov_t"], "h1"), img("annotated.png", W * 0.70), Spacer(1, 2 * mm),
          table(t["ov"], [8 * mm, W / 2 - 8 * mm, 8 * mm, W / 2 - 8 * mm], first_bold=False), P(t["ov_note"], "note"), PageBreak()]
    f += [P(t["c_t"], "h1"), P(t["mode_t"], "h2")] + [P(x) for x in t["mode"]]
    f += [img("knobs_orange.png", W * 0.72), P(t["ko_cap"], "small"), img("knobs_blue.png", W * 0.72), P(t["kb_cap"], "small")]
    f += [P(t["set_t"], "h2"), table(t["sets"], [12 * mm, 20 * mm, 22 * mm, W - 72 * mm, 18 * mm])]
    f += [KeepTogether([P(t["voice_t"], "h2")] + bullets(t["voice"]) + [img("voice_diagram.png", W * 0.62), img("voice_selector.png", W * 0.50)])]
    f += [P(t["bend_t"], "h2")] + bullets(t["bend"]) + [KeepTogether([img("chart_bend.png", W * 0.66), P(t["bend_cap"], "small")]), PageBreak()]
    f += [P(t["fs_t"], "h1"), img("footswitches.png", W * 0.70), Spacer(1, 2 * mm)] + bullets(t["fs"])
    f += [Spacer(1, 2 * mm), table(t["led"], [42 * mm, W - 42 * mm], first_bold=True)]
    f += [P(t["sl_t"], "h2")] + [P(x) for x in t["sl"]] + [KeepTogether([img("status_string.png", W * 0.62), P(t["sl_cap"], "small")]), PageBreak()]
    f += [P(t["mi_t"], "h1"), P(t["mi"]), P(t["ml_t"], "h2")] + bullets(t["ml"])
    f += [KeepTogether([P(t["lc_t"], "h2"), table(t["lc"], [70 * mm, W - 70 * mm], first_bold=True)]), Spacer(1, 2 * mm)] + bullets(t["mb"])
    rows = [[img(p, 92 * mm), P(c, "cell")] for p, c in t["sc"]]
    sct = Table(rows, colWidths=[98 * mm, W - 98 * mm])
    sct.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (0, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    f += [Spacer(1, 3 * mm), KeepTogether(sct)]
    f += [KeepTogether([P(t["w_t"], "h1"), P(t["w"][0])])] + [P(x) for x in t["w"][1:]] + [PageBreak()]
    f += [P(t["pr_t"], "h1"), img("presets_leds.png", W * 0.48), Spacer(1, 2 * mm), P(t["pr"]),
          table(t["pl"], [10 * mm, 30 * mm, W - 40 * mm], first_bold=False)]
    pv = [PV_HDR] + [[(v.replace(".", ",") if lang == "fr" else v) for v in r] for r in PRESET_VALUES]
    f += [KeepTogether([P(t["pv_t"], "h2"), table(pv, [7 * mm] + [(W - 7 * mm - 15 * mm) / 11] * 2 + [15 * mm] + [(W - 7 * mm - 15 * mm) / 11] * 9)])]
    f += [P(t["la_t"], "h2")] + bullets(t["la"]) + [PageBreak()]
    f += [img("larsen_display.png", W * 0.52), P(t["ld_cap"], "small"), img("chart_larsen_bloom.png", W * 0.60), P(t["lb_cap"], "small"),
          img("chart_larsen_bend.png", W * 0.60), P(t["lv_cap"], "small")]
    f += [KeepTogether([P(t["ten_t"], "h2"), table(t["ten"], [W / 3] * 3), P(t["ten_note"], "small")]), PageBreak()]
    f += [P(t["tp_t"], "h1")] + bullets(t["tp"])
    f += [KeepTogether([P(t["ts_t"], "h2"), table(t["ts"], [50 * mm, W - 50 * mm], first_bold=True)])]
    f += [KeepTogether([P(t["sp_t"], "h1"), table(t["sp"], [28 * mm, W - 28 * mm], header=False, first_bold=True)])]
    return f

build([("fr", section("fr"))], "ARC - Notice v" + VERSION)
