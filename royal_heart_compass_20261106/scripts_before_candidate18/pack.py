"""Export the inspected geometry, keeping studio objects out of the asset."""
from pathlib import Path
import sys,json,tempfile,subprocess,shutil,hashlib
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf,Vt,Gf
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];C=ROOT/key/'candidate17';D=np.load(C/'blender_geometry.npz');groups=json.loads((C/'groups.json').read_text());spec=json.loads((C/'materials.json').read_text())
with tempfile.TemporaryDirectory(prefix='royal_badge_',dir='/tmp') as temp:
 pkg=Path(temp);stage=Usd.Stage.CreateNew(str(pkg/'badge.usdc'));root=UsdGeom.Xform.Define(stage,'/Badge');stage.SetDefaultPrim(root.GetPrim());UsdGeom.SetStageUpAxis(stage,'Y');UsdGeom.SetStageMetersPerUnit(stage,1.)
 mats={}
 for role in sorted(set(g['mat'] for g in groups)):
  sp=spec[role];base='/Badge/Materials/'+role;mat=UsdShade.Material.Define(stage,base);sh=UsdShade.Shader.Define(stage,base+'/Surface');sh.CreateIdAttr('UsdPreviewSurface')
  for name,val in [('metallic',sp['metallic']),('roughness',sp['roughness']),('ior',1.1 if role.endswith('_velvet') else sp.get('ior',1.46)),('opacity',1.)]:sh.CreateInput(name,Sdf.ValueTypeNames.Float).Set(val)
  sh.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(tuple(sp['color']));sh.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(),'surface');mats[role]=mat
  filename='gold_color.png' if role=='gold' and (C/'textures/gold_color.png').exists() else 'chart_color.png' if role=='navy' else 'velvet_fold_color.png' if role.endswith('_fold_velvet') and (C/'textures/velvet_fold_color.png').exists() else 'velvet_color.png' if role.endswith('_velvet') else ''
  if filename and (C/'textures'/filename).exists():
   (pkg/'textures').mkdir(exist_ok=True);shutil.copy2(C/'textures'/filename,pkg/'textures'/filename)
   rd=UsdShade.Shader.Define(stage,base+'/UV');rd.CreateIdAttr('UsdPrimvarReader_float2');rd.CreateInput('varname',Sdf.ValueTypeNames.String).Set('BadgeUV');rd.CreateOutput('result',Sdf.ValueTypeNames.Float2)
   tex=UsdShade.Shader.Define(stage,base+'/Chart');tex.CreateIdAttr('UsdUVTexture');tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+filename));tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB');tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(rd.ConnectableAPI(),'result');tex.CreateOutput('rgb',Sdf.ValueTypeNames.Float3);sh.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(),'rgb')
  if role.endswith('_fold_velvet') and (C/'textures/velvet_occlusion.png').exists():
   (pkg/'textures').mkdir(exist_ok=True);shutil.copy2(C/'textures/velvet_occlusion.png',pkg/'textures/velvet_occlusion.png')
   rd=UsdShade.Shader.Get(stage,base+'/UV')
   tex=UsdShade.Shader.Define(stage,base+'/Occlusion');tex.CreateIdAttr('UsdUVTexture');tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/velvet_occlusion.png'));tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('raw');tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(rd.ConnectableAPI(),'result');tex.CreateOutput('r',Sdf.ValueTypeNames.Float);sh.CreateInput('occlusion',Sdf.ValueTypeNames.Float).ConnectToSource(tex.ConnectableAPI(),'r')
  if role=='gold' and (C/'textures/gold_roughness.png').exists():
   (pkg/'textures').mkdir(exist_ok=True);shutil.copy2(C/'textures/gold_roughness.png',pkg/'textures/gold_roughness.png')
   rd=UsdShade.Shader.Define(stage,base+'/BrushUV');rd.CreateIdAttr('UsdPrimvarReader_float2');rd.CreateInput('varname',Sdf.ValueTypeNames.String).Set('BadgeUV');rd.CreateOutput('result',Sdf.ValueTypeNames.Float2)
   tex=UsdShade.Shader.Define(stage,base+'/Brush');tex.CreateIdAttr('UsdUVTexture');tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/gold_roughness.png'));tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('raw');tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(rd.ConnectableAPI(),'result');tex.CreateOutput('r',Sdf.ValueTypeNames.Float);sh.CreateInput('roughness',Sdf.ValueTypeNames.Float).ConnectToSource(tex.ConnectableAPI(),'r')
 allp=[];triangles=0
 for i,g in enumerate(groups):
  p=D[str(i)+'_points'];t=D[str(i)+'_triangles'];n=D[str(i)+'_normals'];m=UsdGeom.Mesh.Define(stage,'/Badge/Part_'+str(i));m.GetPrim().SetDisplayName(g['name']);m.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(p));m.CreateFaceVertexCountsAttr([3]*len(t));m.CreateFaceVertexIndicesAttr(t.ravel().tolist());m.CreateSubdivisionSchemeAttr('none')
  m.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(n.reshape(-1,3)));m.SetNormalsInterpolation('faceVarying');m.CreateExtentAttr([Gf.Vec3f(*map(float,p.min(0))),Gf.Vec3f(*map(float,p.max(0)))]);UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(mats[g['mat']])
  if g['mat'] in ['navy','gold'] or g['mat'].endswith('_velvet'):UsdGeom.PrimvarsAPI(m).CreatePrimvar('BadgeUV',Sdf.ValueTypeNames.TexCoord2fArray,'faceVarying').Set(Vt.Vec2fArray.FromNumpy(D[str(i)+'_uv'].reshape(-1,2)))
  allp.append(p);triangles+=len(t)
 stage.GetRootLayer().Save();out=C/'mobile'/(key+'_badge_mobile.usdz');out.unlink(missing_ok=True)
 files=['badge.usdc']+['textures/'+x.name for x in (pkg/'textures').glob('*.png')] if (pkg/'textures').exists() else ['badge.usdc']
 subprocess.run(['/usr/bin/usdzip',str(out)]+files,cwd=pkg,check=True,capture_output=True)
 result=subprocess.run(['/usr/bin/usdchecker','--arkit',str(out)],capture_output=True,text=True);(C/'usdchecker.txt').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout+result.stderr
 p=np.vstack(allp);assert p[:,1].min()>=-2.45501 and p[:,1].max()<=3.01501 and abs(p[:,0]).max()<=3.35
 meta=dict(meshes=len(groups),sections=len(groups),triangles=triangles,bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bounds=[p.min(0).tolist(),p.max(0).tolist()],arkit_valid=True)
 (C/'validation.json').write_text(json.dumps(meta,indent=2)+'\n');print(key,json.dumps(meta),flush=True)
