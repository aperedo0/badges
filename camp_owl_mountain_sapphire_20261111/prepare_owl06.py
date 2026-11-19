"""Match the actual gold rim width measured on the owner's mockup."""
from pathlib import Path
import numpy as np,json,shutil
R=Path(__file__).resolve().parent;A=R/'amber_owl/candidate05';C=A.parent/'candidate06';assert not C.exists();C.mkdir()
for f in ['parts.npz','parts.json','enamel_config.json','color_role_fix.json']:shutil.copy2(A/f,C/f)
D=dict(np.load(C/'parts.npz'));M=json.loads((C/'parts.json').read_text());U=M['units'];S=U['S'];name='outer_gold_setting';V=D[name+'_v'];center=np.array([(626-U['axis'])*S,2.995-(604.5-U['top'])*S]);r=np.array([586,582.5])*S;xy=V[...,:2]-center;q=np.sqrt(((xy/r)**2).sum(2));new=1-(1-q)*(54/25);V[...,:2]=center+xy*(new/q)[...,None]
np.savez_compressed(C/'parts.npz',**D)
(C/'rim_measurement.json').write_text(json.dumps(dict(reference_row=605,reference_outer_x=40,reference_first_blue_x=94,old_band_width_source_pixels=25,new_band_width_source_pixels=54,outer_outline_preserved=True,reason='The narrow modeled rim exposed reference gold in the blue field texture. This version models the measured full band instead.',blender_review_pending=True),indent=2)+'\n');print('Matched measured owl rim width54 source pixels, outer silhouette unchanged')
