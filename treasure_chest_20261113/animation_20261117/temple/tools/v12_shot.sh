#!/bin/zsh
# Test render of chosen frames of one piece of version 12: v12_shot.sh PIECE "FRAMES" NAME [PCT]
# Writes render/v12_frames/test_NAME/NNNN.png. BORDER="x0,y0,x1,y1" renders part of the picture; HIDE and TWEAK as in shot.sh.
cd /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117
PIECE=$1 ONLY=$2 OUT=render/v12_frames/test_$3 PCT=${4:-50} SAMPLES=${SAMPLES:-24} /Applications/Blender.app/Contents/MacOS/Blender -b chest_reveal_v12_full.blend --python temple/tools/hide.py --python temple/tools/tweak.py --python temple/tools/border.py --python tools/v12_render.py 2>&1 | grep -E "V12 DONE|Error: |Traceback|TWEAK missing" | sed 's/(.*//' | sort | uniq -c | head -5
