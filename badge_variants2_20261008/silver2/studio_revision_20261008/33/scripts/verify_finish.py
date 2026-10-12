"""All export checks for a frozen finish candidate, with complete raw outputs."""
from pathlib import Path
import sys,runpy,contextlib,json
import bpy
import numpy as np
from pxr import Usd,UsdShade,UsdGeom
ROOT=Path(__file__).resolve().parents[1]
kind=sys.argv[sys.argv.index('--')+1]
base=ROOT/kind
model=base/'mobile'/f'{kind}_badge_mobile.usdz'


def check(script,args,log):
    sys.argv=[str(ROOT/'scripts'/script),'--',*map(str,args)]
    with (base/'reports'/log).open('w') as out,contextlib.redirect_stdout(out):
        runpy.run_path(str(ROOT/'scripts'/script),run_name='__main__')


check('shape_check.py',[kind],'shape_checks.txt')
check('compare_finish.py',[kind],'compare_finish.txt')
check('compare_usd.py',[ROOT/'source/silver_base.usdz',model,base/'reports/compare_usd.json'],'compare_usd.txt')
check('reimport_check.py',[model],'reimport_check.txt')
stage=Usd.Stage.Open(str(model))
maps=[]
for prim in stage.Traverse():
    if not prim.IsA(UsdShade.Shader):continue
    shader=UsdShade.Shader(prim)
    if shader.GetIdAttr().Get()=='UsdPrimvarReader_float2':
        assert shader.GetInput('varname').Get()=='USDZ_UV'
    if shader.GetIdAttr().Get()!='UsdUVTexture':continue
    name=str(prim.GetPath());normal=name.endswith('/normal')
    assert shader.GetInput('sourceColorSpace').Get()==('sRGB' if name.endswith('/diffuseColor') else 'raw')
    if normal:
        assert kind=='iron2'
        assert any(f'Iron2_{part}_Satin/' in name for part in ['PlateLeft','PlateRight','Border'])
        assert tuple(shader.GetInput('scale').Get())==(2,2,2,1)
        assert tuple(shader.GetInput('bias').Get())==(-1,-1,-1,0)
    maps.append({'shader':name,'normal':normal,'file':str(shader.GetInput('file').Get())})
# Read the actual exported PNGs rather than just the intended source gradients.
normal_stats=[]
for p in (base/'mobile/textures').glob('*_normal.png'):
    image=bpy.data.images.load(str(p));image.colorspace_settings.name='Non-Color'
    rgb=np.array(image.pixels[:]).reshape(image.size[1],image.size[0],4)[:,:,:3]
    n=2*rgb-1;n/=np.linalg.norm(n,axis=2,keepdims=True)
    tilt=np.degrees(np.arccos(np.clip(n[:,:,2],-1,1)))
    y=np.linspace(-3.015,3.015,image.size[1])
    low=n[y<-2.455+.20*json.loads((base/'reports/build.json').read_text())['height']]
    delta=float(np.linalg.norm(low-low[0,0],axis=2).max())
    normal_stats.append({'file':p.name,'max_actual_tilt_degrees':float(tilt.max()),'mean_tilt_degrees':float(tilt.mean()),'lower_fifth_normal_variation':delta})
    assert delta==0
    assert float(tilt.max())<3.6
    bpy.data.images.remove(image)
out={'all_shader_spaces_and_UV_readers_correct':True,'strength_baked_in_PNG':True,'normal_maps':normal_stats,'texture_connections':maps}
(base/'reports/texture_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(kind,'PASS: ARKit, shape bounds/names/axes, identical geometry, USD comparison, reimport, UV/colorspaces, baked normal strength and plain lower fifth.')
