"""Three closed amber diamonds with real primary front and rear planes."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,distance_transform_edt,map_coordinates

def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
def prepare(root,candidate):
 trace=json.loads((candidate/'trace.json').read_text());cfg=json.loads((root/'design.json').read_text())
 with np.load(candidate/'geometry.npz') as d:data={k:d[k] for k in d.files}
 with np.load(candidate/'finish.npz') as d:albedo=d['albedo'];emission=d['emission']
 W,H=trace['reference_size'];N=albedo.shape[0];mask_image=Image.new('L',(N,N));dr=ImageDraw.Draw(mask_image)
 region=Image.new('L',(W,H));rr=ImageDraw.Draw(region)
 vertices=[];triangles=[];walls=[];uvs=[];count=len(data['reference_points'])
 bezel_vertices=[];bezel_faces=[];bezel_walls=[];bezel_uv=[]
 yy,xx=np.mgrid[:H,:W];grid=np.c_[xx.ravel(),yy.ravel()]
 scale=trace['reference_scale'];lo=np.array(trace['reference_bounds'][0]);cx=trace['reference_center'][0]
 def to_world(p,z):return np.c_[(p[:,0]-cx)*scale,3.015-(p[:,1]-lo[1])*scale,z]
 def orient(v,t):
  t=np.array(t,np.int32);normal=np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]])
  t[normal[:,2]<0]=t[normal[:,2]<0,::-1];return t
 for outer_spec,gem in zip(cfg['facets'][:3],cfg['gems']):
  outer=np.array(outer_spec['outline'],float);center=np.array(outer_spec['center'],float)
  ridge=center+(outer-center)*.76;inner=np.array(gem['outline'],float)
  p=np.vstack([outer,ridge,inner]);z=np.r_[[outer_spec['seat']]*4,[outer_spec['crest']]*4,[gem['seat']+.025]*4]
  front=to_world(p,z);t=[]
  for ring in [0,1]:
   for i in range(4):
    a=ring*4+i;b=ring*4+(i+1)%4;c=(ring+1)*4+i;d=(ring+1)*4+(i+1)%4
    t.extend([(a,b,d),(a,d,c)])
  t=orient(front,t);back=front.copy();back[:,2]*=-1;offset=len(bezel_vertices)
  bezel_vertices.extend(np.vstack([front,back]));bezel_faces.extend(np.vstack([t,t[:,::-1]+12])+offset)
  edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,ids,counts=np.unique(np.sort(edges,axis=1),axis=0,return_index=True,return_counts=True)
  for a,b in edges[ids[counts==1]]:bezel_walls.extend([(offset+a,offset+b+12,offset+b),(offset+a,offset+a+12,offset+b+12)])
  uv=np.c_[p[:,0]/W,1-p[:,1]/H];bezel_uv.extend(np.vstack([uv,uv]))
  # The old raster silhouette remains only as a hidden support. The
  # visible outer walls and bevels are straight geometric planes.
  def support_weight(q):
   limits=[]
   for a,b in zip(outer,np.roll(outer,-1,axis=0)):
    edge=b-a;n=np.array([edge[1],-edge[0]]);limits.append(((q-center)@n)/float((a-center)@n))
   blend=np.clip((1.65-np.max(limits,axis=0))/.65,0,1);return blend*blend*(3-2*blend)
  weight=support_weight(data['reference_points']);seat=outer_spec['seat']-.07
  depth=data['points'][:count,2]*(1-weight)+seat*weight;data['points'][:count,2]=depth;data['points'][count:,2]=-depth
  weight=support_weight(grid).reshape(H,W);data['height']=data['height']*(1-weight)+seat*weight
 data['render_height']=data['height'].copy()
 for spec,gem in zip(cfg['facets'][:3],cfg['gems']):
  outer=np.array(spec['outline'],float);center=np.array(spec['center'],float);p=np.vstack([outer,center+(outer-center)*.76,np.array(gem['outline'],float)])
  depth=np.r_[[spec['seat']]*4,[spec['crest']]*4,[gem['seat']+.025]*4]
  for ring in [0,1]:
   for i in range(4):
    a=ring*4+i;b=ring*4+(i+1)%4;c=(ring+1)*4+i;d=(ring+1)*4+(i+1)%4
    for ia,ib,ic in [(a,b,d),(a,d,c)]:
     aa=p[ib]-p[ia];bb=p[ic]-p[ia];det=aa[0]*bb[1]-aa[1]*bb[0]
     u=((xx-p[ia,0])*bb[1]-(yy-p[ia,1])*bb[0])/det;v=(aa[0]*(yy-p[ia,1])-aa[1]*(xx-p[ia,0]))/det
     inside=(u>=0)&(v>=0)&(u+v<=1);value=depth[ia]*(1-u-v)+depth[ib]*u+depth[ic]*v
     data['render_height'][inside]=value[inside]
 data['explicit_bezel_points']=np.array(bezel_vertices);data['explicit_bezel_triangles']=np.array(bezel_faces,np.int32);data['explicit_bezel_wall_triangles']=np.array(bezel_walls,np.int32);data['explicit_bezel_uv']=np.array(bezel_uv)
 for feature in cfg['gems']:
  outline=np.array(feature['outline'],float);center=np.array(feature['center'],float)
  dr.polygon([tuple(q*[N/W,N/H]) for q in outline],fill=255);rr.polygon([tuple(q) for q in outline],fill=255)
  p=np.vstack([outline,center]);scale=trace['reference_scale'];lo=np.array(trace['reference_bounds'][0]);cx=trace['reference_center'][0]
  v=np.c_[(p[:,0]-cx)*scale,3.015-(p[:,1]-lo[1])*scale,np.r_[[feature['seat']]*4,feature['crest']]]
  t=np.array([(4,(i+1)%4,i) for i in range(4)],np.int32)
  cross=np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]);t[cross[:,2]<0]=t[cross[:,2]<0,::-1]
  back=v.copy();back[:,2]*=-1;offset=len(vertices);vertices.extend(np.vstack([v,back]))
  triangles.extend(np.vstack([t,t[:,::-1]+5])+offset)
  edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,ids,counts=np.unique(np.sort(edges,axis=1),axis=0,return_index=True,return_counts=True)
  for a,b in edges[ids[counts==1]]:walls.extend([(offset+a,offset+b+5,offset+b),(offset+a,offset+a+5,offset+b+5)])
  uv=np.c_[p[:,0]/W,1-p[:,1]/H];uvs.extend(np.vstack([uv,uv]))
 data['explicit_star_points']=np.array(vertices);data['explicit_star_triangles']=np.array(triangles,np.int32);data['explicit_star_wall_triangles']=np.array(walls,np.int32);data['explicit_star_uv']=np.array(uvs)
 lookup={(float(q[0]),float(q[1]),int(np.sign(q[2]))):q[2] for q in data['points']}
 for q in data['wall_points']:q[2]=lookup[(float(q[0]),float(q[1]),int(np.sign(q[2])))]
 np.savez_compressed(candidate/'geometry.npz',**data)
 mask=np.asarray(mask_image)>0;known=~binary_dilation(mask,iterations=5);_,nearest=distance_transform_edt(~known,return_indices=True)
 for name,linear in [('color',albedo),('emission',emission/8)]:
  im=Image.fromarray(encode(linear));im.resize((512,512),Image.Resampling.LANCZOS).save(candidate/'textures'/('star_'+name+'.png'))
  filled=linear.copy();filled[mask]=linear[tuple(nearest[:,mask])];Image.fromarray(encode(filled)).save(candidate/'textures'/('surface_'+name+'.png'))
 (candidate/'gems.json').write_text(json.dumps({'count':3,'front_primary_planes_each':4,'rear_primary_planes_each':4,'closed_gems':True,'texture_size':512},indent=2)+'\n')
 print('Three closed amber diamonds prepared',flush=True)
