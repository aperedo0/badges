from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,map_coordinates,distance_transform_edt
ROOT=Path(__file__).resolve().parents[1]
work=Path(json.loads((ROOT/'manifest.json').read_text())['steel']['work'])
out=work/'candidates/02';edit=out/'usd'
base=Path('/Users/antonioperedo/Desktop/badges/bronze_silver_20261009/silver/source')
SIZE=1024
def mask(name):
 d=np.load(base/(name+'.npz'));uv=d['uv'];f=d['faces'][d['roles']==0]
 im=Image.new('L',(SIZE,SIZE));draw=ImageDraw.Draw(im)
 for tri in f:draw.polygon([tuple(v) for v in np.stack([uv[tri,0]*SIZE,(1-uv[tri,1])*SIZE],-1)],fill=255)
 return np.array(im)>0
upper=mask('SilverChevron_Upper');lower=mask('SilverChevron_Lower');dist=distance_transform_edt(lower)
yy,xx=np.mgrid[:SIZE,:SIZE];delta=288.6/1254*SIZE
blend=np.clip((dist-9)/9,0,1);blend=blend**2*(3-2*blend)
report={'cause':'The reference solve fades directional brushing between 19% and 44% of total badge height, which suppresses the lower chevron interior.','method':'Restore matching upper-chevron fine detail in lower interior while retaining lower broad lighting and unchanged 9-texel outline band.','maps':{}}
for name in ['color.png','emissive.png']:
 path=next(edit.rglob(name));a=np.array(Image.open(path).convert('RGB'),float)/255
 low=gaussian_filter(a,[3,3,0]);res=a-low
 translated=np.stack([map_coordinates(res[...,c],[yy-delta,xx],order=1,mode='nearest') for c in range(3)],-1)
 target=np.clip(low+translated,0,1)
 updated=a*(1-blend[...,None])+target*blend[...,None]
 # Only lower geometry texels change; UV padding remains exactly as shipped.
 updated[~lower]=a[~lower]
 raw=np.uint8(np.clip(updated,0,1)*255+.5);Image.fromarray(raw).save(path,optimize=True)
 interior=dist>18;up_in=distance_transform_edt(upper)>18
 report['maps'][name]={'upper_detail_rms':float(np.sqrt((res[up_in]**2).mean())),'lower_before_detail_rms':float(np.sqrt((res[interior]**2).mean())),'lower_after_detail_rms':float(np.sqrt(((updated-gaussian_filter(updated,[3,3,0]))[interior]**2).mean())),'changed_texels':int(np.any(raw!=np.uint8(a*255+.5),-1).sum()),'outline_unchanged':bool((raw[lower&(dist<=9)]==np.uint8(a[lower&(dist<=9)]*255+.5)).all())}
(out/'sharpness.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
