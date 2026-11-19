from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
W=Path(__file__).resolve().parent;P=W.parent;C=W/'P_physical_fractures';R=W/'review';R.mkdir(exist_ok=True)
def panel(items,name,size):
 out=Image.new('RGB',(size[0]*len(items),size[1]+32),'#202020')
 for i,(path,title) in enumerate(items):
  im=ImageOps.contain(Image.open(path).convert('RGB'),size);x=i*size[0];out.paste(im,(x+(size[0]-im.width)//2,32+(size[1]-im.height)//2));ImageDraw.Draw(out).text((x+10,10),title,fill='white')
 out.save(R/name,quality=94)
panel([(P.parents[1]/'phase03/wood_sample44/reference_wood_close.png','Owner reference'),(W/'baseline_cinema.png','Preserved baseline'),(C/'cinema_close.png','Current test plank')],'wood_comparison.jpg',(650,500))
panel([(P.parents[1]/'reference.png','Owner reference'),(P/'final_renders/master_cinema_full.png','Preserved baseline'),(C/'cinema_full.png','Current: one plank only')],'whole_comparison.jpg',(500,500))
panel([(C/'neutral_close.png','Neutral light'),(C/'clay_graze.png','Actual geometry only, grazing light')],'relief_diagnostics.jpg',(700,520))
print(R.resolve())
