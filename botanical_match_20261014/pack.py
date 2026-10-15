"""USD assembly. Reads the frozen silver package; modifies only working copies."""
from pathlib import Path
import hashlib,json,sys,zipfile
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,UsdUtils,Sdf,Gf,Vt

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'shell_template.usdz'
SHELL_NAMES=['Inset___charcoal_textured_disk','Inner_edge___fine_silver_reveal',
             'Casing___smooth_rounded_outer_edge','Inner_channel___shadowed_bevel','Rim_inner_lip___narrow_highlight']
PALETTE={
 'water':([.025,.25,.38],.12,.30), 'glass':([.045,.075,.09],.10,.30),
 'silver':([.46,.45,.42],1.,.36),'bronze':([.53,.25,.075],1.,.36),
 'gold':([.61,.40,.075],1.,.36), 'emerald':([.02,.25,.105],.28,.30),
 'soil':([.16,.055,.016],.25,.44), 'sand':([.14,.34,.36],.45,.40),
 'background':([.018,.022,.025],.05,.83),
 'emerald_background':([.005,.13,.048],.25,.31),
}

def texture(stage,mat,shader,target,filename,strength=1.):
 reader=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('ReliefUV'))
 reader.CreateIdAttr('UsdPrimvarReader_float2');reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('CoinReliefUV');reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
 tex=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild(target+'Map'));tex.CreateIdAttr('UsdUVTexture')
 tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+filename))
 tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB')
 tex.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(strength,strength,strength,1.))
 tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result')
 tex.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('clamp');tex.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp')
 tex.CreateOutput('rgb',Sdf.ValueTypeNames.Float3)
 shader.CreateInput(target,Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(),'rgb')

def material(stage,name,role,side=False,calibration=False):
 color,_,rough=PALETTE[role]
 # Colored reflective reliefs allow the measured lighting fit to remain linear.
 rough={'background':.90,'emerald_background':.42,'glass':.32,'water':.32,
        'silver':.36,'gold':.36,'bronze':.38,'emerald':.34,'soil':.48,'sand':.52}[role]
 if role=='background':color=[.003,.004,.005]
 mat=UsdShade.Material.Define(stage,'/Badge/_materials/Coin_'+role+('_Wall' if side else '_Face'))
 sh=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('Surface'));sh.CreateIdAttr('UsdPreviewSurface')
 sh.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*(np.array(color)*.25 if side else [.15,.15,.15] if calibration else color)))
 sh.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(1.)
 sh.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(.56 if side else rough)
 sh.CreateInput('opacity',Sdf.ValueTypeNames.Float).Set(1.)
 sh.CreateInput('ior',Sdf.ValueTypeNames.Float).Set(1.46 if role in ['water','glass'] else 1.5)
 sh.CreateInput('clearcoat',Sdf.ValueTypeNames.Float).Set(0.)
 if not side and not calibration:
  scale=.03125 if role=='background' else 1.
  texture(stage,mat,sh,'diffuseColor',role+'_color.png',strength=scale)
  texture(stage,mat,sh,'emissiveColor',role+'_emission.png',strength=16.)
 sh.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(),'surface')
 return mat

def mesh(stage,path,points,triangles,normals,uv,front_count,frontmat,wallmat):
 m=UsdGeom.Mesh.Define(stage,path)
 m.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(points.astype(np.float32)))
 m.CreateFaceVertexCountsAttr([3]*len(triangles));m.CreateFaceVertexIndicesAttr(triangles.ravel().tolist())
 if path.endswith('_water') or path.endswith('_emerald') or path.endswith('_soil') or path.endswith('_emerald_background'):
  m.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(normals.reshape(-1,3).astype(np.float32)));m.SetNormalsInterpolation('faceVarying')
 else:
  vertex_normals=np.zeros_like(points)
  for corner in range(3):np.add.at(vertex_normals,triangles[:,corner],normals[:,corner])
  vertex_normals/=np.maximum(np.linalg.norm(vertex_normals,axis=1,keepdims=True),1e-12)
  m.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(vertex_normals.astype(np.float32)));m.SetNormalsInterpolation('vertex')
 m.CreateSubdivisionSchemeAttr('none');m.CreateDoubleSidedAttr(False)
 m.CreateExtentAttr([Gf.Vec3f(*points.min(0).tolist()),Gf.Vec3f(*points.max(0).tolist())])
 vertex_uv=np.zeros((len(points),2))
 vertex_uv[triangles.ravel()]=uv.reshape(-1,2)
 pv=UsdGeom.PrimvarsAPI(m).CreatePrimvar('CoinReliefUV',Sdf.ValueTypeNames.TexCoord2fArray,'vertex')
 pv.Set(Vt.Vec2fArray.FromNumpy(vertex_uv.astype(np.float32)))
 UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(frontmat)
 if front_count<len(triangles):
  for suffix,indices,mat in [('Face',range(front_count),frontmat),('Walls',range(front_count,len(triangles)),wallmat)]:
   sub=UsdGeom.Subset.Define(stage,m.GetPath().AppendChild(suffix));sub.CreateElementTypeAttr('face');sub.CreateFamilyNameAttr('materialBind');sub.CreateIndicesAttr(list(indices))
   UsdShade.MaterialBindingAPI.Apply(sub.GetPrim()).Bind(mat)
  UsdGeom.Subset.SetFamilyType(m,'materialBind','partition')
 return m

def shell_signature(stage):
 result={}
 for p in stage.Traverse():
  if not p.IsA(UsdGeom.Mesh) or p.GetParent().GetName() not in SHELL_NAMES:continue
  result[str(p.GetPath())]={a.GetName():str(a.Get()) for a in p.GetAttributes() if a.GetName() not in ['material:binding']}
 return result

def build(name,calibration=False):
 d=ROOT/name;data=np.load(d/'reliefs.npz');meta=json.loads((d/'design.json').read_text())
 pkg=d/('calibration_pkg' if calibration else 'pkg');pkg.mkdir(exist_ok=True)
 if not calibration:
  for image in (d/'textures').glob('*.png'):
   target=pkg/'textures'/image.name;target.parent.mkdir(exist_ok=True)
   target.write_bytes(image.read_bytes())
 with zipfile.ZipFile(SOURCE) as z:
  for n in z.namelist():
   if n.endswith('.png'):
    p=pkg/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
 source=Usd.Stage.Open(str(SOURCE));source.GetRootLayer().Export(str(pkg/'coin.usdc'))
 stage=Usd.Stage.Open(str(pkg/'coin.usdc'))
 stage.RemovePrim('/Badge/Emblem___faceted_compass_spear')
 # Owner authorized the mockup colors while keeping every shell vertex.
 tint=[2.4,1.25,.38,1.] if name=='sunrise' else [1.7,1.15,.24,1.] if name=='sprout' else None
 if tint:
  for p in stage.Traverse():
   if p.IsA(UsdShade.Shader):
    sh=UsdShade.Shader(p)
    if sh.GetIdAttr().Get()=='UsdUVTexture' and sh.GetInput('file') and 'Casing_base_color' in str(sh.GetInput('file').Get()):
     sh.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set(Gf.Vec4f(*tint))
    if sh.GetIdAttr().Get()=='UsdPreviewSurface' and ('polished_cut_edges' in str(p.GetPath())):
     c=np.array([.64,.62,.58])*np.array(tint[:3]);c=np.clip(c,0,1)
     sh.GetInput('diffuseColor').Set(Gf.Vec3f(*c.tolist()))
 # Finish the newly authorized shell without changing the template geometry.
 for role,matname in [('face','Silver___circumferential_brushed_steel_Mobile_Casing'),('bevel','Shell_bevel'),('inner','Shell_inner'),('side','Shell_side')]:
  mat=UsdShade.Material(stage.GetPrimAtPath('/Badge/_materials/'+matname));sh=UsdShade.Shader(stage.GetPrimAtPath(str(mat.GetPath())+'/Surface'))
  if role=='side':
   color=(.24,.09,.03) if name=='sunrise' else (.24,.16,.035) if name=='sprout' else (.12,.13,.15)
   glow=(.018,.008,.003) if name=='sunrise' else (.015,.010,.002) if name=='sprout' else (.012,.014,.018)
   sh.GetInput('diffuseColor').Set(Gf.Vec3f(*color));sh.GetInput('roughness').Set(.56)
   sh.CreateInput('emissiveColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*glow))
  elif not calibration:
   texture(stage,mat,sh,'diffuseColor','shell_'+role+'_color.png')
   texture(stage,mat,sh,'emissiveColor','shell_'+role+'_emission.png',strength=16.)
  # The shell uses its own planar UV set.
  if mat.GetPrim().GetChild('ReliefUV'):
   UsdShade.Shader(mat.GetPrim().GetChild('ReliefUV')).GetInput('varname').Set('USDZ_UV')
 materials={role:(material(stage,name,role,False,calibration),material(stage,name,role,True,calibration)) for role in set(f['role'] for f in meta['features'])}
 total=0;front_geometry=[]
 for i,feature in enumerate(meta['features']):
  p=data[f'{i}_points'];t=data[f'{i}_triangles'];n=data[f'{i}_normals'];fc=feature['front_count']
  facep=p[t];uv=(facep[:,:,:2]+3.015)/6.03
  mesh(stage,f'/Badge/ReliefFront_{i}_{feature["role"]}',p,t,n,uv,fc,*materials[feature['role']])
  front_geometry.append({'role':feature['role'],'points':facep[:fc].tolist(),'uv':uv[:fc].tolist()})
  back=p*np.array([-1,1,-1]);back[:,2]-=.33;bn=n*np.array([-1,1,-1])
  mesh(stage,f'/Badge/ReliefBack_{i}_{feature["role"]}',back,t,bn,uv,fc,*materials[feature['role']])
  total+=2*len(t)
 # Rear reveal, channel and lip are genuine copies, not painted rings.
 for parent_name in []:
  original=next(p for p in source.Traverse() if p.IsA(UsdGeom.Mesh) and p.GetParent().GetName()==parent_name)
  src=UsdGeom.Mesh(original);target_path='/Badge/Rear_'+parent_name
  Sdf.CopySpec(stage.GetRootLayer(),original.GetPath(),stage.GetRootLayer(),Sdf.Path(target_path))
  dst=UsdGeom.Mesh(stage.GetPrimAtPath(target_path));p=np.array(src.GetPointsAttr().Get())*[-1,1,-1];p[:,2]-=.33
  dst.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(p.astype(np.float32)))
  dst.GetNormalsAttr().Set(Vt.Vec3fArray.FromNumpy((np.array(src.GetNormalsAttr().Get())*[-1,1,-1]).astype(np.float32)))
  dst.GetExtentAttr().Set([Gf.Vec3f(*p.min(0).tolist()),Gf.Vec3f(*p.max(0).tolist())])
  total+=sum(int(n)-2 for n in src.GetFaceVertexCountsAttr().Get())
 assert shell_signature(stage)==shell_signature(source),'Frozen shell changed.'
 assert UsdGeom.GetStageUpAxis(stage)=='Y' and UsdGeom.GetStageMetersPerUnit(stage)==1
 stage.GetRootLayer().Save()
 out=d/('calibration.usdz' if calibration else 'mobile/'+name+'_badge_mobile.usdz')
 out.parent.mkdir(exist_ok=True)
 out.unlink(missing_ok=True)
 import subprocess
 files=['coin.usdc']+sorted(str(p.relative_to(pkg)) for p in (pkg/'textures').glob('*.png'))
 subprocess.run(['/usr/bin/usdzip',str(out)]+files,cwd=pkg,check=True,capture_output=True)
 checker=subprocess.run(['/usr/bin/usdchecker','--arkit',str(out)],capture_output=True,text=True)
 assert checker.returncode==0,checker.stdout+checker.stderr
 shipped=Usd.Stage.Open(str(out));assert shell_signature(shipped)==shell_signature(source)
 shell_tri=sum(sum(int(x)-2 for x in UsdGeom.Mesh(p).GetFaceVertexCountsAttr().Get()) for p in source.Traverse() if p.IsA(UsdGeom.Mesh) and p.GetParent().GetName() in SHELL_NAMES)
 facts={'name':name,'file':str(out),'bytes':out.stat().st_size,'triangles':shell_tri+total,'shell_geometry_identical':True,'floor_y':-2.895,'calibration':calibration,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
 (d/('calibration.json' if calibration else 'model.json')).write_text(json.dumps(facts,indent=2))
 (d/'front_geometry.json').write_text(json.dumps(front_geometry))
 print(json.dumps(facts),flush=True)

if __name__=='__main__':
 names=[v for v in sys.argv[1:] if v!='--calibration']
 for name in names:build(name,'--calibration' in sys.argv)
