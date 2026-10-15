"""Match the road's inner bend to the actual reference edge."""
from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,gaussian_filter1d
from scipy.interpolate import PchipInterpolator
R=Path(__file__).resolve().parent
b=R/'sunrise';m=json.loads((b/'design.json').read_text());cx,cy,rad=m['circle']
photo=np.asarray(Image.open(m['reference']).convert('RGB'),float)/255
green=gaussian_filter(photo[:,:,1],1)
guide_y=[727,750,775,800,825,850,875,900,925,947]
guide_x=[729,715,653,615,615,634,693,764,836,890]
rows=np.arange(729,948,2);pred=PchipInterpolator(guide_y,guide_x)(rows);x=[]
for y,center in zip(rows,pred):
    grid=np.arange(int(center)-9,int(center)+10)
    gradient=green[y,grid+2]-green[y,grid-2]
    x.append(grid[np.argmin(gradient)])
x=gaussian_filter1d(np.asarray(x,float),2)
right=np.c_[x,rows]
start=np.array([560.,672.]);pixels=[start]
for a,c,end in [
    ((646,669),(751,688),(725,727)),((701,762),(554,787),(551,829)),
    ((545,871),(732,925),(885,947)),((800,1021),(622,1056),(497,989)),
    ((435,956),(400,917),(414,870)),((430,824),(531,784),(598,752)),
    ((641,731),(680,706),(646,695)),((621,686),(583,681),(560,672))]:
    p=pixels[-1]
    for t in np.linspace(0,1,33)[1:]:pixels.append((1-t)**3*p+3*(1-t)**2*t*np.array(a)+3*(1-t)*t*t*np.array(c)+t**3*np.array(end))
pixels=np.asarray(pixels)
assert np.linalg.norm(pixels[32]-[725,727])<.01
pixels=np.r_[pixels[:33],right,pixels[97:]]
m['features'][9]['blender_plate']['points']=((pixels-[cx,cy])*[3.015/rad,-3.015/rad]).tolist()
(b/'design.json').write_text(json.dumps(m,indent=2))
print('Road bend corrected against the reference gradient.')
