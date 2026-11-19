"""Recover reference ornament outlines as actual curved gold relief."""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import binary_closing,binary_fill_holes,distance_transform_edt,gaussian_filter,map_coordinates,label
from scipy.spatial import Delaunay
from contourpy import contour_generator
def ornament(path,box,width,height):
 a=np.asarray(Image.open(path).convert('RGB').crop(box),float)/255;r,g,b=a.transpose(2,0,1)
 mask=(r>g*1.015)&(g>b*1.12)&(g>r*.39)&(r>.20)
 mask=binary_closing(mask,iterations=2);mask=gaussian_filter(mask.astype(float),1.15)>.45;lab,n=label(~mask);area=np.bincount(lab.ravel());mask|=(area[lab]<30)
 lab,n=label(mask);area=np.bincount(lab.ravel());mask&=area[lab]>35
 h,w=mask.shape
 if w<250:
  yy,xx=np.mgrid[:h,:w];mask&=~((xx>w*.82)&(yy<h*.60));mask[0:2]=False;mask[-2:]=False
 distance=distance_transform_edt(mask)
 contours=contour_generator(z=mask.astype(float)).lines(.5);boundary=[]
 for loop in contours:
  if len(loop)>=12:boundary.extend(loop[::2])
 yy,xx=np.mgrid[1:h-1:4,1:w-1:4];xy=np.c_[xx.ravel(),yy.ravel()];xy=xy[mask[yy.ravel(),xx.ravel()]]
 xy=np.unique(np.round(np.vstack([xy,boundary]),3),axis=0);t=Delaunay(xy).simplices
 inside=np.ones(len(t),bool)
 for weights in [[1/3]*3,[.5,.5,0],[0,.5,.5],[.5,0,.5]]:
  p=(xy[t]*np.array(weights)[None,:,None]).sum(1);inside&=map_coordinates(mask.astype(float),[p[:,1],p[:,0]],order=1,mode='constant')>.3
 t=t[inside];used,inv=np.unique(t,return_inverse=True);xy=xy[used];t=inv.reshape(-1,3)
 d=map_coordinates(gaussian_filter(distance,1),[xy[:,1],xy[:,0]],order=1);z=.018+.075*(1-np.exp(-d/5))
 p=np.c_[(xy[:,0]/w-.5)*width,(.5-xy[:,1]/h)*height,z]
 n=np.cross(p[t[:,1]]-p[t[:,0]],p[t[:,2]]-p[t[:,0]]);flip=n[:,2]<0;t[flip]=t[flip,::-1]
 # Close every boundary, including open spaces inside the scrollwork.
 edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);keys=np.sort(edges,axis=1);_,inds,counts=np.unique(keys,axis=0,return_index=True,return_counts=True);edge=edges[inds[counts==1]];N=len(p);back=p.copy();back[:,2]=-.025
 sides=np.array([[a,b+N,b] for a,b in edge]+[[a,a+N,b+N] for a,b in edge],np.int32)
 return np.vstack([p,back]),np.vstack([t,t[:,::-1]+N,sides])
