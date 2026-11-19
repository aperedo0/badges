"""Sweep Ruby Heart's real metal profile over Sapphire's current narrower outline."""
from pathlib import Path
import numpy as np,json,shutil,shapely,importlib.util
from shapely.geometry import Polygon,LineString,Point
from shapely.geometry.polygon import orient
R=Path(__file__).resolve().parent;A=R/'sapphire_teardrop/candidate23';C=A.parent/'candidate24';assert not C.exists();C.mkdir();D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text());name='solid_gold_teardrop_setting';part=next(p for p in M['parts'] if p['name']==name);region=orient(shapely.union_all([Polygon(t[:,:2]) for t in D[name+'_v'][:part['front']]]),sign=1);outer=region.exterior;inner=Polygon(region.interiors[0]);inner=orient(inner,sign=1);iq=np.asarray(inner.exterior.coords)[:-1];oq=np.asarray(outer.coords)[:-1]
locations=list(shapely.line_locate_point(outer,shapely.points(oq)))+list(np.linspace(0,outer.length,128,endpoint=False))
for i,p in enumerate(iq):
 a=p-iq[i-1];b=iq[(i+1)%len(iq)]-p;a/=np.linalg.norm(a);b/=np.linalg.norm(b);n=np.r_[a[1]+b[1],-a[0]-b[0]];n/=np.linalg.norm(n);hit=outer.intersection(LineString([p,p+n*20]));points=[g for g in getattr(hit,'geoms',[hit]) if g.geom_type=='Point'];assert points
 hit=min(points,key=lambda q:Point(p).distance(q));locations.append(outer.project(hit))
s=np.sort(np.asarray(locations));s=s[np.r_[True,np.diff(s)>1e-6]];O=shapely.get_coordinates(shapely.line_interpolate_point(outer,s));Q=shapely.get_coordinates(shapely.line_interpolate_point(inner.exterior,shapely.line_locate_point(inner.exterior,shapely.points(O))));assert Polygon(O).hausdorff_distance(Polygon(oq))<1e-5;assert Polygon(Q).hausdorff_distance(inner)<1e-5
# The source profile is read from the existing Ruby builder, not approximated.
source=R.parent/'ruby_heart_claude_20261107/tools/build_geometry.py';spec=importlib.util.spec_from_file_location('ruby_gold_profile_source',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);profile,crease=module.profile();r=profile[:,0]/module.SEAT;z=profile[:,1];rings=O[None]*(1-r[:,None,None])+Q[None]*r[:,None,None];nring=len(O);t=np.roll(rings,-1,axis=1)-np.roll(rings,1,axis=1);bad=np.linalg.norm(t,axis=2)<1e-10;fallback=np.roll(O,-1,axis=0)-np.roll(O,1,axis=0);t[bad]=np.broadcast_to(fallback,t.shape)[bad];t3=np.concatenate([t,np.zeros((*t.shape[:2],1))],2);across=np.concatenate([np.diff(rings,axis=0),np.broadcast_to(np.diff(z)[:,None,None],(len(z)-1,nring,1))],2);seg=[]
for k in range(len(profile)-1):
 v=np.cross(t3[k]+t3[k+1],across[k]);v/=np.maximum(np.linalg.norm(v,axis=1)[:,None],1e-10);seg.append(v)
seg=np.array(seg);sn=np.concatenate([seg[:1],seg[:-1]+seg[1:],seg[-1:]],0);sn/=np.maximum(np.linalg.norm(sn,axis=2)[:,:,None],1e-10)
start=outer.project(Point(O[np.argmax(O[:,1])]))
bottom=(outer.project(Point(O[np.argmin(O[:,1])]))-start)%outer.length
arc=(s-start)%outer.length;u=np.where(arc<=bottom,arc/bottom,(outer.length-arc)/(outer.length-bottom));vcoord=np.r_[0,np.cumsum(np.linalg.norm(np.diff(profile,axis=0),axis=1))];vcoord/=vcoord[-1]
V=[];N=[];UV=[]
for k in range(len(profile)-1):
 for i in range(nring):
  j=(i+1)%nring
  for corners in [[(k,i),(k,j),(k+1,j)],[(k,i),(k+1,j),(k+1,i)]]:
   vertices=np.array([[*rings[a,b],z[a]] for a,b in corners]);normal=np.cross(vertices[1]-vertices[0],vertices[2]-vertices[0])
   if np.linalg.norm(normal)<1e-10:continue
   normals=np.array([seg[k,b] if crease[a] else sn[a,b] for a,b in corners]);uv=np.array([[u[b],vcoord[a]] for a,b in corners]);
   if normal@normals.mean(0)<0:vertices=vertices[::-1];normals=normals[::-1];uv=uv[::-1]
   V.append(vertices);N.append(normals);UV.append(uv)
V=np.array(V,np.float32);N=np.array(N,np.float32);UV=np.array(UV,np.float32);D[name+'_v']=np.concatenate([V,(V*[1,1,-1])[:,::-1]]).astype(np.float32);D[name+'_n']=np.concatenate([N,(N*[1,1,-1])[:,::-1]]).astype(np.float32);D[name+'_uv']=np.concatenate([UV,UV[:,::-1]]);D[name+'_m']=np.zeros(2*len(V),np.int16);part.update(front=len(V),triangles=2*len(V),materials=['Gold']);np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
for f in ['optical_profile.json','owner_adjustment.json','palette_overrides.json','gold_transfer.json']:shutil.copy2(A/f,C/f)
shutil.copytree(A/'textures',C/'textures');report=json.loads((C/'gold_transfer.json').read_text());report['frame_geometry_and20_percent_narrowing_preserved']=False;report.update(narrower_outer_and_inner_xy_outlines_preserved=True,real_profile_transferred_from=str(source),ruby_profile=profile.tolist(),profile_uv_matches_source=True,frame_triangles=2*len(V),gem_unchanged=True);(C/'gold_transfer.json').write_text(json.dumps(report,indent=2)+'\n');print('Ruby profile on narrower Sapphire outline:',nring,'perimeter positions,',len(profile),'profile points,',2*len(V),'frame triangles')
