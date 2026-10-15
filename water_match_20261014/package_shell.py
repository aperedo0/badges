"""Package the new Blender-built shell on an untouched copy of the original inset."""
from pathlib import Path
import numpy as np,zipfile,subprocess
from pxr import Usd,UsdGeom,UsdShade,Sdf,Gf,Vt
R=Path(__file__).resolve().parent;source=R.parent/'badge_realitykit_silver/mobile/silver_badge_mobile.usdz';pkg=R/'shell_pkg';pkg.mkdir(exist_ok=True)
with zipfile.ZipFile(source) as z:
 for n in z.namelist():
  if 'Inset_' in n and n.endswith('.png'):
   p=pkg/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
s=Usd.Stage.Open(str(source));s.GetRootLayer().Export(str(pkg/'shell.usdc'));s=Usd.Stage.Open(str(pkg/'shell.usdc'))
for p in ['/Badge/Casing___smooth_rounded_outer_edge','/Badge/Inner_edge___fine_silver_reveal','/Badge/Inner_channel___shadowed_bevel','/Badge/Rim_inner_lip___narrow_highlight','/Badge/Emblem___faceted_compass_spear']:s.RemovePrim(p)
for p in list(s.GetPrimAtPath('/Badge/_materials').GetChildren()):
 if 'Inset___' not in p.GetName():s.RemovePrim(p.GetPath())
a=np.load(R/'shell_geometry.npz');p=a['points'];t=a['triangles'];n=a['normals'];roles=a['roles']
parent=UsdGeom.Xform.Define(s,'/Badge/Casing___smooth_rounded_outer_edge');mesh=UsdGeom.Mesh.Define(s,parent.GetPath().AppendChild('Casing___smooth_rounded_outer_edge_mobile_geometry'))
mesh.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(p.astype(np.float32)));mesh.CreateFaceVertexCountsAttr([3]*len(t));mesh.CreateFaceVertexIndicesAttr(t.ravel().tolist());mesh.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(n.reshape(-1,3).astype(np.float32)));mesh.SetNormalsInterpolation('faceVarying');mesh.CreateSubdivisionSchemeAttr('none');mesh.CreateDoubleSidedAttr(False);mesh.CreateExtentAttr([Gf.Vec3f(*p.min(0)),Gf.Vec3f(*p.max(0))])
uv=(p[:,:2]+3.015)/6.03;back=(n.mean(1)[:,2]<-.1);uv[t[back].ravel(),0]=1-uv[t[back].ravel(),0]
for var in ['USDZ_UV','Machining_UV']:UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(var,Sdf.ValueTypeNames.TexCoord2fArray,'vertex').Set(Vt.Vec2fArray.FromNumpy(uv.astype(np.float32)))
for role,rough in [('face',.34),('bevel',.32),('side',.48),('inner',.48)]:
 name='Silver___circumferential_brushed_steel_Mobile_Casing' if role=='face' else 'Shell_'+role
 mat=UsdShade.Material.Define(s,'/Badge/_materials/'+name);sh=UsdShade.Shader.Define(s,mat.GetPath().AppendChild('Surface'));sh.CreateIdAttr('UsdPreviewSurface');sh.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(.15,.15,.15));sh.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(1.);sh.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(rough);sh.CreateInput('opacity',Sdf.ValueTypeNames.Float).Set(1.);sh.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(),'surface')
 sub=UsdGeom.Subset.Define(s,mesh.GetPath().AppendChild(role));sub.CreateElementTypeAttr('face');sub.CreateFamilyNameAttr('materialBind');sub.CreateIndicesAttr(np.flatnonzero(roles==role).tolist());UsdShade.MaterialBindingAPI.Apply(sub.GetPrim()).Bind(mat)
 if role=='face':UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat)
UsdGeom.Subset.SetFamilyType(mesh,'materialBind','partition')
import sys
sys.path.insert(0,str(R.parent))
import coin_rim
coin_rim.apply(s,'clean',pkg,raise_geometry=False)
s.GetRootLayer().Save()
out=R/'shell_template.usdz';out.unlink(missing_ok=True);files=['shell.usdc']+sorted(str(p.relative_to(pkg)) for p in (pkg/'textures').glob('*.png'))
subprocess.run(['/usr/bin/usdzip',str(out)]+files,cwd=pkg,check=True);subprocess.run(['/usr/bin/usdchecker','--arkit',str(out)],check=True)
print('New shell template packaged; original source unchanged.')
