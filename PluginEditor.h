#pragma once

#include <juce_gui_basics/juce_gui_basics.h>
#include <juce_audio_processors/juce_audio_processors.h>
#include "PluginProcessor.h"
#include "WindowMinSize.h"
#include "NineHandsMenu.h"

//==============================================================================
//  ARC v3 (NINE HANDS | DSP) - format double, d'apres design/Arc_Mockup_v003.svg
//  Fond : assets/background.png (2350 x 1800, pedale plein cadre, transparent autour des jacks).
//  Repere du plugin : 1175 x 900 unites (= image / 2). Tout le reste est dessine en vectoriel par l'editeur.
//==============================================================================
namespace arcui
{
    constexpr float UW = 1175.0f, UH = 900.0f;

    const juce::Colour orange   { 0xffff9228 };
    const juce::Colour cyan     { 0xff2ee2ff };
    const juce::Colour textCol  { 0xffe8eaee };
    const juce::Colour noteOrg  { 0xffff8a1f };

    // potards : centre, rayon (unites)
    struct KnobDef { float x, y; const char* idA; const char* idB; const char* nameA; const char* nameB; };
    constexpr float knobR = 52.5f, arcR = 62.5f;
}

//==============================================================================
class InfiniteBowEditor : public juce::AudioProcessorEditor, private juce::Timer
{
public:
    explicit InfiniteBowEditor (InfiniteBowProcessor&);
    ~InfiniteBowEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseDrag (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    void mouseMove (const juce::MouseEvent&) override;
    void mouseDoubleClick (const juce::MouseEvent&) override;
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails&) override;

    // outil de capture (tools/render : apercu, notice) - inutilise dans le plugin
    void forceRenderScale (float s) { forcedScale = s; bgCache = {}; rebuildCache(); }
    void setGlowPercent (int pc) { glow = (float) pc / 100.0f; repaint(); }
    void setWindowHeight (int h) { setSize (juce::roundToInt ((float) h * arcui::UW / arcui::UH), h); }
    void flash (const juce::String& text, double seconds);
    void settleForCapture();

private:
    // ------------------------------------------------------------- zones cliquables
    enum class HitKind { none, knob, mode, voice, preset, presetPrev, presetName, presetNext, bow, hold };
    struct Hit { HitKind kind = HitKind::none; int index = -1; };
    Hit hitAt (juce::Point<float> u) const;
    juce::Point<float> toUnits (juce::Point<float> p) const { return p / k(); }
    float k() const { return (float) getHeight() / arcui::UH; }

    // ------------------------------------------------------------- dessin
    void drawLeds (juce::Graphics&);
    void drawLed (juce::Graphics&, juce::Point<float> c, float r, juce::Colour col, float level);
    void drawKnobs (juce::Graphics&);
    void drawPrint (juce::Graphics&);
    void drawTopScreen (juce::Graphics&);
    void drawMainScreen (juce::Graphics&);
    void drawFootRings (juce::Graphics&);
    juce::String statusText() const;
    juce::String presetText() const;
    static juce::String noteName (float hz);

    // ------------------------------------------------------------- potards
    juce::RangedAudioParameter* knobParam (int i) const;
    void setKnob (int i, float v01, bool gesture);
    int dragKnob = -1; float dragLastY = 0.0f;
    float knobAngle[7] {}, knobDrawn[7] {}, blurSpan[7] {}, blurDir[7] {};

    // ------------------------------------------------------------- menus, MIDI Learn, taille
    void showContextMenu (juce::Point<float> u);
    void showPresetMenu();
    void handleMidiMenu (int r);
    int learnIndexFor (const Hit& h) const;
    void applyScale (float s);
    static constexpr int numSizes = 3;
    static int sizeHeight (int idx);
    float openScale = -1.0f;

    // ------------------------------------------------------------- anti-gel v2
    void timerCallback() override;
    void parentHierarchyChanged() override;
    void visibilityChanged() override;
    void useSoftwareRenderer();
    void rebuildCache();
    void askRepaint (juce::Rectangle<float> unitsRect);
    void attachMinSize();
    void* lastPeer = nullptr;
    double lastRendererCheckMs = 0.0, lastPaintMs = 0.0, repaintAskedMs = 0.0, lastScaleCheckMs = 0.0;
    int resizeSettle = 0;
    float cachedFor = -1.0f, forcedScale = 0.0f;

    InfiniteBowProcessor& proc;
    juce::Image background, bgCache, ledOrange[2], ledCyan[2], marker;
    std::unique_ptr<juce::Drawable> arcLogo, nhLogo;
    juce::Typeface::Ptr poppinsMed, poppinsReg, poppinsBold;
    NineHandsMenu::MenuLnf menuLnf;
    wiga::WindowMinSize minSize;
    int minW = 0, minH = 0, maxW = 0, maxH = 0;

    // ------------------------------------------------------------- etat affiche
    bool layerB = false;
    int voice = 0, preset = 0;
    float glow = 1.0f;
    float ledLvl[13] {};                   // 0 mode, 1-3 voice, 4-11 presets, 12 inutilise
    float bowLvl = 0.0f, holdLvl = 0.0f, shownLevel = 0.0f;
    double phase = 0.0;
    // ecran de corde « flux d'archet » : particules simulees par le timer, dessinees par paint
    struct Particle { float x, v, y, vy, life, ph, r; };
    std::vector<Particle> parts;
    juce::Random rng;
    double flowTime = 0.0;
    void stepFlow (float dt);
    bool footDown[2] { false, false };
    Hit hover;

    // ligne d'etat (meme ecran que la barre de presets) : apparait pendant un reglage puis s'efface
    std::vector<float> lastValues;
    juce::String lastParamId { "attack" }, learnLine;
    double statusUntil = 0.0, learnLineUntil = 0.0;
    float statusAlpha = 0.0f;
    int lastCC = -1, lastCCVal = 0;
    juce::String drawnStatus, drawnPreset, drawnDisplayKey;
    float dStatusA = -1.0f, dLevel = -1.0f, dPos = -1.0f;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (InfiniteBowEditor)
};
