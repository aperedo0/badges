"""Filter unresolved cross band curvature, preserving curvature along each rim."""
from pathlib import Path
import json,shutil,time
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
R=Path(__file__).resolve().parent;B=R/'campfire_night';A=B/'candidate14';C=B/'candidate15';assert not C.exists();C.mkdir()
s=json.loads((R/'schedule.json').read_text());assert s['status']=='active' and s['phase']=='work' and time.time()+300<s['work_until_epoch']
for file in ['parts.npz','parts.json','center_validation.json','palette_enamel.json','palette.json','enamel_config.json','PIECES.json','validation.json']:
 if (A/file).exists():shutil.copy2(A/file,C/file)
shutil.copytree(A/'textures',C/'textures')
D=dict(np.load(C/'parts.npz'));M=json.loads((C/'parts.json').read_text());spec=json.loads((A/'PIECES.json').read_text());specs={p['name']:p for p in spec['pieces']};U=M['units'];counts={}
for p in M['parts']:
 name=p['name'];roles=np.array([p['materials'][i] for i in D[name+'_m']],dtype=object)
 if not ('SmoothGold' in p['materials']):continue
 q=specs[name];samples=[];directions=[]
 for polygon in q['outline']:
  xy=np.array(polygon['exterior'],float);xy[:,0]=(xy[:,0]-U['axis'])*U['S'];xy[:,1]=2.995-(xy[:,1]-U['top'])*U['S'];curve=orient(Polygon(xy),sign=1).exterior;L=curve.length
  t=np.linspace(0,L,max(128,int(L/.008)),endpoint=False)
  loc=np.array([curve.interpolate(float(a)).coords[0] for a in t]);before=np.array([curve.interpolate(float((a-.02)%L)).coords[0] for a in t]);after=np.array([curve.interpolate(float((a+.02)%L)).coords[0] for a in t]);tangent=after-before;out=np.c_[tangent[:,1],-tangent[:,0]];out/=np.maximum(np.linalg.norm(out,axis=1,keepdims=True),1e-9);samples.extend(loc);directions.extend(out)
 tree=cKDTree(samples);directions=np.asarray(directions)
 sel=(roles=='SmoothGold')|(roles=='GoldEdge');v=D[name+'_v'][sel];_,index=tree.query(v[...,:2].reshape(-1,2));out=directions[index].reshape(v.shape[:2]+(2,));tilt=.32 if name=='outer_gold_setting' else .14
 n=np.concatenate([out*tilt,np.ones(v.shape[:2]+(1,))],axis=-1);n[...,2]*=np.where(v.mean(1)[:,2]>=0,1,-1)[:,None];n/=np.linalg.norm(n,axis=-1,keepdims=True);D[name+'_n'][sel]=n.astype(np.float32);counts[name]=int(sel.sum())
np.savez_compressed(C/'parts.npz',**D)
(C/'finish_change.json').write_text(json.dumps(dict(source_geometry='candidate14',all_geometry_uvs_textures_materials_unchanged=True,cause='Narrow bevels contain unresolved normal changes across their width; native flat normal diagnosis removed the beading. Average the cross band normal while retaining continuous normal direction along the actual contour. Give the edge lips the same filtered normal field.',fine_border_tilt_ratio=.14,setting_tilt_ratio=.32,gold_beads_preserved=True,faces_by_piece=counts,native_acceptance_pending=True),indent=2)+'\n')
print('Saved contour filtered normals on',len(counts),'parts')
