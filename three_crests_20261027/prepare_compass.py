"""Build the compass as exact planar cuts above an unpainted navy backing."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation,distance_transform_edt,map_coordinates

def encode(a):return np.uint8(np.clip(np.where(a<=.0031308,a*12.92,1.055*np.maximum(a,0)**(1/2.4)-.055)*255+.5,0,255))
def prepare(root,candidate):
 trace=json.loads((candidate/'trace.json').read_text());cfg=json.loads((root/'design.json').read_text());feature=cfg['facets'][0]
 with np.load(candidate/'geometry.npz') as d:data={k:d[k] for k in d.files}
 with np.load(candidate/'finish.npz') as d:albedo=d['albedo'];emission=d['emission']
 W,H=trace['reference_size'];N=albedo.shape[0];outline=np.array(feature['outline'],float);center=np.array(feature['center'],float)
 bounds=np.r_[outline.min(0)-8,outline.max(0)+8]
 for name,linear in [('color',albedo),('emission',emission/8)]:
  image=Image.fromarray(encode(linear));box=(bounds[0]*N/W,bounds[1]*N/H,bounds[2]*N/W,bounds[3]*N/H)
  image.transform((512,512),Image.Transform.EXTENT,box,resample=Image.Resampling.BICUBIC).save(candidate/'textures'/('star_'+name+'.png'))
 # Reconstruct only the navy surface hidden under the raised star. Its own
 # finish remains on the independent planar compass mesh.
 mask_image=Image.new('L',(N,N));ImageDraw.Draw(mask_image).polygon([tuple(q*[N/W,N/H]) for q in outline],fill=255)
 mask=np.asarray(mask_image)>0;known=~binary_dilation(mask,iterations=8)
 _,nearest=distance_transform_edt(~known,return_indices=True)
 for name,linear in [('color',albedo),('emission',emission/8)]:
  fill=linear.copy();fill[mask]=linear[tuple(nearest[:,mask])];Image.fromarray(encode(fill)).save(candidate/'textures'/('surface_'+name+'.png'))
 # The backing is flat beneath the independent compass, avoiding an extra
 # heightfield star and its stair shaped walls at a side angle.
 region=Image.new('L',(W,H));ImageDraw.Draw(region).polygon([tuple(q) for q in outline],fill=255)
 region=binary_dilation(np.asarray(region)>0,iterations=3)
 reference=data['reference_points'];selected=map_coordinates(region.astype(float),[reference[:,1],reference[:,0]],order=0,mode='nearest')>.5
 count=len(reference);points=data['points'];front=np.flatnonzero(selected);points[front,2]=.075;points[front+count,2]=-.075;data['points']=points;data['height'][region]=.075
 p=np.vstack([outline,center]);scale=trace['reference_scale'];lo=np.array(trace['reference_bounds'][0]);cx=trace['reference_center'][0]
 v=np.c_[(p[:,0]-cx)*scale,3.015-(p[:,1]-lo[1])*scale,np.r_[[feature['seat']]*len(outline),feature['crest']]]
 n=len(outline);t=np.array([(n,(i+1)%n,i) for i in range(n)],np.int32)
 # Ensure the original source Y inversion still produces outward front faces.
 cross=np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]);t[cross[:,2]<0]=t[cross[:,2]<0,::-1]
 back=v.copy();back[:,2]*=-1;v=np.vstack([v,back]);faces=np.vstack([t,t[:,::-1]+n+1])
 uv=np.c_[(p[:,0]-bounds[0])/(bounds[2]-bounds[0]),1-(p[:,1]-bounds[1])/(bounds[3]-bounds[1])];uv=np.vstack([uv,uv])
 walls=[]
 for a in range(n):
  b=(a+1)%n;walls.extend([(a,b+n+1,b),(a,a+n+1,b+n+1)])
 # Reorient walls by following the actual positive front boundary winding.
 edges=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,ids,counts=np.unique(np.sort(edges,axis=1),axis=0,return_index=True,return_counts=True);walls=[]
 for a,b in edges[ids[counts==1]]:walls.extend([(a,b+n+1,b),(a,a+n+1,b+n+1)])
 data['explicit_star_points']=v;data['explicit_star_triangles']=faces;data['explicit_star_uv']=uv;data['explicit_star_wall_triangles']=np.array(walls,np.int32)
 np.savez_compressed(candidate/'geometry.npz',**data)
 (candidate/'compass.json').write_text(json.dumps({'primary_planes':n,'separate_compass_geometry':True,'navy_backing_reconstructed_under_compass':True,'star_texture_size':512},indent=2)+'\n')
 print('Separate compass built with',n,'primary planes on each face')
if __name__=='__main__':
 root=Path(__file__).resolve().parent/'crescent_ocean';candidate=root/(root/'candidate.txt').read_text().strip();prepare(root,candidate)
