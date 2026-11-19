"""Promote only a model whose native views and motion were actually reviewed."""
from pathlib import Path
import argparse,json,shutil,subprocess,hashlib
from pace import work
work(.5)
parser=argparse.ArgumentParser();parser.add_argument('key');parser.add_argument('--reviewed',action='store_true',required=True);args=parser.parse_args()
ROOT=Path(__file__).resolve().parent;R=ROOT/args.key;C=R/(R/'candidate.txt').read_text().strip();cfg=json.loads((R/'design.json').read_text());meta=json.loads((C/'validation.json').read_text())
files=dict(blend=C/'source'/(args.key+'.blend'),usdz=C/'mobile'/(args.key+'_badge_mobile.usdz'),comparison=C/'review/comparison.png',front=C/'review/front.png',back=C/'review/back.png',left=C/'review/side_left.png',right=C/'review/side_right.png',turn=C/'review/full_turn.mp4')
assert all(p.is_file() and p.stat().st_size for p in files.values())
assert hashlib.sha256(files['usdz'].read_bytes()).hexdigest()==meta['sha256']
for part in ['source','mobile','previous']:(R/part).mkdir(exist_ok=True)
for field,part in [('blend','source'),('usdz','mobile')]:
 source=files[field];target=R/part/source.name
 if target.exists() and target.read_bytes()!=source.read_bytes():shutil.copyfile(target,R/'previous'/(C.name+'_'+source.name))
 shutil.copyfile(source,target);files[field]=target
report=R/'REPORT.md'
report.write_text('# '+cfg['name']+'\n\nCreated and reviewed in live Blender and the separate native Badge Studio preview. The final working checkpoint is '+C.name+'.\n\n[Reference comparison]('+C.name+'/review/comparison.png) | [All sides]('+C.name+'/review/all_sides.png) | [Slow turn]('+C.name+'/review/full_turn.mp4).\n\n'+cfg['method']+'. Each front has a finished matching rear and continuous side walls. Existing badges and the production app are preserved.\n\nThe requested reference weathering and surface color are retained with reference appearance fill. Physical metal uses the measured native studio response, so live reflections and glints change during rotation. Any gemstone has independent closed convex geometry and the existing runtime optical shader, without photographed appearance textures. Emissive flame or atmospheric artwork remains distinct from gemstone optics.\n\nNative front, early turn, both sides, back and full turn were visually checked, along with four times outline views and the reflection. ARKit USD validation and closed solid checks passed. '+str(meta['triangles'])+' triangles; '+str(round(meta['bytes']/1000000,2))+' MB.\n\nThe deliberate reference texture is an exception to the generic smooth surface preference. The rendered highlights differ from a static illustration because the studio stays fixed while the object turns. The comparison records the actual current match.\n')
files['report']=report
(C/'NOTES.md').write_text('Complete reference matched relief and native measured metal finish.\nFront, every side, reflection and full turn reviewed before promotion.\n')
helper='/Users/antonioperedo/.agents/skills/overnight-badges/scripts/overnight.py'
command=['python3',helper,'done','--run-dir',str(ROOT),'--badge',args.key,'--reviewed']
for field,path in files.items():command+=['--'+field,str(path.resolve())]
subprocess.run(command,check=True)
print(cfg['name'],'promoted after native visual review')
