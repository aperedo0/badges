#!/bin/zsh
# shoot.sh <outdir> <tier> <mode> [distances...]
#   mode "rest"   : three launches 15 s apart (shader warm-up), then the rest shot  -> <outdir>/<tier>_rest.png
#   mode "poses"  : for each distance, relaunch, slow drag of that many points, shoot -> <outdir>/<tier>_d<distance>.png
#   mode "warm"   : only the three warm-up launches (the rest shot is left to the caller)
# Assumes the newest ScreenTimeUI.app is already installed on the simulator.
SIM=69A29DD2-C91E-487A-81B9-3B146DF8F07B; BID=com.antonioperedo.screentime.uidev
R=/Users/antonioperedo/Desktop/screen_time
AXE=$(ls ~/.npm/_npx/*/node_modules/xcodebuildmcp/bundled/axe | head -1)
OUT=$1; TIER=$2; MODE=$3; shift 3
mkdir -p $OUT
launch() { xcrun simctl terminate $SIM $BID 2>/dev/null; sleep 1; xcrun simctl launch $SIM $BID -BadgeHeroTier $TIER ${=EXTRA} >/dev/null; }
case $MODE in
  warm|rest)
    for i in 1 2 3; do launch; sleep 15; done
    if [ $MODE = rest ]; then $R/tools/sim/shot $OUT/${TIER}_rest.png >/dev/null; echo "rest $TIER"; fi ;;
  poses)
    for d in "$@"; do
      launch; sleep 14
      $AXE swipe --start-x 200 --start-y 600 --end-x 200 --end-y $((600 - d)) --duration 1.5 --udid $SIM >/dev/null 2>&1
      sleep 1.5
      $R/tools/sim/shot $OUT/${TIER}_d${d}.png >/dev/null; echo "pose $TIER $d"
    done ;;
esac
