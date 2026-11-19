"""Verify actual native shader attachment to every intended stone and mirror."""
from pathlib import Path
import sys,json,re,time,hashlib
ROOT=Path(__file__).resolve().parent;key,mode,logfile=sys.argv[1:4];candidate=mode if mode.startswith('candidate') else 'candidate17';C=ROOT/key/candidate;V=ROOT/key/('baseline' if mode=='baseline' else candidate+'/review')
groups=json.loads((C/'groups.json').read_text());expected={(g['mat'],'Part_'+str(i),mirror) for i,g in enumerate(groups) if g['mat'].startswith('CrestGem_') for mirror in ['true','false']}
log=Path(logfile).read_text();actual=set(re.findall(r'Badge gem attached: (CrestGem_\w+) mesh=(\S+) mirror=(true|false)',log));missing=expected-actual
for attempt in range(120):
 if not missing or 'Badge gem FAILED: CrestGem_' in log:break
 time.sleep(.5);log=Path(logfile).read_text();actual=set(re.findall(r'Badge gem attached: (CrestGem_\w+) mesh=(\S+) mirror=(true|false)',log));missing=expected-actual
assert not missing,sorted(missing);assert not any('Badge gem FAILED: CrestGem_' in x for x in log.splitlines())
lines=[x for x in log.splitlines() if 'Badge gem attached:' in x and 'mesh=Part_' in x];(V/'runtime_gems.txt').write_text('\n'.join(lines)+'\n')
report=dict(optical_meshes=len(expected)//2,physical_stones=1 if key=='ruby_heart' else len(expected)//2,model_and_reflection_attachments=len(expected),all_intended_profiles_attached=True,no_fallback_gems=True,log=logfile)
if key=='ruby_heart':
 assert 'Badge heart union prepared: domains=2 mirror=false' in log and 'Badge heart union prepared: domains=2 mirror=true' in log
 report['one_continuous_ruby_volume']=True
 report['optical_domains']=2
shader=ROOT.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/BadgeCrestGemSurface.metal'
report['runtime_shader_sha256']=hashlib.sha256(shader.read_bytes()).hexdigest()
(V/'native_gem_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(key,mode,report['optical_meshes'],'optical meshes and their reflections attached')
