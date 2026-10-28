"""Rebuild a chosen complete badge scene through the live Blender connection."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'water_match_20261014'))
from blender_live import command
name=sys.argv[1] if len(sys.argv)>1 else 'candidate03'
assert name in ['candidate01','candidate02','candidate03','candidate04']
(ROOT/name/'mobile').mkdir(parents=True,exist_ok=True)
code='TROPHY_CANDIDATE='+repr(name)+'\n'+(ROOT/('build_refined_live.py' if name=='candidate04' else 'build_live.py')).read_text()
print(json.dumps(command('execute_code',{'code':code})))
