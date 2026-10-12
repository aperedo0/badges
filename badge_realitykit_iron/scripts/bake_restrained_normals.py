"""Bake gentle physical-scale perturbations into actual tangent frames, with edge padding."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter,distance_transform_edt,map_coordinates
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'scripts'));import generate_forged_textures as tex
p=tex.p;geometry=json.loads((r/'work/normal_bake_geometry.json').read_text());report={}
# Scalar pseudo-height comes from the real reference microcontrast. It is inferred,
# not recovered physical metrology. Filter subtexel noise before differentiation.
fields={}
for short,detail in [('Casing',tex.rim_detail),('Inset',tex.inset_detail),('Emblem',tex.crystal_detail)]:
 height=gaussian_filter(np.log(np.maximum(detail.mean(2),.1)),1.8)
 gy,gx=np.gradient(height);grad=np.stack([gx,-gy],-1)
 if short=='Casing':mask=tex.rim_mask
 elif short=='Inset':mask=tex.inset_mask
 else:
  # Each macro facet has a flat 4-reference-pixel border; no UV seam or bright bevel.
  border=np.zeros(height.shape)
  from PIL import ImageDraw
  for face in p.get('reference_front_faces',p['front_faces']):
   im=Image.new('L',(tex.w,tex.h));ImageDraw.Draw(im).polygon([tuple(p['reference_pixel_vertices'][i]) for i in face],fill=255)
   border=np.maximum(border,np.clip((distance_transform_edt(np.asarray(im)>0)-2)/4,0,1))
  grad*=border[:,:,None];mask=None
 if mask is not None:grad*=np.clip((distance_transform_edt(mask)-2)/4,0,1)[:,:,None]
 fields[short]=grad
for short in ['Casing','Inset','Emblem']:
 g=next(v for k,v in geometry.items() if k.startswith(short+'___'));pts=np.array(g['points']);indices=np.array(g['indices']);uv=np.array(g['uv']);normals=np.array(g['normals']);out=np.zeros((512,512,3));out[:,:,2]=1;valid=np.zeros((512,512),bool)
 for tri,st,ns in zip(indices,uv,normals):
  q=st*np.array([511,-511])+np.array([0,511]);lo=np.maximum(np.floor(q.min(0)).astype(int),0);hi=np.minimum(np.ceil(q.max(0)).astype(int),511);x0,y0=lo;x1,y1=hi
  if x0>x1 or y0>y1:continue
  mat=np.vstack([q.T,np.ones(3)])
  if abs(np.linalg.det(mat))<1e-10:continue
  gy,gx=np.mgrid[y0:y1+1,x0:x1+1];bary=np.linalg.solve(mat,np.stack([gx.ravel(),gy.ravel(),np.ones(gx.size)]));keep=bary.min(0)>=-1e-4;x=gx.ravel()[keep];y=gy.ravel()[keep]
  if not len(x):continue
  weights=bary[:,keep].T;xyz=weights@pts[tri];n=weights@ns;n/=np.linalg.norm(n,axis=1)[:,None]
  if short=='Emblem':sx=629+xyz[:,0]*682/(4.064*p.get('emblem_scale',1.));sy=606-xyz[:,1]*682/(4.064*p.get('emblem_scale',1.));pixels_per_unit=682/(4.064*p.get('emblem_scale',1.))
  elif short=='Inset':sx=624+xyz[:,0]*164;sy=600-xyz[:,1]*164;pixels_per_unit=164
  else:
   radius=np.hypot(xyz[:,0],xyz[:,1]);angle=np.arctan2(xyz[:,1],xyz[:,0]);rr=np.clip(414+(radius-2.45)/.565*113,419,528);sx=624+rr*np.cos(angle);sy=600-rr*np.sin(angle);pixels_per_unit=177
  gradient=np.stack([map_coordinates(fields[short][:,:,i],[sy,sx],order=1,mode='nearest') for i in range(2)],1)*pixels_per_unit*p['normal_height_amplitude'];gradient=np.c_[gradient,np.zeros(len(x))]
  gradient-=n*np.sum(n*gradient,axis=1)[:,None]
  world=n-gradient;world/=np.linalg.norm(world,axis=1)[:,None]
  delta=st[1:]-st[0];position=pts[tri[1:]]-pts[tri[0]];det=np.linalg.det(delta)
  if abs(det)<1e-12:continue
  raw_t=(delta[1,1]*position[0]-delta[0,1]*position[1])/det;raw_b=(-delta[1,0]*position[0]+delta[0,0]*position[1])/det
  t=raw_t[None,:]-n*np.sum(n*raw_t,axis=1)[:,None];length=np.linalg.norm(t,axis=1);safe=length>1e-10;t[safe]/=length[safe,None]
  b=np.cross(n,t);b*=np.where(np.sum(b*raw_b,axis=1)>=0,1,-1)[:,None]
  tangent=np.stack([np.sum(world*t,1),np.sum(world*b,1),np.sum(world*n,1)],1)
  # Export has no normal-strength socket: encode flat+k*(n-flat) now.
  tangent=np.array([0,0,1])+p['normal_baked_strength']*(tangent-np.array([0,0,1]));tangent/=np.linalg.norm(tangent,axis=1)[:,None]
  limit=np.radians(p['normal_max_angle_degrees'][short]);angle=np.arctan2(np.linalg.norm(tangent[:,:2],axis=1),tangent[:,2]);scale=np.minimum(1,np.tan(limit)/np.maximum(np.linalg.norm(tangent[:,:2],axis=1)/tangent[:,2],1e-9));tangent[:,:2]*=scale[:,None];tangent/=np.linalg.norm(tangent,axis=1)[:,None]
  out[y[safe],x[safe]]=tangent[safe];valid[y[safe],x[safe]]=True
 nearest=distance_transform_edt(~valid,return_distances=False,return_indices=True);out[~valid]=out[nearest[0][~valid],nearest[1][~valid]]
 rgb=np.rint(np.clip(out*.5+.5,0,1)*255).astype('uint8');name='USDZ_'+short+'_normal.png';Image.fromarray(rgb).save(r/'source/bakes'/name,compress_level=9)
 encoded=rgb.astype(float)/255*2-1;encoded/=np.linalg.norm(encoded,axis=2)[:,:,None];angles=np.degrees(np.arctan2(np.linalg.norm(encoded[:,:,:2],axis=2),encoded[:,:,2]))
 report[short]={'file':name,'size':[512,512],'strength_baked':p['normal_baked_strength'],'height_amplitude_units':p['normal_height_amplitude'],'angle_mean_degrees':float(angles[valid].mean()),'angle_p95_degrees':float(np.percentile(angles[valid],95)),'angle_max_degrees':float(angles[valid].max()),'edge_fade_reference_pixels':4,'tangent_frame':'actual shipped UV Jacobian and interpolated corner normals','normal_node_strength':1,'bytes':(r/'source/bakes'/name).stat().st_size}
(r/'reports/restrained_normal_bake.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
