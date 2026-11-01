"""Closed crystal forms and straight planar settings for the four crests."""
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,distance_transform_edt,map_coordinates

def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))

def prepare(root,C):
 cfg=json.loads((root/'design.json').read_text());trace=json.loads((C/'trace.json').read_text())
 with np.load(C/'geometry.npz') as f:D={k:f[k] for k in f.files}
 with np.load(C/'finish.npz') as f:color=f['albedo'];emission=f['emission']
 W,H=trace['reference_size'];N=color.shape[0];yy,xx=np.mgrid[:H,:W];scale=trace['reference_scale'];lo=trace['reference_bounds'][0];cx=trace['reference_center'][0];count=len(D['reference_points'])
 def polygon(points):
  im=Image.new('L',(W,H));ImageDraw.Draw(im).polygon([tuple(p) for p in points],fill=255);return np.asarray(im)>0
 def world(p,z):return np.c_[(p[:,0]-cx)*scale,3.015-(p[:,1]-lo[1])*scale,z]
 def orient(v,t):
  t=np.array(t,np.int32);normal=np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]);t[normal[:,2]<0]=t[normal[:,2]<0,::-1];return t
 def mesh_add(group,p,z,t):
  front=world(p,z);t=orient(front,t);back=front.copy();back[:,2]*=-1;n=len(p);offset=len(group['points'])
  group['points'].extend(np.vstack([front,back]));group['triangles'].extend(np.vstack([t,t[:,::-1]+n])+offset)
  edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,ids,counts=np.unique(np.sort(edges,axis=1),axis=0,return_index=True,return_counts=True)
  for a,b in edges[ids[counts==1]]:group['walls'].extend([(offset+a,offset+b+n,offset+b),(offset+a,offset+a+n,offset+b+n)])
  uv=np.c_[p[:,0]/W,1-p[:,1]/H];group['uv'].extend(np.vstack([uv,uv]));return t
 def raster(p,z,t,target):
  for ia,ib,ic in t:
   aa=p[ib]-p[ia];bb=p[ic]-p[ia];det=aa[0]*bb[1]-aa[1]*bb[0]
   if abs(det)<1e-8:continue
   x0=max(0,int(p[[ia,ib,ic],0].min())-1);x1=min(W,int(p[[ia,ib,ic],0].max())+2);y0=max(0,int(p[[ia,ib,ic],1].min())-1);y1=min(H,int(p[[ia,ib,ic],1].max())+2)
   gx=xx[y0:y1,x0:x1]-p[ia,0];gy=yy[y0:y1,x0:x1]-p[ia,1]
   u=(gx*bb[1]-gy*bb[0])/det;v=(aa[0]*gy-aa[1]*gx)/det;m=(u>=-1e-6)&(v>=-1e-6)&(u+v<=1+1e-6)
   values=z[ia]*(1-u-v)+z[ib]*u+z[ic]*v;patch=target[y0:y1,x0:x1];patch[m]=values[m]
 def support(outline,center,seat):
  # A broad transition stays smooth behind a visible planar setting.
  region=polygon(outline);inside=distance_transform_edt(region);outside=distance_transform_edt(~region)
  margin=min(64,max(15,float(np.ptp(outline,axis=0).min())*.3))
  field=np.clip((inside-outside+margin)/margin,0,1);field=field*field*(3-2*field)
  def weight(q):
   return map_coordinates(field,[q[:,1],q[:,0]],order=1,mode='nearest')
  w=weight(D['reference_points']);depth=D['points'][:count,2]*(1-w)+seat*w;D['points'][:count,2]=depth;D['points'][count:,2]=-depth
  # Row batches avoid a large temporary source grid for each setting.
  for start in range(0,H,100):
   end=min(H,start+100);w=weight(np.c_[xx[start:end].ravel(),yy[start:end].ravel()]).reshape(end-start,W)
   D['height'][start:end]=D['height'][start:end]*(1-w)+seat*w
 groups={role:{name:[] for name in ['points','triangles','walls','uv']} for role in ['star','bezel']}
 gem_mask=np.zeros((H,W),bool);bezel_mask=np.zeros((H,W),bool);bezel_specs=[]
 for feature in cfg.get('gems',[]):
  outline=np.array(feature['outline'],float);center=np.array(feature['center'],float);n=len(outline)
  gem_mask|=polygon(outline)
  if feature.get('bezel'):
   spec=feature['bezel'];outer=np.array(spec['outline'],float);inner_outline=np.array(spec.get('inner',outline),float)
   if len(outer)!=len(inner_outline):
    # Match both loops by ray angle, retaining every outer tip.
    angles=np.linspace(-np.pi/2,3*np.pi/2,max(n,len(outer)),endpoint=False)
    def radial(poly):
     out=[]
     for angle in angles:
      direction=np.array([np.cos(angle),np.sin(angle)]);hits=[]
      for a,b in zip(poly,np.roll(poly,-1,axis=0)):
       edge=b-a;M=np.c_[direction,-edge]
       if abs(np.linalg.det(M))<1e-10:continue
       t,u=np.linalg.solve(M,a-center)
       if t>0 and -.00001<=u<=1.00001:hits.append(t)
      out.append(center+direction*min(hits))
     return np.array(out)
    outer=radial(outer);inner=radial(inner_outline)
   else:inner=inner_outline
   bezel_mask|=polygon(outer)&~polygon(inner)
   m=len(outer);ridge=center+(outer-center)*spec.get('ridge_fraction',.76);p=np.vstack([outer,ridge,inner]);z=np.r_[[spec['seat']]*m,[spec['crest']]*m,[spec.get('inner_height',feature['seat']-.01)]*m];t=[]
   for ring in [0,1]:
    for i in range(m):
     a=ring*m+i;b=ring*m+(i+1)%m;c=(ring+1)*m+i;d=(ring+1)*m+(i+1)%m;t.extend([(a,b,d),(a,d,c)])
   t=mesh_add(groups['bezel'],p,z,t);bezel_specs.append((p,z,t));support(outer,center,max(.06,spec['seat']-.07))
  else:support(outline,center,max(.06,feature['seat']-.07))
  if feature.get('lens'):
   p=np.vstack([outline,center+(outline-center)*.65,center+(outline-center)*.28,center]);rise=feature['crest']-feature['seat'];z=np.r_[[feature['seat']]*n,[feature['seat']+rise*.75]*n,[feature['seat']+rise*.96]*n,feature['crest']];t=[]
   for ring in [0,1]:
    for i in range(n):
     a=ring*n+i;b=ring*n+(i+1)%n;c=(ring+1)*n+i;d=(ring+1)*n+(i+1)%n;t.extend([(a,b,d),(a,d,c)])
   t.extend([(3*n,2*n+(i+1)%n,2*n+i) for i in range(n)])
  else:p=np.vstack([outline,center]);z=np.r_[[feature['seat']]*n,feature['crest']];t=[(n,(i+1)%n,i) for i in range(n)]
  t=mesh_add(groups['star'],p,z,t)
  if 'detail_star_height' not in D:D['detail_star_height']=np.zeros((H,W),float)
  raster(p,z,t,D['detail_star_height'])
 for feature in cfg.get('ornaments',[]):
  outline=np.array(feature['outline'],float);center=outline.mean(0);n=len(outline);p=np.vstack([outline,center]);z=np.r_[[feature['seat']]*n,feature.get('crest',feature['seat'])];t=[(n,(i+1)%n,i) for i in range(n)];t=mesh_add(groups['bezel'],p,z,t);bezel_specs.append((p,z,t));bezel_mask|=polygon(outline)
 D['render_height']=D['height'].copy()
 for p,z,t in bezel_specs:raster(p,z,t,D['render_height'])
 for role,group in groups.items():
  if not group['points']:continue
  prefix='explicit_'+role+'_'
  D[prefix+'points']=np.array(group['points']);D[prefix+'triangles']=np.array(group['triangles'],np.int32);D[prefix+'wall_triangles']=np.array(group['walls'],np.int32);D[prefix+'uv']=np.array(group['uv'])
 lookup={(float(p[0]),float(p[1]),int(np.sign(p[2]))):p[2] for p in D['points']}
 for p in D['wall_points']:p[2]=lookup[(float(p[0]),float(p[1]),int(np.sign(p[2])))]
 D['detail_gem_mask']=gem_mask;D['detail_bezel_mask']=bezel_mask;np.savez_compressed(C/'geometry.npz',**D)
 # The independent gem keeps its reference while its hidden support gets
 # the nearest surrounding tone, preventing a duplicate glowing gem.
 atlas_mask=np.asarray(Image.fromarray(np.uint8(gem_mask&~bezel_mask)*255).resize((N,N),Image.Resampling.NEAREST))>0
 known=~binary_dilation(atlas_mask,iterations=5);_,nearest=distance_transform_edt(~known,return_indices=True)
 for suffix,linear in [('color',color),('emission',emission/8)]:
  Image.fromarray(encode(linear)).resize((cfg.get('gem_texture_size',512),)*2,Image.Resampling.LANCZOS).save(C/'textures'/('star_'+suffix+'.png'))
  filled=linear.copy()
  if not cfg.get('keep_support_texture'):filled[atlas_mask]=linear[tuple(nearest[:,atlas_mask])]
  Image.fromarray(encode(filled)).save(C/'textures'/('surface_'+suffix+'.png'))
 (C/'gems.json').write_text(json.dumps({'count':len(cfg.get('gems',[])),'closed_gems':True,'independent_planar_settings':len(bezel_specs),'gem_texture_size':cfg.get('gem_texture_size',512)},indent=2)+'\n')
 print('Prepared closed crystal forms and planar settings',flush=True)

 from dynamic_gems import prepare as prepare_dynamic
 prepare_dynamic(root,C)
