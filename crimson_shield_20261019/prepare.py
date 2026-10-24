"""Trace the reference proportions and prepare intrinsic metal grain."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter
from scipy.spatial import Voronoi

ROOT=Path(__file__).resolve().parent
SCALE=5.395/(1095-30)
def xy(points):
    return (np.asarray(points,float)-[627,1095])*[SCALE,-SCALE]+[0,-2.455]
def curve(start,segments,steps=40):
    out=[];p=np.asarray(start,float)
    for a,b,end in segments:
        a,b,end=map(lambda q:np.asarray(q,float),(a,b,end))
        for t in np.linspace(0,1,steps,endpoint=False):
            out.append((1-t)**3*p+3*(1-t)**2*t*a+3*(1-t)*t*t*b+t**3*end)
        p=end
    p=xy(out)
    if np.cross(p,np.roll(p,-1,axis=0)).sum()<0:p=p[::-1]
    return p
outer=curve((627,30),[
    ((704,111),(899,173),(1042,196)),
    ((1046,415),(1025,662),(947,803)),
    ((881,930),(747,1013),(627,1095)),
    ((507,1013),(373,930),(307,803)),
    ((229,662),(208,415),(212,196)),
    ((355,173),(550,111),(627,30))])
upper=curve((553,153),[
    ((460,177),(375,204),(330,253)),
    ((303,283),(289,323),(278,368)),
    ((299,339),(326,320),(358,310)),
    ((369,309),(381,312),(389,315)),
    ((372,304),(380,282),(392,262)),
    ((426,218),(488,190),(558,173)),
    ((557,166),(555,160),(553,153))],16)
lower=curve((301,639),[
    ((318,697),(349,737),(411,795)),
    ((391,752),(367,706),(354,654)),
    ((341,611),(333,553),(329,491)),
    ((324,491),(320,492),(315,494)),
    ((319,553),(316,601),(301,639))],16)
def setting(top,right,bottom,left):
    t,r,b,l=map(np.asarray,(top,right,bottom,left))
    center=np.array([627,(right[1]+left[1])/2])
    segments=[]
    for a,end in zip([t,r,b,l],[r,b,l,t]):
        # Curved sides produce the reference's four swept silver points.
        c1=a*.65+center*.35;c2=end*.65+center*.35
        segments.append((c1,c2,end))
    return curve(t,segments,18)
top_holder=setting((627,69),(701,148),(627,279),(550,148))
bottom_holder=setting((627,898),(698,990),(627,1084),(557,990))
def diamond(points,steps=18):
    p=[]
    for a,b in zip(points,np.roll(points,-1,axis=0)):
        p.extend(np.asarray(a)*(1-t)+np.asarray(b)*t for t in np.linspace(0,1,steps,endpoint=False))
    p=xy(p)
    if np.cross(p,np.roll(p,-1,axis=0)).sum()<0:p=p[::-1]
    return p
def ridge(start,segments,steps=20):
    out=[];p=np.asarray(start,float)
    for a,b,end in segments:
        a,b,end=map(lambda q:np.asarray(q,float),(a,b,end))
        for t in np.linspace(0,1,steps,endpoint=False):
            out.append((1-t)**3*p+3*(1-t)**2*t*a+3*(1-t)*t*t*b+t**3*end)
        p=end
    out.append(p)
    return xy(out)
upper_ridge=ridge((553,163),[((468,188),(400,217),(372,253)),((347,280),(315,315),(299,343))])
lower_ridge=ridge((322,497),[((323,550),(323,611),(335,654)),((346,694),(369,739),(398,781))])
data={'upper_ridge':upper_ridge.tolist(),'lower_ridge':lower_ridge.tolist(),'outer':outer.tolist(),'upper_left':upper.tolist(),'lower_left':lower.tolist(),
      'top_holder':top_holder.tolist(),'bottom_holder':bottom_holder.tolist(),
      'top_window':diamond([[627,104],[660,148],[627,211],[595,148]]).tolist(),
      'bottom_window':diamond([[627,944],[657,990],[627,1048],[598,990]]).tolist(),
      'top_gem':xy([[627,107],[653,147],[627,205],[601,147]]).tolist(),
      'bottom_gem':xy([[627,950],[651,990],[627,1040],[603,990]]).tolist()}
(ROOT/'design.json').write_text(json.dumps(data,indent=2)+'\n')

source_brush=np.load(ROOT.parent/'coin_brush_grain.npz')['grain']
grain=source_brush.copy()
grain=np.asarray(Image.fromarray(grain.astype(np.float32)).resize((512,512),Image.Resampling.BILINEAR))
grain=gaussian_filter(grain,.65)
grain=grain-gaussian_filter(grain,2.5)
grain=np.clip((grain-grain.mean())/max(grain.std(),1e-6),-2.5,2.5)
# Broader horizontal brushing survives the phone render. The field's rotated
# UVs align these marks with the live material's diagonal reflection direction.
field=gaussian_filter(source_brush,(.25,1.0))
field-=gaussian_filter(field,2.5)
field=np.asarray(Image.fromarray(field.astype(np.float32)).resize((512,512),Image.Resampling.LANCZOS))
field=np.clip((field-field.mean())/max(field.std(),1e-6),-2.5,2.5)
# Fine red mineral veins are intrinsic color and roughness, never emission.
rng=np.random.default_rng(19);vor=Voronoi(rng.uniform(-100,612,(100,2)))
veins=Image.new('L',(512,512),0);draw=ImageDraw.Draw(veins)
for pair in vor.ridge_vertices:
    if -1 in pair or rng.random()>.40:continue
    a,b=vor.vertices[pair]
    if np.linalg.norm(b-a)>160:continue
    mid=(a+b)/2+rng.normal(0,2,2)
    draw.line([tuple(a),tuple(mid),tuple(b)],fill=255,width=1)
veins=gaussian_filter(np.asarray(veins,float)/255,.55)
palette={'steel':([.43,.415,.395],1,.26), 'edge':([.14,.135,.125],1,.48),
         'channel':([.055,.052,.049],1,.42),
         'field':([.095,.099,.100],1,.32), 'red':([.085,.0014,.0035],.45,.27),
         'gem':([.34,.002,.006],.55,.14)}

def encode(v):
    v=np.clip(v,0,1)
    return np.uint8(np.where(v<=.0031308,v*12.92,1.055*v**(1/2.4)-.055)*255+.5)
for role,(color,metal,rough) in palette.items():
    noise=field if role=='field' else grain
    amount=.045 if role=='field' else .025 if role in ['steel','edge'] else .012
    albedo=np.array(color)[None,None,:]*np.exp(noise[:,:,None]*amount)
    if role=='red':albedo+=veins[:,:,None]*np.array([.12,.003,.004])[None,None,:]
    Image.fromarray(encode(albedo)).save(ROOT/'textures'/(role+'_color.png'))
    micro=np.clip(rough+noise*(.010 if role=='field' else .004),.09,.60)
    if role=='red':micro-=veins*.035
    Image.fromarray(np.uint8(micro*255+.5)).save(ROOT/'textures'/(role+'_roughness.png'))
(ROOT/'palette.json').write_text(json.dumps(palette,indent=2)+'\n')
print('Shield contours, swept ornaments, ruby windows and neutral brushed metal prepared.')
