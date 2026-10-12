#!/bin/zsh
E=/Users/antonioperedo/Desktop/badges/edge_fix_20261010
mkdir -p $E/shots2
for t in copper bronze steel silver gold platinum diamond; do
  T=$(echo ${t:0:1} | tr a-z A-Z)${t:1}
  $E/tools/try_tier.sh $t Badge3DModel$T ${t}_badge_mobile.usdz $E/fix2/$t.usdz $E/shots2/$t.png 2>&1 | tail -1
done
cd /Users/antonioperedo/Desktop/screen_time && git status --porcelain
