#!/bin/zsh
# Rebuilds the simple style copy (whole chest) from chest_claude.blend.
set -e
cd "$(dirname "$0")"
PY=/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13
B=/Applications/Blender.app/Contents/MacOS/Blender
$PY tools/make_simple_plank.py simple/maps plank01 L=5.0910 H=1.0238 seed=11 vis0=0.487 top=1 lip=0 tone=1.00
$PY tools/make_simple_plank.py simple/maps plank02 L=5.0910 H=0.5370 seed=23 top=1 lip=1 tone=1.05
$PY tools/make_simple_plank.py simple/maps plank03 L=5.0910 H=0.9875 seed=37 vis1=0.536 top=0 lip=1 tone=0.97
$PY tools/make_simple_iron.py simple/maps
$PY tools/make_simple_panels.py simple/maps
$B -b chest_claude.blend --python tools/build_simple.py -- simple/maps chest_simple.blend 2>&1 | grep -E "SIMPLE|Error|Traceback|line " || true
