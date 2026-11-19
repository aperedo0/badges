"""Apply the saved contour averaged metal finish to a freshly built candidate."""
from pathlib import Path
import json,sys,time
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
R=Path(__file__).resolve().parent.parent;C=Path(sys.argv[1]).resolve();assert C.is_relative_to(R)
s=json.loads((R/'schedule.json').read_text());assert s['status']=='active' and s['phase']=='work' and time.time()<s['work_until_epoch']
D=dict(np.load(C/'parts.npz'));M=json.loads((C/'parts.json').read_text());spec=json.loads((C/'PIECES.json').read_text());specs={p['name']:p for p in spec['pieces']};U=M['units'];report={}
for p in M['parts']:
 name=p['name'];names=p['materials'];mi=D[name+'_m'];roles=np.array([names[i] for i in mi],dtype=object);nf=p['front'];e=(len(mi)-2*nf)//6;assert len(mi)-2*nf==6*e
 lip=np.zeros(len(mi),bool);lip[2*nf:2*nf+2*e]=True;lip[2*nf+4*e:]=True;roles[(roles=='Gold')&lip]='GoldEdge'
 if any(m.startswith('Enamel') for m in names) or name=='outer_gold_setting':
  roles[(roles=='Gold')&(np.arange(len(mi))<2*nf)]='SmoothGold';q=specs[name];samples=[];directions=[]
  for polygon in q['outline']:
   xy=np.array(polygon['exterior'],float);xy[:,0]=(xy[:,0]-U['axis'])*U['S'];xy[:,1]=2.995-(xy[:,1]-U['top'])*U['S'];curve=orient(Polygon(xy),sign=1).exterior;L=curve.length;t=np.linspace(0,L,max(128,int(L/.008)),endpoint=False)
   loc=np.array([curve.interpolate(float(a)).coords[0] for a in t]);before=np.array([curve.interpolate(float((a-.02)%L)).coords[0] for a in t]);after=np.array([curve.interpolate(float((a+.02)%L)).coords[0] for a in t]);tangent=after-before;out=np.c_[tangent[:,1],-tangent[:,0]];out/=np.maximum(np.linalg.norm(out,axis=1,keepdims=True),1e-9);samples.extend(loc);directions.extend(out)
  tree=cKDTree(samples);directions=np.asarray(directions);sel=(roles=='SmoothGold')|(roles=='GoldEdge');v=D[name+'_v'][sel];_,index=tree.query(v[...,:2].reshape(-1,2));out=directions[index].reshape(v.shape[:2]+(2,));tilt=.32 if name=='outer_gold_setting' else .14
  n=np.concatenate([out*tilt,np.ones(v.shape[:2]+(1,))],axis=-1);n[...,2]*=np.where(v.mean(1)[:,2]>=0,1,-1)[:,None];n/=np.linalg.norm(n,axis=-1,keepdims=True);D[name+'_n'][sel]=n.astype(np.float32);report[name]=int(sel.sum())
 names=sorted(set(roles));p['materials']=names;D[name+'_m']=np.array([names.index(x) for x in roles],np.int16)
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
(C/'contour_finish.json').write_text(json.dumps(dict(source='candidate15 contour averaged normal field',fine_border_tilt=.14,setting_tilt=.32,geometry_uvs_unchanged=True,beads_unchanged=True,parts=report,native_review_pending=True),indent=2)+'\n')
print('Applied contour averaged normals:',len(report),'parts')
