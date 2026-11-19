import bpy,numpy as np,math,json,shutil,hashlib
from mathutils import Matrix
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase05/iron_fidelity');A=D/'N_charcoal_scale';C=D/'P_iron_knobs';C.mkdir(exist_ok=True);assert Path(bpy.data.filepath)==A/'master.blend';assert not bpy.app.is_job_running('RENDER');sc=bpy.data.scenes['Test plank master'];rim=sc.objects['Lab Chest Lower Rim'];mat=rim.data.materials[0];R=np.array(Matrix.Rotation(math.radians(32),3,'Y'));names=['Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4'];proof=[]
for name in names:
 o=sc.objects[name];assert not any(o.name in s.objects for s in bpy.data.scenes if s.name=='Chest Complete Form Phase 1');o.data=o.data.copy();me=o.data;co=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',co.ravel());before=hashlib.sha256(co.tobytes()).hexdigest();world=np.array([tuple(o.matrix_world@v.co) for v in me.vertices]);q=np.c_[world[:,0],world[:,2],-world[:,1]]@R
 atlas=me.uv_layers.get('LowerIronAtlas') or me.uv_layers.new(name='LowerIronAtlas');physical=me.uv_layers.get('LowerIronPhysical') or me.uv_layers.new(name='LowerIronPhysical')
 for loop in me.loops:
  x,y,z=q[loop.vertex_index];u=x+2.73;v=y+2.2175;atlas.data[loop.index].uv=(u/18.04,v/.5035);physical.data[loop.index].uv=(u,v)
 me.materials.clear();me.materials.append(mat)
 for face in me.polygons:face.material_index=0
 o['bottom_iron_finish']=True;after=np.empty_like(co);me.vertices.foreach_get('co',after.ravel());assert np.array_equal(co,after);proof.append(dict(object=name,vertices=len(me.vertices),geometry_sha256=before,material=mat.name,uv_scale='Existing rim physical atlas scale, front projection',geometry_unchanged=True))
a=json.loads((A/'design.json').read_text());a.update(source='N_charcoal_scale',iron_knobs=names,knob_geometry_preserved=True);(C/'design.json').write_text(json.dumps(a,indent=2));shutil.copy2(A/'displacement.npz',C/'displacement.npz');(C/'knobs.json').write_text(json.dumps(proof,indent=2));bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);print(json.dumps(proof))
