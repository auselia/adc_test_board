#!/bin/zsh
# usage: fab_bp.sh BP_Module|FMC_Adapter -> fab/NAME_gerbers.zip, pos, BOM, CPL
cd "$(dirname "$0")"
S=/Applications/KiCad/KiCad.app/Contents/SharedSupport; K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
export KICAD10_FOOTPRINT_DIR=$S/footprints KICAD10_SYMBOL_DIR=$S/symbols
N=$1; G=fab/gerber_$N
rm -rf $G; mkdir -p $G
$K pcb export gerbers --layers F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask --use-drill-file-origin -o $G/ $N.kicad_pcb | tail -1
$K pcb export drill --format excellon --excellon-units mm --excellon-separate-th --generate-map --map-format gerberx2 -o $G/ $N.kicad_pcb | tail -1
$K pcb export pos --format csv --units mm --side both --use-drill-file-origin -o fab/${N}_pos_kicad.csv $N.kicad_pcb | tail -1
(cd $G && rm -f ../${N}_gerbers.zip && zip -q ../${N}_gerbers.zip *)
python3 bp_jlc.py $N
ls -la fab/${N}_gerbers.zip
