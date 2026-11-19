"""Correct the asymmetric rear stone, then continue the native normal diagnosis."""
from pathlib import Path
import json,copy,sys,time
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from designs import path,shape
R=Path(__file__).resolve().parent;B=R/'campfire_night';C=B/'candidate14';assert not C.exists();C.mkdir()
s=json.loads((R/'schedule.json').read_text());assert s['status']=='active' and s['phase']=='work' and time.time()+300<s['work_until_epoch']
spec=json.loads((B/'PIECES.json').read_text())
rock=next(p for p in spec['pieces'] if p['name']=='stone_back_right')
rock['outline']=shape(path('M 924 909 C 904 910 891 930 895 954 C 897 974 909 991 930 1002 L 961 972 C 968 949 948 914 924 909 Z'))
# The two rear stones sit behind the crossed logs in the reference.
rear=[p for p in spec['pieces'] if p['name'] in ['stone_back_left','stone_back_right']]
spec['pieces']=[p for p in spec['pieces'] if p not in rear]
i=next(i for i,p in enumerate(spec['pieces']) if p['name']=='left_crossed_log')
spec['pieces'][i:i]=rear
if 'validate_order' in spec:spec['validate_order']=[p['name'] for p in spec['pieces']]
(C/'PIECES.json').write_text(json.dumps(spec,indent=1)+'\n')
config=json.loads((B/'candidate12/enamel_config.json').read_text());(C/'enamel_config.json').write_text(json.dumps(config,indent=1)+'\n')
print('Saved corrected rear stone and its layering')
