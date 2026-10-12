"""Keep the circular band's finish continuous through both side joins."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
w=Path(MANIFEST['gold']['work']);out=w/'candidates/20';out.mkdir(exist_ok=True)
assert not (out/'usd').exists();shutil.copytree(w/'candidates/19/usd',out/'usd')
st=Usd.Stage.Open(str(out/'usd/compacted.usdc'))
source=Usd.Stage.Open(str(w/'source/installed/badge.usdc'))
bp,bf,bn,bm,bu=read_mesh(source.GetPrimAtPath('/GoldCrown/GoldCrown_HollowBand'))
source_uv=np.zeros((len(bp),2));count=np.zeros(len(bp))
for a in list(bu.values())[:1]:
 for c in range(3):np.add.at(source_uv,bf[:,c],a[:,c]);np.add.at(count,bf[:,c],1)
source_uv/=np.maximum(count[:,None],1)
prim=st.GetPrimAtPath('/GoldCrown/GoldCrown_TrueCircularBand');p,f,n,m,uv=read_mesh(prim)
N=192;J=8;vuv=[]
for inner in [False,True]:
 for j in range(J+1):
  t=j/J*6;low=int(np.floor(t));high=min(6,low+1);mix=t-low
  for a in np.arange(N)*2*np.pi/N:
   # Reflection rather than a half-circle reset meets exactly at both joins.
   # The complete front half and the inner band keep their previous UVs.
   aa=a if inner or np.cos(a)>=0 else np.pi-a
   k=aa%(2*np.pi)*128/(2*np.pi);k0=int(k)%128;k1=(k0+1)%128;frac=k-np.floor(k)
   offset=896 if inner else 0
   value=(1-mix)*((1-frac)*source_uv[offset+low*128+k0]+frac*source_uv[offset+low*128+k1])+mix*((1-frac)*source_uv[offset+high*128+k0]+frac*source_uv[offset+high*128+k1])
   vuv.append(value)
uv['BadgeUV']=np.array(vuv)[f]
write_mesh(st,prim.GetPath(),p,f,n,m,uv)
old=json.loads((w/'candidates/19/build.json').read_text())['changes']
layer=Sdf.Layer.CreateAnonymous();layer.TransferContent(st.GetRootLayer());dest=out/'usd/continuous.usdc';layer.Export(str(dest));shutil.copyfile(dest,out/'usd/compacted.usdc')
finish('gold',w,out,Usd.Stage.Open(str(dest)),old+[{'circular_band_side_uv_continuous':True,'front_half_and_inner_band_unchanged':True,'reason':'The former half-turn UV reset left a narrow vertical color seam on each side of the circular band.'}])
(ROOT/'gold20_selection.json').write_text(json.dumps({'gold':'20'})+'\n')
