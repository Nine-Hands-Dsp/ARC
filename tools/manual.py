# ARC (NINE HANDS | DSP) - notice PDF bilingue (partie anglaise complete, puis partie francaise complete).
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
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", NAME + "_Manual_EN-FR_v" + VERSION + ".pdf")

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
    return [Spacer(1, 2 * mm), P(t["lang"], "coverlang"), Spacer(1, 6 * mm), img(cover_img, cover_w), Spacer(1, 4 * mm),
            P(" ".join(TITLE), "cover"), Spacer(1, 2 * mm), P(t["sub"], "coversub"), Spacer(1, 1 * mm), P(t["ver"], "coverver"),
            Spacer(1, 7 * mm), img("logo_white.png", 46 * mm), NextPageTemplate("p"), PageBreak()]

def build(sections, title):
    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=17 * mm, bottomMargin=18 * mm,
                          title=title, author="NINE HANDS | DSP")
    lang = {"v": "en"}
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
"en": dict(
 lang="ENGLISH", sub="Electromagnetic bow simulator<br/>VST3 for Windows and macOS &nbsp;·&nbsp; AU for macOS", ver="User manual &nbsp;·&nbsp; version " + VERSION,
 in_t="1. Introduction",
 intro=["<b>ARC</b> turns your guitar into a bowed instrument. Inspired by the <b>EBow</b>, the hand-held electronic bow, it recreates its sound: notes that swell in without any pick attack, sustain for as long as you like, and can bloom into harmonics or into a controlled, recordable feedback tone.",
        "An electronic bow is a small device held over the string: a pickup coil listens to the string, an amplifier boosts the signal and a driver coil pushes the string back with a magnetic field, so the string keeps vibrating forever. ARC does the same thing on a <b>virtual string</b>: it detects the note you play, tunes a modelled string to it, excites it with your real string, then keeps it alive with the same “pickup &gt; amplifier &gt; driver” loop, with automatic gain control so it never runs away.",
        "<b>Signal path.</b> Guitar in (mono or stereo) &gt; tracking (pitch by YIN, picks and mutes) &gt; virtual string (tuned waveguide, endless sustain) &gt; VOICE and POSITION (harmonics, bow placement, feedback) &gt; SPACE (reverb on the bowed sound) &gt; mix of DRY and BOW LEVEL &gt; OUTPUT.",
        "ARC is <b>monophonic</b>, like a real electronic bow: play one note at a time and it follows you. Re-picking the same note keeps the bowed sound continuous (the virtual string is gently re-synchronised, no “poc” and no drop-out); a new note changes pitch without any silence."],
 pluck_cap="A plucked note dies away; through ARC it swells in, holds, follows the hammer-on and stops when you mute the string (measured on the ARC engine).",
 qs_t="Quick start",
 qs=["Insert ARC <b>first</b> on your guitar track, before any distortion, modulation or delay.",
     "Preset 1 <b>Classic Bow</b> is loaded by default. Play a single note and let it ring: the sound swells in and holds. The note readout (for example A2 / 110.0 Hz) and the BOWING state confirm that ARC is tracking you.",
     "To stop the note, mute the string with your palm, or press the BOW footswitch to bypass ARC.",
     "Press <b>MODE</b>: the LED turns blue and the knobs now adjust the blue settings. Press again to go back to orange."],
 ins_t="2. Installation",
 ins=[("Windows", "Copy <b>Arc.vst3</b> (artifact <b>Arc-Windows-VST3</b>) into <b>C:\\Program Files\\Common Files\\VST3\\</b>, then rescan the plugins in your DAW."),
      ("macOS", "From the artifact <b>Arc-macOS-VST3-AU</b> (universal binary, Apple Silicon and Intel), copy <b>Arc.vst3</b> into <b>~/Library/Audio/Plug-Ins/VST3/</b> and <b>Arc.component</b> (Audio Unit) into <b>~/Library/Audio/Plug-Ins/Components/</b>. The plugin is not notarized: if macOS blocks it, run <b>xattr -cr</b> followed by the plugin path in Terminal."),
      ("Reaper", "Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; <b>Re-scan</b>. ARC is listed as <b>Arc</b> by <b>NINE HANDS | DSP</b>. To control it from a MIDI pedal board, record-arm the track with your MIDI input (or use a MIDI send) so the plugin receives MIDI.")],
 ov_t="3. Interface overview",
 ov=[["#", "Control", "#", "Control"], ["1", "ATTACK / RELEASE", "8", "MODE button and LED"], ["2", "SUSTAIN / SENS", "9", "VOICE selector (NORMAL, HARM, HARM+)"],
     ["3", "POSITION / BUZZ", "10", "Status line"], ["4", "TONE", "11", "String display"], ["5", "LIFE / GLIDE", "12", "Presets 1–8"],
     ["6", "BOW LEVEL / DRY", "13", "BOW footswitch (effect on / bypass)"], ["7", "SPACE / OUTPUT", "14", "HOLD footswitch"]],
 ov_note="Drag a knob to set it, double-click it to reset the active setting to its default. <b>Right-click a control</b> for its MIDI Learn menu (section 6); right-click elsewhere for <b>Plugin size</b> and the <b>MIDI</b> menu. The side jacks (MONO / L, OUTPUTS R, INPUTS, MOD, EXP) are decorative: audio and MIDI are routed by your DAW.",
 c_t="4. The controls one by one",
 mode_t="The MODE button and dual-function knobs",
 mode=["ARC has 7 knobs but 13 settings. Under each knob two settings are printed: the <b>orange</b> one on top, the <b>blue</b> one below. The MODE button chooses which of the two the knobs control.",
       "MODE LED orange: the knobs adjust the orange settings, their arcs and the status line are orange. MODE LED blue: they adjust the blue settings, arcs and status line turn blue.",
       "Each setting keeps its own value: when you switch MODE, every knob jumps to the value of the other setting, nothing is overwritten. TONE is a single-function knob with a white arc: it controls tone in both modes."],
 ko_cap="MODE orange: orange arcs, orange settings.", kb_cap="MODE blue: blue arcs, blue settings.",
 set_t="Settings",
 sets=[["Knob", "Setting", "Range", "What it does", "Default"],
       ["1", "ATTACK", "10 ms – 4 s", "Time for the bowed note to swell in. Short = immediate, long = slow violin-like swell.", "600 ms"],
       ["1", "RELEASE", "20 ms – 5 s", "Fade-out time when you mute the string.", "400 ms"],
       ["2", "SUSTAIN", "0–100 %", "At maximum (“Infinite”) the note holds forever; lower values let it die away 0.3 to 20 s after the real string falls silent.", "Infinite"],
       ["2", "SENS", "−70 to −20 dB", "Detection threshold. Lower it if soft notes are missed, raise it if string noise triggers notes.", "−45 dB"],
       ["3", "POSITION", "0–100 %", "Where the bow sits: near the bridge (0 %) bright and nasal, middle of the string (100 %) hollow, clarinet-like.", "25 %"],
       ["3", "BUZZ", "0–100 %", "The string rattles against the bow, for gritty, buzzing tones.", "0 %"],
       ["4", "TONE", "0–100 %", "Brightness of the virtual string; it follows the note so the timbre stays even across the neck.", "50 %"],
       ["5", "LIFE", "0–100 %", "Gentle vibrato (about 5 Hz) and small natural instabilities of pitch and level.", "30 %"],
       ["5", "GLIDE", "1–600 ms", "Portamento when the note jumps (hammer-on, pull-off, slide). Bends and finger vibrato are never slowed down.", "40 ms"],
       ["6", "BOW LEVEL", "0–100 %", "Level of the bowed sound.", "80 %"],
       ["6", "DRY", "0–100 %", "Level of your direct guitar. At 0 % you get a pure bowed sound with no pick attack.", "0 %"],
       ["7", "SPACE", "0–100 %", "Reverb on the bowed sound only.", "25 %"],
       ["7", "OUTPUT", "−24 to +12 dB", "Final output level.", "0 dB"]],
 voice_t="VOICE",
 voice=["<b>NORMAL</b>: the string is bowed on its fundamental.", "<b>HARM</b>: the string vibrates on its 2nd harmonic, one octave up.",
        "<b>HARM+</b>: the string vibrates on its 3rd harmonic, an octave and a fifth up."],
 bend_t="Bends, vibrato, glide and re-picking",
 bend=["Bends and finger vibrato are followed within about 15 ms, whatever the GLIDE setting. Note jumps (hammer-ons, pull-offs, slides to another fret) use GLIDE. ARC tells them apart automatically: a pitch that moves continuously is a bend, a pitch that jumps is a new note.",
       "Bends are followed while the real string can be heard above the SENS threshold. If the string has died away but ARC still holds the note, bend while the string rings, or lower SENS.",
       "Picking again does not cut the virtual string: the same note stays continuous (soft re-synchronisation), another note changes without silence, with no double trigger after the attack. A mute is confirmed over 20 ms before the note stops, and the pick click never enters the bow loop."],
 bend_cap="Even with GLIDE at 250 ms, ARC follows a whole-tone bend and its release closely (measured on the ARC engine).",
 fs_t="5. Footswitches, LEDs and display",
 fs=["<b>BOW</b>: effect on (LED lit) or bypass (LED off). In bypass your guitar passes through untouched, at its original level whatever DRY, BOW LEVEL and OUTPUT; the display shows BYPASS. The switch-over is a short crossfade, with no click and no drop.",
     "<b>HOLD</b>: infinite hold that ignores muting, for drones and pads. A MIDI control learned on HOLD (for example the sustain pedal of a MIDI keyboard) engages HOLD while pressed (section 6)."],
 led=[["LED", "Behaviour"], ["MODE", "Orange or blue: which settings the knobs control."], ["NORMAL / HARM / HARM+", "Only the selected voice is lit."],
      ["PRESETS 1–8", "Only the loaded preset is lit: orange for 1–4, cyan for 5–8."], ["BOW", "Lit while the effect is on; its brightness breathes with the string."],
      ["HOLD", "Lit when HOLD is on, from the footswitch or from MIDI."]],
 sl_t="Status line and string display",
 sl=["The <b>status line</b> under the ARC logo shows the last setting touched, its value and MIDI equivalent (0–127), for example <b>ATTACK 600 ms (MIDI 59)</b>, then the last CC received (<b>CC20=59</b>) and <b>HOLD</b> when HOLD is engaged by MIDI. Its colour follows MODE. During MIDI Learn it shows the learn messages.",
     "The <b>string display</b> vibrates with 1, 2 or 3 antinodes depending on VOICE, its glow follows the level; the BOW block moves with POSITION. On the right: detected note, frequency and state: IDLE, LISTENING, BOWING, RELEASE, BYPASS, or FEEDBACK x5 when the Larsen effect has taken over."],
 sl_cap="Status line and string display: A2 detected, bowing.",
 mi_t="6. MIDI",
 mi="Every control on the pedal can be driven by MIDI Control Change messages, on any MIDI channel. <b>No CC is assigned by default</b>: you assign each control with <b>MIDI Learn</b>. Assignments are <b>saved with the project</b>.",
 ml_t="MIDI Learn",
 ml=["<b>Right-click a control</b>: a knob (the setting currently visible, orange or blue, is the one learned), MODE, a VOICE button, a preset LED, BOW or HOLD. The top of the menu shows <b>MIDI Learn: &lt;Name&gt; (CC n)</b>, or a dash when nothing is assigned.",
     "Choose it, then move a pedal, knob or footswitch on your controller. The status line shows <b>MIDI LEARN: move a control for &lt;Name&gt;</b>, then <b>&lt;Name&gt; = CC n</b> for two seconds. The learning CC does not change the sound.",
     "<b>Clear MIDI: &lt;Name&gt;</b> removes the assignment; <b>Cancel MIDI learn</b> (or choosing the same Learn item again) stops waiting.",
     "Right-click an empty area: the <b>MIDI</b> sub-menu lists <b>Learn</b> for all 18 controls with their CC, <b>Cancel MIDI learn</b>, <b>Clear all MIDI assignments</b>, and the footswitch behaviour: <b>MIDI footswitches latching (127 = on / 0 = off)</b> (default) or <b>MIDI footswitches momentary (toggle each press)</b>.",
     "A CC drives only one control: learning a CC already used removes it from the other control. CC 120–127 are never learned.",
     "A project saved with an earlier version that still had the old factory assignment (Hold on CC 64, nothing else) opens with no assignment; a project in which you had changed an assignment keeps its assignments."],
 lc_t="Learnable controls",
 lc=[["Control", "Type"],
     ["Attack, Release, Sustain, Sensitivity, Position, Buzz, Tone, Life, Glide, Bow Level, Dry, Space, Output", "Continuous (0–127 over the whole range)"],
     ["Mode button", "Toggle: ≥ 64 = blue settings, &lt; 64 = orange"], ["Voice", "Selector, 3 positions: 0–42 Normal, 43–85 Harm, 86–127 Harm+"],
     ["Preset", "Selector, 8 positions: 0–127 split in 8 equal zones (presets 1 to 8)"],
     ["Bow footswitch", "Footswitch: latching (≥ 64 = on, &lt; 64 = bypass) or momentary (each press toggles)"],
     ["Hold footswitch", "Footswitch: latching (held while ≥ 64, like a sustain pedal) or momentary (each press toggles)"]],
 mb=["MIDI HOLD adds to the HOLD footswitch on screen. Clearing the Hold assignment also releases a MIDI hold.",
     "ARC does not use Program Change: select presets with a learned CC, or with your DAW’s program menu (the 8 presets are listed with their names).",
     "Every setting is also a separate DAW parameter that can be automated, including those sharing a knob: the 13 settings, Voice, Knob Mode (Orange / Cyan), Bow, Hold and the hidden Feedback (see the Larsen preset).",
     "Values received by MIDI are handed to the host by a timer, never from the audio thread (anti-freeze)."],
 sc=[("status_cc.png", "A setting and the last CC received"), ("status_learn.png", "MIDI Learn waiting for a CC"),
     ("status_assigned.png", "Assignment confirmed (2 s)"), ("status_hold.png", "HOLD engaged by MIDI (here a sustain pedal learned on Hold)")],
 w_t="7. Window",
 w=["ARC opens at its default size, <b>60 %</b> at first, the same default size as Ring Think and the other NINE HANDS | DSP pedals, and the window can never be made smaller than 60 %, even if your DAW tries to resize it.",
    "Right-click the pedal &gt; <b>Plugin size</b>: <b>60 %</b>, <b>75 %</b> or <b>100 %</b> (the current size is ticked); <i>(default)</i> is shown next to the default size. You can also drag the window edge anywhere between 60 % and 100 %; the pedal keeps its proportions.",
    "<b>Plugin size &gt; Default size (new windows)</b> chooses the size at which every new ARC window opens. This setting is common to all instances and saved on your computer (<i>settings.xml</i> in the NINE HANDS | DSP\\Arc folder of your user data: %APPDATA% on Windows, ~/Library on macOS); the open window takes that size at once.",
    "A size chosen for an instance (from the menu or by dragging the edge) is remembered with its project and stays the priority for that instance when the project is reopened. An instance whose size was never changed is not tied to a size: it always opens at the current default size."],
 pr_t="8. Presets",
 pr="Click a preset LED (or its number) to load it. Your DAW also sees the 8 presets as programs with their names. To keep your own settings, save the plugin state in your DAW. All presets use SUSTAIN Infinite, SENS −45 dB and OUTPUT 0 dB.",
 pl=[["#", "Preset", "Character"], ["1", "Classic Bow", "The reference bowed sound: medium swell, infinite sustain, a touch of space."],
     ["2", "Violin Swell", "Slow swell near the bridge, lively vibrato: lyrical, string-like lines."],
     ["3", "Ethereal Flute", "HARM voice, hollow mid-string position, dark tone and lots of space."],
     ["4", "Octave Choir", "HARM voice with a little dry signal and long reverb: a soft octave choir."],
     ["5", "Fifth Shimmer", "HARM+ voice: an octave-and-fifth halo over each note."],
     ["6", "Buzz Drone", "Fast attack right at the bridge, heavy BUZZ: gritty, sitar-like drones."],
     ["7", "Slide Lead", "Fast bow, long GLIDE between notes, some dry signal: singing lead lines."],
     ["8", "Larsen", "Simulated guitar feedback: each held note blooms into its own harmonic."]],
 pv_t="Preset values",
 la_t="The Larsen preset (simulated feedback)",
 la=["Play and hold a note: for about one second you hear the bowed note (and a little dry guitar), then it <b>blooms</b>: the bowed sound fades while a harmonic grows, with the slow breathing of real feedback.",
     "The harmonic is the one closest to the resonances of a virtual amp and room, so it depends on the note you play. Two different notes in a row never bloom on the same harmonic, and the resonances drift slowly.",
     "Change note, re-pick or slide: the feedback falls back, then blooms again on the harmonic of the new note.",
     "Bend while it feeds back: it wavers, then jumps to the harmonic that catches better (sometimes several times on a long bend); a wide vibrato between two zones makes it flutter. Bring the string back to its starting pitch and the original harmonic returns, without re-picking.",
     "Bends are followed down to about 30 dB below SENS (hum ignored), and a hard attack catches faster (about 1.2 s against 2.4 s). The display shows <b>FEEDBACK x5</b> (for example) when the harmonic has taken over.",
     "<b>Safe by design</b>: nothing is sent back to your amp, no real feedback loop can form; the feedback level is matched to the normal bowed sound and a soft limiter caps the peaks. The amount is the hidden <b>Feedback</b> parameter (0–100 %, 85 % in the preset), automatable in your DAW and usable with any other setting."],
 ld_cap="Preset 8 Larsen: the display shows FEEDBACK x5 once the 5th harmonic has taken over.",
 lb_cap="Measured on the ARC engine: the bowed note fades while the feedback harmonic grows, then holds.",
 lv_cap="Measured on the ARC engine: during a slow bend the feedback jumps between harmonics; a wide vibrato makes it flutter.",
 ten_t="Ten notes played in a row through the Larsen preset",
 ten=[["Note played", "Feedback on", "Frequency"], ["E2 (82 Hz)", "6th harmonic", "494 Hz"], ["A2 (110 Hz)", "4th harmonic", "440 Hz"],
      ["D3 (147 Hz)", "3rd harmonic", "440 Hz"], ["G3 (196 Hz)", "4th harmonic", "784 Hz"], ["B3 (247 Hz)", "2nd harmonic", "494 Hz"],
      ["E4 (330 Hz)", "4th harmonic", "1319 Hz"], ["A3 (220 Hz)", "6th harmonic", "1320 Hz"], ["E3 (165 Hz)", "3rd harmonic", "494 Hz"],
      ["B2 (123 Hz)", "4th harmonic", "494 Hz"], ["C4 (262 Hz)", "2nd harmonic", "523 Hz"]],
 ten_note="Each note blooms on its own harmonic and two consecutive notes never share one. The resonances drift slowly, so another take may differ slightly.",
 tp_t="9. Tips",
 tp=["In Reaper, put ARC <b>first</b> in the FX chain, before your amp simulator and any drive, modulation or delay: the tracking needs a clean, direct guitar signal. Distortion and delay sound great <b>after</b> ARC.",
     "Neck pickup, clean tone, guitar volume up, one note at a time: the most reliable tracking.",
     "Low tunings are tracked down to G#1 (52 Hz): baritone, <b>7-string</b> and drop tunings. On a low B or A string keep POSITION around 25–40 % and TONE a little higher for definition; HARM gives a cello-like octave above the low string.",
     "Swell chords note by note with HOLD on, then layer them with SPACE. Slide slowly on one string with a long GLIDE for cello-like phrases.",
     "Assign BOW and HOLD to a MIDI foot controller with MIDI Learn, and an expression pedal to BOW LEVEL or SPACE for swells.",
     "Record the Larsen preset at low volume and blend it under a distorted part."],
 ts_t="Troubleshooting",
 ts=[["Symptom", "Solution"],
     ["No sound from the bow", "BOW LED lit and BOW LEVEL up? Play a clear single note; the state should go LISTENING then BOWING."],
     ["Soft notes are not detected", "Lower SENS (blue setting of knob 2)."], ["Notes start by themselves", "Raise SENS, or mute the strings you are not playing."],
     ["Wrong or jumping notes", "One note at a time, neck pickup, clean tone, ARC first in the chain."],
     ["The note never stops", "SUSTAIN at Infinite: mute the string, press BOW, or turn HOLD off (check any MIDI control learned on Hold, such as a sustain pedal)."],
     ["The knobs do not change what I expect", "Check the MODE LED: orange controls the orange settings, blue the blue ones."],
     ["My MIDI pedal does nothing", "No CC is assigned by default: learn it (right-click the control &gt; MIDI Learn). Check that the DAW sends MIDI to the plugin and watch the status line (last CC received)."],
     ["A MIDI footswitch needs two presses", "Choose “MIDI footswitches momentary (toggle each press)” in the MIDI sub-menu."]],
 sp_t="10. Technical specifications",
 sp=[["Formats", "VST3 (Windows 64-bit, macOS), AU (macOS), universal Apple Silicon + Intel; listed as “Arc” by “NINE HANDS | DSP”"],
     ["Channels", "Mono or stereo in, mono or stereo out; MIDI input"], ["Sample rates", "44.1 to 192 kHz"], ["Latency", "0 samples"],
     ["Tracking", "Monophonic, about 48 Hz (G#1) to 1.4 kHz"], ["CPU", "About 3 % of one core for the bow engine (measured offline)"],
     ["Parameters", "18, all automatable (13 settings, Voice, Knob Mode, Bow, Hold, Feedback)"],
     ["MIDI", "MIDI Learn on 18 controls (CC), no CC assigned by default, latching or momentary footswitch mode, assignments saved with the project"],
     ["Presets", "8 factory presets"],
     ["Window", "Plugin size 60 % / 75 % / 100 %, default size of new windows to choose (60 % at first), never smaller than 60 %; proportions kept"],
     ["Stability", "Windows anti-freeze v2: software renderer, caches rebuilt by the timer, redraw watchdog, no host call from the audio thread"],
     ["Version", VERSION]]),
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
     ["3", "POSITION / BUZZ", "10", "Ligne d'état"], ["4", "TONE", "11", "Écran de corde"], ["5", "LIFE / GLIDE", "12", "Presets 1 à 8"],
     ["6", "BOW LEVEL / DRY", "13", "Footswitch BOW (effet / bypass)"], ["7", "SPACE / OUTPUT", "14", "Footswitch HOLD"]],
 ov_note="Tirez un potard pour le régler, double-cliquez pour remettre le réglage actif à sa valeur par défaut. <b>Clic droit sur une commande</b> : son menu MIDI Learn (section 6) ; clic droit ailleurs : <b>Plugin size</b> et menu <b>MIDI</b>. Les jacks des tranches (MONO / L, OUTPUTS R, INPUTS, MOD, EXP) sont décoratifs : l'audio et le MIDI passent par le DAW.",
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
 sl_t="Ligne d'état et écran de corde",
 sl=["La <b>ligne d'état</b> sous le logo ARC affiche le dernier réglage touché, sa valeur et son équivalent MIDI (0–127), par exemple <b>ATTACK 600 ms (MIDI 59)</b>, puis le dernier CC reçu (<b>CC20=59</b>) et <b>HOLD</b> quand HOLD est tenu par le MIDI. Sa couleur suit MODE. Pendant un MIDI Learn, elle affiche les messages d'apprentissage.",
     "L'<b>écran de corde</b> vibre avec 1, 2 ou 3 ventres selon VOICE, sa lueur suit le niveau ; le bloc BOW se déplace avec POSITION. À droite : note détectée, fréquence et état : IDLE, LISTENING, BOWING, RELEASE, BYPASS, ou FEEDBACK x5 quand le larsen a pris le dessus."],
 sl_cap="Ligne d'état et écran de corde : La2 détecté, archet en jeu.",
 mi_t="6. MIDI",
 mi="Toutes les commandes de la pédale se pilotent par des messages MIDI Control Change, sur n'importe quel canal. <b>Aucun CC n'est assigné par défaut</b> : chaque commande s'assigne avec le <b>MIDI Learn</b>. Les assignations sont <b>sauvegardées avec le projet</b>.",
 ml_t="MIDI Learn",
 ml=["<b>Clic droit sur une commande</b> : un potard (c'est le réglage visible, orange ou bleu, qui est appris), MODE, un bouton VOICE, une LED de preset, BOW ou HOLD. Le haut du menu affiche <b>MIDI Learn: &lt;Nom&gt; (CC n)</b>, ou un tiret si rien n'est assigné.",
     "Choisissez-le, puis bougez une pédale, un potard ou un footswitch de votre contrôleur. La ligne d'état affiche <b>MIDI LEARN: move a control for &lt;Nom&gt;</b>, puis <b>&lt;Nom&gt; = CC n</b> pendant deux secondes. Le CC d'apprentissage ne modifie pas le son.",
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
     ["Fenêtre", "Plugin size 60 % / 75 % / 100 %, taille par défaut des nouvelles fenêtres au choix (60 % au départ), jamais plus petite que 60 % ; proportions conservées"],
     ["Stabilité", "Anti-gel v2 sous Windows : rendu logiciel, caches refaits par le timer, chien de garde du redessin, aucun appel à l'hôte depuis le thread audio"],
     ["Version", VERSION]]),
}

def section(lang):
    t = T[lang]; f = cover(t, "cover.png", 100 * mm)
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

build([("en", section("en")), ("fr", section("fr"))], "ARC - User manual / Notice v" + VERSION)
