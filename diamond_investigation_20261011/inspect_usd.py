from pathlib import Path
import json,sys,numpy as np
from pxr import Usd,UsdGeom,UsdShade
root=Path('/Users/antonioperedo/Desktop/badges/diamond_investigation_20261011')
result={}
for label in ['installed','proposed']:
 stage=Usd.Stage.Open(str(next((root/label/'unpacked').glob('*.usd*'))))
 shaders=[]; meshes=[];allp=[]
 for prim in stage.Traverse():
  if prim.IsA(UsdShade.Shader):
   sh=UsdShade.Shader(prim);inputs={}
   for i in sh.GetInputs():
    val=i.Get();connections=[str(v) for v in i.GetAttr().GetConnections()]
    inputs[i.GetBaseName()]={'value':str(val),'connected':connections}
   shaders.append({'path':str(prim.GetPath()),'id':str(sh.GetIdAttr().Get()),'inputs':inputs})
  if prim.IsA(UsdGeom.Mesh):
   m=UsdGeom.Mesh(prim);p=np.array(m.GetPointsAttr().Get(),float);f=np.array(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3);n=np.array(m.GetNormalsAttr().Get(),float)
   gn=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]]);area=np.linalg.norm(gn,axis=1)/2;gn/=np.maximum(area[:,None]*2,1e-12)
   ni=m.GetNormalsInterpolation();nn=n[f] if ni=='vertex' else n.reshape(-1,3,3)
   angles=np.degrees(np.arccos(np.clip(np.einsum('ij,ikj->ik',gn,nn),-1,1)))
   mats=[str(v) for v in UsdShade.MaterialBindingAPI(prim).GetDirectBindingRel().GetTargets()]
   subsets=[]
   for s in UsdGeom.Subset.GetAllGeomSubsets(m):
    ix=np.array(s.GetIndicesAttr().Get(),int)
    subsets.append({'path':str(s.GetPath()),'faces':len(ix),'area':float(area[ix].sum()),'bindings':[str(v) for v in UsdShade.MaterialBindingAPI(s.GetPrim()).GetDirectBindingRel().GetTargets()]})
   meshes.append({'path':str(prim.GetPath()),'vertices':len(p),'triangles':len(f),'bounds':[p.min(0).tolist(),p.max(0).tolist()],'normal_interpolation':str(ni),'max_normal_geometry_angle_degrees':float(angles.max()),'normal_angles_percentiles':np.percentile(angles,[0,50,95,100]).tolist(),'bindings':mats,'subsets':subsets})
   allp.append(p)
   np.savez(root/label/'geometry.npz',points=p,faces=f,normals=nn)
 p=np.concatenate(allp)
 result[label]={'bounds':[p.min(0).tolist(),p.max(0).tolist()],'dimensions':np.ptp(p,axis=0).tolist(),'meshes':meshes,'shaders':shaders}
 stage.GetRootLayer().Export(str(root/label/'inspection.usda'))
(root/'material_geometry_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
