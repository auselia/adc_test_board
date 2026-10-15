#!/bin/zsh
# Build -> GND plane + DSN -> Freerouting -> import SES.   usage: [BOARD=head] tools/route.sh [passes]
cd "$(dirname "$0")/.."
PYK=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
FR=${FREEROUTING:-freerouting}
export BOARD=${BOARD:-adc}
N=ADC_Test; [ "$BOARD" = head ] && N=ADC_Head
$PYK tools/build_board.py 2>&1 | grep -E "saved|moved|Error|Trace"
python3 tools/fix_pro.py
$PYK tools/prep_route.py 2>&1 | grep dsn
$FR -de ${N}_route.dsn -do ${N}_route.ses -mp ${1:-40} --gui.enabled=false > route_$N.log 2>&1
grep -E "Optimization stage completed|Auto-routing.*completed|unrouted" route_$N.log | tail -2 | cut -c1-260
$PYK tools/import_ses.py ${N}_route.ses 2>&1 | grep -E "import|tracks"
python3 tools/fix_pro.py >/dev/null
$PYK tools/finish.py 2>&1 | grep -E "stitching|finished"; python3 tools/fix_pro.py >/dev/null
