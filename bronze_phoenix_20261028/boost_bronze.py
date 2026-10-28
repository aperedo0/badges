"""Increase the reviewed bronze reflection strength in linear light."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

ROOT=Path(__file__).resolve().parent;R=ROOT/'phoenix';source=R/'candidate03';C=R/'candidate04';factor=1.15
if C.exists():raise RuntimeError('Candidate already exists: '+str(C))
C.mkdir();(C/'mobile').mkdir()
for name in ['geometry.npz','polished_normals.npz','trace.json','gems.json','material_fit.json']:
 if (source/name).exists():shutil.copyfile(source/name,C/name)
shutil.copytree(source/'textures',C/'textures')
def decode(a):return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
texture=np.asarray(Image.open(source/'textures/surface_color.png').convert('RGB'),float)/255
linear=decode(texture);data=np.load(source/'metal_surface.npz');bronze=data['category']==3;valid=data['valid']
linear[bronze]*=factor
_,nearest=distance_transform_edt(~valid,return_indices=True);linear[~valid]=linear[tuple(nearest[:,~valid])]
Image.fromarray(encode(linear)).save(C/'textures/surface_color.png')
finish=json.loads((source/'metal_finish.json').read_text())
finish['edge_colors']['gold_edge']=[value*factor for value in finish['edge_colors']['gold_edge']]
finish.update(bronze_reflection_multiplier=factor,reflection_baseline='candidate03',roughness_preserved=True,geometry_preserved=True,amber_face_material_preserved=True)
(C/'metal_finish.json').write_text(json.dumps(finish,indent=2)+'\n')
(C/'NOTES.txt').write_text('Increased bronze face and wall reflectance by 15 percent in linear light.\nRetained the reviewed roughness, geometry, reference fill and amber facet finish.\n')
(R/'candidate.txt').write_text(C.name+'\n')
print('Prepared',C.name,'with bronze reflection multiplier',factor)
