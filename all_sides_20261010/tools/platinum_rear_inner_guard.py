import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['platinum']['work']);out=w/'candidates/08';out.mkdir(exist_ok=True)
assert not (out/'usd').exists();shutil.copytree(w/'candidates/07/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'))
wall=str(st.GetDefaultPrim().GetPath().AppendPath('Materials/PlatinumKnot_TexturedWalls_NoGlow'))
for prim in [q for q in st.Traverse() if q.IsA(UsdGeom.Mesh)]:
 p,f,n,m,uv=read_mesh(prim);row=(np.arange(len(f))//2)%28
 guard=np.isin(row,[16,25]);m[guard]=wall
 write_mesh(st,prim.GetPath(),p,f,n,m,uv)
finish('platinum',w,out,st,[{'method':'Extend the textured non-emissive perimeter guard onto the first rear face row at each edge. Candidate07 retained isolated bright inner-outline samples in rear oblique frame117. Original front and all geometry, normals and UVs remain unchanged from07.','rear_guard_rows':[16,25],'main_rear_rows':list(range(17,25))}])
