from pathlib import Path
import numpy as np
import sys,json
import OpenImageIO as o
R=Path(__file__).resolve().parent

def read(path):return np.asarray(o.ImageBuf(str(path)).get_pixels(o.UINT8))[...,:3]
def save(path,arr,labels=()):
 h,w=arr.shape[:2];b=o.ImageBuf(o.ImageSpec(w,h,3,o.UINT8));b.set_pixels(o.ROI(0,w,0,h,0,1,0,3),arr)
 # Comparisons use original on the left and the edited preview on the right.
 assert b.write(str(path)),b.geterror()
for pose in ['front','side_left','back','side_right']:
 box=(343,297,863,817) if pose=='front' else (340,120,860,640)
 images=[]
 for name in [sys.argv[1] if len(sys.argv)>1 else 'original',sys.argv[2] if len(sys.argv)>2 else json.loads((R/'draft_design.json').read_text())['active_candidate']]:
  a=read(R/name/'review'/(pose+'.png'));x0,y0,x1,y1=box;a=a[y0:y1,x0:x1];images.append(a)
  save(R/name/'review'/(pose+'_4x.png'),np.repeat(np.repeat(a,4,axis=0),4,axis=1))
 canvas=np.full((568,1064,3),18,np.uint8);canvas[40:560,8:528]=images[0];canvas[40:560,536:1056]=images[1]
 save(R/(sys.argv[2] if len(sys.argv)>2 else json.loads((R/'draft_design.json').read_text())['active_candidate'])/'review'/('comparison_'+pose+'.png'),canvas,[(15,27,'Original'),(543,27,'Emerald Sprout: rim and depth reduced 35%')])
print('Saved front and side comparisons at the same camera scale')
