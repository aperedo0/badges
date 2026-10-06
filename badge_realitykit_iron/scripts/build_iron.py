import bpy,bmesh,json,numpy as np,sys,zipfile
from pathlib import Path
from pxr import Usd,UsdGeom,UsdShade,Sdf,Vt,Gf,Tf,UsdUtils
r=Path('/Users/antonioperedo/Downloads/badge_realitykit_iron')
sys.path.insert(0,str(r/'scripts'));import badge_mobile_rules as rules
bpy.ops.wm.open_mainfile(filepath=str(r/'source/silver_master.blend'))
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.frame_set(360)
rig=bpy.data.objects['Turntable | one slow 360 degree spin']
objs={o.name.split(' | ')[0]:o for o in rig.children_recursive if o.type=='MESH'}
# Source casing and all other enclosure meshes are never edited.
source_casing={k:dict(mesh=o.data.name,points=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons]) for k,o in objs.items() if k!='Emblem'}
(r/'reports/master_enclosure_before.json').write_text(json.dumps(source_casing))
palette={
 'Silver | circumferential brushed steel':((.15,.14,.125),1,.325),
 'Outer edge | smooth satin silver':((.105,.102,.094),1,.27),
 'Back and edge | gunmetal':((.055,.052,.048),.95,.32),
 'Silver | polished cut edges':((.30,.285,.26),1,.19),
 'Emblem | satin silver facets':((.36,.34,.30),1,.29),
 'Emblem | shaded outer facets':((.19,.18,.165),1,.29),
 'Recess | smoked nickel':((.045,.043,.039),1,.27),
 'Inset | finely textured charcoal':((.009,.010,.011),.05,.83)}
for name,(color,metal,rough) in palette.items():
 mat=bpy.data.materials[name];mat.node_tree.nodes.clear()
 bs=mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled');out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
 bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 mat.diffuse_color=(*color,1)
 if name.startswith('Silver | circumferential'):
  sock=next((x for x in bs.inputs if x.name in ('Anisotropic','Anisotropic IOR Level')),None)
  if sock:sock.default_value=.48
  tangent=mat.node_tree.nodes.new('ShaderNodeTangent');tangent.direction_type='UV_MAP';tangent.uv_map=objs['Casing'].data.uv_layers.active.name
  mat.node_tree.links.new(tangent.outputs['Tangent'],bs.inputs['Tangent'])
# An irregular elongated crystal, with a tilted ridge and ten broad planes.
outline=[(.10,2.017,.47),(.72,1.63,.40),(1.088,.12,.35),(.51,-1.54,.33),(-.04,-2.047,.38),(-.53,-1.72,.32),(-1.088,.32,.37),(-.56,1.22,.37)]
verts=outline+[(.37,.94,.86),(.025,-.70,.97712)]+[(x,y,.12) for x,y,z in outline]+[(0,0,.12)]
front=[(0,1,8),(1,2,8),(2,9,8),(2,3,9),(3,4,9),(4,5,9),(5,6,9),(6,8,9),(6,7,8),(7,0,8)]
faces=front+[(i,(i+1)%8,10+(i+1)%8,10+i) for i in range(8)]+[(18,10+(i+1)%8,10+i) for i in range(8)]
obj=objs['Emblem'];old=obj.data;name=old.name
mesh=bpy.data.meshes.new('iron_temp');mesh.from_pydata(verts,[],faces);mesh.update();obj.data=mesh
bpy.data.meshes.remove(old);mesh.name=name
for matname in ['Emblem | satin silver facets','Silver | polished cut edges','Emblem | shaded outer facets']:mesh.materials.append(bpy.data.materials[matname])
for i,p in enumerate(mesh.polygons):p.use_smooth=False;p.material_index=2 if i in [1,2,3,4,10,11,12,13,14,15,16,17] else 0
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
obj.modifiers.clear();bev=obj.modifiers.new('Fine glints along facet edges','BEVEL');bev.width=.004;bev.segments=1;bev.material=1;bev.affect='EDGES'
# Inset bevel receives its existing material explicitly; no extra highlight slot.
for o in objs.values():
 for mod in o.modifiers:
  if mod.type=='BEVEL' and mod.material<0:mod.material=0
obj.location=(0,0,0);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1);obj.matrix_parent_inverse.identity()
# Copy the reference locally. All image outputs point only inside the new folder.
for img in bpy.data.images:
 if img.packed_file:continue
 if img.filepath:img.filepath=str(r/'source'/Path(img.filepath).name)
bpy.ops.wm.save_as_mainfile(filepath=str(r/'scenes/iron_medallion_master.blend'),check_existing=False)
assert source_casing=={k:dict(mesh=o.data.name,points=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons]) for k,o in objs.items() if k!='Emblem'}
(r/'reports/material_palette.json').write_text(json.dumps(palette,indent=2))
# Build a baked-geometry input: shipped v3 enclosure arrays + evaluated new emblem.
with zipfile.ZipFile(r/'source/silver_uncut.usdz') as z:
 for n in z.namelist():
  if n.endswith('.png'):
   p=r/'work'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
oldstage=Usd.Stage.Open(str(r/'source/silver_uncut.usdz'))
oldstage.GetRootLayer().Export(str(r/'work/iron_baked.usdc'))
stage=Usd.Stage.Open(str(r/'work/iron_baked.usdc'))
silver=Usd.Stage.Open(str(r/'source/silver_v3/silver_badge_mobile.usdz'))
for prim in stage.Traverse():
 if not prim.IsA(UsdGeom.Mesh):continue
 short=next(k for k in objs if prim.GetParent().GetName()==Tf.MakeValidIdentifier(objs[k].name))
 if short!='Emblem':
  source=next(p for p in silver.Traverse() if p.IsA(UsdGeom.Mesh) and p.GetParent().GetName().startswith(Tf.MakeValidIdentifier(short)+'___'))
  target=UsdGeom.Mesh(prim);src=UsdGeom.Mesh(source)
  for key in ['points','faceVertexCounts','faceVertexIndices','normals','extent']:
   target.GetPrim().GetAttribute(key).Set(src.GetPrim().GetAttribute(key).Get())
  for pv in UsdGeom.PrimvarsAPI(source).GetPrimvars():
   if str(pv.GetTypeName())=='texCoord2f[]':
    new=UsdGeom.PrimvarsAPI(prim).CreatePrimvar(pv.GetPrimvarName(),pv.GetTypeName(),pv.GetInterpolation());new.BlockIndices();new.Set(pv.ComputeFlattened())
  # Geometry subset membership comes from shipped silver, material paths remain baked-source names.
  for subset in UsdGeom.Subset.GetAllGeomSubsets(UsdGeom.Imageable(prim)):
   srcsubset=silver.GetPrimAtPath(str(source.GetPath())+'/'+subset.GetPrim().GetName())
   if srcsubset:subset.GetIndicesAttr().Set(UsdGeom.Subset(srcsubset).GetIndicesAttr().Get())
 else:
  deps=bpy.context.evaluated_depsgraph_get();e=obj.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles()
  tris=list(m.loop_triangles);indices=[v for t in tris for v in t.vertices]
  target=UsdGeom.Mesh(prim);target.GetPointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*(e.matrix_world@v.co)) for v in m.vertices]));target.GetFaceVertexCountsAttr().Set([3]*len(tris));target.GetFaceVertexIndicesAttr().Set(indices)
  target.GetNormalsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*t.normal) for t in tris for li in t.loops]));target.SetNormalsInterpolation('faceVarying')
  pts=np.array(target.GetPointsAttr().Get());target.GetExtentAttr().Set([Gf.Vec3f(*pts.min(0).tolist()),Gf.Vec3f(*pts.max(0).tolist())])
  for pv in UsdGeom.PrimvarsAPI(prim).GetPrimvars():
   if str(pv.GetTypeName())=='texCoord2f[]':
    if pv.IsIndexed():pv.BlockIndices()
    pv.Set(Vt.Vec2fArray([Gf.Vec2f(0,0)]*len(indices)))
  for subset in UsdGeom.Subset.GetAllGeomSubsets(UsdGeom.Imageable(prim)):
   bound=UsdShade.MaterialBindingAPI(subset.GetPrim()).ComputeBoundMaterial()[0].GetPath().name
   mi=next(i for i,mat in enumerate(mesh.materials) if bound.startswith(Tf.MakeValidIdentifier(mat.name)))
   subset.GetIndicesAttr().Set([i for i,t in enumerate(tris) if m.polygons[t.polygon_index].material_index==mi])
  print('NEW CRYSTAL',len(tris),'triangles',pts.min(0),pts.max(0));e.to_mesh_clear()
stage.GetRootLayer().Save()
assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(r/'work/iron_baked.usdc')),str(r/'work/iron_baked.usdz'))
# Noise-free constant maps, preserving shipped texture names and dimensions.
for stem,color,size in [('USDZ_Casing_base_color',(.15,.14,.125),512),('USDZ_Casing_roughness',(.325,.325,.325),512),('USDZ_Casing_normal',(.5,.5,1),512),('USDZ_Emblem_normal',(.5,.5,1),1024),('USDZ_Inset_base_color',(.009,.010,.011),512),('USDZ_Inset_normal',(.5,.5,1),1024)]:
 a=np.array(color)
 if stem.endswith('base_color'):a=np.where(a<=.0031308,12.92*a,1.055*a**(1/2.4)-.055)
 rgb=np.broadcast_to(np.rint(a*255).astype(np.uint8),(size,size,3)).copy();(r/'source/bakes'/ (stem+'.png')).write_bytes(rules.png_bytes(rgb))
print('IRON MASTER BUILT; ENCLOSURE UNTOUCHED')
