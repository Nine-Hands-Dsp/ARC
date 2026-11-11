// Captures PNG de la fenetre reelle d'ARC (meme code que le plugin), pour l'apercu et la notice.
#include "PluginProcessor.h"
#include "PluginEditor.h"
#include "BinaryData.h"
using namespace juce;

int main (int argc, char** argv)
{
    ScopedJuceInitialiser_GUI init;
    const String out = argc > 1 ? argv[1] : ".";
    InfiniteBowProcessor proc;
    proc.prepareToPlay (48000.0, 256);
    std::unique_ptr<AudioProcessorEditor> ed (proc.createEditor());
    auto* se = static_cast<InfiniteBowEditor*> (ed.get());
    std::printf ("taille par defaut : %d x %d\n", ed->getWidth(), ed->getHeight());

    auto pump = [] (int n) { for (int i = 0; i < n; ++i) MessageManager::getInstance()->runDispatchLoopUntil (35); };
    auto set = [&] (const char* id, float v) { if (auto* p = proc.apvts.getParameter (id)) p->setValueNotifyingHost (p->convertTo0to1 (v)); };
    auto save = [&] (const String& name, float scale)
    {
        auto img = ed->createComponentSnapshot (ed->getLocalBounds(), true, scale);
        File f (out + "/" + name + ".png"); f.deleteFile();
        FileOutputStream os (f); PNGImageFormat().writeImageToStream (img, os);
        std::printf ("%s (%d x %d)\n", f.getFullPathName().toRawUTF8(), img.getWidth(), img.getHeight());
    };
    auto state = [&] (int preset, bool bow, bool hold, bool layerB, int glowPc, const String& status)
    {
        proc.setCurrentProgram (preset);
        set ("bow", bow ? 1.f : 0.f); set ("hold", hold ? 1.f : 0.f); set ("layer", layerB ? 1.f : 0.f);
        se->setGlowPercent (glowPc);
        pump (4);
        se->flash (status, status.isNotEmpty() ? 60.0 : 0.0);
        se->settleForCapture();
        pump (2);
    };

    se->forceRenderScale (2.0f);
    state (0, true, false, false, 100, {});
    save ("arc_default", 2.0f);

    se->setWindowHeight (900);
    se->forceRenderScale (2.0f);
    pump (6);
    state (0, true, false, false, 100, {});                    save ("arc_exact_orange", 2.0f);
    state (2, true, true, true, 100, {});                      save ("arc_exact_cyan", 2.0f);
    state (0, false, false, false, 100, {});                   save ("arc_exact_bypass", 2.0f);
    state (0, true, false, false, 100, "ATTACK  0.60 s");      save ("arc_exact_status", 2.0f);
    state (0, true, true, false, 25, {});                      save ("arc_glow_25", 2.0f);

    // ecran de corde en jeu (etat du moteur simule : La2 a l'archet, puis larsen sur le 5e harmonique)
    auto playing = [&] (int preset, float hz, float fb, const String& status, const char* name)
    {
        proc.uiPitchHz.store (hz); proc.uiState.store (2); proc.uiLevel.store (0.85f);
        proc.uiFeedback.store (fb); proc.uiFbHarm.store (5);
        state (preset, true, false, false, 100, status);
        save (name, 2.0f);
    };
    playing (0, 110.0f, 0.0f, "ATTACK  600 ms  (MIDI 59)  |  CC20=59", "arc_play_status");
    playing (0, 110.0f, 0.0f, String::fromUTF8 ("MIDI LEARN  \xc2\xb7  HOLD FOOTSWITCH"), "arc_play_learn");
    playing (0, 110.0f, 0.0f, "HOLD FOOTSWITCH  =  CC 64", "arc_play_assigned");
    playing (0, 110.0f, 0.0f, "ATTACK  600 ms  (MIDI 59)  |  CC64=127  |  HOLD", "arc_play_hold");
    playing (7, 110.0f, 0.8f, {}, "arc_play_larsen");
    ed.reset();
    return 0;
}
