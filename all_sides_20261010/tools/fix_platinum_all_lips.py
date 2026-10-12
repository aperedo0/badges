import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['platinum']['work']);out=w/'candidates/05';out.mkdir(exist_ok=True)
assert not (out/'usd').exists()
shutil.copytree(w/'candidates/04/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'))
lip=shader_material(st,'PlatinumKnot_ContinuousEdgeLip',[.045,.05,.06],.88)
notes=[]
for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
 p,f,n,m,uv=read_mesh(prim)
 assert len(p)==768*28 and len(f)==768*28*2
 row=(np.arange(len(f))//2)%28
 guard=np.isin(row,[0,1,12,13,14,15,26,27]);m[guard]=lip
 write_mesh(st,prim.GetPath(),p,f,n,m,uv)
 notes.append({'continuous_lip_faces':int(guard.sum()),'roughness':.88,
  'method':'Narrow front, rear and side bevels have one continuous dark, rough, non-emissive platinum lip. Main front/rear texture and broad textured side surfaces remain. This removes the solved front silhouette texture from oblique edges.',
  'main_front_rows_unchanged':list(range(2,12)),
  'geometry_normals_uv_unchanged_from_candidate03':True})
finish('platinum',w,out,st,notes)
