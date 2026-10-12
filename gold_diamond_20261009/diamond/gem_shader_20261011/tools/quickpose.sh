#!/bin/zsh
# quickpose.sh <out.png> <drag points> [launch args...] : relaunch, slow drag up by that many points, shoot.
SIM=69A29DD2-C91E-487A-81B9-3B146DF8F07B; BID=com.antonioperedo.screentime.uidev
R=/Users/antonioperedo/Desktop/screen_time
AXE=$(ls ~/.npm/_npx/*/node_modules/xcodebuildmcp/bundled/axe | head -1)
OUT=$1; D=$2; shift 2
xcrun simctl terminate $SIM $BID 2>/dev/null; sleep 1
xcrun simctl launch $SIM $BID -BadgeHeroTier diamond "$@" >/dev/null; sleep ${WAIT:-13}
$AXE swipe --start-x 200 --start-y 600 --end-x 200 --end-y $((600 - D)) --duration 1.5 --udid $SIM >/dev/null 2>&1
sleep 1.5
$R/tools/sim/shot $OUT >/dev/null; echo "$OUT"
