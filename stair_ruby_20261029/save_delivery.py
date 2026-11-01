"""Preserve the private renderer changes and prepare traceable badge deliveries."""
from pathlib import Path
import json,difflib,shutil,hashlib,subprocess
ROOT=Path(__file__).resolve().parent;APP=ROOT.parent/'emerald_trophy_20261025/preview';D=APP/'ScreenTime/Sources/App/Features/Badges';out=ROOT/'runtime';out.mkdir(exist_ok=True)
files=['ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift','ScreenTime/Sources/App/Features/Badges/BadgeCrestGemSurface.metal','ScreenTime.xcodeproj/project.pbxproj']
patch=[]
for rel in files:
 path=APP/rel;before=ROOT/'preview_before'/path.name
 patch.extend(difflib.unified_diff(before.read_text().splitlines(True) if before.exists() else [],path.read_text().splitlines(True),fromfile='a/'+rel if before.exists() else '/dev/null',tofile='b/'+rel))
 shutil.copyfile(path,out/path.name)
shutil.copyfile(D/'GemFacetPlanes.swift',out/'GemFacetPlanes.swift');(ROOT/'runtime_integration.patch').write_text(''.join(patch))
assert hashlib.sha256((D/'BadgeGemSurface.metal').read_bytes()).hexdigest()==(ROOT/'diamond_shader_baseline.sha256').read_text().strip()
items=json.loads((ROOT/'badges.json').read_text());logs=Path('/Users/antonioperedo/Library/Developer/XcodeBuildMCP/workspaces/badges-aa906adb7ece/logs')
for key,item in items.items():
 R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip();specs=json.loads((C/'dynamic_gems.json').read_text());profile=specs[0]['role'];wanted=len(specs);evidence=None
 for log in sorted(logs.glob('com.antonioperedo.badgestudio.preview_*.log'),key=lambda p:p.stat().st_mtime,reverse=True):
  text=log.read_text(errors='replace');lines=[line for line in text.splitlines() if 'Badge gem attached:' in line and profile in line]
  front=set(line.split('mesh=')[1].split()[0] for line in lines if 'mirror=false' in line);rear=set(line.split('mesh=')[1].split()[0] for line in lines if 'mirror=true' in line)
  if len(front)==wanted and len(rear)==wanted and not any('Badge gem FAILED:' in line and profile in line for line in text.splitlines()):evidence=(log,lines);break
 assert evidence,key
 (C/'runtime_attachment.txt').write_text('Source: '+str(evidence[0])+'\n'+'\n'.join(evidence[1])+'\n')
 (C/'notes.txt').write_text(('Replace fixed Frostwing gemstone imagery with actual runtime optical cuts.\nKeep the approved metal body and inspect live reflections through the full turn.\n' if key=='frostwing_dynamic' else 'Sculpt the supplied reference with a matching back and independent closed gemstone cuts.\nFit the non gemstone finish to the fixed app light and inspect live gemstone optics through the full turn.\n'))
 subprocess.run(['/tmp/crest_image_env/bin/python',str(ROOT/'deliver.py'),key],check=True)
print('Saved private renderer patch, attachment evidence and final deliveries')
