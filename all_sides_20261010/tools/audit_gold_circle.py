"""Check the delivered package's band circles, independently of build notes."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model_common import *
number=json.loads((ROOT/'selection.json').read_text())['gold']
package=Path(MANIFEST['gold']['work'])/'candidates'/number/'gold_badge_mobile.usdz'
st=Usd.Stage.Open(str(package));p,*_=read_mesh(st.GetPrimAtPath('/GoldCrown/GoldCrown_TrueCircularBand'))
N=192;J=8;size=(J+1)*N;results=[]
for inner in [0,1]:
 for j in [0,J]:
  ring=p[inner*size+j*N:inner*size+(j+1)*N];center=ring.mean(0);q=ring-center
  _,_,vh=np.linalg.svd(q,full_matrices=False);normal=vh[-1]
  if normal[1]<0:normal=-normal
  radius=np.linalg.norm(q,axis=1);error=float(np.max(abs(radius-radius.mean())))
  plane_error=float(np.max(abs(q@normal)))
  assert error<1e-5 and plane_error<1e-5
  results.append({'surface':'inner' if inner else 'outer','edge':'top' if j==0 else 'bottom','radius':float(radius.mean()),'max_radius_error':error,'max_plane_error':plane_error,'axis':normal.tolist(),'tilt_degrees':float(np.degrees(np.arctan2(normal[2],normal[1])))})
report={'package_sha256':sha(package),'true_parallel_circular_band':True,'rings':results}
(ROOT/'gold_circle_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
