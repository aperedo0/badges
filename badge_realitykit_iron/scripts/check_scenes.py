import bpy,json,numpy as np
from pathlib import Path
from pxr import Usd,UsdGeom,UsdShade
r=Path('/Users/antonioperedo/Downloads/badge_realitykit_iron');stage=Usd.Stage.Open(str(r/'mobile/iron_badge_mobile.usdz'));report={}
for name in ['iron_badge_mobile_reduced','iron_badge_mobile']:
 bpy.ops.wm.open_mainfile(filepath=str(r/f'scenes/{name}.blend'));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==6
 rows={}
 for o in meshes:
  prim=next(p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh) and p.GetCustomDataByKey('sourceObjectName')==o.name);usd=UsdGeom.Mesh(prim);a=np.array([v.co for v in o.data.vertices],dtype=np.float32);b=np.array(usd.GetPointsAttr().Get(),dtype=np.float32);assert np.array_equal(a,b),(name,o.name,'positions')
  o.data.calc_loop_triangles();assert len(o.data.loop_triangles)==len(usd.GetFaceVertexCountsAttr().Get())
  rows[o.name]={'mesh_name':o.data.name,'points_exactly_equal_to_usdz':True,'triangles':len(o.data.loop_triangles),'identity_world_transform':np.array_equal(np.array(o.matrix_world),np.eye(4))}
  if name=='iron_badge_mobile' and o.name.startswith('Emblem'):
   # All broad polygon corner normals are constant; narrow strip normals follow rule 1.
   norms=np.array([n.vector for n in o.data.corner_normals]);widths=[];deviation=[]
   for p in o.data.polygons:
    vs=[o.data.vertices[i].co for i in p.vertices];width=(vs[1]-vs[0]).cross(vs[2]-vs[0]).length/max((vs[1]-vs[0]).length,(vs[2]-vs[1]).length,(vs[0]-vs[2]).length)
    if width>.02:deviation.append(float(np.abs(norms[list(p.loop_indices)]-norms[p.loop_start]).max()))
   rows[o.name]['broad_triangle_max_corner_normal_variation']=max(deviation);assert max(deviation)<1e-5
 report[name]=rows
normal_connections=[]
for prim in stage.Traverse():
 if prim.IsA(UsdShade.Shader) and prim.GetAttribute('info:id').Get()=='UsdPreviewSurface':
  normal_connections += [str(p) for p in prim.GetAttribute('inputs:normal').GetConnections()] if prim.GetAttribute('inputs:normal') else []
assert not normal_connections
report['normal_map_connections']=normal_connections
(r/'proof/scene_and_normals_validation.json').write_text(json.dumps(report,indent=2));print('PASS: reduced/final scene mesh positions and triangles match USDZ; broad facet corner normals are constant; no exported normal maps.')
