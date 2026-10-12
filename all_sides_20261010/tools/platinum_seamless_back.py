import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['platinum']['work']);out=w/'candidates/10'
assert not (out/'usd').exists();shutil.copytree(w/'candidates/08/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'));root=st.GetDefaultPrim().GetPath()
old=root.AppendPath('Materials/PlatinumKnot_Front');new=root.AppendPath('Materials/PlatinumKnot_SeamlessRear')
Sdf.CopySpec(st.GetRootLayer(),old,st.GetRootLayer(),new)
for p in st.Traverse():
 if not p.GetPath().HasPrefix(new):continue
 for a in p.GetAttributes():
  c=a.GetConnections()
  if c:a.SetConnections([q.ReplacePrefix(old,new) for q in c])
 for name in ['file']:
  a=p.GetAttribute('inputs:'+name)
  if a and a.Get():
   src=str(a.Get().path)
   channel='emissive' if 'emissive' in src else 'color'
   shutil.copyfile(out/'atlas'/f'rear_{channel}.png',out/'usd'/f'rear_{channel}.png')
   a.Set(Sdf.AssetPath(f'rear_{channel}.png'))
for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
 p,f,n,m,uv=read_mesh(prim);row=(np.arange(len(f))//2)%28;rear=np.isin(row,np.arange(17,25));m[rear]=str(new)
 ids=f[rear];j=ids//28;k=ids%28;cross=np.clip((28-k)%28,2,12)
 u=j.astype(float)/768
 last=(j.max(1)-j.min(1))>700;u[last]=np.where(j[last]==0,1,u[last])
 v=1-(cross-2)/10
 for name,a in uv.items():a[rear]=np.stack([u,v],-1)
 write_mesh(st,prim.GetPath(),p,f,n,m,uv)
layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(st.GetRootLayer());dest=out/'usd/seamless.usdc';layer.Export(str(dest));finish('platinum',w,out,Usd.Stage.Open(str(dest)),[{'rear_polish':json.loads((out/'atlas/atlas.json').read_text()),'front_geometry_and_maps_unchanged_from08':True,'rear_geometry_preserved':'An actual trefoil has different over-under crossings from behind. Preserve its continuous ribbon; reuse and complete the front polish rather than flattening a reference image onto the rear.'}])
(ROOT/'platinum10_selection.json').write_text(json.dumps({'platinum':'10'})+'\n')
