"""Fit one physical cloth pigment color from measured native panel colors."""
from pathlib import Path
import json,sys,numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import least_squares
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'silver2_metal_claude'));from agx import agx,agx_inv
C=R/'amethyst_crown/candidate09';ref=Image.open(C.parent/'reference.png').convert('RGB');native=Image.open(C/'review/front.png').convert('RGB')
def goldbox(image,is_native):
 a=np.asarray(image,float)/255;r,g,b=a.transpose(2,0,1);mask=(r>g*1.035)&(g>b*1.06)&(r>.16)
 if is_native:
  roi=np.zeros(mask.shape,bool);roi[250:840,300:906]=1;mask&=roi
 else:mask[int(image.height*.885):]=0
 y,x=np.nonzero(mask);return np.array([x.min(),y.min(),x.max(),y.max()],float)
rb=goldbox(ref,False);nb=goldbox(native,True);scale=(nb[2]-nb[0])/(rb[2]-rb[0]);rois=[(505,400,620,490),(916,400,1031,490),(310,470,355,555),(1181,470,1226,555)];rows=[]
def median(image,box):
 a=np.asarray(image.crop(tuple(int(x) for x in box)),float)/255;r,g,b=a.transpose(2,0,1);mask=(r>g*1.6)&(b>g*1.7)&(b>r*.70)&(r>.025)&(b>.035);assert mask.sum()>30,(box,mask.sum());return np.median(a[mask],axis=0)
def inverse(color):
 init=np.log(np.maximum(agx_inv(color[None,:])[0],1e-6));fit=least_squares(lambda x:agx(np.exp(x))[...]-color,init,bounds=(-16,6),max_nfev=200);return np.exp(fit.x)
for box in rois:
 nbox=nb[:2]+(np.array(box).reshape(2,2)-rb[:2])*scale;nbox=nbox.ravel();a=median(ref,box);b=median(native,nbox);rows.append(dict(reference_roi=box,native_roi=nbox.tolist(),reference_rgb=a.tolist(),native_rgb=b.tolist(),native_linear=inverse(b).tolist()))
obs=np.array([r['native_linear'] for r in rows]);target=np.array([r['reference_rgb'] for r in rows]);fit=least_squares(lambda log:((agx(obs*np.exp(log))-target)).ravel(),np.zeros(3),bounds=(np.log(.5),np.log(3)),max_nfev=200);gain=np.exp(fit.x);before=np.array([.034,.00065,.044]);after=before*gain;report=dict(method='One pigment color fitted under measured native panel illumination using the actual AgX LUT',gain=gain.tolist(),old_color=before.tolist(),new_color=after.tolist(),panels=rows,predicted_panel_rgb=agx(obs*gain).tolist(),native_review_pending=True,appearance_texture_baked=False);(R/'velvet_color_fit.json').write_text(json.dumps(report,indent=2));print('Measured pigment gain',gain,'new source color',after)
for image,kind in [(ref,'reference'),(native,'native')]:
 im=image.copy();d=ImageDraw.Draw(im)
 for row in rows:d.rectangle(tuple(row['reference_roi'] if kind=='reference' else row['native_roi']),outline=(80,220,150),width=3)
 im.save(C/'review'/('cloth_measurement_'+kind+'.png'))
