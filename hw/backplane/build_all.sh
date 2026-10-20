#!/bin/zsh
# usage: build_all.sh BP_Module|FMC_Adapter   schematic -> layout -> route -> finish -> DRC -> fab
cd "$(dirname "$0")"
PYK=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
N=$1; L=module; G=module; [ $N = FMC_Adapter ] && { L=adapter; G=adapter; }
python3 $G.py out | tail -1
$PYK layout_$L.py 2>&1 | grep -E "saved|fixed|west|Error|Trace"
./route_bp.sh $N ${2:-30}
$PYK bp_finish.py $N 2>&1 | grep finished
./drc_bp.sh $N
./fab_bp.sh $N
