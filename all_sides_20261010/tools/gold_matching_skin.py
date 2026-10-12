import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['gold']['work']);out=w/'candidates/11'
if (out/'usd/badge.usdc').exists():st=Usd.Stage.Open(str(out/'usd/badge.usdc'))
else:w,out,st=open_copy('gold','11')
wall=shader_material(st,'GoldCrown_MatchingTurnEdges',[.18,.09,.012],.65)
notes=[]
for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
 if any(k in prim.GetName() for k in ['Lip','Collar','Flange']):
  # Closed rolled details are copied intact. Splitting a tiny tubular ring
  # at a grazing triangle produces a pinched seam at a zero-width vertex.
  clone_mesh(st,prim,prim.GetName()+'_MatchingRear',0)
  notes.append({'mesh':str(prim.GetPath()),'original_preserved':True,'rear_detail_copied':True})
  continue
 note=mirror_skin(st,prim,wall,center=0);notes.append(note)
 # The global reference chart must face the viewer from the rear too.
 p,f,n,m,uv=read_mesh(prim);count=note['front_triangles_preserved']
 if not note['paired_mirror_x']:
  for a in uv.values():a[count:count*2,:,0]=1-a[count:count*2,:,0]
  write_mesh(st,prim.GetPath(),p,f,n,m,uv)
layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(st.GetRootLayer());dest=out/'usd/compacted.usdc';layer.Export(str(dest))
finish('gold',w,out,Usd.Stage.Open(str(dest)),notes)
(ROOT/'gold11_selection.json').write_text(json.dumps({'gold':'11'})+'\n')
