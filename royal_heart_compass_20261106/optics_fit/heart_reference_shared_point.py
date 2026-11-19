"""Diagnose a measured front and a single shared physical rear point."""
from pathlib import Path
import json
import numpy as np
from scipy.spatial import ConvexHull
from PIL import Image, ImageDraw
import forward as f

R = Path(__file__).resolve().parent
D = np.load(R.parent/'ruby_heart/candidate20/geometry.npz')
parts = []
for index in [3,4]:
    old = D[f'{index}_points'].astype(float)
    h = ConvexHull(old)
    ids = np.unique(h.simplices[h.equations[:,2] > .001])
    rear = old[48:96].copy()
    point = np.array([[0., .30, rear[:,2].mean()-1.7]])
    p = np.vstack([old[ids], rear, point])
    parts.append(p)
np.savez_compressed(R/'heart_reference_shared_point.npz',**{f'{i}_points':p for i,p in enumerate(parts)})
Y,X = np.mgrid[350:835:4,360:850:4]
shape = X.shape
axis = f.unit(np.array([[0,-2.35,-23.]]))[0]
up = np.cross([1,0,0],axis)
ray = f.unit(axis[None,:]+np.c_[(X.ravel()-603)/1762.5,np.zeros(X.size),np.zeros(X.size)]+((633.3-Y.ravel())/1762.5)[:,None]*up)
eye = np.broadcast_to([0,1.8,23.],ray.shape).copy()
source = Path(f.__file__).read_text()
code = source[source.index('def optical('):source.index('\ndef render')]
code = code.replace('absorption=np.array([.16,9.,2.8])*.5','absorption=np.array([.042528659,9.,.721236937])*.5').replace('*.32','*.681357060')
ns = dict(f.__dict__)
exec(code,ns)
studio = f.Studio()
sheet = Image.new('RGB',(1000,535),(12,12,15))
draw = ImageDraw.Draw(sheet)
current = np.load(R.parent/'ruby_heart/candidate25/geometry.npz')
for col,(name,ps) in enumerate([('Current coordinated cut',[current[f'{i}_points'] for i in [3,4]]),('Measured front with one shared rear point',parts)]):
    hulls = [f.planes_of(p) for p in ps]
    print(name,[len(h[0]) for h in hulls],flush=True)
    ids,lin = ns['optical'](hulls,eye,ray,studio)
    a = np.full((X.size,3),.03)
    a[ids] = np.clip(f.agx(lin),0,1)
    sheet.paste(Image.fromarray(np.uint8(a.reshape(*shape,3)*255)).resize((500,500)),(col*500,30))
    draw.text((col*500+5,8),name,fill='white')
sheet.save(R/'heart_reference_shared_point.png')
