#!/bin/zsh
# cand.sh NN [name=value ...] : sets shader constants, builds, installs, warms up, shoots rest + one drag pose, measures, saves a copy of the shader.
W=/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/gem_shader_20261011
R=/Users/antonioperedo/Desktop/screen_time; SIM=69A29DD2-C91E-487A-81B9-3B146DF8F07B
N=$1; shift; D=$W/candidates/$N; mkdir -p $D
[ $# -gt 0 ] && python3 -I $W/tools/setconst.py "$@"
cd $R && tools/sim/app build 2>&1 | tail -3 | grep -v "^$" || exit 1
APP=$(ls -dt ~/Library/Developer/Xcode/DerivedData/*/Build/Products/Debug-iphonesimulator/ScreenTimeUI.app | head -1); xcrun simctl install $SIM "$APP"
for i in 1 2; do $W/tools/quick.sh /tmp/warm.png >/dev/null; done
$W/tools/quick.sh $D/rest.png >/dev/null
$W/tools/quickpose.sh $D/d70.png 70 >/dev/null
cp $R/ScreenTime/Sources/App/Features/Badges/BadgeGemSurface.metal $D/BadgeGemSurface.metal
grep -E "^constant" $R/ScreenTime/Sources/App/Features/Badges/BadgeGemSurface.metal > $D/constants.txt
BOX=200,250,1000,1000 python3 -I $W/tools/montage.py $D/rest_crop.png c$N=$D/rest.png >/dev/null
echo "== candidate $N: $@"; python3 -I $W/tools/measure_gem.py $D/rest.png ${MASKNPZ:-$W/model/out01/gem_planes.npz}
echo "baseline:"; python3 -I $W/tools/measure_gem.py $W/baseline/diamond_rest.png $W/baseline/baseline_outline.npz
