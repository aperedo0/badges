import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['platinum']['work']);out=w/'candidates/06';out.mkdir(exist_ok=True)
assert not (out/'usd').exists()
shutil.copytree(w/'candidates/05/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'));root=st.GetDefaultPrim().GetPath()
old=root.AppendPath('Materials/PlatinumKnot_TexturedWalls')
new=root.AppendPath('Materials/PlatinumKnot_TexturedWalls_NoGlow')
Sdf.CopySpec(st.GetRootLayer(),old,st.GetRootLayer(),new)
for p in st.Traverse():
 if not p.GetPath().HasPrefix(new):continue
 for a in p.GetAttributes():
  c=a.GetConnections()
  if c:a.SetConnections([q.ReplacePrefix(old,new) for q in c])
s=UsdShade.Shader.Get(st,new.AppendChild('Surface'))
s.GetInput('roughness').Set(.78)
s.GetInput('emissiveColor').DisconnectSource()
s.GetInput('emissiveColor').Set(Gf.Vec3f(0,0,0))
notes=[]
for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
 p,f,n,m,uv=read_mesh(prim);row=(np.arange(len(f))//2)%28
 walls=np.isin(row,[0,13,14,27]);m[walls]=str(new)
 write_mesh(st,prim.GetPath(),p,f,n,m,uv)
 notes.append({'textured_wall_faces':int(walls.sum()),'thin_lip_rows':[1,12,15,26],
  'method':'Broad side walls retain inset source color texture, with moderate roughness and zero emission; only the thin front/rear bevel lips are plain rough metal. Main front and rear solved texture remains unchanged.',
  'geometry_normals_uv_unchanged_from_candidate03':True})
finish('platinum',w,out,st,notes)
