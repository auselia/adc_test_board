#!/bin/zsh
# 1:1 print PDF of the board.  usage: hw/tools/print_1to1.sh <python with pymupdf>
cd "$(dirname "$0")/.."
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli; T=$(mktemp -d)
export KICAD10_FOOTPRINT_DIR=/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints
$K pcb export svg --layers F.Mask,F.Silkscreen,Edge.Cuts --mode-single --black-and-white --fit-page-to-board --exclude-drawing-sheet -o $T/top.svg ADC_Test.kicad_pcb >/dev/null
$K pcb export svg --layers F.Mask,F.Fab,Edge.Cuts --mode-single --black-and-white --fit-page-to-board --exclude-drawing-sheet -o $T/assy.svg ADC_Test.kicad_pcb >/dev/null
$K pcb export svg --layers B.Mask,B.Silkscreen,Edge.Cuts --mode-single --black-and-white --mirror --fit-page-to-board --exclude-drawing-sheet -o $T/bottom.svg ADC_Test.kicad_pcb >/dev/null
for f in top assy bottom; do rsvg-convert -f pdf -o $T/$f.pdf $T/$f.svg; done
${1:-python3} tools/print_1to1.py $T/top.pdf $T/assy.pdf $T/bottom.pdf preview/ADC_Test_print_1to1_letter.pdf
