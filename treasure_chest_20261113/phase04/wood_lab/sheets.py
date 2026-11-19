from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).resolve().parent;R=P.parents[1]
def row(items,output,size=(680,340)):
 im=Image.new('RGB',(size[0]*len(items),size[1]+30),'#171717');d=ImageDraw.Draw(im)
 for i,(f,t) in enumerate(items):
  q=ImageOps.contain(Image.open(f).convert('RGB'),size);im.paste(q,(size[0]*i+(size[0]-q.width)//2,30+(size[1]-q.height)//2));d.text((size[0]*i+10,9),t,fill='white')
 im.save(P/output)
row([(P/'renders'/f'{k}_warm_plank.png',t) for k,t in zip('ABC',['A: existing normal mapped plank','B: same height, actual geometry','C: scanned wood, adapted pigment'])],'screen_warm.jpg')
row([(P/'renders'/f'{k}_neutral_plank.png',t) for k,t in zip('ABC',['A: existing normal mapped plank','B: same height, actual geometry','C: scanned wood, adapted pigment'])],'screen_neutral.jpg')
