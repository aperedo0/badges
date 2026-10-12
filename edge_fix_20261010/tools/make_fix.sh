#!/bin/zsh
# make_fix.sh <tier lowercase> <Material> <inset> <map>... : copies the installed package, refills the front color and emissive maps outside the inset coverage, repacks to fix/<tier>_k<inset>.usdz
set -e
E=/Users/antonioperedo/Desktop/badges/edge_fix_20261010
t=$1; m=$2; k=$3; D=$E/work/${t}_k$k
mkdir -p $D; cp -R $E/orig/$t/* $D/
u=$(cd $D && ls *.usdc | head -1)
maps="${@:4}"
/usr/local/bin/python3 -I $E/tools/edge_fill.py $E/tris/$t.npz $m $D $k ${=maps} > $D/fill.log
mkdir -p $E/fix
files=$(cd $D && unzip -Z1 $E/orig/$t/${t}_badge_mobile.usdz | tr '\n' ' ')
(cd $D && rm -f $E/fix/${t}_k$k.usdz 2>/dev/null; usdzip $E/fix/${t}_k$k.usdz ${=files} >/dev/null)
echo "$t k$k $(usdchecker --arkit $E/fix/${t}_k$k.usdz 2>&1 | grep -c 'Success!') $(stat -f %z $E/fix/${t}_k$k.usdz)"
