"""Narrow the gold band from its outside by twenty percent and use yellow gold reflectance."""
from pathlib import Path
import numpy as np,json,shutil,shapely
from shapely.geometry import Polygon
R=Path(__file__).resolve().parent;A=R/'sapphire_teardrop/candidate18';C=A.parent/'candidate22';assert not C.exists();C.mkdir()
D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text());name='solid_gold_teardrop_setting';part=next(p for p in M['parts'] if p['name']==name);nf=part['front'];old=D[name+'_v'].copy();region=shapely.union_all([Polygon(t[:,:2]) for t in old[:nf]]);assert region.geom_type=='Polygon' and len(region.interiors)==1;inner=region.interiors[0];outer=region.exterior
v=D[name+'_v'];xy=v[...,:2].reshape(-1,2).astype(float);Q=shapely.get_coordinates(shapely.line_interpolate_point(inner,shapely.line_locate_point(inner,shapely.points(xy))));v[...,:2]=(xy*.8+Q*.2).reshape(v[...,:2].shape)
# Keep physical bevels separate when recalculating the real shape normals.
oldfront=old[:nf,:,:2];po=shapely.points(oldfront.reshape(-1,2));do=shapely.distance(po,outer).reshape(-1,3);di=shapely.distance(po,inner).reshape(-1,3);zones=np.ones(nf,np.int16);zones[np.max(do,axis=1)<.04801]=0;zones[np.max(di,axis=1)<.04801]=2
front=v[:nf];P,inv=np.unique(front.reshape(-1,3),axis=0,return_inverse=True);F=inv.reshape(-1,3);fn=np.cross(front[:,1]-front[:,0],front[:,2]-front[:,0]);fn/=np.linalg.norm(fn,axis=1)[:,None];N=np.zeros_like(front)
for group in range(3):
 mask=zones==group;acc=np.zeros_like(P,dtype=float)
 for k in range(3):
  a=front[:,(k+1)%3]-front[:,k];b=front[:,(k+2)%3]-front[:,k];a/=np.linalg.norm(a,axis=1)[:,None];b/=np.linalg.norm(b,axis=1)[:,None];ang=np.arccos(np.clip((a*b).sum(1),-1,1));np.add.at(acc,F[mask,k],fn[mask]*ang[mask,None])
 good=np.linalg.norm(acc,axis=1)>1e-10;acc[good]/=np.linalg.norm(acc[good],axis=1)[:,None];N[mask]=acc[F[mask]]
D[name+'_n'][:nf]=N;D[name+'_n'][nf:2*nf]=(N*[1,1,-1])[:,::-1]
wall=v[2*nf:];P,inv=np.unique(wall.reshape(-1,3),axis=0,return_inverse=True);F=inv.reshape(-1,3);fn=np.cross(wall[:,1]-wall[:,0],wall[:,2]-wall[:,0]);fn/=np.linalg.norm(fn,axis=1)[:,None];acc=np.zeros_like(P,dtype=float)
for k in range(3):
 a=wall[:,(k+1)%3]-wall[:,k];b=wall[:,(k+2)%3]-wall[:,k];a/=np.linalg.norm(a,axis=1)[:,None];b/=np.linalg.norm(b,axis=1)[:,None];ang=np.arccos(np.clip((a*b).sum(1),-1,1));np.add.at(acc,F[:,k],fn*ang[:,None])
acc/=np.linalg.norm(acc,axis=1)[:,None];D[name+'_n'][2*nf:]=acc[F]
# Keep the badge centered on its spin axis and at the existing shared floor gap.
allv=np.concatenate([D[p['name']+'_v'].reshape(-1,3) for p in M['parts']]);delta=np.array([-(allv[:,0].min()+allv[:,0].max())/2,-2.455-allv[:,1].min(),0.],np.float32)
for p in M['parts']:D[p['name']+'_v']+=delta
outerxy=np.asarray(outer.coords)[:-1];q=shapely.get_coordinates(shapely.line_interpolate_point(inner,shapely.line_locate_point(inner,shapely.points(outerxy))));narrow=outerxy*.8+q*.2;before=shapely.distance(shapely.points(outerxy),inner);after=shapely.distance(shapely.points(narrow),inner);ratios=after/before;assert np.max(abs(ratios-.8))<1e-7
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n');palette=json.loads((A/'palette_overrides.json').read_text());palette['Gold']=dict(albedo=[.98,.76,.26],metallic=1,roughness=.20);palette['Side']=dict(albedo=[.78,.53,.14],metallic=1,roughness=.38);(C/'palette_overrides.json').write_text(json.dumps(palette,indent=2)+'\n');shutil.copy2(A/'optical_profile.json',C/'optical_profile.json')
allv=np.concatenate([D[p['name']+'_v'].reshape(-1,3) for p in M['parts']]);report=dict(owner_request='Front outline twenty percent thinner and more yellow gold.',rim_width_factor_min=float(ratios.min()),rim_width_factor_max=float(ratios.max()),rim_inner_edge_unchanged_before_whole_badge_translation=True,whole_badge_translation=delta.tolist(),gem_cut_normals_uvs_and_runtime_unchanged=True,thickness_unchanged=True,expected_y_max=float(allv[:,1].max()),expected_y_min=-2.455,gold_reflectance_before=[.83,.43,.045],gold_reflectance_after=[.98,.76,.26],source='candidate18',no_app_code_edits=True)
(C/'owner_adjustment.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
