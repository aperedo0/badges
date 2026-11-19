from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
S=Path(__file__).resolve().parent;C=S/'candidate02';R=C/'review';R.mkdir(exist_ok=True);B=S.parents[1]
def panel(items,name,size):
 rows=[]
 for path,label in items:
  im=ImageOps.contain(Image.open(path).convert('RGB'),size);a=Image.new('RGB',(size[0],size[1]+30),'#202020');a.paste(im,((size[0]-im.width)//2,30+(size[1]-im.height)//2));ImageDraw.Draw(a).text((10,8),label,fill='white');rows.append(a)
 out=Image.new('RGB',(size[0]*len(rows),size[1]+30))
 for i,a in enumerate(rows):out.paste(a,(size[0]*i,0))
 out.save(R/name)
panel([(B/'reference.png','Owner reference'),(C/'front.png','One test plank: actual Blender render')],'whole.png',(600,600))
panel([(B/'phase03/wood_sample44/reference_wood_close.png','Owner reference wood'),(C/'grain_close.png','Actual Blender close render')],'close.png',(760,580))
panel([(C/'grain_close.png','Normal map active'),(C/'grain_flat_normal_control.png','Diagnostic: normals flat')],'normal_control.png',(650,475))
panel([(C/'grain_close.png','Original studio key'),(C/'grain_opposed_key.png','Key light moved to opposite side')],'light_response.png',(650,475))
panel([(C/(n+'.png'),n) for n in ['front','turn08','turn12','turn16','turn45']],'turns.png',(300,300))
(R/'brief.md').write_text("""Scoped fresh visual material review. Open every listed image in one batch before responding. Judge pictures only. Exactly one lower front plank is being developed. Other wood and all metal are deliberately gray and must not be graded as absent finishes. Owner now explicitly targets high quality STYLIZED medieval fantasy RPG wood, not photographic wood. The reference itself is the visual ground truth: saturated burnt orange and reddish brown, dark brown recessed grain, thick irregular flowing grooves, sculpted knot and split, hand carved broken shoulders, readable large and medium forms, little fine noise, rough rather than plastic. Evaluate the actual rendered wood, not whether a shader is valid. Compare palette, grain thickness, knot, contrast, roughness, sculptural depth and style with the reference. The flat normal diagnostic removes the normal map; the opposed key diagnostic moves one existing light to the other side and then restores it. Virtual normals do not produce real silhouette displacement or groove occlusion. Nearby stills cannot prove a continuous full turn. At small whole chest scale check for fuzzy edges, shiny plastic or crawling fine marks. Reply READY FOR OWNER JUDGMENT: yes or no, then WOOD CHARACTER, VISIBLE ISSUES, DEPTH AND MOTION LIMITS. Be blunt about what still looks drawn, smooth, inflated, printed, too coarse or mismatched. Do not grade full badge shippability or give a final phone score. Read no other file and change nothing.

"""+'\n'.join(str((R/n).resolve()) for n in ['whole.png','close.png','normal_control.png','light_response.png','turns.png'])+'\n')
print(R.resolve())
