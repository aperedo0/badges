#!/bin/zsh
# shoot_sets.sh <pass>:<dir with <tier>.usdz> ... : for each pass, installs that set into the six tiers' data sets, builds once and shoots
# each tier (three launches 15 s apart). Restores the files that were installed before and checks them byte for byte.
E=/Users/antonioperedo/Desktop/badges/edge_fix_20261010; R=/Users/antonioperedo/Desktop/screen_time
SIM=69A29DD2-C91E-487A-81B9-3B146DF8F07B; BID=com.antonioperedo.screentime.uidev
AXE=$(ls ~/.npm/_npx/*/node_modules/xcodebuildmcp/bundled/axe | head -1)
A=$R/ScreenTime/SupportingFiles/Assets.xcassets; O=$E/shots_v2; mkdir -p $O $E/installed_backup
tiers=(steel bronze)
ds() { T=$(echo ${1:0:1} | tr a-z A-Z)${1:1}; echo $A/Badge3DModel$T.dataset/${1}_badge_mobile.usdz; }
for t in $tiers; do cp $(ds $t) $E/installed_backup/$t.usdz; done
restore() { for t in $tiers; do cp $E/installed_backup/$t.usdz $(ds $t); done; for t in $tiers; do cmp -s $(ds $t) $E/installed_backup/$t.usdz || echo "RESTORE FAILED $t"; done; }
trap restore EXIT
xcrun simctl boot $SIM 2>/dev/null
for spec in "$@"; do
  pass=${spec%%:*}; dir=${spec#*:}
  for t in $tiers; do cp $dir/$t.usdz $(ds $t); done
  cd $R; tools/sim/app build > $O/build_$pass.log 2>&1 || { tail -3 $O/build_$pass.log; exit 1; }
  APP=$(ls -dt ~/Library/Developer/Xcode/DerivedData/*/Build/Products/Debug-iphonesimulator/ScreenTimeUI.app | head -1); xcrun simctl install $SIM "$APP"
  for t in $tiers; do
    for i in 1 2 3; do xcrun simctl terminate $SIM $BID 2>/dev/null; sleep 1; xcrun simctl launch $SIM $BID -BadgeHeroTier $t >/dev/null; sleep 15; done
    tools/sim/shot $O/${pass}_$t.png >/dev/null; if [ $pass = v7 ]; then $AXE swipe --start-x 200 --start-y 600 --end-x 200 --end-y 470 --duration 1.5 --udid $SIM >/dev/null 2>&1; sleep 1; tools/sim/shot $O/${pass}_${t}_turn.png >/dev/null; fi; echo "$pass $t"
  done
done
restore; trap - EXIT; cd $R && git status --porcelain | wc -l
