"""Package the native Blender shield with physical brushed metal materials."""
from pathlib import Path
import json,subprocess,shutil,hashlib
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf,Gf,Vt
ROOT=Path(__file__).resolve().parent;TEMP=Path('/tmp/crimson_shield_20261019');PKG=TEMP/'package'
PKG.mkdir(exist_ok=True);shutil.copytree(ROOT/'textures',PKG/'textures',dirs_exist_ok=True)
path=PKG/'shield.usdc';stage=Usd.Stage.CreateNew(str(path));root=UsdGeom.Xform.Define(stage,'/CrimsonShield');stage.SetDefaultPrim(root.GetPrim())
UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.y);UsdGeom.SetStageMetersPerUnit(stage,1.)
palette=json.loads((ROOT/'palette.json').read_text());materials={}
for role,(color,metal,rough) in palette.items():
    name='CrimsonShield_BrushedField' if role=='field' else role
    base='/CrimsonShield/Materials/'+name;mat=UsdShade.Material.Define(stage,base);surface=UsdShade.Shader.Define(stage,base+'/Surface');surface.CreateIdAttr('UsdPreviewSurface')
    surface.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(metal);surface.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(rough)
    surface.CreateInput('opacity',Sdf.ValueTypeNames.Float).Set(1.);surface.CreateInput('ior',Sdf.ValueTypeNames.Float).Set(1.76 if role=='gem' else 1.46)
    if role in ['red','gem']:
        surface.CreateInput('clearcoat',Sdf.ValueTypeNames.Float).Set(.18 if role=='red' else .65);surface.CreateInput('clearcoatRoughness',Sdf.ValueTypeNames.Float).Set(.24 if role=='red' else .13)
    surface.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(surface.ConnectableAPI(),'surface')
    reader=UsdShade.Shader.Define(stage,base+'/UV');reader.CreateIdAttr('UsdPrimvarReader_float2');reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('ShieldUV');reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
    for suffix,param,output,typ in [('color','diffuseColor','rgb',Sdf.ValueTypeNames.Color3f),('roughness','roughness','r',Sdf.ValueTypeNames.Float)]:
        tex=UsdShade.Shader.Define(stage,base+'/'+suffix);tex.CreateIdAttr('UsdUVTexture');tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+role+'_'+suffix+'.png'))
        tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB' if suffix=='color' else 'raw')
        tex.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('repeat');tex.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('repeat')
        tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result');tex.CreateOutput(output,typ)
        surface.CreateInput(param,typ).ConnectToSource(tex.ConnectableAPI(),output)
    materials[role]=mat
arrays=np.load(TEMP/'meshes.npz');manifest=json.loads((TEMP/'meshes.json').read_text());allpoints=[];triangles=0
for role in palette:
    vertices=[];faces=[];normals=[];uvs=[];offset=0
    for item in manifest:
        if item['role']!=role:continue
        key=item['prefix'];v=arrays[key+'_v'];f=arrays[key+'_f']
        if item['name'].startswith('Frame section') or item['name'].startswith('Smooth deep red'):
            front=v[f].mean(axis=1)[:,2]>0
            area_z=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])[:,2]
            assert np.all(area_z[front]>=-1e-10), 'Folded frame or ruby inset faces: '+item['name']
        vertices.append(v);faces.append(f+offset);normals.append(arrays[key+'_n']);uvs.append(arrays[key+'_uv']);offset+=len(v)
    if not vertices:continue
    v=np.vstack(vertices);f=np.vstack(faces);norm=np.vstack(normals);uv=np.vstack(uvs)
    assert np.isfinite(v).all() and np.isfinite(norm).all()
    area=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)
    keep=area>1e-10
    norm=norm.reshape(-1,3,3)[keep].reshape(-1,3);uv=uv.reshape(-1,3,2)[keep].reshape(-1,2);f=f[keep]
    mesh=UsdGeom.Mesh.Define(stage,'/CrimsonShield/Shield_'+role)
    mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(v));mesh.CreateFaceVertexCountsAttr([3]*len(f));mesh.CreateFaceVertexIndicesAttr(f.reshape(-1).tolist())
    mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(norm));mesh.SetNormalsInterpolation('faceVarying')
    UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('ShieldUV',Sdf.ValueTypeNames.TexCoord2fArray,'faceVarying').Set(Vt.Vec2fArray.FromNumpy(uv))
    UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(materials[role]);mesh.CreateExtentAttr([Gf.Vec3f(*map(float,v.min(axis=0))),Gf.Vec3f(*map(float,v.max(axis=0)))])
    triangles+=len(f);allpoints.append(v)
stage.GetRootLayer().Save();out=ROOT/'mobile/crimson_shield_badge_mobile.usdz'
if out.exists():out.unlink()
subprocess.run(['/usr/bin/usdzip',str(out),'shield.usdc']+['textures/'+q.name for q in sorted((PKG/'textures').glob('*.png'))],cwd=PKG,check=True)
for temporary in out.parent.glob('(A Document Being Saved By usdzip*)'):
    if temporary.is_dir():
        try:temporary.rmdir()
        except OSError:pass
v=np.vstack(allpoints);info={'triangles':triangles,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bounds_min':v.min(axis=0).tolist(),'bounds_max':v.max(axis=0).tolist(),'preview_size':1,'preview_lift':0}
assert v[:,1].min()>=-2.45501 and v[:,1].max()<=3.015 and np.abs(v[:,0]).max()<3.35
(ROOT/'model.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info,indent=2))
