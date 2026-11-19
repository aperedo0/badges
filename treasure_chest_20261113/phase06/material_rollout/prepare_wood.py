from pathlib import Path
import numpy as np,json
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter,zoom
D=Path(__file__).resolve().parent;S=D.parents[1]/'phase04/wood_lab/timber_refinement/BC_final_polish';O=D/'wood_atlas';O.mkdir(exist_ok=True)
if (O/'normal.png').exists():raise SystemExit('Using cached coordinated atlas')
H=np.load(S/'master_height.npz')['height'].astype(np.float32);src={r:np.asarray(Image.open(S/(r+'.png')).convert('RGB'),np.float32)[32:-32,32:-32]/255 for r in ['albedo','roughness','normal']};h,w=H.shape
assert src['albedo'].shape[:2]==H.shape
V,U=np.meshgrid(np.linspace(0,1,h,dtype=np.float32),np.linspace(0,1,w,dtype=np.float32),indexing='ij')
def sample(a,u,v):
 co=[np.clip(v,0,1)*(h-1),np.clip(u,0,1)*(w-1)]
 return map_coordinates(a,co,order=1,mode='nearest') if a.ndim==2 else np.stack([map_coordinates(a[:,:,c],co,order=1,mode='nearest') for c in range(a.shape[2])],2)
rho=np.hypot((U-.243)/.145,(V-.37)/.36);mask=np.clip((1.18-rho)/.35,0,1);mask=mask*mask*(3-2*mask)
donorU=np.clip(U+.40,0,1);donorV=np.clip(.12+.75*V,0,1);clean={}
for key,a in dict(height=H,**src).items():
 donor=sample(a,donorU,donorV);alpha=mask if a.ndim==2 else mask[:,:,None];clean[key]=a*(1-alpha)+donor*alpha
W,T=2048,1152;physical=(5.1,2.755);vv,uu=np.meshgrid(np.linspace(0,physical[1],T,dtype=np.float32),np.linspace(0,1,W,dtype=np.float32),indexing='ij');allmaps={k:[] for k in ['albedo','roughness','normal']};heights=[]
for seed in range(4):
 rng=np.random.default_rng(17110+seed);A=dict(height=H,**src) if seed==3 else clean
 warpU=zoom(rng.normal(0,.018,(12,22)).astype(np.float32),(T/12,W/22),order=3)[:T,:W];warpV=zoom(rng.normal(0,.022,(12,22)).astype(np.float32),(T/12,W/22),order=3)[:T,:W];slope=.94+seed*.009;u=np.clip(.025+uu*slope+warpU,0,1)
 # Two coordinated donor courses retain physical grain scale over the full body height.
 v1=np.clip(vv/1.3775+warpV,0,1);v2=np.clip((vv-1.3775)/1.3775+.04+warpV,0,1);blend=np.clip((vv-1.27)/.22,0,1);blend=blend*blend*(3-2*blend)
 fields={}
 for key,a in A.items():
  b=blend if a.ndim==2 else blend[:,:,None];fields[key]=sample(a,u,v1)*(1-b)+sample(a,np.clip(u+.055,0,1),v2)*b
 height=fields['height'];gy,gx=np.gradient(height,physical[1]/(T-1),physical[0]/(W-1));old=fields['normal']*2-1;den=np.maximum(old[:,:,2],.25);microX=old[:,:,0]/den;microY=old[:,:,1]/den;microX-=gaussian_filter(microX,(2,4));microY-=gaussian_filter(microY,(2,4));N=np.stack([-gx+.30*microX,gy+.30*microY,np.ones_like(gx)],2);N/=np.maximum(np.linalg.norm(N,axis=2,keepdims=True),1e-8)
 allmaps['normal'].append(np.uint8(np.clip(N*.5+.5,0,1)*255+.5));gain=np.array([[1.0,.995,.99],[.99,1,1.005],[1.015,1.01,.99],[1,1,1]][seed]);allmaps['albedo'].append(np.uint8(np.clip(fields['albedo']*gain,0,1)*255+.5));allmaps['roughness'].append(np.uint8(np.clip(fields['roughness'],0,1)*255+.5));heights.append(height)
for key,tiles in allmaps.items():Image.fromarray(np.vstack(tiles)).save(O/(key+'.png'))
np.savez_compressed(O/'height_fields.npz',height=np.stack(heights));(O/'recipe.json').write_text(json.dumps(dict(source=str(S),tile_size=[W,T],tiles=4,physical_tile_size=physical,seed_start=17110,knot_free_tiles=[0,1,2],rare_knot_tile=3,source_material_unchanged=True,normal='Full authored height derivatives plus restrained high frequency residual from the existing complementary normal',geometry='New mapped panels use full tangent relief; approved sculpted test plank is retained exactly'),indent=2));print('Prepared four coordinated shared wood variants')
