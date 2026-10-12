"""Keep the installed wall's shading normals while seating its lowest row."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['gold']['work']);out=w/'candidates/22';out.mkdir(exist_ok=True)
assert not (out/'usd').exists();shutil.copytree(w/'candidates/21/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'));oldstage=Usd.Stage.Open(str(w/'candidates/20/usd/compacted.usdc'))
for prim in [q for q in st.Traverse() if q.IsA(UsdGeom.Mesh) and 'ScallopedShell' in q.GetName()]:
 p,f,n,m,uv=read_mesh(prim);oldn=read_mesh(oldstage.GetPrimAtPath(prim.GetPath()))[2]
 write_mesh(st,prim.GetPath(),p,f,oldn,m,uv)
old=json.loads((w/'candidates/21/build.json').read_text())['changes']
layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(st.GetRootLayer());dest=out/'usd/join_normals.usdc';layer.Export(str(dest));shutil.copyfile(dest,out/'usd/compacted.usdc')
finish('gold',w,out,Usd.Stage.Open(str(dest)),old+[{'reference_wall_normals_retained_at_band_join':True,'reason':'Recomputed normals at the new lowest row introduced a visible crease. Preserve the reference wall shading while keeping the slit closed.'}])
(ROOT/'gold22_selection.json').write_text(json.dumps({'gold':'22'})+'\n')
