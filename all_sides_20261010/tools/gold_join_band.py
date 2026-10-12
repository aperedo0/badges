"""Seat the curved crown wall in its circular band, closing the visible slit."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['gold']['work']);out=w/'candidates/21';out.mkdir(exist_ok=True)
if not (out/'usd').exists():shutil.copytree(w/'candidates/20/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'))
band=read_mesh(st.GetPrimAtPath('/GoldCrown/GoldCrown_TrueCircularBand'))[0]
center=band[:192].mean(0);axis=np.array([0,.9553869282796957,-.2953571012728279])
R=float(np.linalg.norm(band[:192]-center,axis=1).mean());notes=[]
for prim in [q for q in st.Traverse() if q.IsA(UsdGeom.Mesh) and 'ScallopedShell' in q.GetName()]:
 p,f,n,m,uv=read_mesh(prim);old=p.copy();half=len(p)//2
 for inner in [False,True]:
  ids=np.arange(281)+(half if inner else 0);q=p[ids]-center;h=q@axis;rad=q-h[:,None]*axis
  p[ids]=center-.012*axis+rad/np.linalg.norm(rad,axis=1,keepdims=True)*(R-(.11 if inner else .01))
 changed=np.r_[np.arange(281),np.arange(half,half+281)];affected=np.isin(f,changed).any(1)
 n[affected]=normals(p,f,True)[affected]
 write_mesh(st,prim.GetPath(),p,f,n,m,uv)
 notes.append({'mesh':prim.GetName(),'wall_seated_in_band':True,'maximum_vertex_shift':float(np.linalg.norm(p-old,axis=1).max()),'reason':'The projected wall ended 0.064 to 0.203 units above the true band, exposing the far-side finish through a slit. Seat only the lowest vertex row inside the annulus.'})
old=json.loads((w/'candidates/20/build.json').read_text())['changes']
layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(st.GetRootLayer());dest=out/'usd/joined.usdc';layer.Export(str(dest));shutil.copyfile(dest,out/'usd/compacted.usdc')
finish('gold',w,out,Usd.Stage.Open(str(dest)),old+notes)
(ROOT/'gold21_selection.json').write_text(json.dumps({'gold':'21'})+'\n')
