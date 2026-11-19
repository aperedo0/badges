import bpy,numpy as np,sys,importlib.util,json,math
from pathlib import Path
from mathutils import Vector,geometry
R=Path('/Users/antonioperedo/Desktop/badges/ruby_heart_gem_20261113');C=R/'candidate03';C.mkdir(exist_ok=True)
sys.path.insert(0,str(R.parent/'ruby_heart_claude_20261107/tools'))
import facets
spec=importlib.util.spec_from_file_location('smooth_frame',R.parent/'ruby_heart_smooth_20261112/tools/smooth_frame.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
left=b.smooth_ring(.39);ring=np.vstack([left,left[-2:0:-1]*[-1,1]])
anchors=np.unique(np.r_[np.arange(0,len(left),10),len(left)-1,len(left)-1+np.arange(10,len(left)-1,10),0]).astype(int);anchors=anchors[anchors<len(ring)]
# Original traced interior landmarks plus deliberately placed points dividing the broad center facets.
names,xy,girdle,faces=facets.layout();inside=xy[~girdle]
extra=np.array([[0,.10],[-.63,1.48],[.63,1.48],[-1.18,.50],[1.18,.50],[-.66,-.48],[.66,-.48],[-1.45,-.73],[1.45,-.73],[0,-1.34]])
controls=np.vstack([ring[anchors],inside,extra]);nb=len(anchors)
verts,edges,faces,origin,oe,of=geometry.delaunay_2d_cdt([Vector(v) for v in controls],[],[list(range(nb))],1,1e-6)
coords=np.asarray(verts);faces=np.asarray(faces,int);assert faces.shape[1]==3
segments=np.roll(ring,-1,axis=0)-ring
p=coords[:,None,:]-ring[None,:,:];t=np.clip((p*segments).sum(2)/(segments*segments).sum(1),0,1)
dist=np.linalg.norm(p-t[:,:,None]*segments,axis=2).min(1)
# A continuous ruby crown; neighboring facets share their actual vertices.
normalized=dist/dist.max()
height=.22+.76*np.power(normalized,1.16)
height+=.025*coords[:,1]*normalized
points=np.c_[coords,height]
coarseids=[int(np.argmin(np.linalg.norm(coords-v,axis=1))) for v in ring[anchors]]
for i,j in enumerate(coarseids):points[j]=np.r_[ring[anchors[i]],.22]
# Orient one real upper lobe facet toward the existing large studio softbox.
# Its mirrored partner uses the same physical cut; light remains fixed.
f=faces[9];center=points[f].mean(0);view=np.array([0,1.8,23.])-center;view/=np.linalg.norm(view)
light=np.array([-.773,.497,.393]);light/=np.linalg.norm(light);n=view+light;n/=np.linalg.norm(n);slope=-n[:2]/n[2]
fixed=next(int(j) for j in f if j in coarseids);anchor=points[fixed].copy()
for j in f:
 if j in coarseids:continue
 points[j,2]=anchor[2]+np.dot(slope,points[j,:2]-anchor[:2])
 mirror=np.flatnonzero(np.linalg.norm(points[:,:2]-points[j,:2]*[-1,1],axis=1)<1e-5)
 for k in mirror:points[k,2]=points[j,2]
np.savez(C/'control_cut.npz',coords=coords,triangles=faces,heights=height,points=points,coarseids=coarseids,distances=dist)
arc={}
for i in range(nb):
 ia,ib=coarseids[i],coarseids[(i+1)%nb];aa,bb=int(anchors[i]),int(anchors[(i+1)%nb]);indices=[];k=(aa+1)%len(ring)
 while k!=bb:indices.append(k);k=(k+1)%len(ring)
 arc[(ia,ib)]=indices;arc[(ib,ia)]=indices[::-1]
V=[];N=[];T=[];boundaryZ=np.full(len(ring),np.nan)
for i,j in enumerate(anchors):boundaryZ[j]=.22
for f in faces:
 real=points[f].copy();normal=np.cross(real[1]-real[0],real[2]-real[0]);normal/=np.linalg.norm(normal)
 if normal[2]<0:f=f[::-1];real=points[f];normal=-normal
 poly=[]
 for a,c in zip(f,np.roll(f,-1)):
  poly.append(points[a])
  for k in arc.get((int(a),int(c)),[]):
   q=ring[k];z=(np.dot(normal,real[0])-normal[0]*q[0]-normal[1]*q[1])/normal[2]
   boundaryZ[k]=z;poly.append(np.r_[q,z])
 poly=np.asarray(poly);base=len(V);center=poly.mean(0);V.append(center);N.append(normal)
 for q in poly:V.append(q);N.append(normal)
 for k in range(len(poly)):T.append([base,base+1+k,base+1+(k+1)%len(poly)])
assert np.isfinite(boundaryZ).all();assert boundaryZ.min()>.02,boundaryZ.min()
V=np.asarray(V);N=np.asarray(N);T=np.asarray(T)
frontV=V.copy();frontN=N.copy();frontT=T.copy()
V=np.vstack([V,V*[1,1,-1]]);N=np.vstack([N,N*[1,1,-1]]);T=np.vstack([T,T[:,::-1]+len(frontV)])
# One closed stone, with its girdle inside the gold setting.
for i in range(len(ring)):
 j=(i+1)%len(ring);q=np.array([np.r_[ring[i],boundaryZ[i]],np.r_[ring[j],boundaryZ[j]],np.r_[ring[j],-boundaryZ[j]],np.r_[ring[i],-boundaryZ[i]]]);n=np.cross(q[1]-q[0],q[2]-q[0]);n/=np.linalg.norm(n)
 centroid=(q.mean(0))[:2];tangent=ring[j]-ring[i];out=np.array([-tangent[1],tangent[0]])
 # Ring is counterclockwise in XY; the right side of each edge is outside.
 area=.5*np.sum(ring[:,0]*np.roll(ring[:,1],-1)-ring[:,1]*np.roll(ring[:,0],-1))
 if area>0:out=-out
 if np.dot(n[:2],out)<0:q=q[::-1];n=-n
 base=len(V);V=np.vstack([V,q]);N=np.vstack([N,np.tile(n,(4,1))]);T=np.vstack([T,[[base,base+1,base+2],[base,base+2,base+3]]])
D=dict(np.load(R.parent/'ruby_heart_smooth_20261112/candidate01/geometry.npz'));D.update(gem_v=V,gem_n=N,gem_t=T)
np.savez(C/'geometry.npz',**D)
# Rebuild only the gem inside its existing object in the live scene.
sc=bpy.context.scene;ob=sc.objects['Ruby Heart gem'];me=ob.data;mat=me.materials[0];me.clear_geometry()
tobl=lambda v:np.c_[v[:,0],-v[:,2],v[:,1]]
me.from_pydata(tobl(V).tolist(),[],T.tolist());me.update();me.polygons.foreach_set('use_smooth',[True]*len(T));ids=np.array([l.vertex_index for l in me.loops]);me.normals_split_custom_set(tobl(N[ids]).tolist())
(C/'design.json').write_text(json.dumps(dict(front_facet_planes=len(faces),gem_triangles=len(T),girdle_height_min=float(boundaryZ.min()),girdle_height_max=float(boundaryZ.max()),max_crown_height=float(height.max()),shared_actual_vertices=True,gold_unchanged=True,app_optics_unchanged=True,appearance_texture=False),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ruby_heart.blend'));sc.render.filepath=str(C/'blender_front.png');bpy.ops.render.render(write_still=True)
print('Built and rendered new complete ruby cut',len(faces),'front planes',len(T),'gem triangles')
