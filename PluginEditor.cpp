#include "PluginEditor.h"
#include "BinaryData.h"
#include "WigaWindowSize.h"
#include "NineHandsGlow.h"

using namespace arcui;
using namespace juce;

//==============================================================================
//  Geometrie (unites du plugin = pixels de background.png / 2), relevee sur Arc_Mockup_v003
//==============================================================================
namespace
{
    const KnobDef knobs[7] =
    {
        {  137.18f, 150.0f, "attack",   "release", "ATTACK",    "RELEASE" },
        {  287.18f, 150.0f, "sustain",  "sens",    "SUSTAIN",   "SENS"    },
        {  437.18f, 150.0f, "position", "buzz",    "POSITION",  "BUZZ"    },
        {  587.18f, 150.0f, "tone",     "",        "TONE",      ""        },
        {  737.18f, 150.0f, "life",     "glide",   "LIFE",      "GLIDE"   },
        {  887.18f, 150.0f, "wet",      "dry",     "BOW LEVEL", "DRY"     },
        { 1037.18f, 150.0f, "space",    "output",  "SPACE",     "OUTPUT"  },
    };

    const Point<float> modeBtn { 137.18f, 355.0f };   constexpr float modeBtnR = 22.5f;
    const Point<float> modeLed { 137.18f, 291.5f };   constexpr float smallLedR = 8.0f;
    const Rectangle<float> voiceBtn[3] = { { 271.555f, 335.0f, 165.0f, 40.0f }, { 504.68f, 335.0f, 165.0f, 40.0f }, { 737.785f, 335.0f, 165.0f, 40.0f } };
    const Point<float> voiceLed[3] = { { 293.055f, 355.0f }, { 526.18f, 355.0f }, { 759.285f, 355.0f } };
    constexpr float voiceLedR = 9.25f;
    const char* voiceNames[3] = { "NORMAL", "HARM", "HARM+" };
    const Rectangle<float> screenTop  { 203.43f, 432.0f, 767.5f, 36.0f };
    const Rectangle<float> screenMain { 203.43f, 477.5f, 767.5f, 95.0f };
    constexpr float presetX0 = 315.93f, presetDX = 77.5f, presetY = 667.5f;
    const Point<float> foot[2] = { { 203.43f, 740.0f }, { 970.93f, 740.0f } };
    constexpr float footR = 40.3f;                                       // rayon du bouton du footswitch
    constexpr float fsRingR = footR * 1.0775f, fsRingW = footR * 0.0674f; // anneau dans la gorge (dessin d'Octopus)
    const Rectangle<float> arcLogoBox { 475.0f, 727.5f, 225.0f, 72.5f };
    const Rectangle<float> nhLogoBox  { 475.0f, 813.0f, 225.0f, 20.5f };
    constexpr float arrowW = 30.0f;

    const char* watchIds[] = { "attack", "release", "sustain", "sens", "position", "buzz", "tone",
                               "life", "glide", "wet", "dry", "space", "output", "mode", "layer", "bow", "hold", "feedback" };
    constexpr int numWatch = (int) (sizeof (watchIds) / sizeof (watchIds[0]));

    constexpr float startA = -0.75f * MathConstants<float>::pi, endA = 0.75f * MathConstants<float>::pi;

    Point<float> presetLed (int i) { return { presetX0 + presetDX * (float) i, presetY }; }
}

//==============================================================================
InfiniteBowEditor::InfiniteBowEditor (InfiniteBowProcessor& p)
    : AudioProcessorEditor (&p), proc (p)
{
    background = ImageCache::getFromMemory (BinaryData::background_png, BinaryData::background_pngSize);
    marker     = ImageCache::getFromMemory (BinaryData::knob_marker_png, BinaryData::knob_marker_pngSize);
    ledOrange[0] = ImageCache::getFromMemory (BinaryData::led_orange_160_png, BinaryData::led_orange_160_pngSize);
    ledOrange[1] = ImageCache::getFromMemory (BinaryData::led_orange_185_png, BinaryData::led_orange_185_pngSize);
    ledCyan[0]   = ImageCache::getFromMemory (BinaryData::led_cyan_160_png, BinaryData::led_cyan_160_pngSize);
    ledCyan[1]   = ImageCache::getFromMemory (BinaryData::led_cyan_185_png, BinaryData::led_cyan_185_pngSize);
    arcLogo = Drawable::createFromImageData (BinaryData::ArcLogoWhite_svg, BinaryData::ArcLogoWhite_svgSize);
    nhLogo  = Drawable::createFromImageData (BinaryData::NineHandsLogoWhite_svg, BinaryData::NineHandsLogoWhite_svgSize);
    poppinsMed  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize);
    poppinsReg  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsRegular_ttf, BinaryData::PoppinsRegular_ttfSize);
    poppinsBold = Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf, BinaryData::PoppinsBold_ttfSize);
    menuLnf.f = { poppinsReg, poppinsMed, poppinsBold };

    glow = (float) NineHandsGlow::percent (JucePlugin_Name) / 100.0f;
    layerB = proc.apvts.getRawParameterValue ("layer")->load() > 0.5f;
    voice  = jlimit (0, 2, roundToInt (proc.apvts.getRawParameterValue ("mode")->load()));
    preset = proc.currentPreset.load();
    for (int i = 0; i < 7; ++i)
        if (auto* prm = knobParam (i)) knobAngle[i] = knobDrawn[i] = startA + prm->getValue() * (endA - startA);

    lastCC = proc.uiMidiCC.load(); lastCCVal = proc.uiMidiVal.load();
    lastValues.assign ((size_t) numWatch, -1.0f);
    for (int i = 0; i < numWatch; ++i)
        if (auto* prm = proc.apvts.getParameter (watchIds[i])) lastValues[(size_t) i] = prm->getValue();

    // fenetre : hauteur de Ring Think par defaut (« 60 % »), jamais plus petite ; 75 % et 100 % au clic droit
    minH = sizeHeight (0); maxH = sizeHeight (numSizes - 1);
    minW = roundToInt ((float) minH * UW / UH); maxW = roundToInt ((float) maxH * UW / UH);
    setOpaque (true);
    setResizable (true, false);
    setResizeLimits (minW, minH, maxW, maxH);
    if (auto* c = getConstrainer()) c->setFixedAspectRatio ((double) UW / (double) UH);
    minSize.setMinimumSize (minW, minH);
    minSize.setMaximumSize (maxW, maxH);

    const float saved = proc.uiScale.load();
    if (saved > 0.0f) applyScale (saved);
    else
    {
        const int def = WigaWindowSize::defaultIndex (JucePlugin_Name, numSizes);
        applyScale ((float) sizeHeight (def) / (float) maxH);
        openScale = (float) sizeHeight (def) / (float) maxH;
        proc.uiScale.store (-1.0f);
    }
    rebuildCache();
    startTimerHz (30);
}

InfiniteBowEditor::~InfiniteBowEditor() { stopTimer(); }

void InfiniteBowEditor::flash (const String& text, double seconds)
{
    const double now = Time::getMillisecondCounterHiRes();
    learnLine = text;
    learnLineUntil = statusUntil = text.isNotEmpty() ? now + seconds * 1000.0 : 0.0;
    statusAlpha = text.isNotEmpty() ? 1.0f : 0.0f;
}

void InfiniteBowEditor::settleForCapture()
{
    for (int i = 0; i < 40; ++i) timerCallback();
    for (int i = 0; i < 7; ++i) blurSpan[i] = 0.0f;
    resizeSettle = 0; rebuildCache(); repaint();
}

int InfiniteBowEditor::sizeHeight (int idx)
{
    const int h[numSizes] = { 495, 619, 743 };                     // « 60 % » (= Ring Think), 75 %, 100 %
    return h[jlimit (0, numSizes - 1, idx)];
}

void InfiniteBowEditor::applyScale (float s)
{
    s = jlimit ((float) minH / (float) maxH, 1.0f, s);
    openScale = -1.0f;
    proc.uiScale.store (s);
    const int h = roundToInt ((float) maxH * s);
    setSize (roundToInt ((float) h * UW / UH), h);
    minSize.enforceNow();
}

void InfiniteBowEditor::resized()
{
    resizeSettle = 4;                                     // anti-gel v2 : le cache du fond est refait par le timer
    const float s = (float) getHeight() / (float) maxH;
    if (getHeight() >= minH - 2 && ! (proc.uiScale.load() < 0.0f && std::abs (s - openScale) < 0.005f))
        proc.uiScale.store (jlimit ((float) minH / (float) maxH, 1.0f, s));
}

//==============================================================================
//  Anti-gel v2
//==============================================================================
void InfiniteBowEditor::useSoftwareRenderer()
{
    auto* peer = getPeer();
    if ((void*) peer != lastPeer) { lastPeer = (void*) peer; repaint(); }
    lastRendererCheckMs = Time::getMillisecondCounterHiRes();
   #if JUCE_WINDOWS
    if (peer != nullptr)
    {
        int sw = peer->getAvailableRenderingEngines().indexOf ("Software Renderer");
        if (sw < 0) sw = 0;
        if (peer->getCurrentRenderingEngine() != sw) peer->setCurrentRenderingEngine (sw);
    }
   #endif
}

void InfiniteBowEditor::visibilityChanged() { useSoftwareRenderer(); if (isShowing()) repaint(); }
void InfiniteBowEditor::parentHierarchyChanged() { useSoftwareRenderer(); attachMinSize(); }

void InfiniteBowEditor::attachMinSize()
{
    if (auto* peer = getPeer())
    {
        void* handle = peer->getNativeHandle();
        if (handle != nullptr && ! minSize.isAttachedTo (handle))
        {
            auto* top = &peer->getComponent();
            minSize.attach (handle, [safe = Component::SafePointer<Component> (top)] { return safe != nullptr ? safe->getWidth() : 0; });
        }
    }
    else minSize.detach();
}

// fond reduit a la taille reelle a l'ecran (net, sans crenelage) : timer seulement, jamais dans paint
void InfiniteBowEditor::rebuildCache()
{
    if (! background.isValid() || getHeight() <= 0) return;
    float display = 1.0f;
    if (auto* d = Desktop::getInstance().getDisplays().getDisplayForRect (getScreenBounds())) display = jmax (1.0f, (float) d->scale);
    const float phys = forcedScale > 0.0f ? forcedScale : jlimit (0.05f, 4.0f, Component::getApproximateScaleFactorForComponent (this) * display);
    const int tw = jmax (1, roundToInt ((float) getWidth() * phys)), th = jmax (1, roundToInt ((float) getHeight() * phys));
    if (bgCache.isValid() && bgCache.getWidth() == tw && bgCache.getHeight() == th) return;
    Image img = background;
    while (img.getWidth() > tw * 2) img = img.rescaled (img.getWidth() / 2, img.getHeight() / 2, Graphics::highResamplingQuality);
    bgCache = (img.getWidth() == tw && img.getHeight() == th) ? img : img.rescaled (tw, th, Graphics::highResamplingQuality);
    cachedFor = phys;
    repaint();
}

void InfiniteBowEditor::askRepaint (Rectangle<float> u)
{
    if (repaintAskedMs <= 0.0) repaintAskedMs = Time::getMillisecondCounterHiRes();
    repaint ((u * k()).getSmallestIntegerContainer().expanded (2));
}

//==============================================================================
//  Paint
//==============================================================================
void InfiniteBowEditor::paint (Graphics& g)
{
    lastPaintMs = Time::getMillisecondCounterHiRes();
    repaintAskedMs = 0.0;
    g.fillAll (Colour (0xff141518));
    if (bgCache.isValid()) g.drawImage (bgCache, getLocalBounds().toFloat());
    else if (background.isValid()) g.drawImage (background, getLocalBounds().toFloat());

    g.addTransform (AffineTransform::scale (k()));
    drawLeds (g);
    drawKnobs (g);
    drawPrint (g);
    drawTopScreen (g);
    drawMainScreen (g);
    drawFootRings (g);
}

void InfiniteBowEditor::drawLed (Graphics& g, Point<float> c, float r, Colour col, float level)
{
    if (level <= 0.003f) return;
    // la facade recoit la lumiere : tache serree + diffusion large (dosee par Glow)
    if (glow > 0.0f)
    {
        const float hr = r * 5.2f;
        ColourGradient gr (col.withAlpha (0.42f * glow * level), c.x, c.y, col.withAlpha (0.0f), c.x + hr, c.y, true);
        gr.addColour (0.18, col.withAlpha (0.30f * glow * level));
        gr.addColour (0.40, col.withAlpha (0.09f * glow * level));
        gr.addColour (0.70, col.withAlpha (0.02f * glow * level));
        g.setGradientFill (gr);
        g.fillEllipse (Rectangle<float> (hr * 2.0f, hr * 2.0f).withCentre (c));
    }
    // lentille allumee : photo de la LED recoloree
    const bool big = r > 8.6f;
    const Image& im = col == cyan ? ledCyan[big ? 1 : 0] : ledOrange[big ? 1 : 0];
    const float s = r * 3.0f;
    g.setOpacity (jmin (1.0f, level));
    g.drawImage (im, Rectangle<float> (s, s).withCentre (c));
    g.setOpacity (1.0f);
}

void InfiniteBowEditor::drawLeds (Graphics& g)
{
    drawLed (g, modeLed, smallLedR, layerB ? cyan : orange, ledLvl[0]);
    for (int i = 0; i < 3; ++i) drawLed (g, voiceLed[i], voiceLedR, i == 0 ? orange : cyan, ledLvl[1 + i]);
    for (int i = 0; i < 8; ++i) drawLed (g, presetLed (i), smallLedR, i < 4 ? orange : cyan, ledLvl[4 + i]);
}

void InfiniteBowEditor::drawKnobs (Graphics& g)
{
    const auto rounded = [] (float w) { return PathStrokeType (w, PathStrokeType::curved, PathStrokeType::rounded); };
    for (int i = 0; i < 7; ++i)
    {
        const auto& kd = knobs[i];
        const bool white = String (kd.idB).isEmpty();
        const Colour col = white ? Colours::white : (layerB ? cyan : orange);
        const float a = knobAngle[i];
        // piste + arc de valeur (style d'origine)
        Path track; track.addCentredArc (kd.x, kd.y, arcR, arcR, 0.0f, startA, endA, true);
        g.setColour (Colours::black.withAlpha (0.47f));
        g.strokePath (track, rounded (4.5f));
        if (a > startA + 0.004f)
        {
            Path v; v.addCentredArc (kd.x, kd.y, arcR, arcR, 0.0f, startA, a, true);
            if (glow > 0.0f)
                for (float w = 9.0f; w > 3.5f; w -= 1.5f)
                {
                    g.setColour (col.withAlpha (0.07f * glow));
                    g.strokePath (v, rounded (w));
                }
            g.setColour (col);
            g.strokePath (v, rounded (3.0f));
            g.setColour (col.interpolatedWith (Colours::white, 0.55f));
            g.strokePath (v, rounded (1.0f));
        }
        // repere photo : seul calque qui tourne (les reflets du chapeau restent fixes), flou de mouvement
        if (marker.isValid())
        {
            const float d = knobR * 2.0f;
            auto place = [&] (float ang)
            {
                return AffineTransform::translation (-marker.getWidth() * 0.5f, -marker.getHeight() * 0.5f)
                         .scaled (d / (float) marker.getWidth()).rotated (ang).translated (kd.x, kd.y);
            };
            g.setImageResamplingQuality (Graphics::highResamplingQuality);
            const float span = blurSpan[i];
            if (span <= 0.0f) g.drawImageTransformed (marker, place (a));
            else
            {
                const int n = jlimit (3, 14, (int) std::ceil (span / degreesToRadians (3.0f)) + 1);
                for (int s = 0; s < n; ++s)
                {
                    const float t = (float) s / (float) (n - 1);
                    g.setOpacity (jmin (1.0f, 1.8f / (float) n));
                    g.drawImageTransformed (marker, place (a - blurDir[i] * span * t));
                }
                g.setOpacity (1.0f);
            }
        }
    }
}

void InfiniteBowEditor::drawPrint (Graphics& g)
{
    auto font = [this] (float h) { return Font (FontOptions (poppinsMed).withHeight (h)); };
    // libelles des potards (double reglage : la couche active est pleine, l'autre attenuee)
    for (int i = 0; i < 7; ++i)
    {
        const auto& kd = knobs[i];
        g.setFont (font (15.5f));
        if (String (kd.idB).isEmpty())
        {
            g.setColour (textCol);
            g.drawText (kd.nameA, Rectangle<float> (130.0f, 20.0f).withCentre ({ kd.x, 233.0f }), Justification::centred, false);
        }
        else
        {
            g.setColour (orange.withAlpha (layerB ? 0.58f : 1.0f));
            g.drawText (kd.nameA, Rectangle<float> (130.0f, 20.0f).withCentre ({ kd.x, 225.0f }), Justification::centred, false);
            g.setColour (cyan.withAlpha (layerB ? 1.0f : 0.58f));
            g.drawText (kd.nameB, Rectangle<float> (130.0f, 20.0f).withCentre ({ kd.x, 245.0f }), Justification::centred, false);
        }
    }
    g.setColour (textCol.withAlpha (0.92f));
    g.setFont (font (14.0f));
    g.drawText ("MODE", Rectangle<float> (80.0f, 18.0f).withCentre ({ modeBtn.x, 396.5f }), Justification::centred, false);
    g.setFont (font (15.0f));
    for (int i = 0; i < 3; ++i)
    {
        const float cx = (voiceLed[i].x + 15.0f + voiceBtn[i].getRight() - 7.0f) * 0.5f;
        g.setColour (textCol.withAlpha (0.94f));
        g.drawText (voiceNames[i], Rectangle<float> (120.0f, 20.0f).withCentre ({ cx, voiceBtn[i].getCentreY() + 0.5f }), Justification::centred, false);
    }
    g.setFont (font (13.0f));
    g.setColour (textCol.withAlpha (0.85f));
    for (int i = 0; i < 8; ++i)
        g.drawText (String (i + 1), Rectangle<float> (30.0f, 16.0f).withCentre (presetLed (i) + Point<float> (0.0f, 22.0f)), Justification::centred, false);
    g.setFont (font (15.0f));
    g.setColour (textCol.withAlpha (0.92f));
    g.drawText ("BOW",  Rectangle<float> (80.0f, 20.0f).withCentre ({ foot[0].x, 815.0f }), Justification::centred, false);
    g.drawText ("HOLD", Rectangle<float> (80.0f, 20.0f).withCentre ({ foot[1].x, 815.0f }), Justification::centred, false);
    // inscriptions des jacks, le long des tranches (OUT a gauche, IN a droite)
    g.setFont (font (11.0f));
    g.setColour (textCol.withAlpha (0.78f));
    const struct { float x, y, rot; const char* t; } jl[4] = { { 64.0f, 404.25f, -MathConstants<float>::halfPi, "OUT L" },
        { 64.0f, 572.5f, -MathConstants<float>::halfPi, "OUT R" }, { 1111.0f, 404.25f, MathConstants<float>::halfPi, "IN L" },
        { 1111.0f, 572.5f, MathConstants<float>::halfPi, "IN R" } };
    for (auto& j : jl)
    {
        Graphics::ScopedSaveState ss (g);
        g.addTransform (AffineTransform::rotation (j.rot).translated (j.x, j.y));
        g.drawText (j.t, Rectangle<float> (80.0f, 14.0f).withCentre ({ 0.0f, 0.0f }), Justification::centred, false);
    }
    // logos (SVG officiels, blancs)
    if (arcLogo != nullptr) arcLogo->drawWithin (g, arcLogoBox, RectanglePlacement::centred, 1.0f);
    if (nhLogo != nullptr)  nhLogo->drawWithin (g, nhLogoBox, RectanglePlacement::centred, 0.95f);
}

juce::String InfiniteBowEditor::presetText() const
{
    return String (preset + 1) + "   " + String (InfiniteBowProcessor::factoryPresets[jlimit (0, InfiniteBowProcessor::numFactoryPresets - 1, preset)].name).toUpperCase();
}

juce::String InfiniteBowEditor::statusText() const
{
    if (learnLine.isNotEmpty()) return learnLine;
    String s;
    if (lastParamId == "layer") s << "MODE  " << (layerB ? "BLUE" : "ORANGE");
    else if (auto* prm = proc.apvts.getParameter (lastParamId))
        s << prm->getName (32).toUpperCase() << "  " << prm->getCurrentValueAsText()
          << "  (MIDI " << roundToInt (prm->getValue() * 127.0f) << ")";
    if (lastCC >= 0) s << "  |  CC" << lastCC << "=" << lastCCVal;
    if (proc.midiHold.load()) s << "  |  HOLD";
    return s;
}

void InfiniteBowEditor::drawTopScreen (Graphics& g)
{
    // ecran du haut : barre de presets au repos, ligne d'etat pendant les reglages (fondu croise)
    const auto r = screenTop.reduced (4.0f, 3.5f);
    const Font f (FontOptions (poppinsMed).withHeight (20.0f));
    g.setFont (f);
    if (statusAlpha > 0.0f)
    {
        g.setColour ((layerB ? cyan : orange).withAlpha (statusAlpha));
        g.drawFittedText (statusText(), r.reduced (18.0f, 0.0f).toNearestInt(), Justification::centred, 1, 0.6f);
    }
    const float a = 1.0f - statusAlpha;
    if (a <= 0.0f) return;
    auto arrow = [&] (Rectangle<float> ar, bool left, bool hot)
    {
        Path p; const auto c = ar.getCentre(); const float sz = 5.5f;
        if (left) p.addTriangle (c.x + sz * 0.6f, c.y - sz, c.x + sz * 0.6f, c.y + sz, c.x - sz * 0.8f, c.y);
        else      p.addTriangle (c.x - sz * 0.6f, c.y - sz, c.x - sz * 0.6f, c.y + sz, c.x + sz * 0.8f, c.y);
        g.setColour (Colour (0xffd8dbe0).withAlpha ((hot ? 1.0f : 0.6f) * a));
        g.fillPath (p);
    };
    arrow (r.withWidth (arrowW), true, hover.kind == HitKind::presetPrev);
    arrow (r.withTrimmedLeft (r.getWidth() - arrowW), false, hover.kind == HitKind::presetNext);
    g.setColour (textCol.withAlpha ((hover.kind == HitKind::presetName ? 1.0f : 0.94f) * a));
    g.drawFittedText (presetText(), r.reduced (arrowW, 0.0f).toNearestInt(), Justification::centred, 1, 0.7f);
}

void InfiniteBowEditor::drawMainScreen (Graphics& g)
{
    const auto& sr = screenMain;
    const float cy = sr.getCentreY(), nutX = sr.getX() + 23.0f, bridgeX = sr.getX() + 565.0f;
    // flux d'archet : corde en fondu aux deux bouts, particules qui partent du point de contact de l'archet
    const Colour mainC = layerB ? orange : cyan, accC = layerB ? cyan : orange;
    {
        ColourGradient lg (Colour (0x00c8d2dc), nutX, cy, Colour (0x00c8d2dc), bridgeX, cy, false);
        lg.addColour (0.14, Colour (0x33c8d2dc));
        lg.addColour (0.86, Colour (0x33c8d2dc));
        g.setGradientFill (lg);
        g.fillRect (nutX, cy - 0.5f, bridgeX - nutX, 1.0f);
    }
    const float kk = (float) (voice + 1), lvl = shownLevel;
    {
        // particules contenues dans la vitre de l'ecran, fondu en haut et en bas
        Graphics::ScopedSaveState clip (g);
        Path glass; glass.addRoundedRectangle (sr.getX() + 5.0f, sr.getY() + 6.0f, 580.0f, sr.getHeight() - 12.0f, 6.0f);
        g.reduceClipRegion (glass);
        const float halfH = sr.getHeight() * 0.5f;
        for (const auto& pt : parts)
        {
            const float u = (pt.x - nutX) / (bridgeX - nutX);
            const float mode = std::sin (MathConstants<float>::pi * u * kk);
            const float bright = 0.06f + 0.94f * std::pow (std::abs (mode), 1.8f);
            const float ef = jlimit (0.0f, 1.0f, jmin (u / 0.14f, (1.0f - u) / 0.14f)), edge = ef * ef * (3.0f - 2.0f * ef);
            const float y = cy + 1.6f * (pt.y + mode * lvl * 15.0f * std::sin ((float) flowTime * 22.0f + pt.ph));
            const float vd = jlimit (0.0f, 1.0f, (halfH - 8.0f - std::abs (y - cy)) / 12.0f), vf = vd * vd * (3.0f - 2.0f * vd);
            const float a = jmin (1.0f, 1.2f * pt.life * bright * edge * vf * (pt.r > 1.7f ? 1.3f : 1.0f));
            if (a < 0.01f) continue;
            const float r = pt.r * (0.6f + 0.6f * pt.life);
            g.setColour (mainC.withAlpha (a));
            g.fillEllipse (pt.x - r, y - r, r * 2.0f, r * 2.0f);
            if (pt.r > 1.8f && a > 0.35f)
            {
                const float rc = pt.r * 0.35f;
                g.setColour (Colour (235, 252, 255).withAlpha (a * 0.8f));
                g.fillEllipse (pt.x - rc, y - rc, rc * 2.0f, rc * 2.0f);
            }
        }
    }
    const float posFrac = 0.04f + 0.46f * proc.apvts.getRawParameterValue ("position")->load();
    const float bx = bridgeX - posFrac * (bridgeX - nutX);
    const bool bowOn = proc.apvts.getRawParameterValue ("bow")->load() > 0.5f;
    if (lvl > 0.02f && glow > 0.0f)
    {
        ColourGradient hg (accC.withAlpha (0.35f * lvl * glow), bx, cy, accC.withAlpha (0.0f), bx + 40.0f, cy, true);
        g.setGradientFill (hg);
        g.fillEllipse (bx - 40.0f, cy - 40.0f, 80.0f, 80.0f);
    }
    if (bowOn && glow > 0.0f)
    {
        ColourGradient dg (accC.withAlpha (0.5f * glow), bx, cy, accC.withAlpha (0.0f), bx + 12.0f, cy, true);
        g.setGradientFill (dg);
        g.fillEllipse (bx - 12.0f, cy - 12.0f, 24.0f, 24.0f);
    }
    const float dr = bowOn ? 4.5f : 3.0f;
    g.setColour (accC.withAlpha (bowOn ? 1.0f : 0.45f));
    g.fillEllipse (bx - dr, cy - dr, dr * 2.0f, dr * 2.0f);
    const bool bowing = proc.uiState.load() == 2;

    // separateur + note detectee
    const float sx = sr.getX() + 590.0f;
    g.setColour (Colour (0xff2c2f36));
    g.fillRect (sx, sr.getY() + 11.0f, 1.5f, sr.getHeight() - 22.0f);
    const float hz = proc.uiPitchHz.load();
    g.setColour (hz > 0.0f ? noteOrg : Colour (0xff6c7380));
    g.setFont (Font (FontOptions (poppinsBold).withHeight (35.0f)));
    g.drawText (hz > 0.0f ? noteName (hz) : "--", Rectangle<float> (sx + 20.0f, sr.getY() + 13.0f, 150.0f, 36.0f), Justification::centredLeft, false);
    const Font mono (FontOptions (Font::getDefaultMonospacedFontName(), 15.0f, Font::plain));
    g.setFont (mono);
    g.setColour (textCol);
    g.drawText (hz > 0.0f ? String (hz, 1) + " Hz" : "no pitch", Rectangle<float> (sx + 22.0f, sr.getY() + 51.0f, 150.0f, 16.0f), Justification::centredLeft, false);
    const char* states[] = { "IDLE", "LISTENING", "BOWING", "RELEASE" };
    String st = states[jlimit (0, 3, proc.uiState.load())];
    const bool bypassed = proc.apvts.getRawParameterValue ("bow")->load() < 0.5f;
    const bool larsen = ! bypassed && proc.uiFeedback.load() > 0.25f;
    if (bypassed) st = "BYPASS";
    if (larsen) st = "FEEDBACK x" + String (proc.uiFbHarm.load());
    g.setColour (larsen ? noteOrg : (bowing ? cyan : Colour (0xff6c7380)));
    g.drawText (st, Rectangle<float> (sx + 22.0f, sr.getY() + 69.0f, 150.0f, 16.0f), Justification::centredLeft, false);
}

void InfiniteBowEditor::drawFootRings (Graphics& g)
{
    // anneau lumineux dans la gorge du footswitch (dessin d'Octopus) : halo dose par Glow, trait net, coeur clair
    for (int i = 0; i < 2; ++i)
    {
        const auto c = foot[i];
        const float lvl = i == 0 ? bowLvl : holdLvl;
        const Colour col = i == 0 ? orange : cyan;
        if (lvl > 0.003f)
        {
            Path ring; ring.addEllipse (c.x - fsRingR, c.y - fsRingR, fsRingR * 2.0f, fsRingR * 2.0f);
            const float kr = fsRingR / 33.2f;
            if (glow > 0.0f)
                for (float hw = 20.0f; hw > 3.0f; hw -= 1.5f)
                {
                    g.setColour (col.withAlpha (jmin (1.0f, 0.075f * glow) * lvl));
                    g.strokePath (ring, PathStrokeType (hw * kr));
                }
            g.setColour (col.withAlpha (0.85f * lvl));
            g.strokePath (ring, PathStrokeType (fsRingW));
            g.setColour (col.interpolatedWith (Colours::white, 0.6f).withAlpha (0.9f * lvl));
            g.strokePath (ring, PathStrokeType (fsRingW * 0.42f));
        }
        if (footDown[i])
        {
            const float r = footR * 0.98f;
            g.setColour (Colours::black.withAlpha (0.25f));
            g.fillEllipse (c.x - r, c.y - r, r * 2.0f, r * 2.0f);
        }
    }
}

// une image du timer (1/30 s) = deux images de l'apercu valide (60 i/s) : vitesses et usure doublees
void InfiniteBowEditor::stepFlow (float dt)
{
    const auto& sr = screenMain;
    const float x0 = sr.getX() + 23.0f, x1 = sr.getX() + 565.0f;
    const float k = dt * 60.0f;
    auto norm = [this] (const char* id) { auto* p = proc.apvts.getParameter (id); return p != nullptr ? p->getValue() : 0.0f; };
    const float attack = norm ("attack"), release = norm ("release"), buzz = norm ("buzz");
    const float posFrac = 0.04f + 0.46f * proc.apvts.getRawParameterValue ("position")->load();
    const float bx = x1 - posFrac * (x1 - x0);
    const bool bowOn = proc.apvts.getRawParameterValue ("bow")->load() > 0.5f;
    const float lvl = shownLevel;
    flowTime += dt;

    // emission au point de contact
    const float sp = 2.2f + 4.5f * (1.0f - attack);
    const int n = (int) std::round ((lvl * lvl * 6.0f + (lvl > 0.05f ? 1.0f : 0.0f)) * k);
    for (int i = 0; i < n; ++i)
        parts.push_back ({ bx + (rng.nextFloat() - 0.5f) * 3.0f, (rng.nextBool() ? -1.0f : 1.0f) * sp * (0.5f + rng.nextFloat() * 0.9f),
                           0.0f, (rng.nextFloat() - 0.5f) * buzz * 3.0f, 1.0f, rng.nextFloat() * 6.28f, 1.0f + rng.nextFloat() * 1.1f });

    const float decay = (0.0022f + 0.009f * (1.0f - release)) * (bowOn ? 1.0f : 2.2f) * k;
    for (auto& p : parts)
    {
        p.x += p.v * k;
        if (p.x < x0) { p.x = 2.0f * x0 - p.x; p.v *= -0.85f; }
        if (p.x > x1) { p.x = 2.0f * x1 - p.x; p.v *= -0.85f; }
        p.life -= decay;
        p.vy += (rng.nextFloat() - 0.5f) * buzz * 1.2f * k;
        p.vy *= std::pow (0.88f, k);
        p.y = (p.y + p.vy * k) * std::pow (0.97f, k);
    }
    parts.erase (std::remove_if (parts.begin(), parts.end(), [] (const Particle& p) { return p.life <= 0.0f; }), parts.end());
    constexpr size_t maxParts = 700;
    if (parts.size() > maxParts) parts.erase (parts.begin(), parts.begin() + (long) (parts.size() - maxParts));
}

juce::String InfiniteBowEditor::noteName (float hz)
{
    static const char* names[] = { "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B" };
    const int midi = roundToInt (69.0f + 12.0f * std::log2 (hz / 440.0f));
    return String (names[((midi % 12) + 12) % 12]) + String (midi / 12 - 1);
}

//==============================================================================
//  Timer (30 Hz) : etat affiche, fondus, redessins cibles
//==============================================================================
void InfiniteBowEditor::timerCallback()
{
    const double now = Time::getMillisecondCounterHiRes();
    if ((void*) getPeer() != lastPeer || now - lastRendererCheckMs > 1000.0) useSoftwareRenderer();
    attachMinSize();
    if (getWidth() < minW - 2 || getHeight() < minH - 2) minSize.enforceNow();

    if (resizeSettle > 0 && --resizeSettle == 0) rebuildCache();
    else if (resizeSettle == 0 && now - lastScaleCheckMs > 250.0) { lastScaleCheckMs = now; rebuildCache(); }

    // chien de garde : redessin demande mais pas servi -> moteur de rendu reapplique, tout redessine
    if (repaintAskedMs > 0.0 && isShowing() && now - repaintAskedMs > 1500.0 && lastPaintMs < repaintAskedMs)
    {
        repaintAskedMs = 0.0; lastPeer = nullptr; useSoftwareRenderer(); repaint();
    }

    // reglage qui vient de bouger (souris, automation, MIDI) -> ligne d'etat
    for (int i = 0; i < numWatch; ++i)
        if (auto* prm = proc.apvts.getParameter (watchIds[i]))
        {
            const float v = prm->getValue();
            if (std::abs (v - lastValues[(size_t) i]) > 1.0e-5f)
            {
                if (lastValues[(size_t) i] >= 0.0f) { lastParamId = watchIds[i]; statusUntil = now + 2500.0; }
                lastValues[(size_t) i] = v;
            }
        }

    // dernier CC recu (affiche dans la ligne d'etat)
    {
        const int cc = proc.uiMidiCC.load(), cv = proc.uiMidiVal.load();
        if (cc != lastCC || cv != lastCCVal) { if (cc >= 0) statusUntil = now + 2500.0; lastCC = cc; lastCCVal = cv; }
    }

    // MIDI Learn
    const int learned = proc.lastLearned.exchange (-1);
    const int lt = proc.learnTarget.load();
    if (learned >= 0)
    {
        learnLine = String (InfiniteBowProcessor::learnDef (learned).name).toUpperCase() + "  =  CC " + String (proc.ccMap[learned].load());
        learnLineUntil = statusUntil = now + 2000.0;
    }
    else if (lt >= 0)
    {
        learnLine = String::fromUTF8 ("MIDI LEARN  \xc2\xb7  ") + String (InfiniteBowProcessor::learnDef (lt).name).toUpperCase();
        learnLineUntil = statusUntil = now + 150.0;
    }
    else if (now >= learnLineUntil) learnLine.clear();

    const float st = now < statusUntil ? 1.0f : 0.0f;
    statusAlpha += (st - statusAlpha) * (st > statusAlpha ? 0.45f : 0.30f);
    if (statusAlpha < 0.005f) statusAlpha = 0.0f;
    if (statusAlpha > 0.995f) statusAlpha = 1.0f;

    // etat des commandes
    const bool lb = proc.apvts.getRawParameterValue ("layer")->load() > 0.5f;
    const int  vc = jlimit (0, 2, roundToInt (proc.apvts.getRawParameterValue ("mode")->load()));
    const int  pr = proc.currentPreset.load();
    const bool bowOn  = proc.apvts.getRawParameterValue ("bow")->load() > 0.5f;
    const bool holdOn = proc.apvts.getRawParameterValue ("hold")->load() > 0.5f || proc.midiHold.load();
    if (lb != layerB || vc != voice || pr != preset) { layerB = lb; voice = vc; preset = pr; repaint(); }

    auto fade = [] (float& v, float target) { const float d = target - v; v += d * (d > 0.0f ? 0.45f : 0.28f); if (std::abs (target - v) < 0.003f) v = target; };
    float before[13]; std::copy (std::begin (ledLvl), std::end (ledLvl), before);
    fade (ledLvl[0], 1.0f);
    for (int i = 0; i < 3; ++i) fade (ledLvl[1 + i], i == voice ? 1.0f : 0.0f);
    for (int i = 0; i < 8; ++i) fade (ledLvl[4 + i], i == preset ? 1.0f : 0.0f);
    const float bowBefore = bowLvl, holdBefore = holdLvl;
    fade (bowLvl, bowOn ? 0.75f + 0.25f * shownLevel : 0.0f);
    fade (holdLvl, holdOn ? 1.0f : 0.0f);
    for (int i = 0; i < 12; ++i)
        if (before[i] != ledLvl[i])
        {
            const auto c = i == 0 ? modeLed : i < 4 ? voiceLed[i - 1] : presetLed (i - 4);
            askRepaint (Rectangle<float> (110.0f, 110.0f).withCentre (c));
        }
    if (bowBefore != bowLvl)   askRepaint (Rectangle<float> (150.0f, 150.0f).withCentre (foot[0]));
    if (holdBefore != holdLvl) askRepaint (Rectangle<float> (150.0f, 150.0f).withCentre (foot[1]));

    // potards : angle suivi sans retard, flou de mouvement (montee immediate, retombee x0,6)
    for (int i = 0; i < 7; ++i)
        if (auto* prm = knobParam (i))
        {
            const float a = startA + prm->getValue() * (endA - startA);
            const float v = a - knobAngle[i];
            if (std::abs (v) > 1.0e-5f) blurDir[i] = v > 0.0f ? 1.0f : -1.0f;
            const float spanBefore = blurSpan[i];
            blurSpan[i] = jmax (jmin (std::abs (v), degreesToRadians (40.0f)), blurSpan[i] * 0.6f);
            if (blurSpan[i] < 0.002f) blurSpan[i] = 0.0f;
            if (std::abs (a - knobAngle[i]) > 1.0e-5f || spanBefore != blurSpan[i])
            {
                knobAngle[i] = a;
                askRepaint (Rectangle<float> (arcR * 2.0f + 24.0f, arcR * 2.0f + 24.0f).withCentre ({ knobs[i].x, knobs[i].y }));
            }
        }

    // ecran du haut
    const String stTxt = statusText(), prTxt = presetText();
    if (std::abs (dStatusA - statusAlpha) > 0.002f || stTxt != drawnStatus || prTxt != drawnPreset)
    {
        dStatusA = statusAlpha; drawnStatus = stTxt; drawnPreset = prTxt;
        askRepaint (screenTop);
    }

    // ecran de corde : anime tant que la corde vibre, sinon seulement si un element change
    shownLevel += (proc.uiLevel.load() - shownLevel) * 0.25f;
    phase += 0.9; if (phase > 1000.0) phase -= 1000.0;
    stepFlow (1.0f / 30.0f);
    const float hz = proc.uiPitchHz.load();
    const String key = String (voice) + "|" + String (proc.uiState.load()) + "|" + (hz > 0.0f ? noteName (hz) + String (hz, 1) : String ("-"))
                     + "|" + String ((int) bowOn) + String (proc.uiFeedback.load() > 0.25f ? proc.uiFbHarm.load() : 0);
    const float pos = proc.apvts.getRawParameterValue ("position")->load();
    if (shownLevel > 0.002f || ! parts.empty() || std::abs (dLevel - shownLevel) > 0.002f || std::abs (dPos - pos) > 0.002f || key != drawnDisplayKey)
    {
        dLevel = shownLevel; dPos = pos; drawnDisplayKey = key;
        askRepaint (screenMain);
    }
}

//==============================================================================
//  Souris
//==============================================================================
InfiniteBowEditor::Hit InfiniteBowEditor::hitAt (Point<float> u) const
{
    for (int i = 0; i < 7; ++i)
        if (u.getDistanceFrom ({ knobs[i].x, knobs[i].y }) <= knobR * 1.1f) return { HitKind::knob, i };
    if (u.getDistanceFrom (modeBtn) <= modeBtnR * 1.25f || u.getDistanceFrom (modeLed) <= 14.0f) return { HitKind::mode, 0 };
    for (int i = 0; i < 3; ++i) if (voiceBtn[i].expanded (2.0f).contains (u)) return { HitKind::voice, i };
    for (int i = 0; i < 8; ++i)
        if (Rectangle<float> (40.0f, 46.0f).withCentre (presetLed (i) + Point<float> (0.0f, 10.0f)).contains (u)) return { HitKind::preset, i };
    for (int i = 0; i < 2; ++i)
        if (u.getDistanceFrom (foot[i]) <= footR * 1.35f) return { i == 0 ? HitKind::bow : HitKind::hold, i };
    if (screenTop.contains (u))
        return { u.x < screenTop.getX() + arrowW + 4.0f ? HitKind::presetPrev : u.x > screenTop.getRight() - arrowW - 4.0f ? HitKind::presetNext : HitKind::presetName, 0 };
    return {};
}

juce::RangedAudioParameter* InfiniteBowEditor::knobParam (int i) const
{
    const auto& kd = knobs[i];
    const bool b = layerB && String (kd.idB).isNotEmpty();
    return proc.apvts.getParameter (b ? kd.idB : kd.idA);
}

void InfiniteBowEditor::setKnob (int i, float v01, bool gesture)
{
    if (auto* prm = knobParam (i))
    {
        v01 = jlimit (0.0f, 1.0f, v01);
        if (! gesture) prm->beginChangeGesture();
        prm->setValueNotifyingHost (v01);
        if (! gesture) prm->endChangeGesture();
    }
}

int InfiniteBowEditor::learnIndexFor (const Hit& h) const
{
    switch (h.kind)
    {
        case HitKind::knob:   if (auto* prm = knobParam (h.index)) return InfiniteBowProcessor::learnIndexOf (prm->getParameterID()); return -1;
        case HitKind::mode:   return InfiniteBowProcessor::learnLayer;
        case HitKind::voice:  return InfiniteBowProcessor::learnVoice;
        case HitKind::preset: case HitKind::presetName: case HitKind::presetPrev: case HitKind::presetNext: return InfiniteBowProcessor::learnPreset;
        case HitKind::bow:    return InfiniteBowProcessor::learnBow;
        case HitKind::hold:   return InfiniteBowProcessor::learnHold;
        default: return -1;
    }
}

void InfiniteBowEditor::mouseMove (const MouseEvent& e)
{
    const auto h = hitAt (toUnits (e.position));
    if (h.kind != hover.kind || h.index != hover.index) { hover = h; askRepaint (screenTop); }
    setMouseCursor (h.kind == HitKind::none ? MouseCursor::NormalCursor
                  : h.kind == HitKind::knob ? MouseCursor::UpDownResizeCursor : MouseCursor::PointingHandCursor);
}

void InfiniteBowEditor::mouseDown (const MouseEvent& e)
{
    const auto u = toUnits (e.position);
    if (e.mods.isPopupMenu()) { showContextMenu (u); return; }
    const auto h = hitAt (u);
    auto toggle = [this] (const char* id)
    {
        if (auto* prm = proc.apvts.getParameter (id))
        {
            prm->beginChangeGesture(); prm->setValueNotifyingHost (prm->getValue() > 0.5f ? 0.0f : 1.0f); prm->endChangeGesture();
        }
    };
    auto setProgram = [this] (int i)
    {
        proc.setCurrentProgram ((i + InfiniteBowProcessor::numFactoryPresets) % InfiniteBowProcessor::numFactoryPresets);
        proc.updateHostDisplay (AudioProcessorListener::ChangeDetails().withProgramChanged (true));
        repaint();
    };
    switch (h.kind)
    {
        case HitKind::knob:
            dragKnob = h.index; dragLastY = e.position.y;
            if (auto* prm = knobParam (h.index)) prm->beginChangeGesture();
            break;
        case HitKind::mode:  toggle ("layer"); break;
        case HitKind::voice:
            if (auto* prm = proc.apvts.getParameter ("mode"))
            { prm->beginChangeGesture(); prm->setValueNotifyingHost (prm->convertTo0to1 ((float) h.index)); prm->endChangeGesture(); }
            break;
        case HitKind::preset:     setProgram (h.index); break;
        case HitKind::presetPrev: setProgram (preset - 1); break;
        case HitKind::presetNext: setProgram (preset + 1); break;
        case HitKind::presetName:
            if (statusAlpha > 0.0f) { statusUntil = 0.0; learnLine.clear(); }  // un clic fait revenir la barre de presets
            else showPresetMenu();
            break;
        case HitKind::bow:  footDown[0] = true; toggle ("bow");  askRepaint (Rectangle<float> (150.0f, 150.0f).withCentre (foot[0])); break;
        case HitKind::hold: footDown[1] = true; toggle ("hold"); askRepaint (Rectangle<float> (150.0f, 150.0f).withCentre (foot[1])); break;
        default: break;
    }
}

void InfiniteBowEditor::mouseDrag (const MouseEvent& e)
{
    if (dragKnob < 0) return;
    const float range = 250.0f * k() * (e.mods.isShiftDown() ? 5.0f : 1.0f);
    const float dy = e.position.y - dragLastY; dragLastY = e.position.y;
    if (auto* prm = knobParam (dragKnob)) setKnob (dragKnob, prm->getValue() - dy / range, true);
}

void InfiniteBowEditor::mouseUp (const MouseEvent&)
{
    if (dragKnob >= 0) if (auto* prm = knobParam (dragKnob)) prm->endChangeGesture();
    dragKnob = -1;
    for (int i = 0; i < 2; ++i)
        if (footDown[i]) { footDown[i] = false; askRepaint (Rectangle<float> (150.0f, 150.0f).withCentre (foot[i])); }
}

void InfiniteBowEditor::mouseDoubleClick (const MouseEvent& e)
{
    const auto h = hitAt (toUnits (e.position));
    if (h.kind == HitKind::knob && ! e.mods.isPopupMenu())
        if (auto* prm = knobParam (h.index)) setKnob (h.index, prm->getDefaultValue(), false);
}

void InfiniteBowEditor::mouseWheelMove (const MouseEvent& e, const MouseWheelDetails& w)
{
    const auto h = hitAt (toUnits (e.position));
    if (h.kind == HitKind::knob)
        if (auto* prm = knobParam (h.index)) setKnob (h.index, prm->getValue() + w.deltaY * 0.05f, false);
}

//==============================================================================
//  Menus (design d'Octopus), toujours ouverts a l'endroit du clic
//==============================================================================
void InfiniteBowEditor::handleMidiMenu (int r)
{
    const int n = InfiniteBowProcessor::numLearn;
    if (r >= 1000 && r < 1000 + n) proc.learnTarget.store (proc.learnTarget.load() == r - 1000 ? -1 : r - 1000);
    else if (r >= 1100 && r < 1100 + n)
    {
        proc.ccMap[r - 1100].store (-1);
        if (r - 1100 == InfiniteBowProcessor::learnHold) proc.midiHold.store (false);
    }
    else if (r == 1200) proc.learnTarget.store (-1);
    else if (r == 1201) { proc.learnTarget.store (-1); proc.resetMidiMap(); }
    else if (r == 1210) proc.midiFsToggle.store (false);
    else if (r == 1211) proc.midiFsToggle.store (true);
}

void InfiniteBowEditor::showContextMenu (Point<float> u)
{
    using namespace NineHandsMenu;
    const int learnIdx = learnIndexFor (hitAt (u));
    const Colour accent = layerB ? cyan : orange;
    auto ccText = [this] (int i) { const int cc = proc.ccMap[i].load(); return cc >= 0 ? "CC " + String (cc) : String ("not assigned"); };
    const int lt = proc.learnTarget.load();

    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    if (learnIdx >= 0)
    {
        const String name = InfiniteBowProcessor::learnDef (learnIdx).name;
        const int type = InfiniteBowProcessor::learnDef (learnIdx).type;
        addHeader (m, menuLnf.f, type == InfiniteBowProcessor::learnContinuous ? icoKnob : type == InfiniteBowProcessor::learnFootswitch ? icoPedal : icoSwitch,
                   accent, name, "MIDI: " + ccText (learnIdx));
        m.addItem (1000 + learnIdx, "MIDI Learn: " + name, true, lt == learnIdx);
        m.addItem (1100 + learnIdx, "Clear MIDI: " + name, proc.ccMap[learnIdx].load() >= 0);
        if (lt >= 0) m.addItem (1200, "Cancel MIDI learn");
        m.addSeparator();
    }
    else
        addHeader (m, menuLnf.f, icoPedal, accent, "Arc", "Electronic bow  v" + String (JucePlugin_VersionString));

    PopupMenu sizes, defSizes;
    {
        const char* labels[numSizes] = { "60 %", "75 %", "100 %" };
        const int def = WigaWindowSize::defaultIndex (JucePlugin_Name, numSizes);
        for (int i = 0; i < numSizes; ++i)
        {
            sizes.addItem (1 + i, String (labels[i]) + (i == def ? "  (default)" : ""), true, std::abs (getHeight() - sizeHeight (i)) <= 2);
            defSizes.addItem (20 + i, labels[i], true, i == def);
        }
        sizes.addSeparator();
        sizes.addSubMenu ("Default size (new windows)", defSizes);
    }
    m.addSubMenu ("Plugin size", sizes);
    PopupMenu glowM;
    {
        const int now = roundToInt (glow * 100.0f);
        for (int i = 0; i < NineHandsGlow::numSteps; ++i)
            glowM.addItem (40 + i, String (NineHandsGlow::steps[i]) + " %", true, now == NineHandsGlow::steps[i]);
    }
    m.addSubMenu ("Glow", glowM);
    m.addSeparator();

    PopupMenu midi;
    for (int i = 0; i < InfiniteBowProcessor::numLearn; ++i)
        midi.addItem (1000 + i, "Learn: " + String (InfiniteBowProcessor::learnDef (i).name) + "  (" + ccText (i) + ")", true, lt == i);
    midi.addSeparator();
    if (lt >= 0) midi.addItem (1200, "Cancel MIDI learn");
    midi.addItem (1201, "Clear all MIDI assignments");
    midi.addSeparator();
    midi.addItem (1210, "MIDI footswitches latching (127 = on / 0 = off)", true, ! proc.midiFsToggle.load());
    midi.addItem (1211, "MIDI footswitches momentary (toggle each press)", true, proc.midiFsToggle.load());
    m.addSubMenu ("MIDI", midi);

    m.showMenuAsync (PopupMenu::Options().withMousePosition(),
        [safe = Component::SafePointer<InfiniteBowEditor> (this)] (int r)
        {
            if (safe == nullptr || r <= 0 || r == 9001) return;
            if (r <= numSizes) safe->applyScale ((float) sizeHeight (r - 1) / (float) safe->maxH);
            else if (r >= 20 && r < 20 + numSizes)
            {
                WigaWindowSize::setDefaultIndex (JucePlugin_Name, r - 20);
                safe->applyScale ((float) sizeHeight (r - 20) / (float) safe->maxH);
            }
            else if (r >= 40 && r < 40 + NineHandsGlow::numSteps)
            {
                NineHandsGlow::setPercent (JucePlugin_Name, NineHandsGlow::steps[r - 40]);
                safe->glow = (float) NineHandsGlow::steps[r - 40] / 100.0f;
                safe->repaint();
            }
            else if (r >= 1000) safe->handleMidiMenu (r);
        });
}

void InfiniteBowEditor::showPresetMenu()
{
    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    NineHandsMenu::addHeader (m, menuLnf.f, NineHandsMenu::icoPreset, layerB ? cyan : orange, "Presets", presetText());
    for (int i = 0; i < InfiniteBowProcessor::numFactoryPresets; ++i)
        m.addItem (100 + i, String (i + 1) + ". " + InfiniteBowProcessor::factoryPresets[i].name, true, i == preset);
    const auto area = (screenTop * k()).getSmallestIntegerContainer();
    m.showMenuAsync (PopupMenu::Options().withTargetScreenArea (localAreaToGlobal (area)),
        [safe = Component::SafePointer<InfiniteBowEditor> (this)] (int r)
        {
            if (safe == nullptr || r < 100) return;
            safe->proc.setCurrentProgram (r - 100);
            safe->proc.updateHostDisplay (AudioProcessorListener::ChangeDetails().withProgramChanged (true));
            safe->repaint();
        });
}
