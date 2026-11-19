"""Compare real pavilion depths using the measured fixed native studio."""
from pathlib import Path
import json,time
import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
import shapely
from PIL import Image,ImageDraw
import forward as f
R=Path(__file__).resolve().parent;C=R.parent/'sapphire_teardrop/candidate07'
s=json.loads((R.parent/'schedule.json').read_text());assert s['phase']=='work' and time.time()+30<s['work_until_epoch']
D=np.load(C/'parts.npz');U=json.loads((C/'parts.json').read_text())['units'];points=np.unique(D['gem_v'].reshape(-1,3),axis=0).astype(float)
xx,yy=np.meshgrid(np.arange(485,776,5),np.arange(440,817,5));x,y=xx.ravel(),yy.ravel()
table=Polygon([[626,432],[772,624],[722,782],[626,818],[531,778],[482,624]]).buffer(-12)
keep=shapely.contains_xy(table,x,y);x,y=x[keep],y[keep]
P=np.c_[(x-U['axis'])*U['S'],2.995-(y-U['top'])*U['S'],np.full(len(x),.64)]
eye=np.broadcast_to([0,1.8,23.],P.shape).copy();initial=f.unit(P-eye);studio=f.Studio()
target=np.asarray(Image.open(C.parent/'reference.png').convert('RGB'))[y,x]/255
native=np.asarray(Image.open(C/'app/front.png').convert('RGB'))/255
axis=f.unit(np.array([[0,-2.35,-23.]]))[0];up=np.cross([1,0,0],axis);delta=P-eye;z=delta@axis
sx=np.rint(603+1762.5*delta[:,0]/z).astype(int);sy=np.rint(633.3-1762.5*(delta@up)/z).astype(int);actual=native[sy,sx]
report={'diagnostic_only':True,'appearance_texture_created':False,'geometry_or_runtime_changed':False,'depths':[]};canvas=Image.new('RGB',(1200,440),(24,24,24));draw=ImageDraw.Draw(canvas)
for col,depth in enumerate([.64,1.0,1.5,2.0]):
 q=points.copy();q[np.isclose(q[:,2],-.64),2]=-depth
 h=ConvexHull(q);eq=np.unique(np.round(h.equations,8),axis=0);hull=(eq[:,:3],-eq[:,3]);hulls=[hull,hull]
 direction=initial.copy();ok,entry,_,normal,_=f.outer(hulls,eye,direction);assert ok.all()
 pos=eye+direction*entry[:,None];share=f.fresnel(-np.sum(normal*direction,1),1,1.77)
 out=share[:,None]*studio.sharp(f.reflect(direction,normal));weight=1-share;direction=f.refract(direction,normal,1/1.77);length=np.zeros(len(x));tir=[]
 for hit in range(3):
  ok,_,distance,_,normal=f.outer(hulls,pos,direction);assert ok.all();length+=distance;pos+=direction*distance[:,None]
  share=f.fresnel(np.sum(normal*direction,1),1.77,1);tir.append(float(np.mean(share>.999)))
  green=f.refract(direction,-normal,1.77);light=[]
  for channel,index in enumerate([1.76,1.77,1.79]):
   bent=f.refract(direction,-normal,index);bent=np.where((np.linalg.norm(bent,axis=1)==0)[:,None],green,bent)
   light.append((studio.sharp(bent)+1.45768306077441*np.minimum(studio.sample(bent,8),3))[:,channel])
  absorption=np.exp(-length[:,None]*np.array([8,4.350359687795594,.2])*.78125)
  out+=(weight*(1-share))[:,None]*absorption*np.stack(light,1);weight*=share;direction=f.reflect(direction,normal)
 out+=weight[:,None]*absorption*(studio.sharp(direction)+1.45768306077441*np.minimum(studio.sample(direction,8),3))
 color=np.clip(f.agx(out*.28),0,1);err=float(np.mean(abs(color-actual))) if col==0 else None
 row=dict(rear_culet_z=-depth,first_three_internal_reflection_fractions=tir,median_color=np.median(color,0).tolist(),color_spread=np.std(color,0).tolist(),native_calibration_error=err,facet_planes=len(eq))
 report['depths'].append(row)
 tile=Image.new('RGB',(300,420),(24,24,24));px=tile.load()
 for a,b,rgb in zip(x,y,color):
  ix=int((a-480)*.9);iy=int((b-430)*.9)
  for dx in range(5):
   for dy in range(5):
    if 0<=ix+dx<300 and 0<=iy+dy<420:px[ix+dx,iy+dy]=tuple(np.uint8(rgb*255))
 canvas.paste(tile,(col*300,20));draw.text((col*300+5,3),f'Culet depth {depth}',fill='white')
report['native_calibration_reliable']=report['depths'][0]['native_calibration_error']<.08
(R/'pavilion_depth_diagnosis.json').write_text(json.dumps(report,indent=2)+'\n');canvas.save(R/'pavilion_depth_diagnosis.png');print(json.dumps(report,indent=2))
