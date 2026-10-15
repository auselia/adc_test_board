#!/bin/zsh
# 1:1 print PDFs of both boards.  usage: hw/tools/print_1to1.sh <python with pymupdf>
cd "$(dirname "$0")/.."
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
export KICAD10_FOOTPRINT_DIR=/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints
for N in ADC_Test ADC_Head; do
  T=$(mktemp -d)
  $K pcb export svg --layers F.Mask,F.Silkscreen,Edge.Cuts --mode-single --black-and-white --fit-page-to-board --exclude-drawing-sheet -o $T/top.svg $N.kicad_pcb >/dev/null
  $K pcb export svg --layers F.Mask,F.Fab,Edge.Cuts --mode-single --black-and-white --fit-page-to-board --exclude-drawing-sheet -o $T/assy.svg $N.kicad_pcb >/dev/null
  $K pcb export svg --layers B.Mask,B.Silkscreen,Edge.Cuts --mode-single --black-and-white --mirror --fit-page-to-board --exclude-drawing-sheet -o $T/bottom.svg $N.kicad_pcb >/dev/null
  for f in top assy bottom; do rsvg-convert -f pdf -o $T/$f.pdf $T/$f.svg; done
  if [ $N = ADC_Head ]; then NM="ADS7057 test board, sensor head"; NT="Board outline 10.0 x 22.0 mm. The SMA J6 stands on this side, the piezo goes on the other face."; else NM="ADS7057 test board"; NT="Board outline 57.0 x 32.0 mm. The right-angle PMOD header J3 sticks out 5.9 mm past the right edge and is not drawn."; fi
  ${1:-python3} tools/print_1to1.py $T/top.pdf $T/assy.pdf $T/bottom.pdf preview/${N}_print_1to1_letter.pdf "$NM" "$NT"
done
