from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).resolve().parent
out=Image.new('RGB',(1500,1050),'#202020');dr=ImageDraw.Draw(out)
for i,n in enumerate(['rough_wood','wood_cabinet_worn_long','texturecan_wood0034']):
 d=P/'resources'/n
 for j,f in enumerate([d/'preview.png',next(d.glob('*diff*'),next(iter((d/'maps').rglob('*base*')),d/'preview.png'))]):
  im=ImageOps.contain(Image.open(f).convert('RGB'),(500,490));out.paste(im,(i*500+(500-im.width)//2,35+j*510));dr.text((i*500+10,10+j*510),n+' '+('preview' if j==0 else 'color'),fill='white')
out.save(P/'resource_sheet.jpg')
print([str(p) for p in (P/'resources/texturecan_wood0034/maps').rglob('*')])
