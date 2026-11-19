from pathlib import Path
import numpy as np,json,shutil
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AW_depth_hierarchy';C=W/'BC_final_polish';C.mkdir(exist_ok=True)
s=np.load(A/'master_height.npz');H=s['height'];edge=np.load(W/'AZ_edge_definition/master_height.npz')['height']-H;right=np.load(W/'BB_right_cohesion/master_height.npz')['height']-H;full=np.minimum(H+edge+right,0);add=full-H
np.savez_compressed(C/'master_height.npz',height=full,delta=s['delta']+add)
g=np.load(A/'surface.npz')['height'];gnew=np.minimum(g+(np.load(W/'AZ_edge_definition/surface.npz')['height']-g)+(np.load(W/'BB_right_cohesion/surface.npz')['height']-g),0);np.savez_compressed(C/'surface.npz',height=gnew)
for name in ['roughness.png','normal_masks.npz']:shutil.copy2(A/name,C/name)
shutil.copy2(W/'AX_chestnut_pigment/albedo.png',C/'albedo.png')
(C/'design.json').write_text(json.dumps(dict(source='AW_depth_hierarchy',retained=['AZ bounded broad grain transitions','BB existing right bay channel hierarchy','AX luminance preserving chestnut pigment'],unchanged=['topology','UV','normal strength','roughness','lighting','core relief','primary fracture source','fine source band'],new_features=0,correction_range=[float(add.min()),float(add.max())],checkpoint='97cce9c'),indent=2));(C/'.gitignore').write_text('geometry.blend\nnormal_frames.npz\n')
print('Combined isolated retained passes without additional features',flush=True)
