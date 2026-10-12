#!/bin/zsh
# try_tier.sh <tier> <Dataset> <file.usdz name> <candidate.usdz> <out.png>: temporarily installs a candidate in its tier's data set, builds, shoots Home, restores.
set -e
SIM=69A29DD2-C91E-487A-81B9-3B146DF8F07B; BID=com.antonioperedo.screentime.uidev
cd /Users/antonioperedo/Desktop/screen_time
DS=ScreenTime/SupportingFiles/Assets.xcassets/$2.dataset/$3
B=/Users/antonioperedo/Desktop/badges/edge_fix_20261010/orig/$1/$3
cmp -s $DS $B || { echo "data set differs from orig before test, stopping"; exit 1; }
trap "cp $B $DS" EXIT
cp $4 $DS
tools/sim/app build > ${5%.png}.build.log 2>&1 || { tail -5 ${5%.png}.build.log; exit 1; }
APP=$(ls -dt ~/Library/Developer/Xcode/DerivedData/*/Build/Products/Debug-iphonesimulator/ScreenTimeUI.app | head -1)
xcrun simctl install $SIM "$APP"
for i in 1 2 3; do xcrun simctl terminate $SIM $BID 2>/dev/null || true; sleep 1; xcrun simctl launch $SIM $BID -BadgeHeroTier $1 >/dev/null; sleep 15; done
tools/sim/shot $5 >/dev/null
echo "shot $5"
