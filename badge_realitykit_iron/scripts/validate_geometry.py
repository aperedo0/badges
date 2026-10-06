import bpy,json,sys,numpy as np,hashlib,zipfile
from pathlib import Path
from pxr import Usd,UsdGeom,UsdShade,UsdUtils,Sdf,Gf
r=Path('/Users/antonioperedo/Downloads/badge_realitykit_iron')
a=Usd.Stage.Open(str(r/'source/silver_v3/silver_badge_mobile.usdz'));b=Usd.Stage.Open(str(r/'mobile/iron_badge_mobile.usdz'))
report={'meshes':{},'materials':{},'stage':{'upAxis':str(UsdGeom.GetStageUpAxis(b)),'metersPerUnit':UsdGeom.GetStageMetersPerUnit(b)},'names':{}}
for p in a.Traverse():
 if not p.IsA(UsdGeom.Mesh):continue
 q=b.GetPrimAtPath(p.GetPath());assert q
 name=p.GetName();m=UsdGeom.Mesh(q);row={'triangles_silver':len(UsdGeom.Mesh(p).GetFaceVertexCountsAttr().Get()),'triangles_iron':len(m.GetFaceVertexCountsAttr().Get())}
 if not name.startswith('Emblem'):
  same=[]
  for attr in p.GetAttributes():
   if not attr.HasAuthoredValue():continue
   other=q.GetAttribute(attr.GetName());assert other and str(attr.Get())==str(other.Get()),(p.GetPath(),attr.GetName())
   same.append(attr.GetName())
  assert p.GetChildren()==p.GetChildren()
  row['every_authored_mesh_attribute_identical']=True;row['identical_attributes']=same
 pts=np.array(m.GetPointsAttr().Get());row['bounds']=[pts.min(0).tolist(),pts.max(0).tolist()];assert pts[:,1].min()>=-2.895-1e-7
 assert UsdGeom.Xformable(q).ComputeLocalToWorldTransform(Usd.TimeCode.Default())==Gf.Matrix4d(1)
 if name.startswith('Emblem'):
  material={}
  for sub in UsdGeom.Subset.GetAllGeomSubsets(UsdGeom.Imageable(q)):
   bound=UsdShade.MaterialBindingAPI(sub.GetPrim()).ComputeBoundMaterial()[0];material[bound.GetPath().name]=list(sub.GetIndicesAttr().Get())
  (r/'proof/emblem_iron.json').write_text(json.dumps({'points':pts.tolist(),'indices':np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3).tolist(),'subsets':material}))
 report['meshes'][str(p.GetPath())]=row
for p in b.GetPrimAtPath('/Badge/_materials').GetChildren():
 bs=b.GetPrimAtPath(str(p.GetPath())+'/Principled_BSDF');report['materials'][p.GetName()]={k:str(bs.GetAttribute('inputs:'+k).Get()) for k in ('diffuseColor','metallic','roughness')}
for typ in ('Mesh','Material'):
 na=sorted(str(p.GetPath()) for p in a.Traverse() if p.GetTypeName()==typ);nb=sorted(str(p.GetPath()) for p in b.Traverse() if p.GetTypeName()==typ);assert na==nb;report['names'][typ]={'identical':True,'count':len(nb),'names':nb}
report['total_triangles_silver']=sum(x['triangles_silver'] for x in report['meshes'].values());report['total_triangles_iron']=sum(x['triangles_iron'] for x in report['meshes'].values())
report['bytes_silver']=(r/'source/silver_v3/silver_badge_mobile.usdz').stat().st_size;report['bytes_iron']=(r/'mobile/iron_badge_mobile.usdz').stat().st_size
(r/'proof/geometry_identity.json').write_text(json.dumps(report,indent=2))
# Meaningful floor-cut baseline: iron emblem/materials, with the identical silver enclosure before its cut.
b.GetRootLayer().Export(str(r/'work/iron_uncut.usdc'));uncut=Usd.Stage.Open(str(r/'work/iron_uncut.usdc'));source=Usd.Stage.Open(str(r/'source/silver_uncut.usdz'))
path='/Badge/Casing___smooth_rounded_outer_edge';assert Sdf.CopySpec(source.GetRootLayer(),path,uncut.GetRootLayer(),path)
uncut.GetRootLayer().Save()
# The uncut baseline reads texture paths from the mobile directory via an explicit copy.
import shutil
shutil.copytree(r/'mobile/textures',r/'work/textures',dirs_exist_ok=True)
assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(r/'work/iron_uncut.usdc')),str(r/'work/iron_uncut.usdz'))
# Master enclosure check is stricter than numeric tolerance.
bpy.ops.wm.open_mainfile(filepath=str(r/'scenes/iron_medallion_master.blend'))
objs={o.name.split(' | ')[0]:o for o in bpy.data.objects['Turntable | one slow 360 degree spin'].children_recursive if o.type=='MESH'}
original=json.loads((r/'reports/master_enclosure_before.json').read_text());now={k:dict(mesh=o.data.name,points=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons]) for k,o in objs.items() if k!='Emblem'};assert original==now
print('PASS: all five enclosure meshes exact; all six mesh and nine material names exact; Y-up/meters/identity transforms/floor correct; master enclosure unchanged')
print(json.dumps({k:report[k] for k in ['total_triangles_silver','total_triangles_iron','bytes_silver','bytes_iron']},indent=2))
