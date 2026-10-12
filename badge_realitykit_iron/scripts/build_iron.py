import bpy,bmesh,json,numpy as np,sys,zipfile
from pathlib import Path
from pxr import Usd,UsdGeom,UsdShade,Sdf,Vt,Gf,Tf,UsdUtils
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r/'scripts'));import badge_mobile_rules as rules
parameters=json.loads((r/'parameters.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(r/'source/silver_master.blend'))
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.frame_set(360)
rig=bpy.data.objects['Turntable | one slow 360 degree spin']
objs={o.name.split(' | ')[0]:o for o in rig.children_recursive if o.type=='MESH'}
# Source casing and all other enclosure meshes are never edited.
source_casing={k:dict(mesh=o.data.name,points=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons]) for k,o in objs.items() if k!='Emblem'}
(r/'reports/master_enclosure_before.json').write_text(json.dumps(source_casing))
palette={
 'Silver | circumferential brushed steel':((.25,.24,.225),1,.325),
 'Outer edge | smooth satin silver':((.245,.235,.22),1,.27),
 'Back and edge | gunmetal':((.055,.052,.048),.95,.32),
 'Silver | polished cut edges':((.30,.285,.26),1,.19),
 'Emblem | satin silver facets':(tuple(parameters['main_color']),1,parameters['roughness']),
 'Emblem | shaded outer facets':(tuple(parameters['shaded_color']),1,parameters.get('shaded_roughness',parameters['roughness'])),
 'Recess | smoked nickel':((.045,.043,.039),1,.27),
 'Inset | finely textured charcoal':(tuple(parameters.get('inset_color',[.009,.010,.011])),.05,.83)}
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
# Reference-traced crystal with seven broad irregular front planes.
outline=parameters['outline'];ridge=parameters['interior'];front=parameters['front_faces']
no=len(outline);nf=len(outline)+len(ridge)
verts=outline+ridge+[(x,y,parameters.get('crystal_back_z',.065)) for x,y,z in outline]
faces=front+[(i,(i+1)%no,nf+(i+1)%no,nf+i) for i in range(no)]+[tuple(range(nf+no-1,nf-1,-1))]
crystal_design=dict(front_planes=len(front),outline=outline,ridge=ridge,
    ridge_vertex_indices=parameters['ridge_vertex_indices'],front_faces=front,
    shaded_front_planes=parameters['shaded_front_planes'],main_front_planes=parameters['main_front_planes'],
    left_front_planes=parameters['main_front_planes'],right_front_planes=parameters['shaded_front_planes'],
    bevel_width=.004,projected_ridge_is_straight=False,side_wall_planes=no)
(r/'reports/crystal_design.json').write_text(json.dumps(crystal_design,indent=2))
obj=objs['Emblem'];old=obj.data;name=old.name
mesh=bpy.data.meshes.new('iron_temp');mesh.from_pydata(verts,[],faces);mesh.update();obj.data=mesh
bpy.data.meshes.remove(old);mesh.name=name
for matname in ['Emblem | satin silver facets','Silver | polished cut edges','Emblem | shaded outer facets']:mesh.materials.append(bpy.data.materials[matname])
for i,p in enumerate(mesh.polygons):p.use_smooth=False;p.material_index=2 if i in parameters['shaded_front_planes'] or len(front)<=i<len(faces)-1 else 0
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
obj.modifiers.clear();bev=obj.modifiers.new('Subpixel edges folded into owner planes','BEVEL');bev.width=.004;bev.segments=1;bev.material=1;bev.affect='EDGES'
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
  deps=bpy.context.evaluated_depsgraph_get();e=obj.evaluated_get(deps);m=e.to_mesh()
  # Blender's bevel miters can warp a broad polygon at a shallow junction.
  # Project broad-face border vertices back onto their original planes; shared
  # vertices satisfy every incident broad-plane equation simultaneously.
  canonical=np.array([p.normal[:] for p in mesh.polygons],dtype=np.float64)
  origins=np.array([mesh.vertices[p.vertices[0]].co[:] for p in mesh.polygons],dtype=np.float64)
  constraints={};maximum_before=0.
  for poly in m.polygons:
   if poly.material_index==1:continue
   candidates=np.flatnonzero(canonical@np.array(poly.normal)>.999)
   assert len(candidates),(poly.index,'no original plane')
   dist=np.abs(np.einsum('ij,ij->i',canonical[candidates],np.array(poly.center)-origins[candidates]))
   owner=int(candidates[np.argmin(dist)]);assert dist.min()<.002
   for vi in poly.vertices:
    constraints.setdefault(vi,set()).add(owner)
    maximum_before=max(maximum_before,float(abs(canonical[owner]@(np.array(m.vertices[vi].co)-origins[owner]))))
  maximum_move=0.
  for vi,owners in constraints.items():
   ids=list(owners);matrix=canonical[ids];v=np.array(m.vertices[vi].co,dtype=float)
   offsets=np.einsum('ij,ij->i',matrix,origins[ids]);error=matrix@v-offsets
   corrected=v-matrix.T@np.linalg.lstsq(matrix@matrix.T,error,rcond=None)[0]
   maximum_move=max(maximum_move,float(np.linalg.norm(corrected-v)));m.vertices[vi].co=corrected.tolist()
  m.update();m.calc_loop_triangles()
  (r/'reports/bevel_planarity_correction.json').write_text(json.dumps({'maximum_before_deviation':maximum_before,'maximum_vertex_correction':maximum_move},indent=2))
  all_tris=list(m.loop_triangles)
  tris=[t for t in all_tris if (m.vertices[t.vertices[1]].co-m.vertices[t.vertices[0]].co).cross(m.vertices[t.vertices[2]].co-m.vertices[t.vertices[0]].co).length>1e-12]
  (r/'reports/zero_area_cleanup.json').write_text(json.dumps({'zero_area_bevel_triangles_removed':len(all_tris)-len(tris)},indent=2))
  indices=[v for t in tris for v in t.vertices]
  target=UsdGeom.Mesh(prim);target.GetPointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*(e.matrix_world@v.co)) for v in m.vertices]));target.GetFaceVertexCountsAttr().Set([3]*len(tris));target.GetFaceVertexIndicesAttr().Set(indices)
  # One canonical float32 normal per original polygon, repeated verbatim for all
  # its triangulation. Do not recalculate individual triangle shading normals.
  canonical=np.array([p.normal[:] for p in mesh.polygons],dtype=np.float32)
  centers=np.array([p.center[:] for p in mesh.polygons])
  tri_planes=[];normals=[]
  for t in tris:
   poly=m.polygons[t.polygon_index]
   if poly.material_index==1:
    owner=-1;normal=np.array(poly.normal,dtype=np.float32)
   else:
    scores=canonical@np.array(poly.normal)
    candidates=np.flatnonzero(scores>.999)
    assert len(candidates),(poly.index,scores.max())
    distance=np.abs(np.einsum('ij,ij->i',canonical[candidates],np.array(poly.center)-centers[candidates]))
    owner=int(candidates[np.argmin(distance)]);assert distance.min()<1e-5,dict(poly=poly.index,material=poly.material_index,center=list(poly.center),normal=list(poly.normal),candidates=candidates.tolist(),distance=distance.tolist(),points=[list(m.vertices[i].co) for i in poly.vertices])
    normal=canonical[owner]
   tri_planes.append(owner);normals.extend([Gf.Vec3f(*map(float,normal))]*3)
  (r/'reports/crystal_triangle_planes.json').write_text(json.dumps({'triangle_original_plane':tri_planes,'canonical_normals':canonical.tolist()},indent=2))
  target.GetNormalsAttr().Set(Vt.Vec3fArray(normals));target.SetNormalsInterpolation('faceVarying')
  pts=np.array(target.GetPointsAttr().Get());target.GetExtentAttr().Set([Gf.Vec3f(*pts.min(0).tolist()),Gf.Vec3f(*pts.max(0).tolist())])
  for pv in UsdGeom.PrimvarsAPI(prim).GetPrimvars():
   if str(pv.GetTypeName())=='texCoord2f[]':
    if pv.IsIndexed():pv.BlockIndices()
    pv.Set(Vt.Vec2fArray([Gf.Vec2f((float(m.vertices[i].co.x)+1.4)/2.8,(float(m.vertices[i].co.y)+2.15)/4.3) for i in indices]))
  for subset in UsdGeom.Subset.GetAllGeomSubsets(UsdGeom.Imageable(prim)):
   bound=UsdShade.MaterialBindingAPI(subset.GetPrim()).ComputeBoundMaterial()[0].GetPath().name
   mi=next(i for i,mat in enumerate(mesh.materials) if bound.startswith(Tf.MakeValidIdentifier(mat.name)))
   subset.GetIndicesAttr().Set([i for i,t in enumerate(tris) if m.polygons[t.polygon_index].material_index==mi])
  print('NEW CRYSTAL',len(tris),'triangles',pts.min(0),pts.max(0));e.to_mesh_clear()
stage.GetRootLayer().Save()
assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(r/'work/iron_baked.usdc')),str(r/'work/iron_baked.usdz'))
# Noise-free constant maps, preserving shipped texture names and dimensions.
for stem,color,size in [('USDZ_Casing_base_color',(.25,.24,.225),512),('USDZ_Casing_roughness',(.325,.325,.325),512),('USDZ_Casing_normal',(.5,.5,1),512),('USDZ_Emblem_normal',(.5,.5,1),1024),('USDZ_Inset_base_color',(.009,.010,.011),512),('USDZ_Inset_normal',(.5,.5,1),1024)]:
 a=np.array(color)
 if stem.endswith('base_color'):a=np.where(a<=.0031308,12.92*a,1.055*a**(1/2.4)-.055)
 rgb=np.broadcast_to(np.rint(a*255).astype(np.uint8),(size,size,3)).copy();(r/'source/bakes'/ (stem+'.png')).write_bytes(rules.png_bytes(rgb))
print('IRON MASTER BUILT; ENCLOSURE UNTOUCHED')

uv_geometry={}
for p in silver.Traverse():
 if not p.IsA(UsdGeom.Mesh):continue
 m=UsdGeom.Mesh(p);pv=UsdGeom.PrimvarsAPI(p).GetPrimvar('USDZ_UV')
 if not pv:continue
 uv_geometry[p.GetParent().GetName()]={'points':np.array(m.GetPointsAttr().Get()).tolist(),'indices':np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3).tolist(),'uv':np.array(pv.ComputeFlattened()).reshape(-1,3,2).tolist()}
(r/'work/uv_geometry.json').write_text(json.dumps(uv_geometry))
