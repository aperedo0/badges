"""Blender-bundled USD authoring, packaging, contract validation and editable master.
Blender --background --factory-startup --python export.py -- <candidate>
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import bpy
from pxr import Usd,UsdGeom,UsdShade,UsdUtils,Sdf,Gf
ROOT=Path(__file__).resolve().parents[1]
arg=sys.argv[sys.argv.index('--')+1]
OUT=ROOT/arg;OUT.mkdir(parents=True,exist_ok=True)
cfg=json.loads((OUT/'settings.json').read_text())
stage=Usd.Stage.CreateNew(str(OUT/'copper_flame.usdc'))
UsdGeom.SetStageUpAxis(stage,'Y');UsdGeom.SetStageMetersPerUnit(stage,1)
root=UsdGeom.Xform.Define(stage,'/CopperFlame');stage.SetDefaultPrim(root.GetPrim())
def material(name,color,rough,textures=None,metal=1.,emission=None):
    mat=UsdShade.Material.Define(stage,'/CopperFlame/Materials/'+name)
    s=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('Surface'));s.CreateIdAttr('UsdPreviewSurface')
    s.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color));s.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(metal)
    s.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(rough)
    if emission:s.CreateInput('emissiveColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*emission))
    s.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(s.ConnectableAPI(),'surface')
    if textures:
        reader=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('UV'));reader.CreateIdAttr('UsdPrimvarReader_float2')
        reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('FlameUV');reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
        for target,file in textures.items():
            tex=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild(target));tex.CreateIdAttr('UsdUVTexture')
            tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+file))
            tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB')
            if target=='emissiveColor':
                scale=cfg.get('emissive_scale',1.)
                tex.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(scale,scale,scale,1))
            tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result')
            for axis in ['S','T']:tex.CreateInput('wrap'+axis,Sdf.ValueTypeNames.Token).Set('clamp')
            tex.CreateOutput('rgb',Sdf.ValueTypeNames.Float3)
            s.CreateInput(target,Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(),'rgb')
    return mat
front=material('CopperFlame_PolishedFront',cfg.get('color',[.61,.255,.115]),cfg.get('roughness',.34),cfg.get('textures'))
back=material('CopperFlame_PolishedBack',[.40,.145,.065],.38)
edge=material('CopperFlame_RolledEdges',[.58,.235,.105],.29)
ids={}
if cfg.get('id'):
    for name,c in zip(['Central','Right','Left'],[[.65,0,0],[0,.65,0],[0,0,.65]]):ids[name]=material('CopperFlame_ID'+name,[0,0,0],1,metal=0,emission=c)
allpoints=[];triangles=0;manifold={}
for name in ['Central','Right','Left']:
    d=np.load(ROOT/'source'/f'{name.lower()}_geometry.npz');p=d['points'];f=d['faces'];n=d['normals'];uv=d['uv'];roles=d['roles']
    allpoints.append(p);triangles+=len(f)
    m=UsdGeom.Mesh.Define(stage,'/CopperFlame/CopperFlame_'+name+'Ribbon')
    m.CreatePointsAttr(p.astype(np.float32).tolist());m.CreateFaceVertexCountsAttr([3]*len(f));m.CreateFaceVertexIndicesAttr(f.ravel().tolist())
    m.CreateSubdivisionSchemeAttr('none');m.CreateDoubleSidedAttr(False);m.CreateNormalsAttr(n.astype(np.float32).tolist());m.SetNormalsInterpolation('vertex')
    m.CreateExtentAttr([Gf.Vec3f(*map(float,p.min(0))),Gf.Vec3f(*map(float,p.max(0)))])
    UsdGeom.PrimvarsAPI(m).CreatePrimvar('FlameUV',Sdf.ValueTypeNames.TexCoord2fArray,'vertex').Set(uv.astype(np.float32).tolist())
    UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(ids.get(name,front))
    if not cfg.get('id'):
        for role,mat in enumerate([front,back,edge]):
            subset=UsdGeom.Subset.Define(stage,m.GetPath().AppendChild('Material_'+str(role)))
            subset.CreateElementTypeAttr('face');subset.CreateFamilyNameAttr('materialBind');subset.CreateIndicesAttr(np.where(roles==role)[0].tolist())
            UsdShade.MaterialBindingAPI.Apply(subset.GetPrim()).Bind(mat)
        UsdGeom.Subset.SetFamilyType(m,'materialBind','partition')
    edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
    manifold[name]=bool(np.all(counts==2));assert manifold[name],name
stage.GetRootLayer().Save()
usdz=OUT/'copper_flame.usdz';assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(OUT/'copper_flame.usdc')),str(usdz))
checker=UsdUtils.ComplianceChecker(arkit=True);checker.CheckCompliance(str(usdz))
compliance=dict(errors=checker.GetErrors(),failed_checks=checker.GetFailedChecks(),warnings=checker.GetWarnings())
points=np.concatenate(allpoints);lo=points.min(0);hi=points.max(0)
assert not compliance['errors'] and not compliance['failed_checks'],compliance
assert lo[1]>=-2.895 and hi[1]<=3.015 and max(abs(lo[0]),abs(hi[0]))<=3.35
report=dict(triangles=triangles,bytes=usdz.stat().st_size,sha256=hashlib.sha256(usdz.read_bytes()).hexdigest(),bounds=[lo.tolist(),hi.tolist()],float_gap=float(lo[1]+2.895),closed_manifold=manifold,compliance=compliance,settings=cfg)
(OUT/'build.json').write_text(json.dumps(report,indent=2)+'\n')
# Packaging localizes texture references. Restore the editable companion's paths.
for prim in stage.Traverse():
    if prim.IsA(UsdShade.Shader):
        file=UsdShade.Shader(prim).GetInput('file')
        if file and file.Get():file.Set(Sdf.AssetPath('textures/'+Path(file.Get().path).name))
stage.GetRootLayer().Save()
if cfg.get('master'):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.wm.usd_import(filepath=str(usdz),import_materials=True,import_cameras=False,import_lights=False,import_textures_mode='IMPORT_PACK')
    for o in list(bpy.data.objects):
        if o.type=='MESH':
            for poly in o.data.polygons:poly.use_smooth=True
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'copper_flame_master.blend'))
print('EXPORTED',json.dumps(report))
