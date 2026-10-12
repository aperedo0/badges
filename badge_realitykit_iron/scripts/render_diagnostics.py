"""Supplement standard proofs with a three-quarter view and raw/realtime checks."""
import subprocess
from pathlib import Path
r=Path(__file__).resolve().parents[1];blender='/Applications/Blender.app/Contents/MacOS/Blender'
for key,pose,extras in [('45','45',['--samples','256']),('0_no_denoise','0',['--samples','512','--no-denoise'])]:
    log=r/f'logs/render_iron_harsh_{key}.log';out=r/f'proof/renders/iron_harsh_{key}.png'
    cmd=[blender,'--background','--factory-startup',str(r/'scenes/iron_medallion_master.blend'),'--python',str(r/'scripts/render_proof.py'),'--','--variant',str(r/'mobile/iron_badge_mobile.usdz'),'--rig','harsh','--pose',pose,'--out',str(out)]+extras
    with log.open('w') as stream:p=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT)
    assert p.returncode==0 and 'Traceback' not in log.read_text() and out.is_file(),key
    print('FINISHED diagnostic',key,flush=True)
