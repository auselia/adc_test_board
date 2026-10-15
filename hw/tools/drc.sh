#!/bin/zsh
cd "$(dirname "$0")/.."
N=ADC_Test; [ "$BOARD" = head ] && N=ADC_Head
S=/Applications/KiCad/KiCad.app/Contents/SharedSupport
KICAD10_SYMBOL_DIR=$S/symbols KICAD10_FOOTPRINT_DIR=$S/footprints /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc --severity-all --schematic-parity -o drc_$N.rpt $N.kicad_pcb | grep -i -E "found|violation|unconnected"
grep -E "^\[" drc_$N.rpt | sed 's/\].*/]/' | sort | uniq -c
