import sys,subprocess,shutil
from pathlib import Path
r=Path(sys.argv[1]).resolve();root=Path(__file__).resolve().parents[1];blender='/Applications/Blender.app/Contents/MacOS/Blender'
for rig in ['stage','harsh']:
 log=r/f'logs/render_iron_{rig}_0.log';out=r/f'proof/renders/iron_{rig}_0.png'
 if out.exists():continue
 cmd=[blender,'--background','--factory-startup',str(r/'scenes/iron_medallion_master.blend'),'--python',str(r/'scripts/render_proof.py'),'--','--variant',str(r/'mobile/iron_badge_mobile.usdz'),'--rig',rig,'--pose','0','--samples','192','--out',str(out)]
 with log.open('w') as stream:p=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT)
 assert p.returncode==0 and out.is_file() and 'Traceback' not in log.read_text(),(rig,p.returncode,out.exists(),log.read_text()[-1400:])
 print('RENDERED',rig,flush=True)
cmd=[blender,'--background','--factory-startup',str(r/'scenes/iron_medallion_master.blend'),'--python',str(root/'scripts/render_plane_mask.py'),'--',str(r)]
with (r/'logs/render_plane_ids.log').open('w') as stream:p=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT)
assert p.returncode==0 and 'Traceback' not in (r/'logs/render_plane_ids.log').read_text()
python=Path('/usr/local/bin/python3')
cmd=[str(python),str(root/'scripts/measure_smoothness.py'),'--emblem',str(r/'proof/emblem_iron.json'),'--pose','0','--out',str(r/'proof/smoothness_pose00.json')]+[f'iron_{rig}={r}/proof/renders/iron_{rig}_0.png' for rig in ['stage','harsh']]
with (r/'proof/smoothness_pose00.txt').open('w') as stream:p=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT)
assert p.returncode==0
p=subprocess.run([str(python),str(root/'scripts/iteration_metrics.py'),str(r)]);assert p.returncode==0
print('PASS rendered mask and measured Blender criteria',flush=True)
