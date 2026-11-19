from pathlib import Path
import numpy as np,json,shutil
from PIL import Image
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AE_controlled_fibers';C=W/'AF_true_normal';C.mkdir(exist_ok=True)
for name in ['geometry.blend','normal_frames.npz','surface.npz','master_height.npz','albedo.png','roughness.png']:shutil.copy2(A/name,C/name)
# Reuse the calibrated geometry basis and boundary guard, changing only the target normal.
s=(D/'solve_normals.py').read_text();s=s.replace("wanted=norm(np.stack([effective[:,:,0]/den-gx,effective[:,:,1]/den+gy,effective[:,:,2]/den],2))", "gy,gx=np.gradient(full['height'].astype(float),dy,dx);wanted=norm(np.stack([-gx,gy,np.ones_like(gx)],2))")
import sys
sys.argv=['solve','AF_true_normal'];exec(compile(s,'absolute_normal_control','exec'))
d=json.loads((A/'design.json').read_text());d.update(source='AE with full height gradient shading normal projected against actual mesh basis',geometry_and_albedo_roughness='AE identical',normal_scope='Isolates inherited V normal reconstruction versus source height');(C/'design.json').write_text(json.dumps(d,indent=2));print('Normal control ready')
