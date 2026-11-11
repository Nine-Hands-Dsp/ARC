# Outil hors plugin : compile le processeur + la fenetre d'ARC sous Linux et exporte des captures PNG (apercu, notice)
#   cmake -B build-render -S tools/render -DJUCE_DIR=/chemin/vers/JUCE && cmake --build build-render -j8
#   build-render/ArcRender_artefacts/ArcRender <dossier de sortie>
cmake_minimum_required(VERSION 3.22)
project(ArcRender VERSION 1.0.0)
set(CMAKE_CXX_STANDARD 17)
add_subdirectory(${JUCE_DIR} JUCE)
set(W ${CMAKE_CURRENT_SOURCE_DIR}/../..)
juce_add_binary_data(ArcAssets SOURCES
  ${W}/assets/background.png ${W}/assets/knob_marker.png
  ${W}/assets/led_orange_160.png ${W}/assets/led_orange_185.png ${W}/assets/led_cyan_160.png ${W}/assets/led_cyan_185.png
  ${W}/assets/ArcLogoWhite.svg ${W}/assets/NineHandsLogoWhite.svg
  ${W}/assets/fonts/Poppins-Regular.ttf ${W}/assets/fonts/Poppins-Medium.ttf ${W}/assets/fonts/Poppins-Bold.ttf)
juce_add_console_app(ArcRender PRODUCT_NAME "ArcRender")
target_sources(ArcRender PRIVATE main.cpp ${W}/PluginProcessor.cpp ${W}/PluginEditor.cpp ${W}/WindowMinSize.cpp)
target_include_directories(ArcRender PRIVATE ${W})
target_compile_definitions(ArcRender PRIVATE JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0 JUCE_ALSA=0 JUCE_JACK=0
  JUCE_USE_XRANDR=0 JUCE_USE_XINERAMA=0 JUCE_USE_XCURSOR=0 JUCE_USE_XSHM=0 JucePlugin_Name="Arc" JucePlugin_Build_VST3=0
  JucePlugin_VersionString="3.1.0" JUCE_STANDALONE_APPLICATION=1 JUCE_MODAL_LOOPS_PERMITTED=1)
target_link_libraries(ArcRender PRIVATE ArcAssets juce::juce_audio_utils juce::juce_dsp juce::juce_recommended_config_flags)
