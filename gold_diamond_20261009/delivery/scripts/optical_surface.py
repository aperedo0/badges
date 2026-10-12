"""Use measured optical color where studio specular response adds artifacts."""
from pathlib import Path
import json,sys,shutil
import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from solve import encode
BASE=ROOT/'diamond';previous=BASE/'candidates/03';out=BASE/'candidates/04'
out.mkdir(parents=True,exist_ok=True);(out/'textures').mkdir(exist_ok=True)
d=np.load(previous/'texture_mapping.npz');cover=d['cover'];total=np.load(previous/'total.npz')['total'];light=d['light']
# Keep a small real reflected component. The reference's optical interior
# has a stable emissive component, rather than amplifying imperfectly
# reconstructed colored studio reflections with a high albedo.
albedo=np.minimum(total/np.maximum(light,1e-5),1)*.01
emission=np.maximum(total-albedo*light,0);scale=4.
assert emission[cover].max()<scale
_,(iy,ix)=distance_transform_edt(~cover,return_indices=True)
Image.fromarray(encode(albedo[iy,ix])).save(out/'textures/color.png',optimize=True)
Image.fromarray(encode(emission[iy,ix]/scale)).save(out/'textures/emissive.png',optimize=True)
cfg=json.loads((previous/'settings.json').read_text());cfg.update(emissive_scale=scale,optical_surface=True)
(out/'settings.json').write_text(json.dumps(cfg,indent=2)+'\n')
(out/'solve.json').write_text(json.dumps({'reference_total_from':'candidates/03','reflected_component_fraction':.01,'emissive_scale':scale,'emission_clipped_fraction':0},indent=2)+'\n')
shutil.copy2(previous/'texture_mapping.npz',out/'texture_mapping.npz')
(out/'NOTES.md').write_text('Used the solved reference optical color as a stable emissive component with 1% of the calibrated reflection component.\nPurpose: remove colored studio-reflection noise from dark blue facets while retaining the real closed crystal, flat facet normals and floor reflection.\n')
print('Prepared measured optical surface:',out)
