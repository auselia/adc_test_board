#!/bin/zsh
# usage: route_bp.sh BP_Module|FMC_Adapter [passes]   (layout_*.py must have been run)
cd "$(dirname "$0")"
PYK=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
FR=${FREEROUTING:-/private/tmp/claude-501/-Users-nico-Documents-GitHub/fead1849-5d70-409e-9ee0-3f60fd37a82d/scratchpad/fr/freerouting.app/Contents/MacOS/freerouting}
N=$1
$PYK bp_prep.py $N 2>&1 | grep -v -i -E "warn|assert"
$FR -de $N.dsn -do $N.ses -mp ${2:-40} --gui.enabled=false > out/route_$N.log 2>&1
grep -E "Optimization stage completed|Auto-routing.*completed|unrouted|ERROR|Exception" out/route_$N.log | tail -3 | cut -c1-250
$PYK bp_import.py $N 2>&1 | grep -E "import|tracks"
