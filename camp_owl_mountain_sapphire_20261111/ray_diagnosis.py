"""Read actual exported triangles at the dark native pixels."""
from pathlib import Path
import json,sys
import numpy as np
from pxr import Usd,UsdGeom,UsdShade
R=Path(__file__).resolve().parent;C=R/'campfire_night'/sys.argv[1]
stage=Usd.Stage.Open(str(C/'model.usdz'));eye=np.array([0,1.8,23.]);axis=np.array([0,-2.35,-23.]);axis/=np.linalg.norm(axis);up=np.cross([1,0,0],axis)
rows=[]
for pixel in [(593,531),(597,531),(595,541),(594,531)]:
 d=axis+(pixel[0]+.5-603)/1762.5*np.array([1,0,0])-(pixel[1]+.5-633.3)/1762.5*up;d/=np.linalg.norm(d);hits=[]
 for prim in stage.Traverse():
  if not prim.IsA(UsdGeom.Mesh):continue
  m=UsdGeom.Mesh(prim);v=np.array(m.GetPointsAttr().Get(),float);f=np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3);t=v[f];e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];p=np.cross(d,e2);det=np.sum(e1*p,1);ok=abs(det)>1e-12;inv=1/np.where(ok,det,1);q=eye-t[:,0];u=np.sum(q*p,1)*inv;b=np.cross(q,e1);w=b@d*inv;dist=np.sum(e2*b,1)*inv;ok&=(u>=0)&(w>=0)&(u+w<=1)&(dist>0)
  material={}
  for sub in UsdGeom.Subset.GetAllGeomSubsets(m):
   mat,_=UsdShade.MaterialBindingAPI(sub.GetPrim()).ComputeBoundMaterial()
   for i in sub.GetIndicesAttr().Get():material[i]=str(mat.GetPath())
  bound,_=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial();normals=np.asarray(m.GetNormalsAttr().Get(),float).reshape(-1,3,3)
  for i in np.flatnonzero(ok):
   bary=np.array([1-u[i]-w[i],u[i],w[i]]);n=bary@normals[i];hits.append(dict(mesh=str(prim.GetPath()),face=int(i),distance=float(dist[i]),material=material.get(int(i),str(bound.GetPath())),position=(eye+dist[i]*d).tolist(),normal=n.tolist(),normal_length=float(np.linalg.norm(n)),area=float(np.linalg.norm(np.cross(e1[i],e2[i]))/2),front_facing=bool(det[i]>0)))
 hits.sort(key=lambda p:p['distance']);rows.append(dict(pixel=pixel,hits=hits[:10]))
(C/'actual_ray_diagnosis.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
