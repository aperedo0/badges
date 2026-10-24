"""Fit only the new reliefs to the measured app light, never the coin rim."""
from pathlib import Path
import importlib.util,json,sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,distance_transform_edt,maximum_filter

ROOT=Path(__file__).resolve().parent
TEMP=Path('/tmp/bronze_coins_20261018')
spec=importlib.util.spec_from_file_location('bronze_fit_backend',ROOT.parent/'star_island_20261016/fit_materials.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
base.ROOT=ROOT;base.TEMP=TEMP
SIZE=base.SIZE

def solve(name):
    if name!='lightning_compass':
        raise ValueError('Zen and Torch use intrinsic finishes. Run prepare_zen.py or prepare_torch.py instead.')
    layers=base.raster(name)
    reference=np.asarray(Image.open(ROOT/'references'/(name+'.png')).convert('RGB'),float)/255
    reference=gaussian_filter(reference,(.75,.75,0))
    calibration=np.asarray(Image.open(TEMP/(name+'_calibration.png')).convert('RGB'),float)/255
    yy,xx=np.indices((SIZE,SIZE));wx=(xx+.5)/SIZE*6.03-3.015;wy=3.015-(yy+.5)/SIZE*6.03
    target=base.sample(reference,623+wx*455/2.42,576-wy*455/2.42)
    z=np.full((SIZE,SIZE),-100.)
    for l in layers.values():
        m=l['cover'];z[m]=np.maximum(z[m],l['pos'][m,2])
    out=ROOT/name/'textures';out.mkdir(exist_ok=True)
    for role,layer in layers.items():
        cover,pos=layer['cover'],layer['pos'];visible=cover&(pos[:,:,2]>=z-.002)
        r,g,b=np.moveaxis(target,-1,0)
        if role=='bronze':
            valid=visible&(r>g*1.035)&(g>b*1.08)&(g>.075)
            if valid.sum()<8:valid=visible
            desired_target=base.fill(target,valid,20)
        else:
            # Intrinsic dark inset with restrained fine texture. Do not paint
            # the reference's offset emblem shadows into the backing plate.
            valid=visible&(np.max(target,axis=-1)<.24)
            if name=='zen_balance':valid &= (r<g*1.25)
            if valid.sum()<8:valid=visible
            med=np.median(target[valid],axis=0)
            lum=target.mean(-1);detail=lum-gaussian_filter(lum,3)
            detail=np.clip(detail,-.009,.009)
            desired_target=np.clip(med[None,None,:]+detail[:,:,None],.012,.25)
        screen=base.project(pos[cover]);observed=base.sample(calibration,screen[:,0]-.5,screen[:,1]-.5)
        light=np.zeros((SIZE,SIZE,3));light[cover]=np.clip(base.inverse(observed)/.15,.003,120.)
        dist=distance_transform_edt(visible);threshold=np.clip(maximum_filter(dist,size=11)*.6,.8,3.2)
        inner=visible&(dist>=threshold)
        if inner.sum()<8:inner=visible
        light=base.fill(light,inner,16)
        dist=distance_transform_edt(cover);border=cover&(dist<np.clip(maximum_filter(dist,size=11)*.6,.8,3.2))
        continued=base.fill(desired_target,cover&~border,18)
        desired_target[border]=continued[border]
        desired=base.inverse(np.clip(desired_target[cover],.006,.92))
        reflectance=np.maximum(desired/light[cover],0)
        # An unreachable bright bronze sample must dim with its hue intact.
        # Clipping RGB independently turns warm highlights yellow or green.
        reflectance/=np.maximum(1,reflectance.max(axis=-1,keepdims=True))
        color=np.zeros((SIZE,SIZE,3));color[cover]=reflectance
        color=base.fill(color,cover,8)
        Image.fromarray(base.encode(color)).save(out/(role+'_color.png'))
        print(name,role,int(cover.sum()),'fitted texels, reflective only',flush=True)

if __name__=='__main__':
    for name in sys.argv[1:]:solve(name)
