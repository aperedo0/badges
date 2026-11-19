"""Intrinsic velvet fibers and traced chart ink. No gemstone appearance maps."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,distance_transform_edt,map_coordinates
ROOT=Path(__file__).resolve().parent
def srgb(a):return np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)
for key in ['amethyst_crown','ruby_crown','emerald_crown']:
 C=ROOT/key/'candidate06';m=json.loads((C/'materials.json').read_text());role=next(k for k in m if k.endswith('_velvet') and k.startswith({'amethyst_crown':'purple','ruby_crown':'red','emerald_crown':'green'}[key]))
 rng=np.random.default_rng(366);noise=gaussian_filter(rng.normal(size=(1024,1024)),.45);noise/=noise.std();fibers=np.clip(1+noise*.18,.6,1.4)
 rgb=srgb(np.clip(np.array(m[role]['color'])*fibers[...,None],0,1));Image.fromarray((rgb*255).astype('uint8')).save(C/'textures/velvet_color.png')
ref=np.asarray(Image.open(ROOT/'ocean_navigator/reference.png').convert('RGB'),float)/255
h,w=ref.shape[:2];yy,xx=np.mgrid[:h,:w];dx=xx-627;dy=yy-570;r=np.hypot(dx,dy)
gold=(ref[...,0]>ref[...,2]*1.45)&(ref[...,1]>ref[...,2]*1.18)&(ref[...,0]>.23)
# Exclude all eight sculpted arms, then retain only the fine map line ink.
theta=np.arctan2(dy,dx);phase=(theta+np.pi/8)%(np.pi/4)-np.pi/8
arm=(np.abs(phase)<(.065+.22*np.exp(-r/170)))&(r<np.where(np.cos(4*theta)>.0,365,250))
mask=gold&(r<345)&(r>105)&~arm&(yy<850)
mask&=distance_transform_edt(mask)<1.2
mask=gaussian_filter(mask.astype(float),.35)
C=ROOT/'ocean_navigator/candidate06';D=np.load(C/'geometry.npz');g=json.loads((C/'groups.json').read_text());i=next(i for i,a in enumerate(g) if a['mat']=='navy');p=D[str(i)+'_points'];rad=p[:,0].max()
# UV coordinates are derived from the actual normalized geometry.
v,u=np.mgrid[:1024,:1024];worldx=u/1023*6.5-3.25;worldy=(1-v/1023)*6.5-2.455;worldcy=(p[:,1].max()+p[:,1].min())/2
sx=627+worldx/rad*440;sy=570-(worldy-worldcy)/rad*440
ink=map_coordinates(mask,[sy,sx],order=1,mode='constant')*.72
navy=np.array([.0015,.005,.013]);goldink=np.array([.22,.102,.024]);color=navy[None,None,:]*(1-ink[...,None])+goldink[None,None,:]*ink[...,None]
Image.fromarray(np.uint8(np.clip(srgb(color),0,1)*255)).save(C/'textures/chart_color.png')
print('Intrinsic material maps saved. Gemstone materials remain untextured.')

for key in ['ruby_heart','amethyst_crown','ruby_crown','emerald_crown','ocean_navigator']:
 C=ROOT/key/'candidate06';rng=np.random.default_rng(642)
 brush=gaussian_filter(rng.normal(size=(1024,1024)),(.40,12));brush/=brush.std()
 rough=np.clip(.245+brush*.009,.213,.277)
 Image.fromarray(np.uint8(rough*255)).save(C/'textures/gold_roughness.png')
