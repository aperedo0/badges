"""Closed sculpted gold from measured outlines, with no photographic material."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_closing,binary_fill_holes,distance_transform_edt,gaussian_filter,map_coordinates,label
from scipy.spatial import Delaunay
from contourpy import contour_generator

def polygon(shape,pts):
 im=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(im).polygon([tuple(p) for p in pts],fill=255);return np.asarray(im)>0

def gold_pixels(rgb):
 r,g,b=rgb.transpose(2,0,1);warm=(r>g*1.015)&(g>b*1.12)&(r>.035)
 white=(rgb.min(2)>.58)&((rgb.max(2)-rgb.min(2))<.24)
 return warm|(white&(distance_transform_edt(~warm)<5))

def central_mask(path):
 rgb=np.asarray(Image.open(path).convert('RGB'),float)/255;shape=rgb.shape[:2]
 outer=[[768,390],[800,437],[856,491],[851,572],[815,641],[768,710],[721,641],[685,572],[680,491],[735,437]]
 inner=[[768,468],[816,506],[812,581],[768,674],[722,581],[721,506]]
 frame=polygon(shape,outer)&~polygon(shape,inner)
 leaf_roi=np.zeros(shape,bool);leaf_roi[510:707,540:736]=True;leaf_roi[510:707,800:997]=True
 leaves=gold_pixels(rgb)&leaf_roi
 leaves=binary_closing(leaves,iterations=1);holes=binary_fill_holes(leaves)&~leaves;lab,n=label(holes);sizes=np.bincount(lab.ravel());leaves|=holes&(sizes[lab]<100)
 mask=frame|leaves;box=(530,385,1007,718)
 return mask[box[1]:box[3],box[0]:box[2]],box

def circlet_mask(path):
 rgb=np.asarray(Image.open(path).convert('RGB'),float)/255;mask=gold_pixels(rgb);roi=np.zeros(mask.shape,bool);roi[755:840,450:711]=True;roi[755:840,825:1086]=True
 # Keep the separately modeled gold kites and central jewel independent.
 roi[745:840,388:450]=False;roi[745:840,1086:1148]=False
 mask&=roi;mask=binary_closing(mask,iterations=1);box=(330,750,1210,845)
 return mask[box[1]:box[3],box[0]:box[2]],box

def side_mask(path,side):
 rgb=np.asarray(Image.open(path).convert('RGB'),float)/255;shape=rgb.shape[:2]
 points=np.array([[202,404],[221,462],[269,483],[286,528],[264,569],[278,638],[322,711],[302,716],[244,622],[215,564],[174,500],[191,466]])
 if side>0:points[:,0]=1536-points[:,0]
 roi=polygon(shape,points);mask=gold_pixels(rgb)&roi;mask=binary_closing(mask,iterations=1)
 box=(168,398,328,719) if side<0 else (1208,398,1368,719)
 return mask[box[1]:box[3],box[0]:box[2]],box

def finial_mask(path):
 rgb=np.asarray(Image.open(path).convert('RGB'),float)/255;shape=rgb.shape[:2]
 outer=[[768,30],[810,100],[815,128],[849,136],[825,151],[832,175],[806,215],[768,272],[730,215],[704,175],[711,151],[687,136],[721,128],[726,100]]
 inner=[[768,80],[815,172],[768,244],[721,172]]
 frame=polygon(shape,outer)&~polygon(shape,inner)
 left=[[[755,274],[735,252],[710,232],[678,221],[647,221],[618,228],[590,242],[562,252],[565,231],[579,214],[605,201],[630,196],[657,196],[685,204],[710,219],[735,243]],[[740,252],[711,217],[685,196],[651,184],[620,187],[601,197],[624,194],[655,200],[687,216],[712,240],[730,269]],[[731,269],[702,240],[669,225],[641,222],[618,226],[602,244],[616,269],[619,246],[641,236],[674,240],[707,257]]]
 mask=frame.copy()
 for outline in left:
  mask|=polygon(shape,outline);mask|=polygon(shape,[(1536-x,y) for x,y in outline])
 mask[265:302,744:793]=True
 box=(545,20,992,304)
 return mask[box[1]:box[3],box[0]:box[2]],box

def relief(mask,box,step=3):
 mask=gaussian_filter(mask.astype(float),1.35)>.45
 lab,n=label(mask);sizes=np.bincount(lab.ravel());mask&=sizes[lab]>22
 h,w=mask.shape;dist=distance_transform_edt(mask);boundaries=[]
 for loop in contour_generator(z=mask.astype(float)).lines(.5):
  if len(loop)>=8:boundaries.extend(loop[::2])
 yy,xx=np.mgrid[1:h-1:step,1:w-1:step];inside=mask[yy.ravel(),xx.ravel()];xy=np.c_[xx.ravel(),yy.ravel()][inside]
 xy=np.unique(np.round(np.vstack([xy,boundaries]),3),axis=0);t=Delaunay(xy).simplices;ok=np.ones(len(t),bool)
 for weights in [[1/3]*3,[.5,.5,0],[0,.5,.5],[.5,0,.5]]:
  probes=(xy[t]*np.array(weights)[None,:,None]).sum(1);ok&=map_coordinates(mask.astype(float),[probes[:,1],probes[:,0]],order=1,mode='constant')>.25
 t=t[ok];used,inv=np.unique(t,return_inverse=True);xy=xy[used];t=inv.reshape(-1,3)
 # Separate surface fans that touch at only one contour point. They remain
 # visually coincident while each extruded component has a closed shell.
 edges=np.sort(np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]),axis=1)
 unique,count=np.unique(edges,axis=0,return_counts=True);boundary=unique[count==1]
 degree=np.bincount(boundary.ravel(),minlength=len(xy))
 for vertex in np.flatnonzero(degree>2):
  incident=np.flatnonzero((t==vertex).any(1));remaining=set(incident.tolist());fans=[]
  while remaining:
   todo=[remaining.pop()];fan=[]
   while todo:
    current=todo.pop();fan.append(current);other=set(t[current])-{vertex}
    neighbors=[j for j in remaining if other.intersection(set(t[j])-{vertex})]
    remaining.difference_update(neighbors);todo.extend(neighbors)
   fans.append(fan)
  for fan in fans[1:]:
   new_index=len(xy);xy=np.vstack([xy,xy[vertex]])
   for tri_index in fan:t[tri_index][t[tri_index]==vertex]=new_index

 # Pixel Y is inverted later, so the front uses clockwise pixel triangles.
 cross=np.cross(np.c_[xy[t[:,1]]-xy[t[:,0]],np.zeros(len(t))],np.c_[xy[t[:,2]]-xy[t[:,0]],np.zeros(len(t))])[:,2];flip=cross>0;t[flip]=t[flip,::-1]
 d=map_coordinates(gaussian_filter(dist,.7),[xy[:,1],xy[:,0]],order=1)
 bevel=np.clip(d/4,0,1);bevel=bevel*bevel*(3-2*bevel)
 z=.018+.072*bevel
 # Rounded relief has genuine broad surface curvature beneath its short bevel.
 if box[1] in [20,385]:z+=.15*(1-np.exp(-np.maximum(d,0)/12))
 pixel=xy+np.array(box[:2])
 if box[1]==385:
  from scipy.spatial import cKDTree
  curves=[[[594,521],[650,531],[684,566],[708,615]],[[552,650],[565,585],[631,568],[699,637]],[[588,706],[654,700],[710,683],[685,654]]]
  f=np.linspace(0,1,100)[:,None]
  for controls in curves:
   a,b,c,e=np.asarray(controls,float);curve=(1-f)**3*a+3*(1-f)**2*f*b+3*(1-f)*f*f*c+f**3*e
   for side in [1,-1]:
    q=curve.copy()
    if side<0:q[:,0]=1536-q[:,0]
    distance=cKDTree(q).query(pixel)[0]
    z+=.026*np.exp(-.5*(distance/6)**2)*np.minimum(d/4,1)
  half_width=np.interp(pixel[:,1],[390,437,491,572,641,710],[1,32,88,83,47,1])
  ridge=np.clip(1-abs(pixel[:,0]-768)/np.maximum(half_width,1),0,1)
  z+=ridge*np.where(pixel[:,1]<468,.040,np.where(pixel[:,1]>674,.025,0))
 p=np.c_[pixel,z];N=len(p);back=p.copy();back[:,2]=-.035
 edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,idx,count=np.unique(np.sort(edges,axis=1),axis=0,return_index=True,return_counts=True);edge=edges[idx[count==1]]
 walls=np.array([[a,b+N,b] for a,b in edge]+[[a,a+N,b+N] for a,b in edge],np.int32)
 return np.vstack([p,back]),np.vstack([t,t[:,::-1]+N,walls])
