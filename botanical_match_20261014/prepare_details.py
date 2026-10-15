from pathlib import Path
import json, numpy as np
R=Path(__file__).resolve().parent
def bezier(start, sections, samples=32):
    out=[np.array(start,float)]
    for a,b,c in sections:
        p=out[-1]
        for t in np.linspace(0,1,samples+1)[1:]:out.append((1-t)**3*p+3*(1-t)**2*t*np.array(a)+3*(1-t)*t*t*np.array(b)+t**3*np.array(c))
    return np.array(out)
b=R/'sunrise';m=json.loads((b/'design.json').read_text());cx,cy,r=m['circle']
# Keep the exact continuous S outline. The prior builder projected its lower
# points radially onto a smaller circle, distorting the road's lower bend.
road=bezier((560,672),[
    ((646,669),(751,688),(725,727)),((701,762),(554,787),(551,829)),
    ((545,871),(732,925),(885,947)),((800,1021),(622,1056),(497,989)),
    ((435,956),(400,917),(414,870)),((430,824),(531,784),(598,752)),
    ((641,731),(680,706),(646,695)),((621,686),(583,681),(560,672))])
m['features'][9]['blender_plate']={'points':((road-[cx,cy])*[3.015/r,-3.015/r]).tolist(),'radius':.018,'z':.13,'extrude':.065}
(b/'design.json').write_text(json.dumps(m,indent=2))
b=R/'sprout';m=json.loads((b/'design.json').read_text())
for i in [1,3]:
    d=m['features'][i]['blender_curve'];d['radius']=.055;d.pop('conform',None);d['z']=.29
for i in [5,6]:m['features'][i]['blender_curve']['radius']=.035
m['features'][4]['blender_plate'].update({'radius':.028,'z':.225,'extrude':.035})
m['features'][8]['blender_curve'].update({'radius':.045,'z':.28})
(b/'design.json').write_text(json.dumps(m,indent=2))
print('Continuous road outline and raised conforming leaf borders prepared.')
