from pathlib import Path
import json
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter, distance_transform_edt
ROOT=Path(__file__).resolve().parents[1]
# Derive restrained broad forged color from the reference, removing its lighting.
a=np.array(Image.open(ROOT/'source/iron_reference.png').convert('RGB'),float)/255
lum=a.mean(2);mask=lum>.07
smooth=gaussian_filter(lum,5)
base=gaussian_filter(lum*mask,12)/np.maximum(gaussian_filter(mask.astype(float),12),.01)
detail=(smooth-base)/np.maximum(base,.12)
valid=mask&(distance_transform_edt(mask)>24)
scale=np.percentile(np.abs(detail[valid]),97)
detail=np.clip(detail/max(scale,.001),-1,1)*np.clip((distance_transform_edt(mask)-12)/24,0,1)
Image.fromarray(np.uint8(np.clip(detail*.5+.5,0,1)*255)).save(ROOT/'source/forged_field.png')
