#!/bin/zsh
# try.sh <name>: installs <name>/silver2_badge_mobile.usdz into the Silver data set, builds, shoots Home (Silver 2), then restores whatever file was installed before.
set -e
W=/Users/antonioperedo/Desktop/badges/silver2_metal_claude
DS=/Users/antonioperedo/Desktop/screen_time/ScreenTime/SupportingFiles/Assets.xcassets/Badge3DModelSilver.dataset/silver_badge_mobile.usdz
SIM=69A29DD2-C91E-487A-81B9-3B146DF8F07B; BID=com.antonioperedo.screentime.uidev
cp $DS $W/$1/dataset_before.usdz
cp $W/$1/silver2_badge_mobile.usdz $DS
trap "cp $W/$1/dataset_before.usdz $DS" EXIT
cd /Users/antonioperedo/Desktop/screen_time
tools/sim/app build > $W/$1/build.log 2>&1 || { tail -5 $W/$1/build.log; exit 1; }
APP=$(ls -dt ~/Library/Developer/Xcode/DerivedData/*/Build/Products/Debug-iphonesimulator/ScreenTimeUI.app | head -1)
xcrun simctl install $SIM "$APP"
for i in 1 2 3; do xcrun simctl terminate $SIM $BID 2>/dev/null || true; sleep 1; xcrun simctl launch $SIM $BID -BadgeHeroTier silver >/dev/null; sleep 15; done
tools/sim/shot $W/$1/app.png >/dev/null
echo "shot $1"
