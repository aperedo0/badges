"""Create independently closed convex gemstone cuts without image textures."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.spatial import ConvexHull
from scipy.ndimage import binary_dilation

def prepare(root,C):
 cfg=json.loads((root/'design.json').read_text())
 if not cfg.get('dynamic_gems'):return
 trace=json.loads((C/'trace.json').read_text());W,H=trace['reference_size'];scale=trace['reference_scale'];cx=trace['reference_center'][0];lo=trace['reference_bounds'][0]
 with np.load(C/'geometry.npz') as f:D={k:f[k] for k in f.files if not k.startswith('explicit_star_') and not k.startswith('dynamic_gem_')}
 specs=[]
 for i,g in enumerate(cfg['gems']):
  outline=np.array(g['outline'],float);center=np.array(g['center'],float);seat=g['seat'];crest=g['crest'];rise=crest-seat
  ring=center+(outline-center)*g.get('table_fraction',.62)
  xy=np.vstack([outline,ring,center]);z=np.r_[[seat]*len(outline),[seat+rise*.76]*len(ring),crest]
  if g.get('front_ridge'):
   ridge=np.array(g['front_ridge'],float);xy=np.vstack([outline,ridge[:,:2]]);z=np.r_[[seat]*len(outline),ridge[:,2]]
  p=np.c_[(xy[:,0]-cx)*scale,3.015-(xy[:,1]-lo[1])*scale,z]
  points=np.vstack([p,p*np.array([1,1,-1])]);hull=ConvexHull(points);t=hull.simplices.copy()
  normals=np.cross(points[t[:,1]]-points[t[:,0]],points[t[:,2]]-points[t[:,0]])
  swap=(normals*hull.equations[:,:3]).sum(1)<0;t[swap]=t[swap,::-1]
  ids=np.unique(t);remap=np.full(len(points),-1);remap[ids]=np.arange(len(ids));points=points[ids];t=remap[t]
  uv=np.c_[np.tile(xy[:,0]/W,2),np.tile(1-xy[:,1]/H,2)][ids]
  # Runtime plane extraction must see this whole closed stone in one mesh.
  planes=np.unique(np.round(hull.equations,5),axis=0)
  assert len(planes)<=256 and len(planes)>=4
  assert np.max(points@hull.equations[:,:3].T+hull.equations[:,3])<1e-7
  e=np.vstack([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);_,counts=np.unique(np.sort(e,axis=1),axis=0,return_counts=True);assert (counts==2).all()
  D[f'dynamic_gem_{i}_points']=points;D[f'dynamic_gem_{i}_triangles']=t;D[f'dynamic_gem_{i}_uv']=uv
  specs.append({'name':g['name'],'role':'CrestGem_'+g.get('style',cfg.get('gem_style','Ice')),'convex':True,'closed':True,'planes':len(planes),'triangles':len(t),'appearance_textures':False})
 D['dynamic_gem_count']=np.array(len(specs));np.savez_compressed(C/'geometry.npz',**D)
 (C/'dynamic_gems.json').write_text(json.dumps(specs,indent=2)+'\n')
 # Remove the old optical image from hidden supports, preserving metal settings.
 gem=Image.new('L',(W,H));draw=ImageDraw.Draw(gem)
 for g in cfg['gems']:draw.polygon([tuple(p) for p in g['outline']],fill=255)
 for outline in cfg.get('support_erase',[]):draw.polygon([tuple(p) for p in outline],fill=255)
 mask=np.asarray(gem)>0;bezel=D['detail_bezel_mask'];mask &= ~bezel
 for suffix in ['color','emission']:
  path=C/'textures'/('surface_'+suffix+'.png');im=np.asarray(Image.open(path).convert('RGB')).copy();m=np.asarray(Image.fromarray(np.uint8(mask)*255).resize((im.shape[1],im.shape[0]),Image.Resampling.NEAREST))>0
  im[m]=[9,16,22] if suffix=='color' else [0,0,0];Image.fromarray(im).save(path)
 print('Prepared',len(specs),'closed runtime gemstones')
if __name__=='__main__':
 import sys
 ROOT=Path(__file__).resolve().parent;R=ROOT/sys.argv[1];prepare(R,R/(R/'candidate.txt').read_text().strip())
