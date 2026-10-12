#!/bin/zsh
# shoot_pairs.sh: pass 1 shoots every tier with the installed originals; pass 2 installs all seven fix3 files at once, shoots every
# tier plus a slow scroll proof of 3D, then restores all seven from orig/ and checks git status.
E=/Users/antonioperedo/Desktop/badges/edge_fix_20261010; R=/Users/antonioperedo/Desktop/screen_time
SIM=69A29DD2-C91E-487A-81B9-3B146DF8F07B; BID=com.antonioperedo.screentime.uidev
AXE=$(ls ~/.npm/_npx/*/node_modules/xcodebuildmcp/bundled/axe | head -1)
A=$R/ScreenTime/SupportingFiles/Assets.xcassets; O=$E/pairs; mkdir -p $O
tiers=(copper bronze steel silver gold platinum diamond)
cap() { echo ${1:0:1} | tr a-z A-Z; }
restore() { for t in $tiers; do T=$(cap $t)${t:1}; cp $E/orig/$t/${t}_badge_mobile.usdz $A/Badge3DModel$T.dataset/${t}_badge_mobile.usdz; done; }
for t in $tiers; do T=$(cap $t)${t:1}; cmp -s $A/Badge3DModel$T.dataset/${t}_badge_mobile.usdz $E/orig/$t/${t}_badge_mobile.usdz || { echo "$t data set differs from orig, stopping"; exit 1; }; done
shoot() { # $1 prefix
  cd $R; tools/sim/app build > $O/build_$1.log 2>&1 || { tail -3 $O/build_$1.log; return 1; }
  APP=$(ls -dt ~/Library/Developer/Xcode/DerivedData/*/Build/Products/Debug-iphonesimulator/ScreenTimeUI.app | head -1); xcrun simctl install $SIM "$APP"
  for t in $tiers; do
    for i in 1 2 3; do xcrun simctl terminate $SIM $BID 2>/dev/null; sleep 1; xcrun simctl launch $SIM $BID -BadgeHeroTier $t >/dev/null; sleep 15; done
    tools/sim/shot $O/${1}_$t.png >/dev/null
    if [ $1 = after ]; then $AXE swipe --start-x 200 --start-y 600 --end-x 200 --end-y 470 --duration 1.5 --udid $SIM >/dev/null 2>&1; sleep 1; tools/sim/shot $O/${1}_${t}_turn.png >/dev/null; fi
    echo "$1 $t"
  done
}
shoot before || exit 1
trap restore EXIT
for t in $tiers; do T=$(cap $t)${t:1}; cp $E/fix3/$t.usdz $A/Badge3DModel$T.dataset/${t}_badge_mobile.usdz; done
shoot after
restore; trap - EXIT
cd $R && git status --porcelain
