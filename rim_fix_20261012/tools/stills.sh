#!/bin/zsh
# stills.sh <tier> <model.usdz> <home_rest.png> <out.png> : Badges screen still (600 x 600) cut from a real Home render at the
# fixed art frame, alpha from the model's projected triangles (Codex's still_cut.py)
R=~/Desktop/badges/rim_fix_20261012; PY=/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13
$PY -I ~/Desktop/badges/stills/usdz_tris.py $2 $R/work/$1/final_tris.npz | tail -1
python3 -I ~/Desktop/badges/gold_diamond_20261009/diamond/codex_rest_20261011/approved5/tools/still_cut.py $R/work/$1/final_tris.npz $3 $4
