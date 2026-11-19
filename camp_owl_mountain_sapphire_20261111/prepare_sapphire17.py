"""Keep the measured broad cut, shorten its girdle and add the two reference bezel edges in real geometry."""
from pathlib import Path
import numpy as np,json,shutil,shapely
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
R=Path(__file__).resolve().parent;A=R/'sapphire_teardrop/candidate16';C=A.parent/'candidate17';assert not C.exists();C.mkdir()
D=dict(np.load(A/'parts.npz'));M=json.loads((A/'parts.json').read_text());U=M['units'];S=U['S']
# All crown vertices are outside the old vertical girdle. Translate the two crowns
# toward each other without changing any measured XY, plane normal or table shape.
g=D['gem_v'];assert np.min(abs(g[...,2]))>.15999;g[...,2]-=np.sign(g[...,2])*.14
face=np.cross(g[:,1]-g[:,0],g[:,2]-g[:,0]);face/=np.linalg.norm(face,axis=1)[:,None];assert np.min((face*D['gem_n'][:,0]).sum(1))>.9999
name='solid_gold_teardrop_setting';p=next(p for p in M['parts'] if p['name']==name);old=D[name+'_v'][:p['front']];region=shapely.union_all([Polygon(t[:,:2]) for t in old]).simplify(.000001,preserve_topology=True);assert region.geom_type=='Polygon' and len(region.interiors)==1
outerxy=np.asarray(region.exterior.coords).copy();top=outerxy[:,1].max();tipx=outerxy[np.argmax(outerxy[:,1]),0];weight=np.clip((outerxy[:,1]-(top-.03))/.03,0,1);outerxy[:,0]=tipx+(outerxy[:,0]-tipx)*(1-.5*weight);O=Polygon(outerxy);I=Polygon(region.interiors[0]);region=orient(O.difference(I),sign=1);assert region.is_valid
b=.048;OB=O.buffer(-b);IB=I.buffer(b);zones=[O.difference(OB),OB.difference(IB),IB.difference(I)];assert abs(sum(a.area for a in zones)-region.area)<1e-7
front=[];zoneids=[]
for k,area in enumerate(zones):
 tri=shapely.constrained_delaunay_triangles(area)
 for t in tri.geoms:
  xy=np.asarray(t.exterior.coords)[:3];pts=shapely.points(xy);do=shapely.distance(pts,O.exterior);di=shapely.distance(pts,I.exterior);ratio=do/np.maximum(do+di,1e-10);height=.26+.14*ratio-.05*np.clip(1-do/b,0,1)-.05*np.clip(1-di/b,0,1);v=np.c_[xy,height]
  if np.cross(v[1]-v[0],v[2]-v[0])[2]<0:v=v[::-1]
  front.append(v);zoneids.append(k)
V=np.asarray(front,np.float32);zid=np.asarray(zoneids);pts,inv=np.unique(V.reshape(-1,3),axis=0,return_inverse=True);F=inv.reshape(-1,3);fn=np.cross(V[:,1]-V[:,0],V[:,2]-V[:,0]);length=np.linalg.norm(fn,axis=1);assert (length>1e-12).all();fn/=length[:,None];N=np.zeros_like(V)
# Separate normal fields on the outer bevel, broad sloping face and inner bevel.
for k in range(3):
 mask=zid==k;acc=np.zeros_like(pts,dtype=np.float64)
 for j in range(3):
  a=V[:,(j+1)%3]-V[:,j];q=V[:,(j+2)%3]-V[:,j];a/=np.linalg.norm(a,axis=1)[:,None];q/=np.linalg.norm(q,axis=1)[:,None];angle=np.arccos(np.clip((a*q).sum(1),-1,1));np.add.at(acc,F[mask,j],fn[mask]*angle[mask,None])
 good=np.linalg.norm(acc,axis=1)>1e-8;acc[good]/=np.linalg.norm(acc[good],axis=1)[:,None];N[mask]=acc[F[mask]]
# Welded front boundary creates a closed, mirrored mounting body.
edges=np.concatenate([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]);_,idx,count=np.unique(np.sort(edges,axis=1),axis=0,return_index=True,return_counts=True);E=edges[idx[count==1]];walls=[];wn=[]
for a,q in E:
 A0=pts[a];A1=pts[q];B0=A0*[1,1,-1];B1=A1*[1,1,-1];normal=np.cross(B0-A0,A1-A0);normal/=np.linalg.norm(normal);walls.extend([[A0,B0,A1],[A1,B0,B1]]);wn.extend([[normal,normal,normal],[normal,normal,normal]])
allv=np.concatenate([V,(V*[1,1,-1])[:,::-1],np.array(walls)]).astype(np.float32);alln=np.concatenate([N,(N*[1,1,-1])[:,::-1],np.array(wn)]).astype(np.float32);D[name+'_v']=allv;D[name+'_n']=alln;px=allv[...,0]/S+U['axis'];py=U['top']+(2.995-allv[...,1])/S;D[name+'_uv']=np.stack([px/U['width_px'],1-py/U['height_px']],2).astype(np.float32);D[name+'_m']=np.r_[np.zeros(2*len(V),np.int16),np.ones(len(walls),np.int16)];p.update(materials=['Gold','Side'],front=len(V),triangles=len(allv))
np.savez_compressed(C/'parts.npz',**D);(C/'parts.json').write_text(json.dumps(M,indent=1)+'\n')
for f in ['palette_overrides.json','optical_profile.json']:shutil.copy2(A/f,C/f)
(C/'cut_design.json').write_text(json.dumps(dict(change='Measured broad six sided table and crown normals preserved. Vertical girdle shortened from0.32 to0.04, overall gemstone depth1.0. Native density automatically normalizes to1.0, preserving central body attenuation.',front_and_rear_crown_normals_unchanged=True,projected_gem_cut_unchanged=True,bezel='Real0.048 unit outer bevel and inner bevel, with separate broad sloping face and sharper tip. Complete mirrored closed body.',bezel_front_triangles=len(V),no_app_changes=True,blender_review_pending=True),indent=2)+'\n')
print('Prepared17:',sum(p['triangles'] for p in M['parts']),'triangles, real two edge bezel and compact girdle')
