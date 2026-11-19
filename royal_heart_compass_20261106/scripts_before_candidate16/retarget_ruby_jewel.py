"""Rebuild the central ruby setting from the preserved ninth geometry."""
from pathlib import Path
import json,numpy as np
from sculpted_gold import frame
R=Path(__file__).resolve().parent;B=R/'ruby_crown/candidate09';C=R/'ruby_crown/candidate15';D=np.load(B/'geometry.npz');G=json.loads((B/'groups.json').read_text());materials=json.loads((B/'materials.json').read_text());materials['CrestGem_CrownRuby']=dict(materials['CrestGem_Ruby']);parts=[];info=[]
for face in [1,-1]:
 i=next(i for i,g in enumerate(G) if g['name']=='Large central ruby jewel independent gemstone' and D[f'{i}_points'][:,2].mean()*face>0)
 p=D[f'{i}_points'].astype(float).copy();old=p[:4].mean(0);new=old.copy();new[1]+=.278;p[:,0]=(p[:,0]-old[0])*1.2+new[0];p[:,1]=(p[:,1]-old[1])*.82+new[1];coef=np.linalg.lstsq(np.c_[p[:4,:2],np.ones(4)],p[:4,2],rcond=None)[0]
 info.append(dict(face=face,gem_index=i,old=old,new=new,coef=coef,points=p))
for i,g in enumerate(G):
 p=D[f'{i}_points'].astype(float).copy();t=D[f'{i}_triangles'].copy();g=dict(g);name=g['name']
 if name in ['Large central ruby jewel closed gold prong frame','Broad beveled central ruby jewel gold mount','Large central solid gold pave surround']:continue
 if name=='Large central ruby jewel independent gemstone':
  row=next(a for a in info if a['gem_index']==i);p=row['points']
 elif name in ['Pave gold bead seat','Central border brilliant']:
  face=1 if p[:,2].mean()>0 else -1;row=next(a for a in info if a['face']==face);oldc=(p.min(0)+p.max(0))/2;newc=oldc.copy();newc[1]=row['new'][1]+(oldc[1]-row['old'][1])*.695;newc[2]=np.dot([newc[0],newc[1],1],row['coef'])+face*(.11 if name=='Central border brilliant' else .075);p+=newc-oldc
 if g['mat']=='CrestGem_Ruby':g['mat']='CrestGem_CrownRuby'
 parts.append((g,p,t))
for row in info:
 face=row['face'];center=row['new'];coef=row['coef'];rx=(row['points'][:4,0].max()-row['points'][:4,0].min())/2*.99;ry=(row['points'][:4,1].max()-row['points'][:4,1].min())/2*.99
 outer=np.array([[.82611,0],[0,-1.04],[-.82611,0],[0,1.04]]);inner=np.array([[rx,0],[0,-ry],[-rx,0],[0,ry]]);p,t=frame(outer,inner,.105);x=p[:,0]+center[0];y=-p[:,1]+center[1];z=np.c_[x,y,np.ones(len(x))]@coef+face*p[:,2];p=np.c_[x,y,z]
 if face<0:t=t[:,::-1]
 parts.append((dict(name='Ruby crown clean sculpted central gold setting',mat='gold',smooth=True),p,t))
minimum=min(p[:,1].min() for _,p,_ in parts);lift=-2.455-minimum;out={};groups=[]
for i,(g,p,t) in enumerate(parts):
 p[:,1]+=lift;out[f'{i}_points']=p.astype(np.float32);out[f'{i}_triangles']=t;groups.append(g)
np.savez_compressed(C/'geometry.npz',**out);(C/'groups.json').write_text(json.dumps(groups,indent=2));(C/'materials.json').write_text(json.dumps(materials,indent=2));(C/'retarget_report.json').write_text(json.dumps(dict(source='candidate09',gem_scale_xy=[1.2,.82],mount_half_extent_xy=[.82611,1.04],gem_center_y_shift=.278,pave_center_y_scale=.695,pave_stone_shapes_preserved=True,whole_model_lift=float(lift),upper_stones_remain_red=True),indent=2));print('Ruby center retargeted, duplicate setting layers removed, original pave cuts retained',len(groups))
