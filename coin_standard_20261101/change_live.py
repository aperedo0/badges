from pathlib import Path
import bpy,numpy as np,sys,json
R=Path('/Users/antonioperedo/Desktop/badges/coin_standard_20261101');sys.path.insert(0,str(R))
assert json.loads((R/'draft_design.json').read_text()).get('active_candidate','candidate01')=='candidate01', 'Use build_candidate.py for the active draft.'
from geometry import points_after,normals_after
scene=bpy.context.scene
assert not scene.get('sprout_dimensions_changed'), 'Import the original complete coin again before a new adjustment.'
scene['sprout_dimensions_changed']=True
scene.name='Emerald Sprout rim and depth 65 percent';data={}
for ob in scene.objects:
 if ob.type!='MESH':continue
 me=ob.data;p=np.array([v.co[:] for v in me.vertices],float);old_normals=np.array([n.vector[:] for n in me.corner_normals]);loop_points=p[[l.vertex_index for l in me.loops]];new_normals=normals_after(loop_points,old_normals)
 target=points_after(p)
 for v,q in zip(me.vertices,target):v.co=q
 me.update();me.normals_split_custom_set(new_normals.tolist());me.update()
 data[ob.name]=np.array([v.co[:] for v in me.vertices],np.float32)
np.savez_compressed(R/'candidate01/inspected_points.npz',**data)
bpy.data.libraries.write(str(R/'candidate01/source/emerald_sprout.blend'),{scene},compress=True)
print('Only Emerald Sprout changed. Rim band and full coin depth are 65 percent of the original.')
