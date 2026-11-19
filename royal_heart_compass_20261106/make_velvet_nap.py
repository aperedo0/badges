"""Intrinsic cloth pile color and tangent normals, with no photographed light."""
from pathlib import Path
import os,sys,json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
R=Path(__file__).resolve().parent;key=sys.argv[1];C=R/key/os.environ['BADGE_CANDIDATE'];g=json.loads((C/'groups.json').read_text());D=np.load(C/'geometry.npz');i=next(i for i,a in enumerate(g) if 'velvet cushion' in a['name']);N,M=g[i]['cloth_grid'];p=D[f'{i}_points'].reshape(M+1,N,3)
length_u=np.median(np.linalg.norm(np.roll(p,-1,axis=1)-p,axis=2).sum(1)[M//4:3*M//4]);length_v=np.median(np.linalg.norm(np.diff(p,axis=0),axis=2).sum(0));aspect=float(length_u/length_v);rng=np.random.default_rng(726)
size=1024;height=gaussian_filter(rng.normal(size=(size,size)),(.45*aspect,.45),mode='wrap');height/=height.std();dy,dx=np.gradient(height);dx*=size/length_u;dy*=size/length_v;std=np.sqrt(np.mean(dx*dx+dy*dy));dx*=.11/std;dy*=.11/std
normal=np.stack([-dx,dy,np.ones_like(dx)],axis=2);normal/=np.linalg.norm(normal,axis=2,keepdims=True);Image.fromarray(np.uint8(np.clip(normal*.5+.5,0,1)*255)).save(C/'textures/velvet_normal.png')
spec=json.loads((C/'materials.json').read_text());role={'ruby_crown':'red_velvet','amethyst_crown':'purple_velvet','emerald_crown':'green_velvet'}[key];base=np.array(spec[role]['color']);noise=gaussian_filter(rng.normal(size=(size,size)),.30,mode='wrap');noise/=noise.std();color=base*np.clip(1+.055*noise,.85,1.15)[...,None];rgb=np.where(color<=.0031308,color*12.92,1.055*np.maximum(color,0)**(1/2.4)-.055);Image.fromarray(np.uint8(np.clip(rgb,0,1)*255)).save(C/'textures/velvet_cap_intrinsic.png')
(C/'velvet_nap.json').write_text(json.dumps(dict(intrinsic_pile_normals=True,appearance_photo_used=False,normal_rms_slope=.11,color_deviation=.055,texture_size=size,physical_uv_aspect=aspect,shared_studio_unchanged=True),indent=2));print(key,'intrinsic nap normals saved')
