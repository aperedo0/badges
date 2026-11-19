import bpy,numpy as np
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/ruby_heart_gem_20261113');sc=bpy.context.scene;ob=sc.objects['Ruby Heart gem'];me=ob.data;script=next(n for n in me.materials[0].node_tree.nodes if n.bl_idname=='ShaderNodeScript');script.update()
for lv in (1,2,3,8):script.inputs['Mip'+str(lv)].default_value=str(R/'optics'/f'studio_linear_mip{lv}.exr')
def update(D):
 v,n,t=D['gem_v'],D['gem_n'],D['gem_t'];conv=lambda a:np.c_[a[:,0],-a[:,2],a[:,1]];me.clear_geometry();me.from_pydata(conv(v).tolist(),[],t.tolist());me.update();me.polygons.foreach_set('use_smooth',[True]*len(t));ids=np.array([l.vertex_index for l in me.loops]);me.normals_split_custom_set(conv(n[ids]).tolist())
for folder in ['baseline','candidate03']:
 update(np.load(R/folder/'geometry.npz'));sc.render.filepath=str(R/folder/'blender_front_calibrated.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'ruby_heart.blend'));print('Rendered both optical parity baseline and real cut with calibrated light map orientation')
