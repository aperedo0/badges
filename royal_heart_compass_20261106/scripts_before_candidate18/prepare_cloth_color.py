"""Apply measured geometric visibility to cloth diffuse, never to gems or metal."""
from pathlib import Path
import shutil,numpy as np,json,sys
from PIL import Image
R=Path(__file__).resolve().parent;C=R/(sys.argv[1] if len(sys.argv)>1 else 'amethyst_crown')/'candidate17';B=C/'previous_material';B.mkdir(exist_ok=True)
for p in [C/'model.usdz',C/'source'/(C.parent.name+'.blend'),C/'source'/(C.parent.name+'_compact.blend'),C/'review/native_front_precheck.png',C/'review/reference_comparison.png']:
 if p.exists() and not (B/p.name).exists():shutil.copy2(p,B/p.name)
ao=np.asarray(Image.open(C/'textures/velvet_occlusion.png').convert('L'),float)/255
intrinsic=C/'textures/velvet_cap_intrinsic.png'
if not intrinsic.exists():intrinsic=C/'textures/velvet_color.png'
rgb=np.asarray(Image.open(intrinsic).convert('RGB'),float)/255
linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
visibility=.12+.88*ao**1.8
linear*=visibility[...,None]
rgb=np.where(linear<=.0031308,linear*12.92,1.055*np.maximum(linear,0)**(1/2.4)-.055)
Image.fromarray(np.uint8(np.clip(rgb,0,1)*255)).save(C/'textures/velvet_fold_color.png')
(C/'cloth_finish.json').write_text(json.dumps(dict(ambient_occlusion_from_real_geometry=True,lights_baked=False,diffuse_visibility_floor=.12,diffuse_visibility_power=1.8,reason='Native point lights keep filling recesses. Geometric visibility is included in cloth diffuse to retain the fold depth under the fixed studio.',native_review_pending=True),indent=2)+'\n')
p=R/'pack.py';s=p.read_text();s=s.replace("filename='chart_color.png' if role=='navy' else 'velvet_color.png' if role.endswith('_velvet') else ''", "filename='chart_color.png' if role=='navy' else 'velvet_fold_color.png' if role.endswith('_fold_velvet') and (C/'textures/velvet_fold_color.png').exists() else 'velvet_color.png' if role.endswith('_velvet') else ''");p.write_text(s)
