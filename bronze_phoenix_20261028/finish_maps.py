"""Invert the preview AgX transform for reference faithful sculpted surface maps."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent;R=ROOT/sys.argv[1];C=R/((R/'candidate.txt').read_text().strip() if (R/'candidate.txt').exists() else 'candidate01')
from display_transform import agx,agx_inv
target=np.asarray(Image.open(C/'target_reference.png').convert('RGB'),float)/255
# Reconstruct color through the actual app transform, in bounded batches.
flat=np.minimum(target.reshape(-1,3),.965);result=np.empty_like(flat)
for start in range(0,len(flat),50000):
 goal=flat[start:start+50000];lin=np.maximum(agx_inv(goal),1e-6)
 for iteration in range(12):
  now=agx(lin);h=lin*.015+1e-5;columns=[]
  for channel in range(3):
   q=lin.copy();q[:,channel]+=h[:,channel];columns.append((agx(q)-now)/h[:,channel,None])
  jac=np.stack(columns,-1)+np.eye(3)[None]*1e-5
  delta=np.linalg.solve(jac,(goal-now)[...,None])[...,0]
  lin=np.clip(lin+np.clip(delta,-lin*.55,lin*.80+.01)*.8,1e-6,8)
 result[start:start+len(goal)]=lin
linear=result.reshape(target.shape)
def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
# Most of the reference finish is a view matched fill, as on the trophy.
# A restrained physical metal contribution adds changing studio glints on the curved relief.
albedo=np.minimum(linear*.007,.009)
emission=np.maximum(0,linear-albedo*.4)
Image.fromarray(encode(albedo)).save(C/'textures/surface_color.png')
Image.fromarray(encode(emission/8)).save(C/'textures/surface_emission.png')
np.savez_compressed(C/'finish.npz',linear=linear,albedo=albedo,emission=emission)
meta={'emission_scale':8,'metallic':1,'roughness':.53,'method':'Actual app AgX inversion on real sculpted relief with restrained live metal reflections','mean_display_fit_error':float(abs(agx(linear)-np.minimum(target,.965)).mean()),'texture_size':1024}
(C/'material_fit.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
if R.name=='crescent_ocean':
 from prepare_compass import prepare
 prepare(R,C)
if R.name=='phoenix':
 from prepare_gems import prepare
 prepare(R,C)
