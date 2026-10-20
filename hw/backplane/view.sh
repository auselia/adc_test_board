#!/bin/zsh
# usage: view.sh NAME "layers" width_px  -> out/NAME_view.png
cd "$(dirname "$0")"
S=/Applications/KiCad/KiCad.app/Contents/SharedSupport; export KICAD10_FOOTPRINT_DIR=$S/footprints
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb export svg --layers "${2:-F.Cu,F.Silkscreen,Edge.Cuts}" --exclude-drawing-sheet --page-size-mode 2 -o out/$1_v.svg $1.kicad_pcb >/dev/null
rsvg-convert -w ${3:-2400} -b white out/$1_v.svg -o out/$1_view.png
