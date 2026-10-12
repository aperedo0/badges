import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['platinum']['work']);out=w/'candidates/11';out.mkdir(exist_ok=True)
assert not (out/'usd').exists();shutil.copytree(w/'candidates/08/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'));cal=shader_material(st,'RearLightCalibration',[.12,.12,.12],.32)
for prim in [p for p in st.Traverse() if p.IsA(UsdGeom.Mesh)]:
 p,f,n,m,uv=read_mesh(prim);row=(np.arange(len(f))//2)%28;rear=np.isin(row,np.arange(17,25));m[rear]=cal
 write_mesh(st,prim.GetPath(),p,f,n,m,uv)
layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(st.GetRootLayer());dest=out/'usd/calibration.usdc';layer.Export(str(dest));shutil.copyfile(dest,out/'usd/compacted.usdc')
finish('platinum',w,out,Usd.Stage.Open(str(dest)),[{'calibration_only':True,'purpose':'Measure the real rear studio illumination so the front polish can be solved onto the rear rather than layered with mismatched highlights.'}])
(ROOT/'platinum11_selection.json').write_text(json.dumps({'platinum':'11'})+'\n')
