"""Transfer de-lit reference detail into the preserved silver UV atlas; no normals."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,map_coordinates,distance_transform_edt
r=Path(__file__).resolve().parents[1];bakes=r/'source/bakes'
p=json.loads((r/'parameters.json').read_text());ref=np.asarray(Image.open(r/'source/forged_reference.png').convert('RGB'),dtype=float)/255
linear=np.where(ref<=.04045,ref/12.92,((ref+.055)/1.055)**2.4)
h,w=linear.shape[:2];yy,xx=np.mgrid[:h,:w];rad=np.hypot(xx-624,yy-600)
def field(mask,sigma,limits=(.45,1.65)):
 weights=gaussian_filter(mask.astype(float),sigma)
 blur=np.stack([gaussian_filter(linear[:,:,i]*mask,sigma) for i in range(3)],2)/np.maximum(weights[:,:,None],1e-8)
 f=np.clip(linear/np.maximum(blur,.004),*limits)
 f[~mask]=1
 return f
rim_mask=(rad>414)&(rad<535);rim_detail=field(rim_mask,14)
inset_mask=(rad<421)
emask=Image.new('L',(w,h));dr=ImageDraw.Draw(emask);dr.polygon([tuple(x) for x in p['reference_pixel_vertices'][:7]],fill=255)
inset_mask &= gaussian_filter(np.array(emask,dtype=float),12)<.1
inset_detail=field(inset_mask,10)
crystal_detail=np.ones_like(linear)
for face in p.get('reference_front_faces',p['front_faces']):
 mask=Image.new('L',(w,h));ImageDraw.Draw(mask).polygon([tuple(p['reference_pixel_vertices'][i]) for i in face],fill=255)
 m=np.array(mask)>0;f=field(m,15,p.get('crystal_texture_limits',[.45,1.65]));crystal_detail[m]=f[m]
def sample(field,x,y):
 return np.stack([map_coordinates(field[:,:,i],[y,x],order=1,mode='nearest') for i in range(3)],axis=-1)
def encode(color):
 color=np.clip(color,0,1);return np.rint(np.where(color<=.0031308,12.92*color,1.055*color**(1/2.4)-.055)*255).astype('uint8')
def save(name,a,color=False):
 a=encode(a) if color else np.rint(np.clip(a,0,1)*255).astype('uint8')
 if a.ndim==2:a=np.repeat(a[:,:,None],3,2)
 Image.fromarray(a).save(bakes/(name+'.png'),compress_level=9)
geometry=json.loads((r/'work/uv_geometry.json').read_text())
def atlas(key,detail,role):
 g=next(v for k,v in geometry.items() if k.startswith(key+'___'));pts=np.array(g['points']);uv=np.array(g['uv']);indices=np.array(g['indices'])
 result=np.ones((512,512,3));valid=np.zeros((512,512),bool)
 for tri,tex in zip(indices,uv):
  q=tex*np.array([511,-511])+np.array([0,511]);x0,y0=np.maximum(np.floor(q.min(0)).astype(int),0);x1,y1=np.minimum(np.ceil(q.max(0)).astype(int),511)
  if x0>x1 or y0>y1:continue
  mat=np.vstack([q.T,np.ones(3)])
  if abs(np.linalg.det(mat))<1e-10:continue
  gy,gx=np.mgrid[y0:y1+1,x0:x1+1];bary=np.linalg.solve(mat,np.stack([gx.ravel(),gy.ravel(),np.ones(gx.size)]))
  keep=(bary.min(0)>=-1e-4);x=gx.ravel()[keep];y=gy.ravel()[keep]
  if not len(x):continue
  xyz=bary[:,keep].T@pts[tri];radius=np.hypot(xyz[:,0],xyz[:,1]);angle=np.arctan2(xyz[:,1],xyz[:,0])
  if role=='rim':
   radius=np.clip(414+(radius-2.45)/(3.015-2.45)*113,419,528)
   sx=624+radius*np.cos(angle);sy=600-radius*np.sin(angle)
  else:sx=624+xyz[:,0]*164;sy=600-xyz[:,1]*164
  result[y,x]=sample(detail,sx,sy);valid[y,x]=True
 # Nearest valid padding prevents texture-filter seams without modifying UVs.
 nearest=distance_transform_edt(~valid,return_distances=False,return_indices=True);result[~valid]=result[nearest[0][~valid],nearest[1][~valid]]
 return result
rim=atlas('Casing',rim_detail,'rim');inset=atlas('Inset',inset_detail,'inset')
strength=p.get('texture_strength',1.)
for stem,col,rough,f in [('USDZ_Casing',(.25,.24,.225),.325,rim),('USDZ_Casing_outer',(.245,.235,.22),.30,rim),('USDZ_Casing_back',(.055,.052,.048),.32,np.ones_like(rim)),('USDZ_Inset',tuple(p.get('inset_color',[.009,.010,.011])),.83,inset)]:
 detail=np.clip(1+(f-1)*strength,.45,1.65);save(stem+'_base_color',np.array(col)*detail,color=True)
 save(stem+'_roughness',np.clip(rough+.14*(1-detail.mean(2)),.22,.95))
y,x=np.mgrid[:512,:512];wx=(x/511)*2.8-1.4;wy=(1-y/511)*4.3-2.15
emblem_scale=p.get('emblem_scale',1.)
f=sample(crystal_detail,629+wx*682/(4.064*emblem_scale),606-wy*682/(4.064*emblem_scale));f=np.clip(1+(f-1)*p.get('crystal_texture_strength',strength),*p.get('crystal_texture_limits',[.45,1.65]))
gain=np.ones((512,512))
for index,value in p.get('plane_color_gains',{}).items():
 face=p['front_faces'][int(index)];pts=[]
 for i in face:
  ox,oy,_=(p['outline']+p['interior'])[i];px=(ox+1.4)/2.8*511;py=(1-(oy+2.15)/4.3)*511;pts.append((px,py))
 mask=Image.new('L',(512,512));ImageDraw.Draw(mask).polygon(pts,fill=255);gain[np.array(mask)>0]=value
f*=gain[:,:,None]
save('USDZ_Emblem_base_color',np.array(p['main_color'])*f,color=True)
save('USDZ_Emblem_shaded_base_color',np.array(p['shaded_color'])*f,color=True)
save('USDZ_Emblem_roughness',np.clip(p['roughness']+.17*(1-f.mean(2)),.25,.53))
summary={}
for path in bakes.glob('*.png'):
 if 'normal' in path.name:continue
 a=np.asarray(Image.open(path).convert('RGB'));summary[path.name]={'size':list(a.shape[:2]),'rgb_min':a.min((0,1)).tolist(),'rgb_max':a.max((0,1)).tolist(),'bytes':path.stat().st_size}
(r/'reports/forged_textures.json').write_text(json.dumps(summary,indent=2))
# Unretouched texture sheet for inspecting the real shipped detail.
sheet=Image.new('RGB',(1536,1054),(22,22,22));draw=ImageDraw.Draw(sheet)
for i,n in enumerate(['USDZ_Casing_base_color','USDZ_Inset_base_color','USDZ_Emblem_base_color','USDZ_Casing_roughness','USDZ_Inset_roughness','USDZ_Emblem_roughness']):
 xx=i%3*512;yy=i//3*527;draw.text((xx+4,yy+2),n,fill='white');sheet.paste(Image.open(bakes/(n+'.png')).convert('RGB'),(xx,yy+15))
sheet.save(r/'proof/forged_texture_sheet.png')
print(json.dumps(summary,indent=2));print('Forged reference detail transferred without normal maps.')
