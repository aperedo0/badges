"""Fit relief colors against measured Home light, keeping the rim untouched."""
from pathlib import Path
import sys,json,importlib.util,shutil
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,distance_transform_edt,maximum_filter
ROOT=Path(__file__).resolve().parent;TEMP=Path('/tmp/emerald_archer_20261023')
spec=importlib.util.spec_from_file_location('archer_fit_helpers',ROOT.parent/'star_island_20261016/fit_materials.py')
fit=importlib.util.module_from_spec(spec);spec.loader.exec_module(fit)
fit.ROOT=ROOT;fit.TEMP=TEMP
agx=fit.inverse.__globals__['agx'];agx_inv=fit.inverse.__globals__['agx_inv']
def inverse(target):
    lin=np.clip(agx_inv(target),2**-12,64.)
    best=lin.copy();best_error=np.full(target.shape[:-1],np.inf)
    for _ in range(16):
        value=agx(lin);error=target-value;cost=(error*error).sum(-1)
        better=cost<best_error;best[better]=lin[better];best_error=np.minimum(cost,best_error)
        jac=np.empty(lin.shape[:-1]+(3,3))
        for c in range(3):
            changed=lin.copy();changed[...,c]*=1.035
            jac[...,c]=(agx(changed)-value)/np.log(1.035)
        lhs=np.einsum('...ji,...jk->...ik',jac,jac)+np.eye(3)*.00003
        rhs=np.einsum('...ji,...j->...i',jac,error)
        delta=np.linalg.solve(lhs,rhs[...,None])[...,0]
        lin=np.clip(lin*np.exp(np.clip(delta,-.7,.7)),2**-12,64.)
    return best
fit.inverse=inverse
(TEMP/'candidate01_geometry.npz').write_bytes((TEMP/'emerald_archer_geometry.npz').read_bytes())
layers=fit.raster('candidate01');SIZE=fit.SIZE
meta=json.loads((ROOT/'candidate01/design.json').read_text());palette=meta['palette']
ref=gaussian_filter(np.asarray(Image.open(ROOT/'reference.png').convert('RGB'),float)/255,(1.0,1.0,0))
shot=np.asarray(Image.open(TEMP/'app_front.png').convert('RGB'),float)/255
yy,xx=np.indices((SIZE,SIZE));wx=(xx+.5)/SIZE*6.03-3.015;wy=3.015-(yy+.5)/SIZE*6.03
target=fit.sample(ref,627+wx*458/2.42,566-wy*458/2.42)
z=np.full((SIZE,SIZE),-100.)
for layer in layers.values():z[layer['cover']]=np.maximum(z[layer['cover']],layer['pos'][layer['cover'],2])
out=ROOT/'candidate02';(out/'textures').mkdir(parents=True,exist_ok=True);(out/'mobile').mkdir(exist_ok=True)
shutil.copyfile(ROOT/'candidate01/design.json',out/'design.json')
for role,layer in layers.items():
    if role in ['gold_edge','gold_vein','setting_shadow']:continue
    cover,pos=layer['cover'],layer['pos'];visible=cover&(pos[:,:,2]>=z-.002)
    r,g,b=np.moveaxis(target,-1,0)
    if role=='gold':valid=visible&(r>g*1.08)&(g>b*1.45)&(g>.20)
    else:valid=visible&(g>r*1.4)&(g>b*1.15)
    if valid.sum()<8:valid=visible
    dist=distance_transform_edt(visible)
    inner=valid&(dist>=np.clip(maximum_filter(dist,size=9)*.65,.6,2.4))
    if inner.sum()<8:inner=valid
    continued=fit.fill(target,inner,16)
    # Blend the field target broadly so carved object shadows cannot become marks.
    if role=='field':continued=gaussian_filter(continued,(7,7,0))
    screen=fit.project(pos[cover]);observed=fit.sample(shot,screen[:,0]-.5,screen[:,1]-.5)
    light=np.zeros((SIZE,SIZE,3));old=np.array(palette[role][0])
    light[cover]=fit.inverse(np.clip(observed,.005,.995))/old
    light=fit.fill(np.clip(light,.001,1000),inner,12)
    desired=fit.inverse(np.clip(continued,.004,.91))
    albedo=np.clip(desired/np.maximum(light,.001),1e-6,1.)
    glow=np.maximum(desired-albedo*light,0)
    # The stones can fill light the studio cannot supply. Gold remains reflective.
    if not role.startswith('emerald'):glow*=0
    albedo=fit.fill(albedo,cover,8)
    Image.fromarray(fit.encode(albedo)).save(out/'textures'/(role+'_color.png'))
    if role.startswith('emerald'):
        glow=fit.fill(np.clip(glow,0,1),cover,8)
        Image.fromarray(fit.encode(glow)).save(out/'textures'/(role+'_emission.png'))
    if role=='field':shutil.copyfile(ROOT/'candidate01/textures/field_roughness.png',out/'textures/field_roughness.png')
    print(role,': measured',int(inner.sum()),'interior samples',flush=True)
print('Rim geometry, material graphs, and rim maps excluded from fitting')
