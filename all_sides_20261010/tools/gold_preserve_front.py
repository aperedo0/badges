import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['gold']['work']);out=w/'candidates/10'
if (out/'usd/badge.usdc').exists():st=Usd.Stage.Open(str(out/'usd/badge.usdc'))
else:w,out,st=open_copy('gold','10')
root=st.GetDefaultPrim().GetPath()
front=str(root.AppendPath('Materials/GoldCrown_Front'))
changes=[]
for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
 p,f,n,mats,uv=read_mesh(prim);rear=np.array(['Back' in x for x in mats])
 # The installed chart projects the reference image. Mirror that chart on
 # the rear so its highlight arrangement faces the viewer after a half turn.
 for name,a in uv.items():
  a[rear,:,0]=1-a[rear,:,0]
 mats[rear]=front
 write_mesh(st,prim.GetPath(),p,f,n,mats,uv)
 changes.append({'mesh':str(prim.GetPath()),'geometry_and_normals_unchanged':True,'original_front_material_and_uv_unchanged':True,'rear_faces_with_reference_finish':int(rear.sum())})
layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(st.GetRootLayer());dest=out/'usd/compacted.usdc';layer.Export(str(dest))
finish('gold',w,out,Usd.Stage.Open(str(dest)),changes)
(out/'NOTES.md').write_text('Original installed crown geometry and front finish retained.\nThe original plain rear receives the same reference finish, projected from the rear camera direction. This first test preserves the existing oval depth; it is not a redesigned circular crown.\n')
(ROOT/'gold10_selection.json').write_text(json.dumps({'gold':'10'},indent=2)+'\n')
