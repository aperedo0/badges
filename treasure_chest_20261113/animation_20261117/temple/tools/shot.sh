#!/bin/zsh
# Test render of frame 213 from the version 10 file: shot.sh NAME [PCT] [extra env as VAR=value ...]
# Writes render/${FRAMES_DIR:-v11_frames}/NAME/0213.png. HIDE="a,b" hides objects for this render only.
cd /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117
name=$1; pct=${2:-50}
mkdir -p render/${FRAMES_DIR:-v11_frames}/$name
FRAMES=${FRAMES:-213} OUT=render/${FRAMES_DIR:-v11_frames}/$name PCT=$pct /Applications/Blender.app/Contents/MacOS/Blender -b ${BLEND:-chest_reveal_v11_torches.blend} --python temple/tools/hide.py --python temple/tools/tweak.py --python temple/tools/other_badge.py --python temple/tools/dais_style.py --python temple/tools/torch_style.py --python temple/tools/border.py --python temple/tools/closeup.py --python tools/v8_render.py 2>&1 | grep -E "V8 F|Error|Traceback|OTHER BADGE" | sort | uniq -c | head -5
