"""Package the inspected Blender sculpture as one app native USDZ."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf,Gf,Vt
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/((R/'candidate.txt').read_text().strip() if (R/'candidate.txt').exists() else 'candidate01');PKG=Path('/tmp/crest_package')/key;PKG.mkdir(parents=True,exist_ok=True)
shutil.copytree(C/'textures',PKG/'textures',dirs_exist_ok=True)
path=PKG/'crest.usdc'
if path.exists():path.unlink()
stage=Usd.Stage.CreateNew(str(path));root=UsdGeom.Xform.Define(stage,'/Crest');stage.SetDefaultPrim(root.GetPrim());UsdGeom.SetStageUpAxis(stage,'Y');UsdGeom.SetStageMetersPerUnit(stage,1.)
mats={}
for role,color in [('surface',(.004,.004,.004)),('star',(.004,.004,.004)),('silver_edge',(.16,.20,.27)),('gold_edge',(.32,.14,.025)),('blue_edge',(.018,.045,.09))]:
 if role=='star' and not (C/'textures/star_color.png').exists():continue
 base='/Crest/Materials/'+role;mat=UsdShade.Material.Define(stage,base);s=UsdShade.Shader.Define(stage,base+'/Surface');s.CreateIdAttr('UsdPreviewSurface')
 for name,value in [('metallic',1.),('roughness',.53 if role=='surface' else .55),('opacity',1.),('ior',1.46)]:s.CreateInput(name,Sdf.ValueTypeNames.Float).Set(value)
 s.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(color);s.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(s.ConnectableAPI(),'surface')
 if role in ['surface','star']:
  reader=UsdShade.Shader.Define(stage,base+'/UV');reader.CreateIdAttr('UsdPrimvarReader_float2');reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('CrestUV');reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
  for suffix,param in [('color','diffuseColor'),('emission','emissiveColor')]:
   tex=UsdShade.Shader.Define(stage,base+'/'+suffix);tex.CreateIdAttr('UsdUVTexture');tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+role+'_'+suffix+'.png'));tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB')
   tex.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('clamp');tex.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp');tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result')
   if suffix=='emission':tex.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set((8,8,8,1))
   tex.CreateOutput('rgb',Sdf.ValueTypeNames.Float3);s.CreateInput(param,Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(),'rgb')
 mats[role]=mat
data=np.load(C/'blender_geometry.npz');groups=json.loads((C/'groups.json').read_text());allpoints=[];total=0
for i,g in enumerate(groups):
 p=data[str(i)+'_points'];t=data[str(i)+'_triangles'];n=data[str(i)+'_normals'].reshape(-1,3);uv=data[str(i)+'_uv'].reshape(-1,2)
 mesh=UsdGeom.Mesh.Define(stage,'/Crest/Relief_'+str(i));mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(p));mesh.CreateFaceVertexCountsAttr([3]*len(t));mesh.CreateFaceVertexIndicesAttr(t.ravel().tolist());mesh.CreateSubdivisionSchemeAttr('none')
 mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(n));mesh.SetNormalsInterpolation('faceVarying');UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('CrestUV',Sdf.ValueTypeNames.TexCoord2fArray,'faceVarying').Set(Vt.Vec2fArray.FromNumpy(uv))
 mesh.CreateExtentAttr([Gf.Vec3f(*map(float,p.min(0))),Gf.Vec3f(*map(float,p.max(0)))]);UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mats[g['role']]);allpoints.append(p);total+=len(t)
stage.GetRootLayer().Save();out=C/'mobile'/(key+'_badge_mobile.usdz')
if out.exists():out.unlink()
subprocess.run(['/usr/bin/usdzip',str(out),'crest.usdc']+['textures/'+p.name for p in sorted((PKG/'textures').glob('*.png'))],cwd=PKG,check=True)
p=np.vstack(allpoints);meta={'triangles':total,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bounds_min':p.min(0).tolist(),'bounds_max':p.max(0).tolist(),'preview_size':1,'preview_lift':0}
assert p[:,1].min()>=-2.45501 and p[:,1].max()<=3.01501 and abs(p[:,0]).max()<3.35
(C/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
