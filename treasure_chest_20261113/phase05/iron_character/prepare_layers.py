from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw,ImageOps
from scipy.ndimage import gaussian_filter,map_coordinates,label,distance_transform_edt
D=Path(__file__).resolve().parent;P=D.parents[1];F=D/'layers';F.mkdir(exist_ok=True);R=P/'phase05/lower_iron/resources';W,H=8192,256;L,T=18.04,.5035;U,Y=np.meshgrid(np.linspace(0,L,W,dtype=np.float32),np.linspace(-1.714,-2.2175,H,dtype=np.float32));X=U-2.73

def ss(a,b,z):t=np.clip((z-a)/(b-a),0,1);return t*t*(3-2*t)
def source(asset,role,period,offset):
 image=Image.open(next((R/asset).glob('*'+role+'.png')));raw=np.asarray(image);im=raw.astype(np.float32)/65535 if raw.dtype==np.uint16 or (image.mode=='I' and raw.max()>255) else np.asarray(image.convert('L'),dtype=np.float32)/255;u=(U/period+offset)%1*(im.shape[1]-1);v=((Y+2.2175)/period+.327)%1*(im.shape[0]-1);return map_coordinates(im,[v,u],order=1,mode='wrap')
def normalize(a,p=4):return np.clip((a-np.percentile(a,p))/(np.percentile(a,100-p)-np.percentile(a,p)+1e-8),0,1)
weather=normalize(gaussian_filter(source('Metal025','Roughness',1.1,.19),(1.4,2.5)));roughness=normalize(gaussian_filter(source('Metal003','Roughness',.62,.58),(.6,1.0)));pigment=normalize(gaussian_filter(source('Metal025','Displacement',.87,.71),(2.5,4.0)))
assert np.isfinite(pigment).all() and np.ptp(pigment)>.1,'Intended pigment variation was flattened during source loading'
protection=np.ones_like(U)
for xc in [-1.1255,1.1255]:protection*=ss(.105,.17,np.hypot(X-xc,Y+1.96575))
# Rectify the owner's reference. Only interior feature shapes are used, never source RGB or directional illumination.
ref=Image.open(P/'reference.png').convert('RGB');configs=[([-2.08,-.34],[(505,951),(737,932),(740,1007),(516,1024)]),([.35,2.08],[(841,925),(1076,908),(1066,988),(842,1008)])];mark=np.zeros_like(U);previews=[]
for (lo,hi),corners in configs:
 tl,tr,br,bl=corners;rect=ref.transform((700,210),Image.Transform.QUAD,tuple(v for p in [tl,bl,br,tr] for v in p),Image.Resampling.BICUBIC);a=np.asarray(rect,dtype=np.float32)/255;lum=a@np.array([.2126,.7152,.0722],np.float32);sig=1.2;xx=gaussian_filter(lum,sig,order=(0,2));yy=gaussian_filter(lum,sig,order=(2,0));xy=gaussian_filter(lum,sig,order=(1,1));eigmin=(xx+yy-np.sqrt((xx-yy)**2+4*xy*xy))*.5;ridge=np.maximum(-eigmin,0);detail=np.maximum(lum-gaussian_filter(lum,(3.5,4.8)),0);feature=ss(.003,.014,ridge)*ss(.008,.065,detail)
 v,u=np.meshgrid(np.linspace(0,1,210),np.linspace(0,1,700),indexing='ij');inside=ss(.025,.09,u)*(1-ss(.91,.98,u))*ss(.05,.14,v)*(1-ss(.76,.88,v));source_knob=np.hypot((u-.49)*(hi-lo),(v-.50)*T);inside*=ss(.13,.18,source_knob)*ss(.14,.19,np.hypot((u-.44)*(hi-lo),(v-.64)*T));theta=.5*np.arctan2(2*xy,xx-yy);normalx=-np.sin(theta);normaly=np.cos(theta);gy,gx=np.indices(ridge.shape,dtype=np.float32);ahead=map_coordinates(ridge,[gy+normaly,gx+normalx],order=1,mode='nearest');behind=map_coordinates(ridge,[gy-normaly,gx-normalx],order=1,mode='nearest');binary=(feature>.20)&(inside>.1)&(ridge>=ahead)&(ridge>=behind);labs,n=label(binary);sizes=np.bincount(labs.ravel());binary&=(sizes[labs]>=3);shape=np.clip(gaussian_filter(binary.astype(np.float32),.8)*2.1,0,1)*inside
 ids=(X>=lo)&(X<=hi);tx=(X[ids]-lo)/(hi-lo)*699;ty=(-1.714-Y[ids])/T*209;mark[ids]=map_coordinates(shape,[ty,tx],order=1,mode='constant');previews.append((rect,Image.fromarray(np.uint8(shape*255))))
mark*=protection;exposed=mark*ss(.35,.76,roughness);markheight=np.maximum(mark,0)**.80;assert np.isfinite(markheight).all()
# Preserve existing chip locations and add an editable mask for their locally exposed lips.
edge=np.zeros_like(U);damage=[]
for side,items in [('top',[(-1.97,.052,.011),(-.68,.067,.017),(.55,.041,.011),(1.42,.060,.017),(1.88,.040,.010)]),('bottom',[(-1.65,.060,.010),(-.95,.047,.010),(.8,.072,.014),(1.9,.048,.009)])]:
 for xc,width,depth in items:
  xx=(X-xc)/width;shape=np.where(xx<.15,np.clip((xx+1)/1.15,0,1),np.clip((1-xx)/.85,0,1))**1.3;v=(Y+1.714) if side=='top' else (Y+2.2175);lip=np.exp(-(v/.035)**2);edge=np.maximum(edge,shape*lip*.93);damage.append(dict(side=side,x=xc,width=width,extra_depth=depth))
edge*=protection
for name,a in [('weather',weather),('roughness',roughness),('pigment',pigment),('protection',protection),('exposed',exposed),('edge_wear',edge)]:Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5)).save(F/(name+'.png'))
Image.fromarray(np.uint16(markheight*65535+.5)).save(F/'mark_height16.png');np.savez_compressed(F/'fields.npz',weather=weather,roughness=roughness,pigment=pigment,mark=mark,exposed=exposed,edge=edge,protection=protection);(F/'design.json').write_text(json.dumps(dict(reference_surface_corners=configs,reference_usage='Interior ridge shapes only, rebuilt shallow relief. No copied base color or baked directional light.',weathering='Independent scalar channels from cached CC0 ambientCG Metal025 and Metal003. Rust color is not used.',extra_edge_damage=damage,existing_hammer_fields_unchanged=True,contact_regions_protected=True,ridge_nonmaximum_suppression=True),indent=2))
out=Image.new('RGB',(1400,470),'#202020');dr=ImageDraw.Draw(out)
for i,(r,m) in enumerate(previews):out.paste(r,(i*700,30));out.paste(ImageOps.colorize(m,'black','white'),(i*700,260));dr.text((i*700+10,8),'Original reference surface '+str(i+1),fill='white');dr.text((i*700+10,240),'Isolated surface markings, no copied color',fill='white')
out.save(D/'marking_source.jpg',quality=97);print('Prepared independent surface layers; no new hammering')
