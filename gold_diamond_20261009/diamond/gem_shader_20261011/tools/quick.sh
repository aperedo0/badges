#!/bin/zsh
# quick.sh <out.png> [launch args...] : relaunches the Diamond with the given extra launch args, waits for the 3D badge, shoots Home.
SIM=69A29DD2-C91E-487A-81B9-3B146DF8F07B; BID=com.antonioperedo.screentime.uidev
R=/Users/antonioperedo/Desktop/screen_time
OUT=$1; shift
xcrun simctl terminate $SIM $BID 2>/dev/null; sleep 1
xcrun simctl launch $SIM $BID -BadgeHeroTier diamond "$@" >/dev/null; sleep ${WAIT:-13}
$R/tools/sim/shot $OUT >/dev/null; echo "$OUT"
