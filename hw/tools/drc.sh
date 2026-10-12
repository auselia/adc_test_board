#!/bin/zsh
cd "$(dirname "$0")/.."
S=/Applications/KiCad/KiCad.app/Contents/SharedSupport
KICAD10_SYMBOL_DIR=$S/symbols KICAD10_FOOTPRINT_DIR=$S/footprints /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc --severity-all --schematic-parity -o drc.rpt ADC_Test.kicad_pcb | grep -i -E "found|violation|unconnected"
grep -E "^\[" drc.rpt | sed 's/\].*/]/' | sort | uniq -c
