"""Reference proportions and intrinsic surface maps for the two new coins."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/badges_matplotlib')
import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.spatial import Delaunay
from matplotlib.path import Path as PolygonPath

ROOT=Path(__file__).resolve().parent

def curve(start,sections,n=16):
    out=[np.array(start,float)]
    for a,b,c in sections:
        p=out[-1].copy()
        for t in np.linspace(0,1,n+1)[1:]:
            out.append((1-t)**3*p+3*(1-t)**2*t*np.array(a)+3*(1-t)*t*t*np.array(b)+t**3*np.array(c))
    return np.array(out)

def xy(points):
    return ((np.asarray(points)-[626,613])*[2.42/485,-2.42/480]).tolist()

def leaf(start,sections):return xy(curve(start,sections))

leaves=[
 leaf((600,413), [((647,274),(624,179),(520,167)),((486,164),(466,172),(453,183)),((481,194),(511,216),(531,234)),((518,229),(513,228),(505,230)),((559,286),(587,342),(600,413))]),
 leaf((596,406), [((548,247),(398,186),(313,340)),((344,323),(384,316),(423,314)),((414,321),(408,328),(403,336)),((478,324),(550,347),(596,406))]),
 leaf((607,405), [((701,196),(852,202),(900,345)),((859,327),(820,315),(762,314)),((771,318),(777,325),(783,335)),((709,318),(654,350),(607,405))]),
 leaf((612,415), [((754,326),(857,380),(866,540)),((843,515),(819,492),(796,478)),((799,488),(804,500),(811,511)),((718,449),(673,431),(612,415))]),
 leaf((612,423), [((741,439),(794,532),(689,631)),((690,608),(677,581),(666,568)),((665,583),(663,599),(660,610)),((647,513),(633,459),(612,423))]),
 leaf((590,413), [((495,322),(410,341),(386,463)),((424,443),(451,422),(482,417)),((474,428),(472,434),(470,439)),((523,413),(559,407),(590,413))]),
]

# The smaller palm repeats the same design with its own hub and scale.
small=[]
for p in leaves:
    p=np.asarray(p);hub=np.array(xy([[603,418]])[0]);newhub=np.array(xy([[380,537]])[0])
    small.append(((p-hub)*.58+newhub).tolist())
design={'leaves':leaves,'small_leaves':small,
 'island':xy(curve((178,820), [((297,772),(373,711),(444,734)),((548,721),(631,824),(711,853)),((581,870),(470,833),(365,813)),((299,795),(220,811),(178,820))])),
 'wave1':xy(curve((177,829), [((332,761),(485,851),(632,874)),((776,904),(912,867),(1072,821))])),
 'wave2':xy(curve((257,913), [((410,853),(524,939),(683,970)),((810,991),(922,946),(1003,914))])),
 'sun_center':xy([[856,755]])[0],'sun_radius':182*2.42/485,
 'horizon':xy([[175,756],[1082,756]]),
 'trunk':xy([[535,750],[603,425]]),'small_trunk':xy([[430,738],[380,539]])}
(ROOT/'design.json').write_text(json.dumps(design,indent=2))

arrays={}
for i,outline in enumerate(leaves+small+[design['island']]):
    boundary=np.asarray(outline)
    if np.linalg.norm(boundary[0]-boundary[-1])<1e-6:boundary=boundary[:-1]
    lo,hi=boundary.min(0),boundary.max(0)
    gx,gy=np.meshgrid(np.arange(lo[0],hi[0],.075),np.arange(lo[1],hi[1],.075))
    grid=np.c_[gx.ravel(),gy.ravel()];inside=PolygonPath(boundary).contains_points(grid,radius=-.005)
    points=np.r_[boundary,grid[inside]]
    t=Delaunay(points).simplices;poly=PolygonPath(boundary)
    keep=poly.contains_points(points[t].mean(1),radius=1e-6)
    t=t[keep]
    distances=np.full(len(points),10.)
    for a,b in zip(boundary,np.roll(boundary,-1,axis=0)):
        ab=b-a;u=np.clip(((points-a)*ab).sum(1)/max(ab@ab,1e-12),0,1)
        distances=np.minimum(distances,np.linalg.norm(points-a-u[:,None]*ab,axis=1))
    z=.17+(.07 if i<12 else .03)*np.sin(np.clip(distances/max(distances.max(),1e-6),0,1)*np.pi/2)
    arrays[str(i)+'_points']=np.c_[points,z];arrays[str(i)+'_triangles']=t
np.savez_compressed(ROOT/'leaf_geometry.npz',**arrays)

radius=2.445;hy=design['horizon'][0][1]
gx,gy=np.meshgrid(np.arange(-radius,radius,.11),np.arange(-radius,hy,.11))
grid=np.c_[gx.ravel(),gy.ravel()];grid=grid[(np.linalg.norm(grid,axis=1)<radius-.02)&(grid[:,1]<hy-.01)]
angle=np.arcsin(hy/radius)
arc=np.linspace(np.pi-angle,2*np.pi+angle,100)
boundary=np.c_[radius*np.cos(arc),radius*np.sin(arc)]
line=np.c_[np.linspace(boundary[-1,0],boundary[0,0],45),np.full(45,hy)]
points=np.r_[boundary,line,grid];triangles=Delaunay(points).simplices
mid=points[triangles].mean(1);triangles=triangles[(mid[:,1]<=hy+1e-6)&(np.linalg.norm(mid,axis=1)<=radius+1e-6)]
height=np.full(len(points),.078)
for key in ['wave1','wave2']:
    wave=np.asarray(design[key]);order=np.argsort(wave[:,0]);wy=np.interp(points[:,0],wave[order,0],wave[order,1])
    height+=.045*np.exp(-((points[:,1]-wy)/.16)**2)
np.savez_compressed(ROOT/'sea_geometry.npz',points=np.c_[points,height],triangles=triangles)

def save(name,values):
    values=np.clip(values,0,1)
    s=np.where(values<=.0031308,values*12.92,1.055*values**(1/2.4)-.055)
    Image.fromarray(np.uint8(np.rint(s*255))).save(ROOT/'textures'/name)

(ROOT/'textures').mkdir(exist_ok=True)
y,x=np.indices((512,512));wy=3.015-(y+.5)/512*6.03
rng=np.random.default_rng(1602026);grain=gaussian_filter(rng.normal(size=(512,512)),(.5,3))
grain=grain/max(grain.std(),1e-8)
# Surface grain only. No light bands on any metal.
save('silver.png',np.array([.52,.50,.47])[None,None,:]*(1+.018*grain[:,:,None]))
save('gold.png',np.array([.78,.47,.065])[None,None,:]*(1+.018*grain[:,:,None]))
save('charcoal.png',np.array([.005,.006,.007])[None,None,:]*(1+.09*grain[:,:,None]))
save('leaf.png',np.array([.008,.155,.026])[None,None,:]*(1+.018*grain[:,:,None]))
save('sea.png',np.array([.006,.205,.255])[None,None,:]*(1+.035*grain[:,:,None]))
sky=np.zeros((512,512,3));stops=[(-.75,[.95,.29,.018]),(-.35,[.82,.055,.075]),(.65,[.50,.008,.17]),(1.55,[.17,.003,.27]),(2.42,[.055,.001,.14])]
for c in range(3):sky[:,:,c]=np.interp(wy,[a for a,_ in stops],[v[c] for _,v in stops])
save('sky.png',sky*(1+.012*grain[:,:,None]))
sun=np.zeros_like(sky)
for c,(lo,hi) in enumerate(zip([.94,.20,.003],[1.,.74,.06])):
    sun[:,:,c]=lo+(hi-lo)*np.clip((wy+.75)/.91,0,1)
save('sun.png',sun)
print('Reference curves and intrinsic material maps prepared.')
