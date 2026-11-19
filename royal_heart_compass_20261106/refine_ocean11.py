"""Replace segmented crest relief with closed, smoothly sculpted waves."""
from pathlib import Path
import json,shutil
import numpy as np
import build_geometry as shape
R=Path(__file__).resolve().parent;B=R/'ocean_navigator/candidate09';C=R/'ocean_navigator/candidate11'
assert not (C/'geometry.npz').exists()
for name in ['source','mobile','review','textures']:(C/name).mkdir(parents=True,exist_ok=True)
D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());spec=json.loads((B/'materials.json').read_text())
i=next(i for i,g in enumerate(G) if g['name']=='Double sided navy nautical chart body');body=D[f'{i}_points'];cy=(body[:,1].min()+body[:,1].max())/2;scale=np.ptp(body[:,0])/(2*2.94*.934);unit=2.94/480*scale
parts=[]
for i,g in enumerate(G):
 if g['name']=='Measured flowing gold ocean wave crests':continue
 p=D[f'{i}_points'].copy();t=D[f'{i}_triangles'].copy()
 if g['name'].startswith('Real raised compass '):
  face=np.sign(p[:,2].mean());p[4,2]=face*(abs(p[:4,2].mean())+.24*scale)
 parts.append((dict(g),p,t))
def chain(segments,N=32):
 return np.vstack([shape.bez(segment,N) if i==0 else shape.bez(segment,N)[1:] for i,segment in enumerate(segments)])
def wave(a,b,height=.10):
 a=chain(a);b=chain(b);assert a.shape==b.shape
 N=len(a);M=12;p=[]
 for back in [False,True]:
  for j,s in enumerate(np.linspace(0,1,N)):
   for u in np.linspace(0,1,M):
    xy=a[j]*(1-u)+b[j]*u;dome=np.sin(np.pi*u)**.72*np.sin(np.pi*s)**.4
    p.append([*xy,(-.035 if back else .025+height*dome)])
 p=np.array(p);K=N*M;t=[]
 for j in range(N-1):
  for k in range(M-1):
   aa=j*M+k;bb=aa+1;cc=aa+M+1;dd=aa+M;t.extend([[aa,bb,cc],[aa,cc,dd],[aa+K,cc+K,bb+K],[aa+K,dd+K,cc+K]])
 boundary=list(range(M))+[j*M+M-1 for j in range(1,N)]+list(range(K-2,K-M-1,-1))+[j*M for j in range(N-2,0,-1)]
 for aa,bb in zip(boundary,boundary[1:]+boundary[:1]):t.extend([[aa,bb+K,bb],[aa,aa+K,bb+K]])
 unique,inv=np.unique(np.round(p,8),axis=0,return_inverse=True);t=inv[np.array(t)];valid=(t[:,0]!=t[:,1])&(t[:,0]!=t[:,2])&(t[:,1]!=t[:,2]);return unique,t[valid]
waves=[
 ('outer returning curl',
  [[[354,850],[260,865],[246,752],[304,766]],[[304,766],[328,771],[335,796],[320,808]]],
  [[[354,850],[280,854],[270,788],[299,787]],[[299,787],[313,783],[328,792],[320,808]]],.12),
 ('upper long crest',
  [[[250,835],[306,895],[363,824],[431,823]],[[431,823],[481,817],[519,850],[515,878]]],
  [[[250,835],[312,912],[367,851],[431,847]],[[431,847],[467,836],[494,854],[515,878]]],.11),
 ('inner rolling curl',
  [[[616,908],[578,889],[545,895],[514,905]],[[514,905],[485,917],[451,915],[449,891]],[[449,891],[443,857],[480,845],[495,864]],[[495,864],[508,870],[509,880],[509,886]]],
  [[[616,908],[578,903],[552,912],[522,921]],[[522,921],[482,934],[430,920],[433,887]],[[433,887],[434,861],[460,848],[489,857]],[[489,857],[501,862],[507,878],[509,886]]],.11),
 ('lower flowing crest',
  [[[607,948],[572,929],[547,943],[517,957]],[[517,957],[483,980],[453,981],[407,970]]],
  [[[607,948],[572,941],[550,958],[521,968]],[[521,968],[481,993],[451,990],[407,970]]],.075),
 ('bottom returning crest',
  [[[597,978],[565,952],[541,970],[519,987]]],
  [[[597,978],[565,964],[545,978],[519,987]]],.065),
 ('small outer crest',
  [[[468,943],[427,934],[414,956],[376,953]]],
  [[[468,943],[434,948],[415,964],[376,953]]],.055),
]
for face in [1,-1]:
 for side in [-1,1]:
  for name,a,b,height in waves:
   p,t=wave(a,b,height);p[:,0]=(p[:,0]-627)*unit*side;p[:,1]=cy+(570-p[:,1])*unit;p[:,2]=face*(.255*scale+p[:,2]*scale)
   if np.einsum('ij,ij->i',p[t[:,0]],np.cross(p[t[:,1]],p[t[:,2]])).sum()<0:t=t[:,::-1]
   parts.append((dict(name=f'Smooth measured ocean {name} {face} {side}',mat='gold',smooth=True),p.astype(np.float32),t))
out={};groups=[]
for i,(g,p,t) in enumerate(parts):out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t;groups.append(g)
points=np.vstack([p for _,p,_ in parts]);assert points[:,1].min()>=-2.45501 and points[:,1].max()<=3.01501 and abs(points[:,0]).max()<=3.35
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(groups,indent=2));(C/'materials.json').write_text(json.dumps(spec,indent=2))
for p in (B/'textures').glob('*.png'):shutil.copy2(p,C/'textures'/p.name)
(C/'wave_sculpture.json').write_text(json.dumps(dict(source='candidate09',segmented_gold_relief_replaced=True,closed_smooth_wave_bodies=24,measured_reference_curves=True,chart_rope_gems_and_frame_preserved=True,real_compass_ridge_depth=.24*scale,no_appearance_photograph_on_gold=True),indent=2));print('Ocean11 complete geometry prepared',len(groups),'parts',sum(len(t) for _,_,t in parts),'triangles')
