"""Fit sculpted leaf boundaries to the actual ornament silhouette."""
from pathlib import Path
import ast,json,time
import numpy as np
from PIL import Image,ImageDraw
from scipy.optimize import minimize
from scipy.ndimage import gaussian_filter,binary_erosion
R=Path(__file__).resolve().parent;V=R/'emerald_crown/candidate14/review/outline_fit';V.mkdir(exist_ok=True)
tree=ast.parse((R/'refine_emerald14.py').read_text());outlines=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='outlines' for t in n.targets))
box=np.array([235,606,568,795]);target=np.asarray(Image.open(R/'emerald_crown/candidate13/review/acanthus_geometry_mask.png').convert('L'))>0;H,W=target.shape;blur=gaussian_filter(target.astype(float),1.2);s=np.linspace(0,1,75)[:,None]
def bez(p):
 a,b,c,d=np.array(p);return (1-s)**3*a+3*(1-s)**2*s*b+3*(1-s)*s*s*c+s**3*d
def controls(q):
 result=[]
 for j,(aa,bb,height,layer) in enumerate(outlines):
  aa=np.array(aa,float);bb=np.array(bb,float);mid=(aa+bb)/2;width,dx,dy=q[j*3:j*3+3];aa=mid+(aa-mid)*width;bb=mid+(bb-mid)*width;aa[1:3]+=[dx,dy];bb[1:3]+=[dx,dy];result.append((aa,bb,height,layer))
 return result
def mask(q):
 im=Image.new('L',(W,H));draw=ImageDraw.Draw(im)
 for aa,bb,_,_ in controls(q):
  p=np.vstack([bez(aa),bez(bb)[::-1]])-box[:2];draw.polygon([tuple(v) for v in p],fill=255)
 return np.asarray(im)>0
initial=np.tile([1.30,0,0],len(outlines));best=[np.inf,initial.copy()];start=time.time();calls=0
def loss(q):
 global calls
 if time.time()-start>150:raise TimeoutError()
 m=mask(q);smooth=gaussian_filter(m.astype(float),1.2);value=float(np.mean((smooth-blur)**2))+.000008*float(np.mean(q.reshape(-1,3)[:,1:]**2))
 if value<best[0]:best[:]=[value,q.copy()]
 calls+=1;return value
base=loss(initial)
try:minimize(loss,initial,method='Powell',bounds=[v for _ in outlines for v in [(.65,4.0),(-28,28),(-25,25)]],options=dict(maxiter=12,maxfev=10000,xtol=.02,ftol=.00005))
except TimeoutError:pass
q=best[1];items=[dict(a=aa.tolist(),b=bb.tolist(),height=h,layer=l) for aa,bb,h,l in controls(q)];(V/'fitted_controls.json').write_text(json.dumps(items,indent=2))
photo=Image.open(R/'emerald_crown/reference.png').convert('RGB').crop(tuple(box));sheet=Image.new('RGB',(W*3,H+28),(12,12,15));draw=ImageDraw.Draw(sheet)
for i,(title,m) in enumerate([('Reference geometry mask',target),('Current separate leaf outlines',mask(initial)),('Fitted separate leaf outlines',mask(q))]):
 a=np.asarray(photo).copy();edge=m&~binary_erosion(m,iterations=1);a[edge]=[70,255,100];sheet.paste(Image.fromarray(a),(i*W,28));draw.text((i*W+4,5),title,fill='white')
sheet.resize((W*3*2,(H+28)*2)).save(V/'outline_comparison.png')
iou=lambda m:float(np.sum(m&target)/np.sum(m|target));report=dict(status='geometry_diagnostic_only_not_native',no_material_or_appearance_fit=True,root_and_tip_positions_fixed=True,initial_loss=base,final_loss=best[0],before_silhouette_iou=iou(mask(initial)),after_silhouette_iou=iou(mask(q)),seconds=time.time()-start,calls=calls,parameters=q.tolist());(V/'fit_report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='parameters'}),flush=True)
