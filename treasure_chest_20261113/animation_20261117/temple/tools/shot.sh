#!/bin/zsh
# Test render of frame 213 from the version 10 file: shot.sh NAME [PCT] [extra env as VAR=value ...]
# Writes render/v10_frames/NAME/0213.png. HIDE="a,b" hides objects for this render only.
cd /Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117
name=$1; pct=${2:-50}
mkdir -p render/v10_frames/$name
FRAMES=${FRAMES:-213} OUT=render/v10_frames/$name PCT=$pct /Applications/Blender.app/Contents/MacOS/Blender -b chest_reveal_v10_temple_polish.blend --python temple/tools/hide.py --python temple/tools/tweak.py --python tools/v8_render.py 2>&1 | grep -E "V8 F|Error|Traceback" | sort | uniq -c | head -5
