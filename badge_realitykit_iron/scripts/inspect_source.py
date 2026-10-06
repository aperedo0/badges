import bpy,json,numpy as np
from pathlib import Path
from pxr import Usd,UsdGeom,UsdShade
r=Path('/Users/antonioperedo/Downloads/badge_realitykit_iron')
bpy.ops.wm.open_mainfile(filepath=str(r/'source/silver_master.blend'))
bpy.context.scene.frame_set(360)
d=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects['Turntable | one slow 360 degree spin'].children_recursive:
 if o.type!='MESH':continue
 e=o.evaluated_get(d);m=e.to_mesh();p=np.array([e.matrix_world@v.co for v in m.vertices]);m.calc_loop_triangles()
 print('OBJ',o.name,'DATA',o.data.name,'bounds',p.min(0),p.max(0),'tri',len(m.loop_triangles),'mods',[(x.name,x.type,getattr(x,'width',None),getattr(x,'material',None)) for x in o.modifiers]);e.to_mesh_clear()
 for mat in o.data.materials:
  bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');print('MAT',mat.name,[(k,str(bs.inputs[k].default_value),bs.inputs[k].is_linked) for k in ['Base Color','Metallic','Roughness','Anisotropic IOR Level'] if bs.inputs.get(k)])
s=Usd.Stage.Open(str(r/'source/silver_v3/silver_badge_mobile.usdz'))
for p in s.Traverse():
 if p.IsA(UsdGeom.Mesh):
  m=UsdGeom.Mesh(p);a=np.array(m.GetPointsAttr().Get());print('USD',str(p.GetPath()),'bounds',a.min(0),a.max(0),'tri',len(m.GetFaceVertexCountsAttr().Get()))
print('CAMERA',bpy.context.scene.camera.name,tuple(bpy.context.scene.camera.location),bpy.context.scene.camera.data.lens)
