"""Cloth appearance fitting diagnostic under the measured native studio.

This is an appearance fit, not a claim that a photograph supplies pure albedo.
Gemstones and metal are excluded. No reflection or emission map is created.
"""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw
from scipy.spatial import ConvexHull
from scipy.ndimage import map_coordinates,gaussian_filter,binary_erosion,distance_transform_edt
from reference_projection import CrownReference
R=Path(__file__).resolve().parent;key,mode=sys.argv[1:3];C=R/key/mode;V=C/'review/cloth_fit_diagnostic';V.mkdir(exist_ok=True)
sys.path.insert(0,str(R.parent/'silver2_metal_claude'));from agx import agx,agx_inv
G=json.loads((C/'groups.json').read_text());D=np.load(C/'blender_geometry.npz');i=next(i for i,g in enumerate(G) if 'velvet cushion' in g['name']);p=D[f'{i}_points'].astype(float);t=D[f'{i}_triangles'];uv=D[f'{i}_uv'].astype(float)
config={'ruby_crown':(627,1022,1010),'emerald_crown':(724,964,914),'amethyst_crown':(768,900,895)}[key];projection=CrownReference(D,G,*config);A=1762.5;cx=603.;native=np.asarray(Image.open(C/'review/native_front_precheck.png').convert('RGB'),float)/255;ref=np.asarray(Image.open(R/key/'reference.png').convert('RGB'),float)/255
# The top source gold point and its native silhouette locate the fixed stage.
gold=np.vstack([D[f'{j}_points'] for j,g in enumerate(G) if g['mat'].startswith('gold')]);qgold=projection.project(gold);rr,gg,bb=native.transpose(2,0,1);mask=(rr>gg*1.035)&(gg>bb*1.06)&(rr>.16);roi=np.zeros(mask.shape,bool);roi[250:840,300:906]=True;ys,xs=np.nonzero(mask&roi);cy=float(ys.min()+.5+A*qgold[:,1].max())
q=projection.project(p);screen=np.c_[cx+A*q[:,0],cy-A*q[:,1]];depth=projection.distance-projection.sine*(p[:,1]+.55)-projection.cosine*p[:,2]
H,W=native.shape[:2];zbuffer=np.full((H,W),np.inf,np.float32);atlas=np.zeros((H,W,2),np.float32)
for tri,tex in zip(t,uv):
 xyz=screen[tri];x0=max(300,int(np.floor(xyz[:,0].min())));x1=min(906,int(np.ceil(xyz[:,0].max()))+1);y0=max(250,int(np.floor(xyz[:,1].min())));y1=min(840,int(np.ceil(xyz[:,1].max()))+1)
 if x0>=x1 or y0>=y1:continue
 den=(xyz[1,1]-xyz[2,1])*(xyz[0,0]-xyz[2,0])+(xyz[2,0]-xyz[1,0])*(xyz[0,1]-xyz[2,1])
 if abs(den)<1e-8:continue
 yy,xx=np.mgrid[y0:y1,x0:x1];xx=xx+.5;yy=yy+.5;b0=((xyz[1,1]-xyz[2,1])*(xx-xyz[2,0])+(xyz[2,0]-xyz[1,0])*(yy-xyz[2,1]))/den;b1=((xyz[2,1]-xyz[0,1])*(xx-xyz[2,0])+(xyz[0,0]-xyz[2,0])*(yy-xyz[2,1]))/den;b2=1-b0-b1;inside=(b0>=-1e-6)&(b1>=-1e-6)&(b2>=-1e-6)
 weights=np.stack([b0,b1,b2],axis=2)/depth[tri];reciprocal=weights.sum(2);distance=1/np.maximum(reciprocal,1e-9);view=zbuffer[y0:y1,x0:x1];use=inside&(distance<view)
 if not use.any():continue
 values=(weights@tex)/reciprocal[...,None];view[use]=distance[use];atlas[y0:y1,x0:x1][use]=values[use]
yy,xx=np.mgrid[:H,:W];qx=(xx+.5-cx)/A;qy=(cy-yy-.5)/A;sx=config[0]+qx/projection.k;sy=config[2]-(qy-projection.bottom)/projection.k;target=np.stack([map_coordinates(ref[:,:,c],[sy,sx],order=1,mode='constant') for c in range(3)],axis=2)
def cloth_mask(a):
 r,g,b=a.transpose(2,0,1)
 if key=='ruby_crown':return (r>g*2.5)&(r>b*1.8)&(r>.025)
 if key=='emerald_crown':return (g>r*2.5)&(g>b*1.25)&(g>.025)
 return (r>g*2)&(b>g*2)&(np.maximum(r,b)>.025)
valid=np.isfinite(zbuffer)&cloth_mask(native)&cloth_mask(target)
# Exclude source stones, including their partly covered edge pixels.
front_stone_mask=np.zeros((H,W),bool)
for j,g in enumerate(G):
 if not g['mat'].startswith('CrestGem_'):continue
 points=D[f'{j}_points'];qj=projection.project(points);x=cx+A*qj[:,0];y=cy-A*qj[:,1];x0=max(0,int(x.min())-3);x1=min(W,int(x.max())+4);y0=max(0,int(y.min())-3);y1=min(H,int(y.max())+4)
 if x0<x1 and y0<y1:
  valid[y0:y1,x0:x1]=False
  stone_depth=projection.distance-projection.sine*(points[:,1]+.55)-projection.cosine*points[:,2]
  hull=ConvexHull(np.c_[x,y]);stamp=Image.new('L',(x1-x0,y1-y0));ImageDraw.Draw(stamp).polygon([(float(x[k]-x0),float(y[k]-y0)) for k in hull.vertices],fill=255);silhouette=np.asarray(stamp)>0
  front_stone_mask[y0:y1,x0:x1]|=silhouette&np.isfinite(zbuffer[y0:y1,x0:x1])&(stone_depth.min()<zbuffer[y0:y1,x0:x1]+.04)
display_mask=np.isfinite(zbuffer)&cloth_mask(native)&~front_stone_mask
valid=binary_erosion(valid,iterations=3);y,x=np.nonzero(valid);assert len(x)>2000,len(x)
def inverse(display):
 desired=np.clip(display,1/1024,1-1/1024);log=np.log2(np.maximum(agx_inv(desired),2**-16))
 for _ in range(9):
  linear=2**log;base=agx(linear);jac=[]
  for c in range(3):
   trial=log.copy();trial[:,c]+=.03;jac.append((agx(2**trial)-base)/.03)
  J=np.stack(jac,axis=2)+np.eye(3)[None,:,:]*.0003
  update=np.linalg.solve(J,(desired-base)[...,None])[...,0];log=np.clip(log+.7*np.clip(update,-2,2),-16,6)
 return 2**log
actual_linear=inverse(native[y,x]);target_linear=inverse(target[y,x]);ratio=np.clip(target_linear/np.maximum(actual_linear,1e-5),.03,30);N=1024;sumlog=np.zeros((N,N,3));weight=np.zeros((N,N));u=atlas[y,x,0]%1;v=np.clip(atlas[y,x,1],0,1);row=np.clip(((1-v)*(N-1)).round().astype(int),0,N-1);col=np.clip((u*(N-1)).round().astype(int),0,N-1)
for offset in [0,N//2]:
 c=(col+offset)%N;np.add.at(weight,(row,c),1)
 for channel in range(3):np.add.at(sumlog[:,:,channel],(row,c),np.log(ratio[:,channel]))
known=weight>0;raw=sumlog/np.maximum(weight[:,:,None],1);tiled_known=np.tile(known,(1,3));distance,nearest=distance_transform_edt(~tiled_known,sampling=(1/4.,1),return_indices=True);filled=np.tile(raw,(1,3,1))[nearest[0],nearest[1]];mean=np.stack([gaussian_filter(filled[:,:,c],(24.,6.),mode=('nearest','wrap'))[:,N:2*N] for c in range(3)],axis=2);confidence=np.exp(-distance[:,N:2*N]/128.);mean*=confidence[:,:,None]

old=np.asarray(Image.open(C/'textures/velvet_fold_color.png').convert('RGB'),float)/255;oldlin=np.where(old<=.04045,old/12.92,((old+.055)/1.055)**2.4);newlin=np.clip(oldlin*np.exp(mean),0,.85);newrgb=np.where(newlin<=.0031308,newlin*12.92,1.055*np.maximum(newlin,0)**(1/2.4)-.055);Image.fromarray(np.uint8(np.clip(newrgb,0,1)*255)).save(V/'proposed_cloth_appearance_fit.png')
# This is only a predicted color correction. Native validation is still required.
py,px=np.nonzero(display_mask);pu=atlas[py,px,0]%1;pv=np.clip(atlas[py,px,1],0,1);fitted=np.stack([map_coordinates(mean[:,:,c],[(1-pv)*(N-1),pu*(N-1)],order=1,mode='wrap') for c in range(3)],axis=1);pred=native.copy();pred[py,px]=agx(inverse(native[py,px])*np.exp(fitted));sheet=Image.new('RGB',(1560,620),(15,16,18));draw=ImageDraw.Draw(sheet)
for j,(a,title) in enumerate([(target,'Reference aligned to the existing rim'),(native,'Actual native capture'),(pred,'Predicted cloth correction, not a native capture')]):
 im=Image.fromarray(np.uint8(np.clip(a,0,1)*255)).crop((320,370,890,970));im.thumbnail((510,570));sheet.paste(im,(j*520,35));draw.text((j*520+5,10),title,fill='white')
sheet.save(V/'cloth_fit_prediction.png');report=dict(appearance_fit_only=True,physical_albedo_not_proven=True,gemstones_and_metal_excluded=True,no_emission_created=True,native_stage_pixel_center=[cx,cy],focal_pixels=A,fitted_native_pixels=len(x),appearance_ratio_percentiles=np.percentile(ratio,[5,50,95],axis=0).tolist(),texels_at_reflectance_ceiling=float(np.mean(newlin>=.85)),next='Inspect prediction. No model or installed texture has been modified. Actual native full turn review is required before adopting this cloth appearance fit.');(V/'diagnostic.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
