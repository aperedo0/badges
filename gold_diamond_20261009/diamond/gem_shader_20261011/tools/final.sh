#!/bin/zsh
# final.sh : builds the current code, installs it, and shoots the final Diamond set under final/: rest, the 94/133/171 poses, the 12 contact frames.
W=/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/gem_shader_20261011
R=/Users/antonioperedo/Desktop/screen_time; SIM=69A29DD2-C91E-487A-81B9-3B146DF8F07B
OUT=${1:-$W/final}; mkdir -p $OUT/contact $OUT/contact2
cd $R && tools/sim/app build 2>&1 | tail -2
APP=$(ls -dt ~/Library/Developer/Xcode/DerivedData/*/Build/Products/Debug-iphonesimulator/ScreenTimeUI.app | head -1); xcrun simctl install $SIM "$APP"
$W/tools/shoot.sh $OUT diamond rest
$W/tools/shoot.sh $OUT diamond poses 94 133 171
for d in 57 58 59 60 61 62 64 65 66 68 69 71; do $W/tools/quickpose.sh $OUT/contact/d$d.png $d >/dev/null; echo -n "c$d "; done; echo
for d in 66 67 68 69 70 71 72 73 74 76 78 80; do $W/tools/quickpose.sh $OUT/contact2/d$d.png $d >/dev/null; echo -n "k$d "; done; echo
