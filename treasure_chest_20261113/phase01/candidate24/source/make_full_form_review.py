from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'phase01/candidate24'
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',22)
ref=Image.open(R/'reference.png').convert('RGB').resize((1100,1100),Image.Resampling.LANCZOS)
new=Image.open(C/'reference.png').convert('RGB')
canvas=Image.new('RGB',(2200,1140),'white');canvas.paste(ref,(0,40));canvas.paste(new,(1100,40));d=ImageDraw.Draw(canvas);d.text((25,8),'Owner reference: proportions and inspiration',fill='black',font=font);d.text((1125,8),'Phase 1: complete solid construction',fill='black',font=font);canvas.save(C/'comparison.png')
views=[n for n in ['reference','straight_front','left_end','right_end','back','joint_oblique'] if (C/(n+'.png')).exists()];out=Image.new('RGB',(1650,1160),(230,230,230));d=ImageDraw.Draw(out)
for i,n in enumerate(views):
 im=Image.open(C/(n+'.png')).convert('RGB').resize((550,550),Image.Resampling.LANCZOS);x=(i%3)*550;y=(i//3)*580;out.paste(im,(x,y+30));d.text((x+15,y+3),n.replace('_',' ').title(),fill='black',font=font)
out.save(C/'all_views.png')
new.save(C/'finish_full_size.png');up=new.resize((2200,2200),Image.Resampling.NEAREST)
for i,(x,y) in enumerate([(0,0),(1100,0),(0,1100),(1100,1100)]):up.crop((x,y,x+1100,y+1100)).save(C/f'finish_2x_{i}.png')
new.crop((535,410,840,820)).resize((1220,1640),Image.Resampling.NEAREST).save(C/'finish_4x_hardware.png')
new.crop((50,370,400,610)).resize((1400,960),Image.Resampling.NEAREST).save(C/'finish_4x_corner.png')
print('Saved comparison, available rendered views and full coverage finish crops')

for name,box in [('lock',(515,360,870,835)),('corner',(205,355,465,600)),('foot',(180,700,475,980)),('handle',(100,490,340,810)),('crown_tab',(145,150,285,295))]:
 a=ref.crop(box);b=new.crop(box);w,h=a.size;pair=Image.new('RGB',(w*4,h*2));pair.paste(a.resize((w*2,h*2),Image.Resampling.LANCZOS),(0,0));pair.paste(b.resize((w*2,h*2),Image.Resampling.LANCZOS),(w*2,0));pair.save(C/('close_'+name+'.png'))

change=Image.new('RGB',(2100,740),'white');draw=ImageDraw.Draw(change)
for i,(title,im) in enumerate([('Reference',ref),('Previous construction',Image.open(R/'phase01/candidate21/reference.png').convert('RGB')),('Updated construction',new)]):
 change.paste(im.resize((700,700),Image.Resampling.LANCZOS),(i*700,40));draw.text((i*700+20,8),title,fill='black',font=font)
change.save(C/'changes.png')
