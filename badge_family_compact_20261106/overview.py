from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parent;rows=json.loads((R/'manifest.json').read_text());res=json.loads((R/'results.json').read_text());rows=[r for r in rows if res[r['key']]['status']=='validated_candidate']
for start in range(0,len(rows),5):
 sheet=Image.new('RGB',(1500,1025),(20,20,22));d=ImageDraw.Draw(sheet)
 for y,row in enumerate(rows[start:start+5]):
  for x,pose in enumerate(['front','angle','side_left','back','side_right']):
   im=Image.open(R/'badges'/row['slug']/'candidate01'/('blender_'+pose+'.png')).convert('RGB');im.thumbnail((300,180));sheet.paste(im,(x*300,y*205+22));d.text((x*300+3,y*205+4),row['title']+' '+pose,fill='white')
 sheet.save(R/('blender_overview_'+str(start//5+1)+'.jpg'))
