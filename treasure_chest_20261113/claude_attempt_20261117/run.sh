#!/bin/zsh
# usage: ./run.sh vNN [full]   regenerates maps, rebuilds my copy and renders a 2x closeup (and a full view)
set -e
cd "$(dirname "$0")"
V=$1
PY=/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13
B=/Applications/Blender.app/Contents/MacOS/Blender
$PY tools/make_wood.py maps & $PY tools/make_iron.py maps & wait
$B -b source_copy.blend --python tools/build_scene.py -- maps chest_claude.blend 2>&1 | grep -E "Error|Traceback|saved" || true
$B -b chest_claude.blend --python tools/render.py -- renders/${V}_close.png samples=${SAMPLES:-48} res=2800 border=0.30,0.871,0.143,0.443 2>&1 | grep -E "Error|Traceback" || true
if [[ "$2" == full ]]; then $B -b chest_claude.blend --python tools/render.py -- renders/${V}_full.png samples=64 res=1400 2>&1 | grep -E "Error|Traceback" || true; fi
sips -Z 1600 renders/${V}_close.png --out renders/${V}_close_view.png >/dev/null
