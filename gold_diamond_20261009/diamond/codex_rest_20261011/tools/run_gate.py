"""Run the requested real gate on an archived candidate, then restore our edits."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('/Users/antonioperedo/Desktop/screen_time')
candidate = Path(sys.argv[1])
proof = ROOT / 'gate'
proof.mkdir(exist_ok=True)
metadata = {'candidate_directory': str(candidate), 'started_unix': time.time(), 'candidate_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in candidate.iterdir() if p.name in ['BadgeHeroCard.swift', 'BadgeGemSurface.metal', 'diamond_badge_mobile.usdz']}}
(proof / 'candidate.json').write_text(json.dumps(metadata, indent=2))
subprocess.run(['python3', str(ROOT / 'tools/guard.py'), 'stage', str(candidate)], check=True)
try:
    with (proof / 'gate_output.log').open('w') as log:
        result = subprocess.run([str(REPO / 'tools/sim/gate')], cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
finally:
    subprocess.run(['python3', str(ROOT / 'tools/guard.py'), 'restore'], check=True)
print((proof / 'gate_output.log').read_text())
sys.exit(result.returncode)
