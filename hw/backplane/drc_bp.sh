#!/bin/zsh
cd "$(dirname "$0")"
S=/Applications/KiCad/KiCad.app/Contents/SharedSupport
KICAD10_SYMBOL_DIR=$S/symbols KICAD10_FOOTPRINT_DIR=$S/footprints /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb drc --severity-all -o out/drc_$1.rpt $1.kicad_pcb | grep -i -E "found|violation|unconnected"
grep -E "^\[" out/drc_$1.rpt | sed 's/\].*/]/' | sort | uniq -c
