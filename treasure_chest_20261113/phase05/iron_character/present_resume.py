from pathlib import Path
import sys,json
D=Path(__file__).resolve().parent;source=(D.parent/'iron_fidelity/present.py').read_text().split('ref=Image.open(R)')[0];exec(compile(source,'existing_comparison_helpers','exec'));env=json.loads((D/'selection.json').read_text())['environment'];left=C/('iron_'+env+'_final.png');right=C/('right_'+env+'_final.png');context=C/('context_'+env+'_final.png');start=D/'11_restored_pigment/iron_reference_lift_final.png';ref=Image.open(R).convert('RGB').crop((505,920,740,1026))
def rail(path):
 im=Image.open(path).convert('RGB');scale=im.width/1600;return im.crop(tuple(round(v*scale) for v in (390,235,1260,595)))
sheet([(ref,'Original reference'),(rail(start),'Starting saved look'),(rail(left),'Current iron and review lighting')],'resume_reference.jpg',3,(700,330))
sheet([(left,'Current iron: left bay'),(right,'Current iron: right bay')],'resume_close_views.jpg',1,(1400,700))
bounds=json.loads((C/'context_frame.json').read_text())['projected_chest_bounds']
def normalize(im,b):
 scale=760/(b[2]-b[0]);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS);out=Image.new('RGB',(850,850),'#151315');out.paste(im,(round(425-(b[0]+b[2])*.5*scale),round(65-b[1]*scale)));return out
sheet([(normalize(Image.open(R).convert('RGB'),[68,176,1184,1080]),'Original reference'),(normalize(Image.open(context).convert('RGB'),bounds),'Current bottom iron; other finishes temporary')],'resume_context.jpg',2,(850,850))
