#!/bin/zsh
E=/Users/antonioperedo/Desktop/badges/edge_fix_20261010
mkdir -p $E/shots
for spec in "copper Badge3DModelCopper 8" "bronze Badge3DModelBronze 7" "steel Badge3DModelSteel 6" "gold Badge3DModelGold 7" "platinum Badge3DModelPlatinum 7" "diamond Badge3DModelDiamond 6"; do
  set -- ${=spec}
  $E/tools/try_tier.sh $1 $2 ${1}_badge_mobile.usdz $E/fix/${1}_k$3.usdz $E/shots/${1}_k$3.png 2>&1 | tail -1
done
cd /Users/antonioperedo/Desktop/screen_time && git status --porcelain
