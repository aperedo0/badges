import bpy,numpy as np,math,json
from pathlib import Path
from mathutils import Matrix
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab')
F=P/'timber_refinement'/KEY
assert not bpy.data.is_dirty,'Unknown unsaved changes: do not overwrite or switch files'
sc=bpy.data.scenes['Test plank master'];source=bpy.data.scenes['Chest Complete Form Phase 1'];body=sc.objects['Master Chest Body Envelope']
assert len(body.data.vertices)==641121 and not body.modifiers
old=body.data;mesh=old.copy();body.data=mesh
R=np.array(Matrix.Rotation(math.radians(32),3,'Y'))
a=np.empty((len(mesh.vertices),3));mesh.vertices.foreach_get('co',a.ravel())
q=np.c_[a[:,0],a[:,2],-a[:,1]]@R
n=len(source.objects['Chest Body Envelope'].data.vertices)
X,Y=q[n:,0],q[n:,1]
height=np.load(F/'surface.npz')['height'];h,w=height.shape
u=np.clip((X+2.55)/5.1,0,1)*(w-1);v=np.clip(1-(Y+2.2175)/1.3775,0,1)*(h-1)
ix,iy=u.astype(int),v.astype(int);fx,fy=u-ix,v-iy
z=height[iy,ix]*(1-fx)*(1-fy)+height[iy,np.minimum(ix+1,w-1)]*fx*(1-fy)+height[np.minimum(iy+1,h-1),ix]*(1-fx)*fy+height[np.minimum(iy+1,h-1),np.minimum(ix+1,w-1)]*fx*fy
yb,yt=-2.1605000495910645,-.862500011920929
half=2.49114990234375+(2.3499999046325684-2.49114990234375)*(Y-yb)/(yt-yb)
edge=np.minimum.reduce([half-abs(X),Y-yb,yt-Y]);fade=np.clip(edge/.045,0,1);fade=fade*fade*(3-2*fade)
q[n:,2]=np.minimum(1.6+z*fade,1.6)
new=q@R.T;new=np.c_[new[:,0],-new[:,2],new[:,1]]
new[:n]=a[:n]
mesh.vertices.foreach_set('co',new.ravel());mesh.update()
# Retain the old boundary shading, refresh only the actual relief normal region.
keptloops=sum(len(f.vertices) for f in source.objects['Chest Body Envelope'].data.polygons if f.index not in [354,356,357])
norm=np.zeros((len(mesh.loops),3),dtype=np.float32)
old.corner_normals.foreach_get('vector',norm.ravel());norm[keptloops:]=0
mesh.normals_split_custom_set(norm)
mat=bpy.data.materials['Wood Lab H'].copy();mat.name='Wood Lab '+KEY
for role in ['albedo','normal','roughness']:
    im=bpy.data.images.load(str(F/(role+'.png')),check_existing=False)
    im.colorspace_settings.name='sRGB' if role=='albedo' else 'Non-Color';im.pack()
    mat.node_tree.nodes['Single plank '+role].image=im
slots=[i for i,m in enumerate(mesh.materials) if m and m.name.startswith('Wood Lab ')]
assert len(slots)==1
mesh.materials[slots[0]]=mat
edgeids=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('edge_index',edgeids)
counts=np.bincount(edgeids,minlength=len(mesh.edges));assert np.all(counts==2)
assert q[n:,2].max()<=1.600001 and q[n:,2].min()>1.52
assert np.array_equal(new[:n],a[:n])
proof=dict(key=KEY,vertices=len(mesh.vertices),polygons=len(mesh.polygons),watertight=True,original_boundary_vertices_exact=True,max_recession=float(1.6-q[n:,2].min()),front_datum_preserved=True,source_scene_untouched=True,images_packed=True)
(F/'validation.json').write_text(json.dumps(proof,indent=2))
body['timber_refinement']=KEY
body['normal_split_sigma_units']=json.loads((F/'design.json').read_text()).get('normal_split',.0055)
oldpref=bpy.context.preferences.filepaths.save_version
try:
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(F/'master.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=oldpref
print(json.dumps(proof))
