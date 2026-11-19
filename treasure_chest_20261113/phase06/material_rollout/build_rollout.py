import bpy,numpy as np,math,json,hashlib
from pathlib import Path
from mathutils import Matrix
D=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(D/'baseline.blend'));sc=bpy.data.scenes['Test plank master'];R=np.array(Matrix.Rotation(math.radians(32),3,'Y'));UV='ChestRolloutWood';records=[]
def local(a):return np.c_[a[:,0],a[:,2],-a[:,1]]@R
def coords(me):
 a=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',a.ravel());return local(a)
def stable(name):return int(hashlib.sha256(name.encode()).hexdigest()[:8],16)
def arrays(me):
 a=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',a);return a
woodsource=sc.objects['Master Chest Body Envelope'].data.materials[1];wood=woodsource.copy();wood.name='Chest wood shared varied atlas';wood.node_tree.nodes['Single plank explicit UV'].uv_map=UV;wood.node_tree.nodes['Single plank physical tangent normal'].uv_map=UV
for role in ['albedo','normal','roughness']:
 im=bpy.data.images.load(str(D/'wood_atlas'/(role+'.png')),check_existing=True);im.colorspace_settings.name='sRGB' if role=='albedo' else 'Non-Color';im.pack();wood.node_tree.nodes['Single plank '+role].image=im
angles=np.linspace(0,np.pi,4097);arc=np.r_[0,np.cumsum(np.hypot(1.9475*np.cos((angles[1:]+angles[:-1])*.5),1.65*np.sin((angles[1:]+angles[:-1])*.5))*np.diff(angles))]
def theta(q):return np.clip(np.arctan2((q[:,1]-.38075)/1.9475,q[:,2]/1.65),0,np.pi)
def wood_surface(name):
 obj=sc.objects[name];obj.data=obj.data.copy();me=obj.data;q=coords(me);newuv=np.zeros((len(me.loops),2),np.float32);groups={};old_index=np.array([p.material_index for p in me.polygons]);me.materials[0]=wood
 for p in me.polygons:
  if name.startswith('Master') and old_index[p.index]==1:continue
  ids=np.array(p.vertices);a=q[ids];c=a.mean(0);n=local(np.array([p.normal]))[0];row=0;rare=False
  if name.startswith('Master'):
   if abs(c[2])>1.48 or (abs(n[2])>.65 and abs(c[2])>1.35):
    side=1 if c[2]>0 else -1;outer=abs(c[2])>1.48;row=int(c[1]>-.84) if outer else 0;label=f'body {"outer" if outer else "inside"} face {side} row {row}';s=a[:,0]*side;t=a[:,1];rare=side==-1 and outer and row==0
   elif abs(c[0])>2.40 or (abs(n[0])>.65 and abs(c[0])>2.30):
    side=1 if c[0]>0 else -1;outer=abs(c[0])>2.40;row=int(c[1]>-.84) if outer else 0;label=f'body {"outer" if outer else "inside"} end {side} row {row}';s=-side*a[:,2];t=a[:,1]
   else:label='body floor '+str(int(c[1]<-2.1));s=a[:,0];t=a[:,2]
  else:
   if abs(n[0])>.65 and abs(c[0])>2.35:
    side=1 if c[0]>0 else -1;outer=abs(c[0])>2.5;row=int(c[1]>1.30);label=f'lid {"outer" if outer else "inside"} end {side} row {row}';s=-side*a[:,2];t=a[:,1]
   else:
    th=theta(a);tc=float(theta(c[None])[0]);row=min(6,int(tc/np.pi*7));inside=((c[1]-.38075)/1.9475)**2+(c[2]/1.65)**2<.95;label=f'lid {"inner" if inside else "outer"} stave {row}';s=a[:,0];t=np.interp(th,angles,arc)
  
  area2=abs(float(np.dot(s,np.roll(t,-1))-np.dot(t,np.roll(s,-1))))
  if area2<1e-9 and p.area>1e-8:
   axis=int(np.argmax(abs(n)));s=a[:,(axis+1)%3];t=a[:,(axis+2)%3];label+=' cap '+str(axis)
  g=groups.setdefault(label,dict(s=[],t=[],loops=[],rare=rare));g['s'].extend(s.tolist());g['t'].extend(t.tolist());g['loops'].extend(p.loop_indices)
 for label,g in groups.items():
  rng=np.random.default_rng(stable(label));s=np.array(g['s']);t=np.array(g['t']);L=np.ptp(s);B=np.ptp(t);tile=3 if g['rare'] else int(rng.integers(0,3));scale=min(float(rng.uniform(.91,.99)),.98*5.1/max(L,1e-5),.97*2.755/max(B,1e-5));u0=float(rng.uniform(.005,max(.006,1-L*scale/5.1-.005)));v0=.45 if g['rare'] else float(rng.uniform(.03,max(.031,2.755-B*scale-.03)));u=u0+(s-s.min())*scale/5.1;v=(3-tile)/4+(v0+(t-t.min())*scale)/(2.755*4);newuv[np.array(g['loops'])]=np.c_[u,v];records.append(dict(kind='wood',object=name,chart=label,tile=tile,physical_scale=scale,grain_length=float(L),cross_width=float(B),rare_knot=bool(g['rare'])))
 layer=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);layer.data.foreach_set('uv',newuv.ravel());assert np.isfinite(newuv).all()
 obj['material_rollout']='Varied coordinated wood atlas';me.update()
wood_surface('Master Chest Body Envelope');wood_surface('Lab Chest Barrel Lid Envelope')
ironsource=sc.objects['Lab Chest Lower Rim'].data.materials[0];iron=ironsource.copy();iron.name='Chest forged iron shared varied surface';nt=iron.node_tree
# The original rim already carries broad physical hammering. New unchanged meshes need that same authored layer in shading.
nt.nodes['coarse16.png independent strength'].inputs['Strength'].default_value=1
for name,value in [('wear.png',0),('Character edge_wear.png',0),('Character protection.png',1)]:
 n=nt.nodes[name];v=nt.nodes.new('ShaderNodeValue');v.name='Rollout '+name;v.outputs[0].default_value=value
 for link in list(n.outputs['Color'].links):nt.links.new(v.outputs[0],link.to_socket)
# Existing facet wear connections now read local bevel curvature instead of a mask painted for the test rail.
structural=[]
for o in sc.objects:
 if o.type!='MESH':continue
 name=o.name
 if name in ['Lab Chest Upper Lid Rim','Lab Chest Body Upper Rim','Lab Chest Central Lock Strap','Lab Chest Central Lower Cuff'] or name.startswith(('Lab Chest Corner Upright','Lab Chest Angular Boot','Lab Chest End Arch Crown Tab')) or name.endswith(' Seat'):structural.append(o)
def components(me):
 parent=np.arange(len(me.vertices))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in me.edges:
  a,b=map(root,e.vertices)
  if a!=b:parent[b]=a
 return np.array([root(i) for i in range(len(parent))])
def iron_surface(obj):
 obj.data=obj.data.copy();me=obj.data;q=coords(me);comp=components(me);groups={};uvar=np.zeros((len(me.loops),2),np.float32);rng=np.random.default_rng(stable(obj.name));seed=float(rng.uniform(0,6.28));component_info={}
 for cid in np.unique(comp):
  points=q[comp==cid];lo=points.min(0);hi=points.max(0);span=hi-lo;component_info[int(cid)]=(lo,hi,span)
 roofx=np.sort(q[q[:,1]>1.1,0]) if obj.name=='Lab Chest Upper Lid Rim' else np.array([]);roofgroups=np.split(roofx,np.flatnonzero(np.diff(roofx)>.68)+1) if len(roofx) else [];roofcenters=np.array([(g.min()+g.max())*.5 for g in roofgroups if len(g)])
 for p in me.polygons:
  a=q[list(p.vertices)];c=a.mean(0);n=local(np.array([p.normal]))[0];cid=int(comp[p.vertices[0]]);lo,hi,span=component_info[cid];mode='';axis=int(np.argmax(abs(n)))
  if obj.name=='Lab Chest Upper Lid Rim' and c[1]>.79:
   hoop=int(np.argmin(abs(roofcenters-c[0])));s=np.interp(theta(a),angles,arc);side=abs(n[0])>.65;t=(np.hypot((a[:,1]-.38075)/1.9475,a[:,2]/1.65)-1)*1.8 if side else a[:,0];mode='curved hoop '+str(hoop)+(' side' if side else ' face')
  elif obj.name in ['Lab Chest Upper Lid Rim','Lab Chest Body Upper Rim'] and span[0]>4:
   # Perimeter distance keeps long belt charts in physical units, including end returns.
   hx=max(abs(lo[0]),abs(hi[0]));hz=max(abs(lo[2]),abs(hi[2]));front=abs(c[2])/max(hz,1e-5)>=abs(c[0])/max(hx,1e-5)
   if front:s=(a[:,0]+hx) if c[2]>=0 else (3*hx+2*hz-a[:,0])
   else:s=(2*hx+hz-a[:,2]) if c[0]>=0 else (4*hx+3*hz+a[:,2])
   t=a[:,1] if axis!=1 else np.maximum(abs(a[:,0])-hx,abs(a[:,2])-hz);mode='perimeter '+str(axis==1)
  else:
   # Orthogonal charts on actual faces avoid stretched textures on boots, posts and small plates.
   if axis==2:s=a[:,1];t=a[:,0]
   elif axis==0:s=a[:,1];t=a[:,2]
   else:s=a[:,0];t=a[:,2]
   mode='plane '+str(axis)+' '+str(int(n[axis]>0))
  area2=abs(float(np.dot(s,np.roll(t,-1))-np.dot(t,np.roll(s,-1))))
  if area2<1e-9 and p.area>1e-8:s=a[:,(axis+1)%3];t=a[:,(axis+2)%3];mode+=' cap '+str(axis)
  label=str(cid)+' '+mode;g=groups.setdefault(label,dict(s=[],t=[],loops=[],mode=mode));g['s'].extend(s.tolist());g['t'].extend(t.tolist());g['loops'].extend(p.loop_indices)
 for label,g in groups.items():
  s=np.array(g['s']);t=np.array(g['t']);L=np.ptp(s);B=np.ptp(t);scale=min(1.0,.76*.5035/max(B,1e-5));phase=float(rng.uniform(.015,max(.016,.98-L*scale/18.04)));u=phase+(s-s.min())*scale/18.04;v=.5+(t-(t.min()+t.max())/2)*scale/.5035;uvar[np.array(g['loops'])]=np.c_[u,v];records.append(dict(kind='iron',object=obj.name,chart=label,mapping=g['mode'],physical_scale=scale,phase=phase,cross_width=float(B)))
 me.calc_loop_triangles();bad=set()
 for tri in me.loop_triangles:
  if tri.area<1e-6:continue
  a=uvar[list(tri.loops)];det=(a[1,0]-a[0,0])*(a[2,1]-a[0,1])-(a[1,1]-a[0,1])*(a[2,0]-a[0,0])
  if abs(det)<1e-10:bad.add(tri.polygon_index)
 for pi in bad:
  p=me.polygons[pi];a=q[list(p.vertices)];n=local(np.array([p.normal]))[0];axis=int(np.argmax(abs(n)));s=a[:,(axis+1)%3]+.173*a[:,axis];t=a[:,(axis+2)%3]+.113*a[:,axis];scale=min(1.,.76*.5035/max(float(np.ptp(t)),1e-6));phase=(stable(obj.name+str(pi))%700)/1000+.02;uvar[list(p.loop_indices)]=np.c_[phase+(s-s.min())*scale/18.04,.5+(t-(t.max()+t.min())*.5)*scale/.5035]
 if bad:records.append(dict(kind='iron uv repair',object=obj.name,faces=len(bad),method='Actual face plane projection for degenerate corner triangles'))
 for uvname in ['LowerIronAtlas','LowerIronPhysical']:
  uv=me.uv_layers.get(uvname) or me.uv_layers.new(name=uvname);uv.data.foreach_set('uv',(uvar if uvname=='LowerIronAtlas' else uvar*np.array([18.04,.5035],np.float32)).ravel())
 normals=np.array([p.normal[:] for p in me.polygons]);centers=np.array([p.center[:] for p in me.polygons]);edgefaces={}
 for p in me.polygons:
  for li in p.loop_indices:edgefaces.setdefault(me.loops[li].edge_index,[]).append(p.index)
 wear=np.zeros(len(me.vertices),np.float32)
 for ei,faces in edgefaces.items():
  if len(faces)!=2:continue
  f,g=faces;angle=math.acos(float(np.clip(normals[f]@normals[g],-1,1)))
  if angle<.065 or normals[f]@(centers[g]-centers[f])>1e-5:continue
  value=min(.82,(angle-.065)/.55)
  for vi in me.edges[ei].vertices:wear[vi]=max(wear[vi],value)
 noise=.5+.24*np.sin(q[:,0]*23+np.sin(q[:,1]*11)+seed)+.24*np.sin(q[:,2]*29-q[:,1]*9+seed*2);mask=np.clip((noise-.31)/.48,0,1);mask=mask*mask*(3-2*mask);wear*=mask
 attr=me.attributes.get('Damaged bevel facet wear') or me.attributes.new('Damaged bevel facet wear','FLOAT','POINT');attr.data.foreach_set('value',wear);me.materials.clear();me.materials.append(iron)
 for p in me.polygons:p.material_index=0
 obj['material_rollout']='Existing layered forged iron, unique physical charts and local convex bevel wear';me.update();assert np.isfinite(uvar).all()
for o in structural:iron_surface(o)
# Keep the original camera, reference, lighting and functional rig. The existing isolated review scene is the full chest review.
review=bpy.data.scenes['Bottom iron reflection review'];review.name='Full chest material evaluation'
for w in bpy.context.window_manager.windows:w.scene=review
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(D/'master.blend'),compress=True)
(D/'assignments.json').write_text(json.dumps(dict(wood_objects=['Master Chest Body Envelope','Lab Chest Barrel Lid Envelope'],iron_objects=[o.name for o in structural],preserved_iron_benchmark=['Lab Chest Lower Rim','Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4'],wood_material=wood.name,iron_material=iron.name,charts=records,decorative_hardware='All preexisting materials unchanged',geometry='All vertex coordinates and topology unchanged; new panels use coordinated full tangent surface relief',review_scene=review.name),indent=2));print('ROLLOUT SAVED',len(structural),'new iron objects',len(records),'varied charts',flush=True)
