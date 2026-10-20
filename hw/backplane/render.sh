#!/bin/zsh
# usage: render.sh BP_Module [layers]  -> out/BP_Module_top.png
cd "$(dirname "$0")"
S=/Applications/KiCad/KiCad.app/Contents/SharedSupport; K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
export KICAD10_FOOTPRINT_DIR=$S/footprints KICAD10_SYMBOL_DIR=$S/symbols
L=${2:-F.Cu,F.Silkscreen,F.Courtyard,Edge.Cuts}
$K pcb export pdf --layers $L -o out/$1.pdf $1.kicad_pcb >/dev/null 2>&1
pdftoppm -r ${3:-80} -png out/$1.pdf out/$1_view >/dev/null 2>&1; ls out/$1_view*
