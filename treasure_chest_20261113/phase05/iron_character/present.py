from pathlib import Path
import json,sys
F=Path(__file__).resolve().parent.parent/'iron_fidelity';source=(F/'present.py').read_text().split('ref=Image.open(R)')[0];exec(compile(source,'reused_comparison_sheet_helpers','exec'));env=sys.argv[2];left=C/('iron_'+env+'_final.png');right=C/('right_'+env+'_final.png');context=C/('context_'+env+'_final.png');base=D/'baseline'/('iron_'+env+'_final.png');ref=Image.open(R).convert('RGB').crop((505,933,740,1024))
sheet([(ref,'Original reference crop'),(rail(base),'Starting iron, identical warm lighting'),(rail(left),'Selected surface character')],'reference_comparison.jpg',3,(700,330))
sheet([(base,'Starting iron'),(left,'Selected iron, identical lighting')],'baseline_comparison.jpg',1,(1200,600))
sheet([(left,'Left bay'),(right,'Right bay')],'close_views.jpg',1,(1400,700))
if (C/'iron_neutral_final.png').exists():sheet([(C/'iron_neutral_final.png','Neutral studio reflections'),(left,'Warm reflections, unchanged material')],'neutral_comparison.jpg',2,(1000,500))
bounds=json.loads((C/'context_frame.json').read_text())['projected_chest_bounds']
def normalize(im,b):
 scale=760/(b[2]-b[0]);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS);out=Image.new('RGB',(850,850),'#151315');out.paste(im,(round(425-(b[0]+b[2])*.5*scale),round(65-b[1]*scale)));return out
sheet([(normalize(Image.open(R).convert('RGB'),[68,176,1184,1080]),'Original reference'),(normalize(Image.open(context).convert('RGB'),bounds),'Bottom iron development; temporary context')],'chest_comparison.jpg',2,(850,850))
print('Created compact final comparisons')
