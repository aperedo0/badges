import bpy,bmesh,numpy as np,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def hash36(a):return hashlib.sha256(np.asarray(a).tobytes()).hexdigest()

def capture36(ob):
 me=ob.data;me.calc_loop_triangles();V=np.array([v.co[:] for v in me.vertices]);T=np.array([t.vertices[:] for t in me.loop_triangles]);N=np.array([n.vector[:] for n in me.corner_normals]);TN=N[np.array([t.loops[:] for t in me.loop_triangles])];attrs=[dict(smooth=me.polygons[t.polygon_index].use_smooth,material=me.polygons[t.polygon_index].material_index,source=ob.name) for t in me.loop_triangles]
 return dict(v=V,t=T,n=N,tn=TN,attrs=attrs,vertex_hash=hash36(V),triangle_hash=hash36(T),normal_hash=hash36(N),uv_layers=len(me.uv_layers),materials=[m.name if m else None for m in me.materials])

def mesh36(ob,d,material):
 me=ob.data;me.clear_geometry();me.from_pydata(d['v'].tolist(),[],d['t'].tolist());me.update();me.materials.clear();me.materials.append(material)
 for p,a in zip(me.polygons,d['attrs']):p.use_smooth=a['smooth'];p.material_index=0
 me.normals_split_custom_set(d['tn'].reshape(-1,3).tolist())

def topology36(ob):
 me=ob.data;me.calc_loop_triangles();v=np.array([v.co[:] for v in me.vertices]);t=np.array([t.vertices[:] for t in me.loop_triangles]);edges,counts=np.unique(np.sort(np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1),axis=0,return_counts=True);assert (counts==2).all(),(ob.name,'open frame');assert len(np.unique(np.sort(t,axis=1),axis=0))==len(t),(ob.name,'duplicate triangles');areas=np.linalg.norm(np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]),axis=1)/2;assert areas.min()>1e-10,(ob.name,'degenerate frame',float(areas.min()));parents={int(i):int(i) for i in np.unique(t)}
 def root(i):
  while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
  return i
 for a,b in edges:
  a,b=root(int(a)),root(int(b))
  if a!=b:parents[b]=a
 components=len({root(i) for i in parents});assert components==1,(ob.name,'disconnected frame',components);chi=len(np.unique(t))-len(edges)+len(t);vol=float(np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6);assert vol>0,(ob.name,'negative frame volume')
 return dict(closed=True,connected=True,euler=int(chi),volume=vol,triangles=len(t))

def source_field36(items):
 V=[];T=[];TN=[];attrs=[];offset=0
 for d in items:V.append(d['v']);T.append(d['t']+offset);TN.append(d['tn']);attrs+=d['attrs'];offset+=len(d['v'])
 v=np.vstack(V);t=np.vstack(T);tn=np.vstack(TN);tri=v[t];G=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);G/=np.linalg.norm(G,axis=1)[:,None];tree=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True,epsilon=0);return dict(v=v,t=t,tn=tn,tri=tri,geom=G,tree=tree,index=index36(tri),attrs=attrs)

def transfer36(ob,field):
 me=ob.data;normals=[];distances=[];source_indices=[];matched=0;conflicts=[]
 for face in me.polygons:
  vertices=np.array([me.vertices[i].co[:] for i in face.vertices]);normal=np.cross(vertices[1]-vertices[0],vertices[2]-vertices[0]);normal/=np.linalg.norm(normal);smooth=False
  for li in face.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;near=near36(field,p,.0008);near=[h for h in near if np.dot(field['geom'][h[2]],normal)>(.80 if field['attrs'][h[2]]['smooth'] else .90)]
   assert near,(ob.name,'new surface has no original normal field',face.index,tuple(p))
   h=min(near,key=lambda h:h[3]+.001*(1-float(np.dot(field['geom'][h[2]],normal))));
   nearby_equal=[x for x in near if x[3]<=h[3]+1e-5]
   candidates=[]
   for x in nearby_equal:
    weights=weights36(field['tri'][x[2]],np.array(x[0]));cn=(field['tn'][x[2]]*weights[:,None]).sum(0);cn/=np.linalg.norm(cn);candidates.append(cn)
   if len(candidates)>1:
    cn=np.array(candidates);angle=float(np.degrees(np.arccos(np.clip(cn@cn.T,-1,1))).max())
    if angle>3:conflicts.append(dict(face=face.index,position=list(p),candidate_normal_degrees=angle,source_members=sorted({field['attrs'][x[2]]['source'] for x in nearby_equal})))
   k=int(h[2]);q=np.array(h[0]);weights=weights36(field['tri'][k],q);n=(field['tn'][k]*weights[:,None]).sum(0);n/=np.linalg.norm(n);normals.append(n.tolist());distances.append(float(h[3]));source_indices.append(k);smooth=smooth or field['attrs'][k]['smooth'];matched+=1
  face.use_smooth=smooth;face.material_index=0
 me.normals_split_custom_set(normals)
 actual=np.array([n.vector[:] for n in me.corner_normals]);target=np.array(normals);dot=np.einsum('ij,ij->i',actual,target)/(np.linalg.norm(actual,axis=1)*np.linalg.norm(target,axis=1));angle=float(np.degrees(np.arccos(np.clip(dot,-1,1))).max());assert angle<.75,(ob.name,'normal encoding changed',angle)
 return dict(loop_targets=target,maximum_surface_error=max(distances),maximum_normal_encoding_degrees=angle,matched_loops=matched,conflicting_normal_candidates=conflicts)

def inside36(tree,point):
 out=[]
 for d in ((.93,.21,.3),(-.23,.89,.34),(.27,.31,.91)):
  p=Vector(point);direction=Vector(d).normalized();hits=0
  for _ in range(64):
   q,n,idx,dist=tree.ray_cast(p,direction,50)
   if q is None:break
   hits+=1;p=q+direction*1e-5
  else:raise AssertionError('Parity ray failed to leave frame')
  out.append(bool(hits%2))
 assert len(set(out))==1,('Ambiguous parity classification',point,out);return out[0]


def clean36(me):
 bm=bmesh.new();bm.from_mesh(me)
 try:
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
  bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
  repaired=[]
  for step in range(128):
   bad=[]
   for face in bm.faces:
    assert len(face.verts)==3
    v=np.array([v.co[:] for v in face.verts]);area=float(np.linalg.norm(np.cross(v[1]-v[0],v[2]-v[0]))/2)
    longest=max(e.calc_length() for e in face.edges);altitude=2*area/longest
    if area<=1e-10 or altitude<1e-6:bad.append((area,face))
   if not bad:break
   area,face=min(bad,key=lambda x:x[0]);edge=min(face.edges,key=lambda e:e.calc_length());length=edge.calc_length()
   assert length<.0016 and len(edge.link_faces)==2 and all(len(f.verts)==3 for f in edge.link_faces),('Sliver cannot be locally collapsed',area,length)
   bmesh.ops.collapse(bm,edges=[edge],uvs=False)
   repaired.append(dict(area_before=area,collapsed_edge_length=length,maximum_endpoint_motion=length/2))
  else:raise AssertionError('Sliver repair did not converge')
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);me.update()
  return repaired
 finally:bm.free()

# Double precision bounds and closest points. Blender BVH distances lose precision
# on the long thin bevel triangles in this saved chest. Never loosen the gate.
def index36(tri):
 low=tri.min(1);high=tri.max(1);centers=(low+high)/2
 def node(ids):
  lo=low[ids].min(0);hi=high[ids].max(0)
  if len(ids)<=16:return (lo,hi,ids,None,None)
  axis=int(np.ptp(centers[ids],axis=0).argmax());order=ids[np.argsort(centers[ids,axis],kind='stable')];mid=len(order)//2
  return (lo,hi,None,node(order[:mid]),node(order[mid:]))
 return node(np.arange(len(tri)))

def close36(tri,p):
 a=tri[:,0];b=tri[:,1];c=tri[:,2];e=b-a;f=c-a;n=np.cross(e,f);nn=np.einsum('ij,ij->i',n,n);assert (nn>0).all()
 q=p-n*(np.einsum('ij,ij->i',p-a,n)/nn)[:,None]
 u=np.einsum('ij,ij->i',np.cross(q-a,f),n)/nn;w=np.einsum('ij,ij->i',np.cross(e,q-a),n)/nn
 inside=(u>=-1e-12)&(w>=-1e-12)&(u+w<=1+1e-12)
 points=q.copy();distance2=np.einsum('ij,ij->i',q-p,q-p);distance2[~inside]=np.inf
 for A,B in ((a,b),(b,c),(c,a)):
  E=B-A;factor=np.clip(np.einsum('ij,ij->i',p-A,E)/np.einsum('ij,ij->i',E,E),0,1);Q=A+E*factor[:,None];D=np.einsum('ij,ij->i',Q-p,Q-p);better=D<distance2;points[better]=Q[better];distance2[better]=D[better]
 return points,np.sqrt(distance2)

def near36(field,p,radius):
 p=np.asarray(p,dtype=float);stack=[field['index']];ids=[];r2=radius*radius
 while stack:
  lo,hi,leaf,left,right=stack.pop();d=np.maximum(np.maximum(lo-p,p-hi),0)
  if d@d>r2:continue
  if leaf is not None:ids.extend(leaf)
  else:stack.append(left);stack.append(right)
 if not ids:return []
 ids=np.array(ids,dtype=int);points,dist=close36(field['tri'][ids],p);return [(q,field['geom'][k],int(k),float(d)) for k,q,d in zip(ids,points,dist) if d<=radius]

def weights36(tri,q):
 A,B,C=tri;e=B-A;f=C-A;n=np.cross(e,f);den=n@n;d=q-A;u=np.dot(np.cross(d,f),n)/den;w=np.dot(np.cross(e,d),n)/den;weights=np.clip([1-u-w,u,w],0,1);return weights/sum(weights)
