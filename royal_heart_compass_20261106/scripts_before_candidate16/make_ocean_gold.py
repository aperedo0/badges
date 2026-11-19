"""Subtle intrinsic aged gold color and roughness. No light is baked."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree
C=Path(__file__).resolve().parent/'ocean_navigator/candidate15';rng=np.random.default_rng(940);n=1024;yy,xx=np.mgrid[:n,:n]
fine=gaussian_filter(rng.normal(size=(n,n)),(.8,3.0),mode='wrap');fine/=fine.std();cloud=gaussian_filter(rng.normal(size=(n,n)),8,mode='wrap');cloud/=cloud.std();seed=np.c_[rng.uniform(-30,n+30,1900),rng.uniform(-30,n+30,1900)];d,_=cKDTree(seed).query(np.c_[xx.ravel(),yy.ravel()],k=2);edge=np.clip(1-(d[:,1]-d[:,0]).reshape(n,n)/1.2,0,1)**2
factor=np.clip(1+.035*fine+.045*cloud-.055*edge,.86,1.10);spec=json.loads((C/'materials.json').read_text());linear=np.array(spec['gold']['color'])*factor[...,None];rgb=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055);Image.fromarray(np.uint8(np.clip(rgb,0,1)*255)).save(C/'textures/gold_color.png');rough=np.clip(.255+.014*fine+.020*edge,.21,.31);Image.fromarray(np.uint8(rough*255)).save(C/'textures/gold_roughness.png');(C/'gold_finish.json').write_text(json.dumps(dict(intrinsic_hue_preserved=True,baked_lighting=False,normal_maps_used=False,metallic_value=1,texture_size=1024,neutral_color_factor_range=[.86,1.1],roughness_range=[.21,.31],purpose='Fine worn gold surface seen in the reference. Actual glints remain light reflections.'),indent=2));print('Intrinsic aged gold maps saved for Ocean Navigator only')
