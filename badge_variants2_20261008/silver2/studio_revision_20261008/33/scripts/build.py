import sys,json,math,shutil,hashlib
from pathlib import Path
import numpy as np
import bpy
from pxr import Usd,UsdGeom,UsdShade,UsdUtils,Sdf,Gf,Vt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from geometry import silver_geometry,iron_geometry,MESH_IDS
kind=sys.argv[sys.argv.index('--')+1];tier='Silver2' if kind=='silver2' else 'Iron2';base=ROOT/kind
settings=json.loads((base/'settings.json').read_text())
meshes,metadata=(silver_geometry if kind=='silver2' else iron_geometry)(settings)
allpoints=np.concatenate([m.points for m in meshes.values() if m.points]);lo=allpoints.min(0);hi=allpoints.max(0)
xy=min(6.03/(hi[0]-lo[0]),5.30/(hi[1]-lo[1]));scales=np.array([xy,xy,.65/(hi[2]-lo[2])]);offset=np.array([-(hi[0]+lo[0])/2,-lo[1],-(hi[2]+lo[2])/2])
for m in meshes.values():
    if not m.points:continue
    m.points=((np.array(m.points)+offset)*scales+np.array([0,-2.455,0])).astype(np.float32).tolist()
    n=np.array(m.normals)/scales;n/=np.linalg.norm(n,axis=1,keepdims=True);m.normals=n.astype(np.float32)
metadata['reference_to_world']={'source_bounds':[lo.tolist(),hi.tolist()],'offset':offset.tolist(),'scale':scales.tolist(),'y_shift':-2.455}
roles=['LeafBlades','LeafEdges','Stems','Star','InnerLeaves','UpperLeaves'] if kind=='silver2' else ['PlateLeft','InnerReveal','Border','PlateRight','InnerChannel','InnerLip']
material_roles=['LeafLit','Reveal','StemsLit','StarLit','StarShaded','Back','Outline','Channel','LeafShaded'] if kind=='silver2' else ['PlateLeft','Reveal','Border','PlateRight','PlateEdge','Back','Outline','Channel','Lip']
if kind=='silver2':
    colors=[settings['leaf_color'],[.3,.291,.273],[.34,.33,.31],settings['main_color'],settings['shaded_color'],[.16,.155,.146],[.28,.272,.253],[.10,.098,.092],[.27,.263,.248]]
    rough=[settings.get('leaf_roughness',.40),.40,.40,settings['roughness'],settings.get('shaded_roughness',settings['roughness']),.45,.40,.45,settings.get('leaf_roughness',.40)]
else:
    colors=[settings['plate_color'],[.21,.203,.19],settings['rim_color'],settings['plate_color'],settings['plate_color'],settings['back_color'],settings['outer_color'],[.035,.033,.03],[.19,.183,.17]]
    rough=[settings['plate_roughness'],.40,.40,settings['plate_roughness'],.49,.48,.40,.50,.40]
allpoints=np.concatenate([m.points for m in meshes.values() if m.points]);bounds=[allpoints.min(0).tolist(),allpoints.max(0).tolist()]
height=bounds[1][1]-bounds[0][1]
# Texture PNGs are authored in exact USDZ_UV coordinates before this export.
finish=json.loads((base/'reports/finish_maps.json').read_text())
texture_files={int(k):v for k,v in finish['materials'].items()}
# Fresh stage; shape identifiers deliberately do not trigger app coin-only patches.
usdpath=base/'mobile'/f'{kind}_badge_mobile.usdc';stage=Usd.Stage.CreateNew(str(usdpath));UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.y);UsdGeom.SetStageMetersPerUnit(stage,1)
root=UsdGeom.Xform.Define(stage,'/'+tier);stage.SetDefaultPrim(root.GetPrim());materials={};mat_table=[]
for i,role in enumerate(material_roles):
    name=f'{tier}_{role}_Satin';mat=UsdShade.Material.Define(stage,f'/{tier}/Materials/{name}');shader=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('Surface'));shader.CreateIdAttr('UsdPreviewSurface')
    shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*colors[i]));shader.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(1. if i!=5 else .95);shader.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(rough[i]);shader.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),'surface')
    if i in texture_files:
        reader=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('UV'));reader.CreateIdAttr('UsdPrimvarReader_float2');reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('USDZ_UV');reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
        for target,filename in texture_files[i].items():
            space='sRGB' if target=='diffuseColor' else 'raw'
            tex=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild(target));tex.CreateIdAttr('UsdUVTexture');tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+filename));tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set(space);tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result');tex.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('clamp');tex.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp');tex.CreateOutput('rgb',Sdf.ValueTypeNames.Float3);tex.CreateOutput('r',Sdf.ValueTypeNames.Float)
            if target=='normal':
                tex.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(2,2,2,1));tex.CreateInput('bias',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(-1,-1,-1,0));shader.CreateInput('normal',Sdf.ValueTypeNames.Normal3f)
            shader.GetInput(target).ConnectToSource(tex.ConnectableAPI(),'r' if target=='roughness' else 'rgb')
    materials[i]=mat;mat_table.append({'name':name,'color_linear':colors[i],'metallic':1. if i!=5 else .95,'roughness':rough[i],'textures':texture_files.get(i)})
flatness={};triangles=0
for source,role in zip(MESH_IDS,roles):
    m=meshes[source]
    if not m.faces:continue
    name=f'{tier}_{role}_Satin';mesh=UsdGeom.Mesh.Define(stage,f'/{tier}/{name}');mesh.CreatePointsAttr(m.points);mesh.CreateFaceVertexCountsAttr([3]*len(m.faces));mesh.CreateFaceVertexIndicesAttr(np.array(m.faces).ravel().tolist());mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateNormalsAttr([Gf.Vec3f(*map(float,n)) for n in m.normals]);mesh.SetNormalsInterpolation('faceVarying');mesh.CreateDoubleSidedAttr(False)
    coords=np.array(m.points);mesh.CreateExtentAttr([Gf.Vec3f(*map(float,coords.min(0))),Gf.Vec3f(*map(float,coords.max(0)))]);uv=(coords[np.array(m.faces).ravel(),:2]+3.015)/6.03
    if settings.get('star_uv_islands') and role=='Star':
        from star_atlas import uv_for_plane
        uv=np.tile([.875,.125],(len(m.faces)*3,1))
        for j,region in enumerate(m.regions):
            if region.startswith('star plane'):
                plane=int(region.split()[-1]);tri=coords[np.array(m.faces)[j]]
                uv[j*3:j*3+3]=uv_for_plane(tri,plane,tri)
    if settings.get('plain_leaf_back_uv') and role!='Star':
        for j,material_index in enumerate(m.materials):
            if material_index==4:
                assert m.regions[j].endswith('back')
                uv[j*3:j*3+3]=[.875,.125]
    UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('USDZ_UV',Sdf.ValueTypeNames.TexCoord2fArray,'faceVarying').Set([Gf.Vec2f(*map(float,u)) for u in uv])
    UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(materials[m.materials[0]])
    for index in sorted(set(m.materials)):
        subset=UsdGeom.Subset.Define(stage,mesh.GetPath().AppendChild(f'Material_{index}'));subset.CreateElementTypeAttr('face');subset.CreateFamilyNameAttr('materialBind');subset.CreateIndicesAttr([j for j,k in enumerate(m.materials) if k==index]);UsdShade.MaterialBindingAPI.Apply(subset.GetPrim()).Bind(materials[index])
    UsdGeom.Subset.SetFamilyType(mesh,'materialBind','partition')
    normals=np.asarray(m.normals).reshape(-1,3,3)
    for region in sorted(set(m.regions)):
        if not region.startswith('star plane'):continue
        ns=normals[np.array(m.regions)==region].reshape(-1,3);flatness[region]=float(np.linalg.norm(ns-ns[0],axis=1).max())
    triangles+=len(m.faces)
    (base/'reports'/f'{role}_geometry.json').write_text(json.dumps({'points':m.points,'indices':m.faces,'normals':m.normals.tolist(),'regions':m.regions,'subsets':{'front':[j for j,r in enumerate(m.regions) if r.startswith('star plane')]}}))
stage.GetRootLayer().Save();usdz=base/'mobile'/f'{kind}_badge_mobile.usdz';assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(usdpath)),str(usdz))
# USD compliance checker inside Blender's bundled USD: equivalent ARKit profile.
checker=UsdUtils.ComplianceChecker(arkit=True,skipARKitRootLayerCheck=False);checker.CheckCompliance(str(usdz));compliance={'errors':checker.GetErrors(),'failed_checks':checker.GetFailedChecks(),'warnings':checker.GetWarnings()}
metrics={'tier':tier,'triangles':triangles,'file_bytes':usdz.stat().st_size,'sha256':hashlib.sha256(usdz.read_bytes()).hexdigest(),'bounds':bounds,'height':height,'width':bounds[1][0]-bounds[0][0],'thickness':bounds[1][2]-bounds[0][2],'lowest_y':bounds[0][1],'float_above_floor':bounds[0][1]+2.895,'flat_plane_max_normal_difference':flatness,'metal_normal_maps':finish['evidence']['normal_maps'],'finish_evidence':finish['evidence'],'material_table':mat_table,'metadata':metadata,'compliance':compliance}
(base/'reports/build.json').write_text(json.dumps(metrics,indent=2)+'\n');assert not compliance['errors'] and not compliance['failed_checks'],compliance
# Keep external USD companion texture paths usable after package localization.
for prim in stage.Traverse():
    if prim.IsA(UsdShade.Shader):
        shader=UsdShade.Shader(prim);file=shader.GetInput('file')
        if file and file.Get():file.Set(Sdf.AssetPath('textures/'+Path(file.Get().path).name))
stage.GetRootLayer().Save()
# Artist master, reduced and final scenes are stage copies with final exact mobile meshes.
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'source/silver_master.blend'));scene=bpy.context.scene;scene.frame_set(360);rig=bpy.data.objects['Turntable | one slow 360 degree spin'];rig.animation_data_clear();rig.location=(0,0,0);rig.rotation_euler=(0,0,0);rig.scale=(1,1,1)
for obj in list(rig.children_recursive):bpy.data.objects.remove(obj,do_unlink=True)
before=set(bpy.data.objects);bpy.ops.wm.usd_import(filepath=str(usdz),import_materials=True,import_usd_preview=True,import_cameras=False,import_lights=False,create_world_material=False,import_textures_mode='IMPORT_PACK');new=[o for o in bpy.data.objects if o not in before]
for obj in new:
    if obj.parent is None:obj.matrix_world.identity();obj.parent=rig;obj.matrix_parent_inverse.identity()
bpy.context.preferences.filepaths.save_version=0;scene['shape_standard']='AGENTS.md 2B; Y=-2.455, thickness .65, tier-specific IDs';scene['geometry_source']='Procedurally authored exact reference silhouette; no decimation necessary'
for suffix in ['master','mobile_reduced','mobile']:bpy.ops.wm.save_as_mainfile(filepath=str(base/'scenes'/f'{kind}_badge_{suffix}.blend'))
(base/'scripts').mkdir(exist_ok=True)
for filename in ['render_proof.py','reimport_check.py','measure_smoothness.py']:shutil.copyfile(ROOT/'scripts'/filename,base/'scripts'/filename)
print('BUILT',json.dumps({k:metrics[k] for k in ['tier','triangles','file_bytes','bounds','flat_plane_max_normal_difference','compliance']}))
