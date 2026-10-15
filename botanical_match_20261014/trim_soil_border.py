from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parent
p=R/'sprout/design.json';m=json.loads(p.read_text());d=m['features'][8]['blender_curve'];points=np.asarray(d['points']);limit=2.385
result=[]
for a,b in zip(points[:-1],points[1:]):
    inside_a=np.linalg.norm(a)<=limit;inside_b=np.linalg.norm(b)<=limit
    if inside_a:result.append(a)
    if inside_a!=inside_b:
        delta=b-a;roots=np.roots([delta@delta,2*(a@delta),a@a-limit**2]);t=next(float(x) for x in roots if np.isreal(x) and 0<=x<=1)
        result.append(a+t*delta)
if np.linalg.norm(points[-1])<=limit:result.append(points[-1])
d['points']=np.asarray(result).tolist();p.write_text(json.dumps(m,indent=2))
print('Soil border terminates inside the raised rim.')
