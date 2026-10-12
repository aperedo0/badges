"""One PreviewSurface USDZ, independent of any app changes."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import bpy
from pxr import Usd,UsdGeom,UsdShade,UsdUtils,Sdf,Gf
ROOT=Path(__file__).resolve().parents[1]
kind,folder=sys.argv[sys.argv.index('--')+1:sys.argv.index('--')+3]
BASE=ROOT/kind;OUT=BASE/folder;cfg=json.loads((OUT/'settings.json').read_text());mapping=json.loads((BASE/'source/mapping.json').read_text())
PREFIX='GoldCrown' if kind=='gold' else 'DiamondCrystal'
stage=Usd.Stage.CreateNew(str(OUT/'badge.usdc'));UsdGeom.SetStageUpAxis(stage,'Y');UsdGeom.SetStageMetersPerUnit(stage,1)
root=UsdGeom.Xform.Define(stage,'/'+PREFIX);stage.SetDefaultPrim(root.GetPrim())
def material(name,color,rough,textures=None,emission=None,metal=1.):
    mat=UsdShade.Material.Define(stage,f'/{PREFIX}/Materials/{PREFIX}_{name}')
    shader=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('Surface'));shader.CreateIdAttr('UsdPreviewSurface')
    shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*color));shader.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(metal)
    shader.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(rough)
    if emission:shader.CreateInput('emissiveColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*emission))
    shader.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),'surface')
    if textures:
        reader=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('UV'));reader.CreateIdAttr('UsdPrimvarReader_float2');reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('BadgeUV');reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
        for target,file in textures.items():
            tex=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild(target));tex.CreateIdAttr('UsdUVTexture')
            tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+file));tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB')
            if target=='emissiveColor':
                scale=cfg.get('emissive_scale',3.);tex.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(scale,scale,scale,1))
            tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result')
            for axis in ['S','T']:tex.CreateInput('wrap'+axis,Sdf.ValueTypeNames.Token).Set('clamp')
            tex.CreateOutput('rgb',Sdf.ValueTypeNames.Float3);shader.CreateInput(target,Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(),'rgb')
    return mat
color=cfg.get('color',[.65,.40,.04] if kind=='gold' else [.055,.20,.50])
front=material('Front',color,cfg.get('roughness',.38),cfg.get('textures'))
back=material('Back',[.36,.22,.018] if kind=='gold' else [.018,.075,.23],.40)
edge=material('Edges',[.60,.36,.025] if kind=='gold' else [.06,.24,.53],.32)
points=[];count=0;manifold={}
for record in mapping['meshes']:
    name=record['name'];d=np.load(BASE/'source'/f'{name}.npz');p=d['points'];f=d['faces'];n=d['normals'];uv=d['uv'];roles=d['roles']
    points.append(p);count+=len(f)
    mesh=UsdGeom.Mesh.Define(stage,f'/{PREFIX}/{name}');mesh.CreatePointsAttr(p.astype(np.float32).tolist());mesh.CreateFaceVertexCountsAttr([3]*len(f));mesh.CreateFaceVertexIndicesAttr(f.ravel().tolist())
    mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(False);mesh.CreateNormalsAttr(n.reshape(-1,3).astype(np.float32).tolist());mesh.SetNormalsInterpolation('faceVarying')
    mesh.CreateExtentAttr([Gf.Vec3f(*map(float,p.min(0))),Gf.Vec3f(*map(float,p.max(0)))])
    face_uv=d['face_uv'] if 'face_uv' in d else uv[f]
    UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('BadgeUV',Sdf.ValueTypeNames.TexCoord2fArray,'faceVarying').Set(face_uv.reshape(-1,2).astype(np.float32).tolist())
    UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(front)
    for role,mat in enumerate([front,back,edge]):
        if not (roles==role).any():continue
        sub=UsdGeom.Subset.Define(stage,mesh.GetPath().AppendChild('Material_'+str(role)));sub.CreateElementTypeAttr('face');sub.CreateFamilyNameAttr('materialBind');sub.CreateIndicesAttr(np.where(roles==role)[0].tolist());UsdShade.MaterialBindingAPI.Apply(sub.GetPrim()).Bind(mat)
    UsdGeom.Subset.SetFamilyType(mesh,'materialBind','partition')
    e=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,c=np.unique(e,axis=0,return_counts=True)
    manifold[name]=bool((c==2).all());assert manifold[name],(name,int((c!=2).sum()))
stage.GetRootLayer().Save();package=OUT/'badge.usdz';assert UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath(str(OUT/'badge.usdc')),str(package))
checker=UsdUtils.ComplianceChecker(arkit=True);checker.CheckCompliance(str(package));compliance=dict(errors=checker.GetErrors(),failed_checks=checker.GetFailedChecks(),warnings=checker.GetWarnings());assert not compliance['errors'] and not compliance['failed_checks'],compliance
p=np.concatenate(points);lo,hi=p.min(0),p.max(0);assert lo[1]>=-2.895 and hi[1]<=3.015 and max(abs(lo[0]),abs(hi[0]))<=3.35
report=dict(kind=kind,triangles=count,bytes=package.stat().st_size,bounds=[lo.tolist(),hi.tolist()],float_gap=float(lo[1]+2.895),closed_meshes=manifold,sha256=hashlib.sha256(package.read_bytes()).hexdigest(),compliance=compliance,settings=cfg)
(OUT/'build.json').write_text(json.dumps(report,indent=2)+'\n')
for prim in stage.Traverse():
    if prim.IsA(UsdShade.Shader):
        file=UsdShade.Shader(prim).GetInput('file')
        if file and file.Get():file.Set(Sdf.AssetPath('textures/'+Path(file.Get().path).name))
stage.GetRootLayer().Save()
if cfg.get('master'):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.wm.usd_import(filepath=str(package),import_materials=True,import_cameras=False,import_lights=False,import_textures_mode='IMPORT_PACK')
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'{kind}_badge_master.blend'))
print('EXPORTED',json.dumps(report))
