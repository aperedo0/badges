"""Compact the inspected mesh without exporting any studio or construction guide."""
from pathlib import Path
import sys,json,subprocess,tempfile,shutil,hashlib,numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf,Vt,Gf
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));from pace import work
work(1)
key=sys.argv[1];R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip();cfg=json.loads((R/'design.json').read_text());spec=json.loads((C/'material_specs.json').read_text());groups=json.loads((C/'groups.json').read_text());D=np.load(C/'blender_geometry.npz')
with tempfile.TemporaryDirectory(prefix='overnight_badge_',dir='/tmp') as temp:
 pkg=Path(temp);shutil.copytree(C/'textures',pkg/'textures');stage=Usd.Stage.CreateNew(str(pkg/'badge.usdc'));root=UsdGeom.Xform.Define(stage,'/Badge');stage.SetDefaultPrim(root.GetPrim());UsdGeom.SetStageUpAxis(stage,'Y');UsdGeom.SetStageMetersPerUnit(stage,1.)
 mats={}
 for role,sp in spec.items():
  name=role if role.startswith('CrestGem_') else key+'_'+role;base='/Badge/Materials/'+name;mat=UsdShade.Material.Define(stage,base);sh=UsdShade.Shader.Define(stage,base+'/Surface');sh.CreateIdAttr('UsdPreviewSurface')
  for name,value in [('metallic',sp['metallic']),('roughness',sp['roughness']),('ior',1.77 if role.startswith('CrestGem_') else 1.46),('opacity',1.)]:sh.CreateInput(name,Sdf.ValueTypeNames.Float).Set(value)
  sh.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(tuple(sp.get('color',[.004,.004,.004])));sh.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(),'surface')
  if sp['textured']:
   reader=UsdShade.Shader.Define(stage,base+'/UV');reader.CreateIdAttr('UsdPrimvarReader_float2');reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('BadgeUV');reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
   for suffix,param in [('color','diffuseColor'),('emission','emissiveColor'),('roughness','roughness')]:
    tex=UsdShade.Shader.Define(stage,base+'/'+suffix);tex.CreateIdAttr('UsdUVTexture');tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+role+'_'+suffix+'.png'));tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('raw' if suffix=='roughness' else 'sRGB')
    tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result');tex.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('clamp');tex.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp')
    if suffix=='emission':tex.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set((8,8,8,1))
    if suffix=='roughness':tex.CreateOutput('r',Sdf.ValueTypeNames.Float);sh.CreateInput(param,Sdf.ValueTypeNames.Float).ConnectToSource(tex.ConnectableAPI(),'r')
    else:tex.CreateOutput('rgb',Sdf.ValueTypeNames.Float3);sh.CreateInput(param,Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(),'rgb')
  mats[role]=mat
 allpoints=[];count=0
 for i,g in enumerate(groups):
  p=D[str(i)+'_points'];t=D[str(i)+'_triangles'];n=D[str(i)+'_normals'];uv=D[str(i)+'_uv'];mesh=UsdGeom.Mesh.Define(stage,'/Badge/Part_'+str(i));mesh.GetPrim().SetDisplayName(g['name'])
  mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(p));mesh.CreateFaceVertexCountsAttr([3]*len(t));mesh.CreateFaceVertexIndicesAttr(t.ravel().tolist());mesh.CreateSubdivisionSchemeAttr('none')
  if np.max(abs(n-n[:,:1,:]))<2e-6:mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(n[:,0,:]));mesh.SetNormalsInterpolation('uniform')
  else:
   vn=np.zeros((len(p),3),np.float32);vn[t.ravel()]=n.reshape(-1,3)
   if np.max(abs(vn[t.ravel()]-n.reshape(-1,3)))<2e-6:mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(vn));mesh.SetNormalsInterpolation('vertex')
   else:mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(n.reshape(-1,3)));mesh.SetNormalsInterpolation('faceVarying')
  if g['role'] in cfg['textured_roles']:
   vu=np.zeros((len(p),2),np.float32);vu[t.ravel()]=uv.reshape(-1,2);assert np.max(abs(vu[t.ravel()]-uv.reshape(-1,2)))<1e-7
   UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('BadgeUV',Sdf.ValueTypeNames.TexCoord2fArray,'vertex').Set(Vt.Vec2fArray.FromNumpy(vu))
  mesh.CreateExtentAttr([Gf.Vec3f(*map(float,p.min(0))),Gf.Vec3f(*map(float,p.max(0)))]);UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mats[g['role']]);allpoints.append(p);count+=len(t)
  if str(i)+'_side_mask' in D.files and D[str(i)+'_side_mask'].any():
   subset=UsdGeom.Subset.Define(stage,mesh.GetPath().AppendChild('PlainSideWalls'));subset.CreateElementTypeAttr('face');subset.CreateFamilyNameAttr('materialBind');subset.CreateIndicesAttr(np.flatnonzero(D[str(i)+'_side_mask']).tolist());UsdShade.MaterialBindingAPI.Apply(subset.GetPrim()).Bind(mats['side']);UsdGeom.Subset.SetFamilyType(mesh,'materialBind','nonOverlapping')
 stage.GetRootLayer().Save();out=C/'mobile'/(key+'_badge_mobile.usdz');out.unlink(missing_ok=True)
 subprocess.run(['/usr/bin/usdzip',str(out),'badge.usdc']+['textures/'+p.name for p in sorted((pkg/'textures').glob('*.png'))],cwd=pkg,check=True,capture_output=True)
 check=subprocess.run(['/usr/bin/usdchecker','--arkit',str(out)],capture_output=True,text=True);(C/'usdchecker.txt').write_text(check.stdout+check.stderr);assert check.returncode==0,check.stdout+check.stderr
 p=np.vstack(allpoints);assert p[:,1].min()>=-2.45501 and p[:,1].max()<=3.01501 and abs(p[:,0]).max()<3.35
 meta=dict(triangles=count,bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bounds_min=p.min(0).tolist(),bounds_max=p.max(0).tolist(),arkit_valid=True)
 (C/'validation.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta),flush=True)
