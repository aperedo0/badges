from PIL import Image,ImageDraw,ImageOps
from pathlib import Path
P=Path(__file__).resolve().parent;d=P/'resources/texturecan_wood0034/maps'
a=Image.open(d/'wood_0034_color_2k.jpg').resize((1024,1024));draw=ImageDraw.Draw(a)
for y in range(0,2048,128):draw.line((0,y/2,1024,y/2),fill='red');draw.text((10,y/2+3),str(y),fill='white')
for x in range(0,2048,256):draw.line((x/2,0,x/2,1024),fill='cyan');draw.text((x/2+3,20),str(x),fill='white')
a.save(P/'texturecan_grid.jpg')
