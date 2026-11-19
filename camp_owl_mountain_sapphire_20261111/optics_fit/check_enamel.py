from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
import forward as f
R=Path(__file__).resolve().parent.parent;C=R/'campfire_night/candidate10';D=np.load(C/'parts.npz');M=json.loads((C/'parts.json').read_text());native=np.asarray(Image.open(C/'app/front.png').convert('RGB'))/255;ref=np.asarray(Image.open(R/'campfire_night/reference.png').convert('RGB'))/255;tex=np.asarray(Image.open(C/'textures/enamel_emission.png').convert('RGB'))/255
lin=lambda a:np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
report={}
for p in M['parts']:
 if 'Enamel' not in p['materials']:continue
 name=p['name'];mask=D[name+'_m'][:p['front']]==p['materials'].index('Enamel');P=D[name+'_v'][:p['front']][mask].mean(1);uv=D[name+'_uv'][:p['front']][mask].mean(1)
 if not len(P):continue
 eye=np.array([0,1.8,23.]);axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis);delta=P-eye;depth=delta@axis;sx=np.rint(603+1762.5*delta[:,0]/depth).astype(int);sy=np.rint(633.3-1762.5*(delta@up)/depth).astype(int)
 tx=np.clip(np.rint(uv[:,0]*(tex.shape[1]-1)).astype(int),0,tex.shape[1]-1);ty=np.clip(np.rint((1-uv[:,1])*(tex.shape[0]-1)).astype(int),0,tex.shape[0]-1)
 rx=np.clip(np.rint(uv[:,0]*1254).astype(int),0,1253);ry=np.clip(np.rint((1-uv[:,1])*1254).astype(int),0,1253)
 predicted=f.agx(lin(tex[ty,tx])*8);actual=native[sy,sx];target=ref[ry,rx]
 report[name]=dict(predicted=np.median(predicted,0).tolist(),actual=np.median(actual,0).tolist(),reference=np.median(target,0).tolist(),error=float(np.median(abs(predicted-actual))))
print(json.dumps(report,indent=2))
(R/'optics_fit/enamel_diagnostic.json').write_text(json.dumps(report,indent=2)+'\n')
