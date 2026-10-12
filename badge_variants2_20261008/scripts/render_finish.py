"""Refresh proofs from the exported scene, opening a clean copy for each view."""
from pathlib import Path
import sys, runpy
import bpy

root = Path(__file__).resolve().parents[1]
kind = sys.argv[sys.argv.index('--') + 1]
base = root / kind
for rig, pose, name in [('stage', 0, 'front.png'), ('stage', 30, 'three_quarter.png'), ('harsh', 0, 'app_light_front.png')]:
    bpy.ops.wm.open_mainfile(filepath=str(base / 'scenes' / f'{kind}_badge_mobile.blend'))
    script = base / 'scripts' / 'render_proof.py'
    sys.argv = [str(script), '--', '--variant', 'master', '--rig', rig, '--pose', str(pose), '--samples', '128', '--out', str(base / 'proof' / name)]
    runpy.run_path(str(script), run_name='__main__')
bpy.ops.wm.open_mainfile(filepath=str(base / 'scenes' / f'{kind}_badge_mobile.blend'))
script = root / 'scripts' / 'stills.py'
sys.argv = [str(script), '--', kind]
runpy.run_path(str(script), run_name='__main__')
