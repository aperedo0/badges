"""Keep the reference appearance while retaining a small live metal response."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;C=R/'candidate05';D=np.load(C/'light_solution.npz')
backup=C/'material_pass01';backup.mkdir(exist_ok=True)
for name in ['relief_color.png','relief_emission.png']:
 p=C/'textures'/name
 if not (backup/name).exists():shutil.copyfile(p,backup/name)
if not (C/'app_material_pass01.png').exists():shutil.copyfile(C/'app_front.png',C/'app_material_pass01.png')
T=D['linear'];L=D['light'];valid=D['valid'];A=D['albedo']*.012
# A pure metal removes the neutral dielectric reflection floor. Most of the reference
# tone is supplied by the allowed material color fill, avoiding a second highlight pattern.
A=np.clip(A,.00001,.012);E=np.clip(T-A*L,0,8)
from scipy.ndimage import distance_transform_edt
_,near=distance_transform_edt(~valid,return_indices=True)
for tex in [A,E]:tex[~valid]=tex[tuple(near[:,~valid])]
def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
Image.fromarray(encode(A)).save(C/'textures/relief_color.png');Image.fromarray(encode(E/8)).save(C/'textures/relief_emission.png')
p=C/'design.json';meta=json.loads(p.read_text());meta['palette']['relief']=[[.001,.001,.001],1.,.55];p.write_text(json.dumps(meta,indent=2))
fit=json.loads((C/'material_fit.json').read_text());fit.update({'reference_color_fill_dominant':True,'live_metal_fraction':.012,'metallic':1,'roughness':.55,'reason':'Reference fidelity, removing the neutral dielectric wash and duplicate highlights'});(C/'material_fit.json').write_text(json.dumps(fit,indent=2)+'\n')
np.savez_compressed(C/'final_surface_maps.npz',albedo=A,emission=E)
print('Reference surface appearance retained with a small live metal contribution')
