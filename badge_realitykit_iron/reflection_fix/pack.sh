#!/bin/zsh
# pack.sh <faded dir> <out.usdz>: repacks the usdc + textures (no previews) into a USDZ and checks it
set -e
D=$1; OUT=$2; P=$(mktemp -d)
cp $D/iron_badge_mobile.usdc $P/ && mkdir $P/textures && cp $D/textures/*.png $P/textures/ && rm -f $P/textures/*.weight.png
cd $P && rm -f $OUT && usdzip $OUT iron_badge_mobile.usdc textures/*.png >/dev/null
usdchecker --arkit $OUT 2>&1 | tail -2
rm -rf $P
