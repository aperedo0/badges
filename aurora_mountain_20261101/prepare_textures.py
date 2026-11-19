"""Map the atmospheric and rock artwork through the existing preview view transform."""
from pathlib import Path
import sys,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;C=R/(R/'candidate.txt').read_text().strip()
sys.path.insert(0,str(R.parent/'stair_ruby_20261029'))
from display_transform import agx,agx_inv
def encode(x):return np.uint8(np.clip(np.where(x<=.0031308,x*12.92,1.055*np.maximum(x,0)**(1/2.4)-.055)*255+.5,0,255))
for role in ['sky','rock']:
 target=np.asarray(Image.open(C/'textures'/(role+'_target.png')).convert('RGB'),float)/255
 flat=np.minimum(target.reshape(-1,3),.97);result=np.empty_like(flat)
 for start in range(0,len(flat),50000):
  goal=flat[start:start+50000];lin=np.maximum(agx_inv(goal),1e-6)
  for iteration in range(10):
   now=agx(lin);h=lin*.015+1e-5;columns=[]
   for channel in range(3):
    q=lin.copy();q[:,channel]+=h[:,channel];columns.append((agx(q)-now)/h[:,channel,None])
   jac=np.stack(columns,-1)+np.eye(3)[None]*1e-5;delta=np.linalg.solve(jac,(goal-now)[...,None])[...,0]
   lin=np.clip(lin+np.clip(delta,-lin*.55,lin*.8+.01)*.8,1e-6,8)
  result[start:start+len(goal)]=lin
 linear=result.reshape(target.shape)
 # These maps represent the illustrated aurora and rock finish, never metal or gems.
 color=np.minimum(linear*.035,.012);emission=np.maximum(0,linear-color*.4)
 Image.fromarray(encode(color)).save(C/'textures'/(role+'_color.png'))
 Image.fromarray(encode(emission/8)).save(C/'textures'/(role+'_emission.png'))
 print(role,'prepared',flush=True)
