"""Export inspected Blender geometry and real material parameters to USDZ."""
from pathlib import Path
import json,subprocess,shutil,tempfile,hashlib
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf,Vt,Gf
R=Path(__file__).resolve().parent;C=R/(R/'candidate.txt').read_text().strip()
D=np.load(C/'blender_geometry.npz');groups=json.loads((C/'groups.json').read_text());spec=json.loads((C/'material_specs.json').read_text())
with tempfile.TemporaryDirectory(prefix='aurora_mountain_',dir='/tmp') as temp:
 pkg=Path(temp);(pkg/'textures').mkdir()
 for p in (C/'textures').glob('*.png'):
  if not p.name.endswith('_target.png'):shutil.copyfile(p,pkg/'textures'/p.name)
 stage=Usd.Stage.CreateNew(str(pkg/'crest.usdc'));root=UsdGeom.Xform.Define(stage,'/AuroraMountain');stage.SetDefaultPrim(root.GetPrim());UsdGeom.SetStageUpAxis(stage,'Y');UsdGeom.SetStageMetersPerUnit(stage,1.)
 mats={}
 for role,(color,metal,rough) in spec.items():
  name=role if role.startswith('CrestGem_') else 'AuroraMountain_'+role;base='/AuroraMountain/Materials/'+name
  mat=UsdShade.Material.Define(stage,base);shader=UsdShade.Shader.Define(stage,base+'/Surface');shader.CreateIdAttr('UsdPreviewSurface')
  for key,value in [('metallic',metal),('roughness',rough),('ior',1.55 if role.startswith('CrestGem_') else 1.46),('opacity',1.)]:shader.CreateInput(key,Sdf.ValueTypeNames.Float).Set(value)
  shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(tuple(color));shader.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),'surface')
  if role in ['sky','rock']:
   reader=UsdShade.Shader.Define(stage,base+'/UV');reader.CreateIdAttr('UsdPrimvarReader_float2');reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('AuroraUV');reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
   for suffix,param in [('color','diffuseColor'),('emission','emissiveColor')]:
    tex=UsdShade.Shader.Define(stage,base+'/'+suffix);tex.CreateIdAttr('UsdUVTexture');tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+role+'_'+suffix+'.png'));tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB')
    tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result');tex.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('clamp');tex.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp')
    if suffix=='emission':tex.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set((8,8,8,1))
    tex.CreateOutput('rgb',Sdf.ValueTypeNames.Float3);shader.CreateInput(param,Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(),'rgb')
  if role=='star':shader.CreateInput('emissiveColor',Sdf.ValueTypeNames.Color3f).Set((.12,.045,.002))
  if role=='star_minor':shader.CreateInput('emissiveColor',Sdf.ValueTypeNames.Color3f).Set((.8,.35,.025))
  if role=='star_core':shader.CreateInput('emissiveColor',Sdf.ValueTypeNames.Color3f).Set((4,2,.5))
  mats[role]=mat
 points=[];count=0
 for i,g in enumerate(groups):
  p=D[str(i)+'_points'];t=D[str(i)+'_triangles'];norm=D[str(i)+'_normals'].reshape(-1,3);uv=D[str(i)+'_uv'].reshape(-1,2)
  mesh=UsdGeom.Mesh.Define(stage,'/AuroraMountain/Part_'+str(i));mesh.GetPrim().SetDisplayName(g['name']);mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(p));mesh.CreateFaceVertexCountsAttr([3]*len(t));mesh.CreateFaceVertexIndicesAttr(t.ravel().tolist());mesh.CreateSubdivisionSchemeAttr('none')
  face_norm=norm.reshape(-1,3,3)
  if np.max(abs(face_norm-face_norm[:,:1,:]))<2e-6:
   mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(face_norm[:,0,:]));mesh.SetNormalsInterpolation('uniform')
  else:
   vertex_norm=np.zeros((len(p),3),np.float32);vertex_norm[t.ravel()]=norm
   if np.max(abs(vertex_norm[t.ravel()]-norm))<2e-6:
    mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(vertex_norm));mesh.SetNormalsInterpolation('vertex')
   else:
    mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(norm));mesh.SetNormalsInterpolation('faceVarying')
  if g['role'] in ['sky','rock']:
   vertex_uv=np.zeros((len(p),2),np.float32);vertex_uv[t.ravel()]=uv
   assert np.max(abs(vertex_uv[t.ravel()]-uv))<1e-7
   UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('AuroraUV',Sdf.ValueTypeNames.TexCoord2fArray,'vertex').Set(Vt.Vec2fArray.FromNumpy(vertex_uv))
  mesh.CreateExtentAttr([Gf.Vec3f(*map(float,p.min(0))),Gf.Vec3f(*map(float,p.max(0)))]);UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mats[g['role']]);points.append(p);count+=len(t)
 stage.GetRootLayer().Save();out=C/'mobile/aurora_mountain_badge_mobile.usdz'
 if out.exists():out.unlink()
 subprocess.run(['/usr/bin/usdzip',str(out),'crest.usdc']+['textures/'+p.name for p in sorted((pkg/'textures').glob('*.png'))],cwd=pkg,check=True,capture_output=True)
 check=subprocess.run(['/usr/bin/usdchecker','--arkit',str(out)],capture_output=True,text=True);(C/'usdchecker.txt').write_text(check.stdout+check.stderr);assert check.returncode==0,check.stdout+check.stderr
 p=np.vstack(points);assert p[:,1].min()>=-2.45501 and p[:,1].max()<=3.01501 and abs(p[:,0]).max()<3.35
 meta=dict(triangles=count,bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bounds_min=p.min(0).tolist(),bounds_max=p.max(0).tolist(),arkit_valid=True,gem_appearance_textures=False)
 (C/'validation.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
