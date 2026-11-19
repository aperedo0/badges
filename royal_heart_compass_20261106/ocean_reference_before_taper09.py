"""Closed wave crests and cardinal settings from reference outlines."""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import binary_opening,binary_closing,binary_fill_holes,label,distance_transform_edt,map_coordinates,gaussian_filter
from reference_gold_relief import relief
from sculpted_gold import frame
UNIT=2.94/480

def waves(path):
 rgb=np.asarray(Image.open(path).convert('RGB'),float)/255;r,g,b=rgb.transpose(2,0,1);yy,xx=np.mgrid[:rgb.shape[0],:rgb.shape[1]];radius=np.hypot(xx-627,yy-570)
 leftx=np.minimum(xx,1254-xx)
 envelope=np.interp(leftx,[230,250,275,300,325,350,375,400,425,450,475,500,525,550,575,600,627],[788,768,764,767,794,829,832,820,818,823,833,878,897,894,895,908,908])-7
 roi=(yy>=envelope)&(yy<1030)&(xx>=230)&(xx<1024)&(radius<447)&(abs(xx-627)>35)
 mask=(r>g*1.035)&(g>b*1.10)&(r>.045)&roi
 mask=binary_opening(mask,iterations=1);mask=binary_closing(mask,iterations=1);holes=binary_fill_holes(mask)&~mask;lab,_=label(holes);sizes=np.bincount(lab.ravel());mask|=holes&(sizes[lab]<80);lab,_=label(mask);sizes=np.bincount(lab.ravel());mask&=sizes[lab]>80
 box=(195,735,1060,1040);crop=mask[box[1]:box[3],box[0]:box[2]];p,t=relief(crop,box,step=3)
 dist=gaussian_filter(distance_transform_edt(crop),2.0);front=len(p)//2;d=map_coordinates(dist,[p[:front,1]-box[1],p[:front,0]-box[0]],order=1)
 p[:front,2]=.014+.045*(1-np.exp(-d*UNIT*.30/.045));p[front:,2]=-.028
 rows=[('Measured flowing gold ocean wave crests',p,t,'gold')]
 # Closed blue water is behind the raised gold, with genuine shallow ridges.
 tops=np.full(mask.shape[1],np.nan)
 for x in range(195,1060):
  y=np.flatnonzero(mask[:,x])
  if len(y):tops[x]=y.min()
 good=np.flatnonzero(np.isfinite(tops));top=np.interp(np.arange(mask.shape[1]),good,tops[good]);water=(yy>=top[None,:]+2)&(radius<445)&(yy>740)&(xx>=195)&(xx<1060)
 p,t=relief(water[box[1]:box[3],box[0]:box[2]],box,step=4);front=len(p)//2;distance=gaussian_filter(distance_transform_edt(~mask),2.0);d=map_coordinates(distance,[p[:front,1],p[:front,0]],order=1);p[:front,2]=.025+.035*np.exp(-d*UNIT/.055);p[front:,2]=-.025
 rows.append(('Sculpted deep blue water beneath gold crests',p,t,'ocean_water'))
 return rows

def radial(outer,center,N=64):
 outer=np.asarray(outer,float);center=np.asarray(center,float);result=[]
 def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
 for a in np.arange(N)*2*np.pi/N+.00001:
  ray=np.array([np.cos(a),np.sin(a)]);edges=np.roll(outer,-1,axis=0)-outer;den=cross(ray,edges);q=outer-center;radius=cross(q,edges)/np.where(abs(den)>1e-10,den,np.nan);s=cross(q,ray)/np.where(abs(den)>1e-10,den,np.nan);valid=(radius>0)&(s>=0)&(s<=1);assert valid.any();result.append(center+ray*radius[valid].min())
 return np.array(result)

def setting(k):
 center=np.array([[627,151],[1030,570],[627,999],[222,570]][k],float)
 if k in [0,2]:
  top=np.array([[627,72],[637,101],[664,139],[689,159],[723,177],[697,168],[674,173],[650,195],[627,244],[604,195],[580,173],[557,168],[532,177],[565,159],[592,139],[617,101]],float)
  outer=top if k==0 else (top-[627,151])*-1+center
 else:
  x,y=center;outer=np.array([[x-50,y],[x-23,y-17],[x,y-53],[x+23,y-17],[x+50,y],[x+23,y+17],[x,y+53],[x-23,y+17]])
 outer=radial(outer,center);a=np.arange(len(outer))*2*np.pi/len(outer)+.00001;inner=center+np.c_[np.cos(a),np.sin(a)]*21;p,t=frame(outer,inner,.1)
 return center,p,t
