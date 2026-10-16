#!/bin/zsh
# Gerbers + drill + pick-and-place, zipped for JLCPCB, for both boards.  usage: tools/fab.sh
cd "$(dirname "$0")/.."
S=/Applications/KiCad/KiCad.app/Contents/SharedSupport; K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
export KICAD10_FOOTPRINT_DIR=$S/footprints KICAD10_SYMBOL_DIR=$S/symbols
PYK=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
rm -rf fab/gerber fab/gerber_head; mkdir -p fab/gerber fab/gerber_head
for N in ADC_Test ADC_Head; do
  G=fab/gerber; [ $N = ADC_Head ] && G=fab/gerber_head
  $K pcb export gerbers --layers F.Cu,B.Cu,F.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask --use-drill-file-origin -o $G/ $N.kicad_pcb | tail -1
  $K pcb export drill --format excellon --excellon-units mm --excellon-separate-th --generate-map --map-format gerberx2 -o $G/ $N.kicad_pcb | tail -1
  $K pcb export pos --format csv --units mm --side front --use-drill-file-origin -o fab/${N}_pos_kicad.csv $N.kicad_pcb | tail -1
  (cd $G && rm -f ../${N}_gerbers.zip && zip -q ../${N}_gerbers.zip *)
done
ls -la fab/*.zip
# solder-joint counts for tools/cost.py
$PYK - <<'PY' 2>&1 | grep -v -E "assert|Warn"
import pcbnew,json
out={}
for name,skip in (('ADC_Test',('H1','H2')+tuple('JP%d'%k for k in range(1,7))+tuple('TP%d'%k for k in range(1,21))),('ADC_Head',('TP1','TP2'))):
    b=pcbnew.LoadBoard(name+'.kicad_pcb'); smd=tht=0
    for f in b.GetFootprints():
        if f.GetReference() in skip or f.GetReference().startswith('MB'): continue
        for p in f.Pads():
            if not p.GetNumber(): continue
            if p.GetAttribute()==pcbnew.PAD_ATTRIB_PTH: tht+=1
            else: smd+=1
    out[name]={'smd':smd,'tht':tht}
out['smd']=out['ADC_Test']['smd']; out['tht']=out['ADC_Test']['tht']     # keeps cost.py's reading of the main board
json.dump(out,open('fab/joints.json','w')); print('joints',out)
PY
