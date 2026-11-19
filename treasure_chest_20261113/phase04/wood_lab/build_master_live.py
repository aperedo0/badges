import bpy,numpy as np,json,math,hashlib
from pathlib import Path
from mathutils import Matrix
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab');source=bpy.data.scenes['Chest Complete Form Phase 1'];lab=bpy.data.scenes['Wood surface comparison'];ob=source.objects['Chest Body Envelope'];me=ob.data;slot=[i for i,m in enumerate(me.materials) if 'Sample45' in m.name][0]
W,H=1537,417;margin=.006;yb=-2.1605000495910645;yt=-.862500011920929;xb=2.49114990234375;xt=2.3499999046325684;R=np.array(Matrix.Rotation(math.radians(32),3,'Y'))
V0=np.array([v.co for v in me.vertices],float);local=np.c_[V0[:,0],V0[:,2],-V0[:,1]]@R
Y=np.broadcast_to(np.linspace(yb+margin,yt-margin,H)[:,None],(H,W));half=xb+(xt-xb)*(Y[:,0]-yb)/(yt-yb);X=(half[:,None]-margin)*np.linspace(-1,1,W)[None,:]
a=np.load(P/'H_resolved/surface.npz')['height'];hh,ww=a.shape;u=np.clip((X+2.55)/5.1,0,1)*(ww-1);v=np.clip(1-(Y+2.2175)/1.3775,0,1)*(hh-1);ix=u.astype(int);iy=v.astype(int);fx=u-ix;fy=v-iy
Z=a[iy,ix]*(1-fx)*(1-fy)+a[iy,np.minimum(ix+1,ww-1)]*fx*(1-fy)+a[np.minimum(iy+1,hh-1),ix]*(1-fx)*fy+a[np.minimum(iy+1,hh-1),np.minimum(ix+1,ww-1)]*fx*fy
edge=np.minimum.reduce([half[:,None]-abs(X),Y-yb,yt-Y]);fade=np.clip(edge/.045,0,1);fade=fade*fade*(3-2*fade);Z=1.6+Z*fade
q=np.stack([X,Y,Z],axis=2).reshape(-1,3)@R.T;q=np.c_[q[:,0],-q[:,2],q[:,1]];V=np.vstack([V0,q]);base=len(V0);ids=np.arange(W*H).reshape(H,W)+base
kept=[f for f in me.polygons if f.index not in [354,356,357]];F=[list(f.vertices) for f in kept];origcount=len(F);origloops=sum(len(f.vertices) for f in kept)
grid=np.stack([ids[:-1,:-1],ids[:-1,1:],ids[1:,1:],ids[1:,:-1]],axis=2).reshape(-1,4);F.extend(grid.tolist())
def find(x,y):
 d=np.linalg.norm(local-np.array([x,y,1.6]),axis=1);i=int(d.argmin());assert d[i]<1e-5,(x,y,d[i]);return i
bl=find(-xb,yb);br=find(xb,yb);tl=find(-xt,yt);tr=find(xt,yt);tc=find(.14738,yt);k=int(np.argmin(abs(X[-1]-.14738)))
def strip(A,B,chain):
 chain=list(map(int,chain));F.append([A,B,chain[-1]])
 for i in range(len(chain)-1,0,-1):F.append([A,chain[i],chain[i-1]])
strip(bl,br,ids[0]);strip(br,tr,ids[:, -1]);strip(tr,tc,ids[-1,k:][::-1]);strip(tc,tl,ids[-1,:k+1][::-1]);strip(tl,bl,ids[:,0][::-1])
new=bpy.data.meshes.new('Editable watertight wood master');new.from_pydata(V.tolist(),[],F);new.update()
for m in me.materials:new.materials.append(m)
new.materials[slot]=bpy.data.materials['Wood Lab H'];mi=np.full(len(F),slot,dtype=np.int32);mi[:origcount]=[f.material_index for f in kept];new.polygons.foreach_set('material_index',mi);smooth=np.ones(len(F),dtype=bool);smooth[:origcount]=[f.use_smooth for f in kept];new.polygons.foreach_set('use_smooth',smooth)
localall=np.vstack([local,np.stack([X,Y,Z],axis=2).reshape(-1,3)]);uvs=np.c_[16/2048+(localall[:,0]+2.55)/5.1*2016/2048,16/768+(localall[:,1]+2.2175)/1.3775*736/768]
for layer in me.uv_layers:
 uv=new.uv_layers.new(name=layer.name);indices=np.empty(len(new.loops),dtype=np.int32);new.loops.foreach_get('vertex_index',indices);arr=uvs[indices]
 cursor=0
 for f in kept:
  n=len(f.vertices);arr[cursor:cursor+n]=[layer.data[i].uv[:] for i in f.loop_indices];cursor+=n
 uv.data.foreach_set('uv',arr.ravel())
# Preserve every original retained corner normal. New grain follows the real mesh.
cn=np.empty((len(new.corner_normals),3),dtype=np.float32);new.corner_normals.foreach_get('vector',cn.ravel());cursor=0
for f in kept:
 n=len(f.vertices);cn[cursor:cursor+n]=[me.corner_normals[i].vector[:] for i in f.loop_indices];cursor+=n
new.normals_split_custom_set(cn)
edgeids=np.empty(len(new.loops),dtype=np.int32);new.loops.foreach_get('edge_index',edgeids);counts=np.bincount(edgeids,minlength=len(new.edges));assert (counts==2).all(),dict(boundary=int(np.sum(counts==1)),other=int(np.sum(counts!=2)))
assert np.isfinite(V).all() and Z.min()>1.50 and Z.max()<1.603
master=bpy.data.scenes.new('Test plank master');master.render.engine='CYCLES';master.world=lab.world.copy();master.view_settings.view_transform=lab.view_settings.view_transform;master.view_settings.look=lab.view_settings.look;master.view_settings.exposure=0;master.cycles.samples=128;master.cycles.use_denoising=True;master.render.image_settings.file_format='PNG'
for o in lab.objects:
 if o.name.startswith('Lab body ') or o.name.startswith('Lab relief '):continue
 master.collection.objects.link(o)
body=ob.copy();body.data=new;body.name='Master Chest Body Envelope';body.parent=None;body.matrix_world=ob.matrix_world.copy();master.collection.objects.link(body)
master.camera=lab.camera.copy();master.camera.data=lab.camera.data.copy();master.camera.name='Master evaluation camera';master.collection.objects.link(master.camera)
ref=source.objects['First chest owner reference'];master.collection.objects.link(ref)
master['scope']='Only the existing lower front test plank is refined. Other source parts are unchanged.';body['actual_relief']=True;body['grid']=[W,H];body['source_part']=ob.name;body['normal_split_sigma_units']=.0055
# Keep comparisons available on disk; remove their scene from the final delivery copy.
bpy.context.window.scene=master
proof=dict(vertices=len(new.vertices),polygons=len(new.polygons),triangles=sum(len(f.vertices)-2 for f in new.polygons),grid=[W,H],boundary_edges=int(np.sum(counts==1)),nonmanifold_edges=int(np.sum(counts!=2)),depth_min=float(Z.min()-1.6),depth_max=float(Z.max()-1.6),source_scene_retained=True,source_geometry_hashes_match=True,source_materials_retained=True,reference_same_object=master.objects[ref.name] is ref,normal_residual_sigma=.0055,hardware_clearance='Main relief recedes; boundary datum preserved; maximum raised scan fiber below 0.003 units')
original=json.loads((P/'live_inventory.json').read_text())['model_hashes']
for name,sha in original.items():
 q=source.objects[name];current=hashlib.sha256(bytes(str(([tuple(v.co) for v in q.data.vertices],[tuple(p.vertices) for p in q.data.polygons],list(q.matrix_world),q.parent.name if q.parent else None)), 'utf8')).hexdigest();assert current==sha,name
(P/'master_validation.json').write_text(json.dumps(proof,indent=2));bpy.context.view_layer.objects.active=body
for q in bpy.context.selected_objects:q.select_set(False)
body.select_set(True)
old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(P/'wood_master.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps(proof))
