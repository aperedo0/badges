import sys
from PIL import Image, ImageDraw
ref=Image.open(sys.argv[1]).convert('RGB')
x0,y0,x1,y1=map(int,sys.argv[2:6]); sc=float(sys.argv[6]); out=sys.argv[7]
c=ref.crop((x0,y0,x1,y1)).resize((int((x1-x0)*sc),int((y1-y0)*sc)),Image.LANCZOS)
d=ImageDraw.Draw(c); step=int(sys.argv[8]) if len(sys.argv)>8 else 50
for x in range((x0//step+1)*step,x1,step):
    X=(x-x0)*sc; d.line([(X,0),(X,c.height)],fill=(0,200,255),width=1); d.text((X+2,2),str(x),fill=(255,255,0))
for y in range((y0//step+1)*step,y1,step):
    Y=(y-y0)*sc; d.line([(0,Y),(c.width,Y)],fill=(0,200,255),width=1); d.text((2,Y+2),str(y),fill=(255,255,0))
c.save(out)
