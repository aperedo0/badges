import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['platinum']['work']);out=w/'candidates/09';out.mkdir(exist_ok=True)
assert not (out/'usd').exists();shutil.copytree(w/'candidates/08/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'));source=Usd.Stage.Open(str(w/'source/installed/badge.usdc'))
for prim in [q for q in st.Traverse() if q.IsA(UsdGeom.Mesh)]:
 p,f,n,m,uv=read_mesh(prim);sp,sf,sn,sm,suv=read_mesh(source.GetPrimAtPath(prim.GetPath()))
 assert np.array_equal(p,sp) and np.array_equal(f,sf)
 rows=(np.arange(len(f))//2)%28;rear=np.isin(rows,np.arange(17,25))
 for name,a in uv.items():
  original=suv[name];values=np.zeros((len(p),2));counts=np.zeros(len(p))
  for k in range(3):np.add.at(values,sf[:,k],original[:,k]);np.add.at(counts,sf[:,k],1)
  values/=counts[:,None]
  ids=f[rear];longitudinal=ids//28;cross=ids%28
  counterpart=np.clip((28-cross)%28,4,10)
  a[rear]=values[longitudinal*28+counterpart]
 write_mesh(st,prim.GetPath(),p,f,n,m,uv)
layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(st.GetRootLayer());dest=out/'usd/fresh.usdc';layer.Export(str(dest));shutil.copyfile(dest,out/'usd/compacted.usdc');st.GetRootLayer().Reload(True);dest.unlink()
finish('platinum',w,out,st,[{'method':'Rear UVs follow the corresponding front surface across the ribbon cross section, rather than projecting the photographic front onto the rear plane. The first sampled front UV row is four, excluding the front silhouette highlight strip. Front faces, all geometry and normals, and bounded side materials remain unchanged from08.','front_sample_rows':[4,5,6,7,8,9,10]}])
(ROOT/'platinum09_selection.json').write_text(json.dumps({'platinum':'09'})+'\n')
