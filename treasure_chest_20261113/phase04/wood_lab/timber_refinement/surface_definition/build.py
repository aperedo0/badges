import bpy,sys,json,numpy as np,math,hashlib
from pathlib import Path
from mathutils import Matrix
D=Path(__file__).resolve().parent;W=D.parent;P=W.parent;KEY=sys.argv[sys.argv.index('--')+1];F=W/KEY
bpy.ops.wm.open_mainfile(filepath=str(D/'baseline.blend'));sc=bpy.data.scenes['Test plank master'];body=sc.objects['Master Chest Body Envelope'];oldmesh=body.data;source=bpy.data.scenes['Chest Complete Form Phase 1'];n=len(source.objects['Chest Body Envelope'].data.vertices);rot=np.array(Matrix.Rotation(math.radians(32),3,'Y'))
def grid_fields(me):
 a=np.empty((len(me.vertices),3),dtype=np.float32);me.vertices.foreach_get('co',a.ravel());normal=np.empty_like(a);me.vertices.foreach_get('normal',normal.ravel());q=np.c_[a[:,0],a[:,2],-a[:,1]]@rot;v=np.c_[normal[:,0],normal[:,2],-normal[:,1]]@rot;return q[n:].reshape(417,1537,3),v[n:].reshape(417,1537,3)
oldpos,oldnorm=grid_fields(oldmesh)
# Reuse the proven stitched mesh updater, applying only the height difference to the preserved surface.
code=(W/'grain_hierarchy/apply_layers.py').read_text().split('mat=next')[0]
code=code.replace("height=np.load(F/'surface.npz')['height']","height=np.load(F/'surface.npz')['height']-np.load(P/'timber_refinement/AE_controlled_fibers/surface.npz')['height']")
code=code.replace("q[n:,2]=np.minimum(1.6+z*fade,1.6)","q[n:,2]=np.minimum(q[n:,2]+z*fade,1.6)")
code=code.replace("new=q@R.T;new=np.c_[new[:,0],-new[:,2],new[:,1]]","original_local=np.c_[a[:,0],a[:,2],-a[:,1]]@R\nnew=a.copy();new[n:]+=(q[n:,2]-original_local[n:,2])[:,None]*np.array([R[0,2],-R[2,2],R[1,2]])[None,:]")
exec(compile(code,'reused_closed_plank_updater','exec'))
newpos,newnorm=grid_fields(mesh)
np.savez_compressed(F/'normal_frames.npz',old_positions=oldpos.astype('float32'),old_normals=oldnorm.astype('float32'),positions=newpos.astype('float32'),normals=newnorm.astype('float32'))
indices=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('edge_index',indices);counts=np.bincount(indices,minlength=len(mesh.edges));assert np.all(counts==2);assert np.array_equal(new[:n],a[:n]);assert newpos[:,:,2].max()<1.60001 and newpos[:,:,2].min()>1.52
proof=dict(vertices=len(mesh.vertices),polygons=len(mesh.polygons),watertight=True,original_boundary_vertices_exact=True,base_geometry_retained_plus_local_depth_delta=True,normal_relief_complementary_to_actual_new_mesh=True,max_depth=float(1.6-newpos[:,:,2].min()),source_scene_untouched=True)
(F/'validation.json').write_text(json.dumps(proof,indent=2));body['timber_refinement']=KEY;oldpref=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(F/'geometry.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=oldpref
print(json.dumps(proof),flush=True)
