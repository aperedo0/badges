import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['platinum']['work']);out=w/'candidates/04'
out.mkdir(exist_ok=True)
assert not (out/'usd').exists()
shutil.copytree(w/'candidates/03/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'))
lip=shader_material(st,'PlatinumKnot_RearEdgeLip',[.13,.14,.16],.78)
notes=[]
for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
 p,f,n,m,uv=read_mesh(prim)
 assert len(p)==768*28 and len(f)==768*28*2
 # The source ribbon has 28 closed cross-section rows. Rows 14/15 and
 # 26/27 form the two narrow rear bevels, including the rear outline.
 # A non-emissive continuous metal lip avoids sampling the solved front's
 # bright silhouette pixels as isolated glints on an oblique rear edge.
 row=(np.arange(len(f))//2)%28
 guard=np.isin(row,[14,15,26,27])
 m[guard]=lip
 write_mesh(st,prim.GetPath(),p,f,n,m,uv)
 notes.append({'rear_lip_faces':int(guard.sum()),'roughness':.78,
  'method':'Narrow continuous rear bevel uses non-emissive rough platinum metal; front rows and the main textured rear and wall surfaces are retained.',
  'front_half_materials_unchanged_from_candidate03':True,
  'geometry_normals_uv_unchanged_from_candidate03':True})
finish('platinum',w,out,st,notes)
