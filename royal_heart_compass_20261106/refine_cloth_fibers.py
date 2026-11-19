import os
"""Intrinsic fiber colors with scale measured on the actual cloth surface."""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
R=Path(__file__).resolve().parent;key=sys.argv[1] if len(sys.argv)>1 else 'amethyst_crown';C=R/key/os.environ.get('BADGE_CANDIDATE','candidate21');D=np.load(C/'geometry.npz');G=json.loads((C/'groups.json').read_text());i=next(i for i,g in enumerate(G) if 'velvet cushion' in g['name']);N,M=G[i]['cloth_grid'];p=D[f'{i}_points'].reshape(M+1,N,3).astype(float)
circumference=np.linalg.norm(np.roll(p,-1,axis=1)-p,axis=2).sum(1);meridians=np.linalg.norm(np.diff(p,axis=0),axis=2).sum(0);ratio=float(np.median(circumference[M//4:3*M//4])/np.median(meridians));spec=json.loads((C/'materials.json').read_text());role={'amethyst_crown':'purple_velvet','ruby_crown':'red_velvet','emerald_crown':'green_velvet'}[key];base=np.array(spec[role]['color']);rng=np.random.default_rng(366)
def rgb(linear):return np.where(linear<=.0031308,linear*12.92,1.055*np.maximum(linear,0)**(1/2.4)-.055)
def texture(aspect,nap_weight):
 fine=gaussian_filter(rng.normal(size=(1024,1024)),(.5*aspect,.5),mode='wrap');fine/=fine.std();nap=gaussian_filter(rng.normal(size=(1024,1024)),(1.2*aspect,1.2),mode='wrap');nap/=nap.std();v=np.clip(1+.10*fine+nap_weight*nap,.65,1.35);return np.uint8(np.clip(rgb(base*v[...,None]),0,1)*255)
Image.fromarray(texture(ratio,.15)).save(C/'textures/velvet_cap_intrinsic.png');Image.fromarray(texture(1,.08)).save(C/'textures/velvet_color.png');report=dict(midcap_circumference=float(np.median(circumference[M//4:3*M//4])),median_meridian_length=float(np.median(meridians)),intrinsic_v_to_u_filter_ratio=ratio,cap_and_band_have_independent_intrinsic_maps=True,geometric_ao_uv_unchanged=True,appearance_photo_used=False);(C/'fiber_scale.json').write_text(json.dumps(report,indent=2));print(report)
