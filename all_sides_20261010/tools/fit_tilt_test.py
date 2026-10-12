import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['gold']['work']);out=w/'candidates/08';st=Usd.Stage.Open(str(next((out/'usd').glob('*.usd*'))))
records=[]
for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
 p,f,n,m,uv=read_mesh(prim);p[:,[0,2]]*=.997
 n[:,[0,2]]/=.997;n/=np.linalg.norm(n,axis=-1,keepdims=True)
 write_mesh(st,prim.GetPath(),p,f,n,m,uv)
finish('gold',w,out,st,[{'test_only':True,'baked_tilt_degrees':10,'xz_scale':.997,'reason':'Fit every turn within the 6.7-unit picture frame. Baked tilt leans away on the rear.'}])
