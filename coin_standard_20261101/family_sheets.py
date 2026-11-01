"""Create compact contact sheets for visual review, without changing badge images."""
from pathlib import Path
import json,sys
import numpy as np
import OpenImageIO as oiio
R=Path(__file__).resolve().parent;F=R/'family'
names=[x['name'] for x in json.loads((F/'manifest.json').read_text())]
mode=sys.argv[1] if len(sys.argv)>1 else 'blender'
for pose in (['front','side_left','back','side_right'] if mode=='blender' else ['front','early_turn','side_left','back','side_right','full_turn']):
    grid=np.zeros((3*360,4*360,3),dtype=np.uint8)
    for i,name in enumerate(names):
        path=F/name/'candidate01/review'/((('blender_' if mode=='blender' else '')+pose)+'.png')
        img=oiio.ImageBuf(str(path));arr=np.asarray(img.get_pixels(oiio.UINT8))[:,:,:3]
        if mode=='blender':
            h,w=arr.shape[:2];arr=arr[int(h*.04):int(h*.96),int(w*.18):int(w*.82)]
        else:
            arr=arr[297:817,343:863] if pose=='front' else arr[120:640,340:860]
        buf=oiio.ImageBuf();buf.reset(oiio.ImageSpec(arr.shape[1],arr.shape[0],3,oiio.UINT8));buf.set_pixels(buf.roi,arr)
        scale=350/max(arr.shape[:2]);height=round(arr.shape[0]*scale);width=round(arr.shape[1]*scale)
        small=oiio.ImageBuf(oiio.ImageSpec(width,height,3,oiio.UINT8));oiio.ImageBufAlgo.resize(small,buf)
        y=(i//4)*360+(350-height)//2;x=(i%4)*360+(350-width)//2
        grid[y:y+height,x:x+width]=np.asarray(small.get_pixels(oiio.UINT8))
    out=oiio.ImageBuf();out.reset(oiio.ImageSpec(grid.shape[1],grid.shape[0],3,oiio.UINT8));out.set_pixels(out.roi,grid)
    out.write(str(F/(mode+'_'+pose+'.png')))
print('Contact sheet rows follow manifest order:',', '.join(names))
