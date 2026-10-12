#!/bin/zsh
# Gerbers + drill + pick-and-place, zipped for JLCPCB.  usage: tools/fab.sh
cd "$(dirname "$0")/.."
S=/Applications/KiCad/KiCad.app/Contents/SharedSupport; K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
export KICAD10_FOOTPRINT_DIR=$S/footprints KICAD10_SYMBOL_DIR=$S/symbols
rm -rf fab/gerber; mkdir -p fab/gerber
$K pcb export gerbers --layers F.Cu,B.Cu,F.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask --use-drill-file-origin -o fab/gerber/ ADC_Test.kicad_pcb | tail -1
$K pcb export drill --format excellon --excellon-units mm --excellon-separate-th --generate-map --map-format gerberx2 -o fab/gerber/ ADC_Test.kicad_pcb | tail -1
$K pcb export pos --format csv --units mm --side front --use-drill-file-origin -o fab/ADC_Test_pos_kicad.csv ADC_Test.kicad_pcb | tail -1
(cd fab/gerber && rm -f ../ADC_Test_gerbers.zip && zip -q ../ADC_Test_gerbers.zip *)
ls fab/gerber; ls -la fab/ADC_Test_gerbers.zip
# solder-joint counts for tools/cost.py
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 - <<'PY' 2>&1 | grep -v -E "assert|Warn"
import pcbnew,json
b=pcbnew.LoadBoard('ADC_Test.kicad_pcb'); smd=tht=0
for f in b.GetFootprints():
    if f.GetReference() in('H1','H2','C31'): continue
    n=len([p for p in f.Pads() if p.GetNumber()]); t=any(p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH for p in f.Pads())
    if t: tht+=n
    else: smd+=n
json.dump({'smd':smd,'tht':tht},open('fab/joints.json','w')); print('joints: SMD',smd,'THT',tht)
PY
