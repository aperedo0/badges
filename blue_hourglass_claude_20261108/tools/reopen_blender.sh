#!/bin/zsh
# Reopen the live Emerald Stag file with the connection on, if Blender is not already listening.
if lsof -nP -iTCP:9876 -sTCP:LISTEN >/dev/null 2>&1; then echo "Blender already open"; exit 0; fi
nohup /Applications/Blender.app/Contents/MacOS/Blender /Users/antonioperedo/Desktop/badges/emerald_stag_claude_20261108/live/emerald_stag_live.blend \
  --python /Users/antonioperedo/Desktop/badges/forge_tide_compass_20261103/start_blender.py > /tmp/blender_live.log 2>&1 &
for i in $(seq 1 30); do sleep 2; lsof -nP -iTCP:9876 -sTCP:LISTEN >/dev/null 2>&1 && { echo "reopened after $((i*2)) s"; exit 0; }; done
echo "Blender did not come back"; exit 1
