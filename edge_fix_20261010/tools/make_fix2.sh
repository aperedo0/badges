#!/bin/zsh
# make_fix2.sh <tier lowercase> <inset_px> : silhouette based refill of every color and emissive map, repacked to fix2/<tier>.usdz
set -e
E=/Users/antonioperedo/Desktop/badges/edge_fix_20261010; t=$1; k=$2; D=$E/work3/$t
mkdir -p $D $E/fix3 $E/model; cp -R $E/orig/$t/* $D/
u=$(cd $D && ls *.usdc | head -1)
[ -f $E/model/$t.npz ] || /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 $E/tools/export_all.py $D/$u $E/model/$t.npz 2>&1 | grep -v Coding
/usr/local/bin/python3 -I $E/tools/edge_fill2.py $E/model/$t.npz $D $k
files=$(unzip -Z1 $E/orig/$t/${t}_badge_mobile.usdz | tr '\n' ' ')
(cd $D && usdzip $E/fix3/$t.usdz ${=files} >/dev/null)
echo "$t $(usdchecker --arkit $E/fix3/$t.usdz 2>&1 | grep -c 'Success!') $(stat -f %z $E/fix3/$t.usdz)"
