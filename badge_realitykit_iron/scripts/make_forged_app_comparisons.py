from pathlib import Path
from PIL import Image,ImageDraw
import sys
root=Path(__file__).resolve().parents[1];r=Path(sys.argv[1]).resolve();box=(330,340,875,920)
def pair(labels,images,name):
 sheet=Image.new('RGB',(1110,625),(20,20,20));dr=ImageDraw.Draw(sheet)
 for i,(label,im) in enumerate(zip(labels,images)):
  dr.text((i*565+8,8),label,fill='white');sheet.paste(im,(i*565,30))
 sheet.save(r/'proof'/name)
app=Image.open(r/'app_rest.png').convert('RGB').crop(box)
ref=Image.open(r/'source/forged_reference.png').convert('RGB').crop((52,28,1196,1172)).resize((545,545),Image.Resampling.LANCZOS)
pair(['Original forged reference',f'Forged Iron {r.name}: actual app'],[ref,app],'reference_vs_app.png')
pair(['Previous smooth Iron','Rebuilt forged Iron'],[Image.open(root/'previous/final08/proof/app_iron_rest.png').convert('RGB').crop(box),app],'before_vs_forged_app.png')
pair(['Silver: actual app','Forged Iron: actual app'],[Image.open(root/'app_reference/app_silver_rest.png').convert('RGB').crop(box),app],'app_silver_vs_iron_rest.png')
app.save(r/'proof/app_badge_crop.png')
print('Reference, previous Iron and silver app comparisons updated.')
