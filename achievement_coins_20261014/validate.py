"""Validate the exported coin contract and mirrored reliefs."""
from pathlib import Path
import json,hashlib,subprocess,zipfile
import sys
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Gf
sys.path.insert(0,str(Path(__file__).resolve().parent))
from pack import ROOT,SOURCE,shell_signature

source=Usd.Stage.Open(str(SOURCE));results=[]
for name in ['clean','hourglass_teal','hourglass_gold','sunrise','sprout']:
    path=ROOT/name/'mobile'/(name+'_badge_mobile.usdz')
    stage=Usd.Stage.Open(str(path))
    assert shell_signature(stage)==shell_signature(source)
    assert UsdGeom.GetStageUpAxis(stage)=='Y'
    assert UsdGeom.GetStageMetersPerUnit(stage)==1.
    all_points=[]
    for prim in stage.Traverse():
        assert prim.GetTypeName() not in ['Camera','DomeLight','SphereLight','RectLight','DiskLight','DistantLight']
        if prim.IsA(UsdGeom.Xformable):
            assert np.allclose(np.asarray(UsdGeom.Xformable(prim).ComputeLocalToWorldTransform(Usd.TimeCode.Default())),np.eye(4))
        if prim.IsA(UsdGeom.Mesh):
            mesh=UsdGeom.Mesh(prim);points=np.asarray(mesh.GetPointsAttr().Get())
            assert np.isfinite(points).all();all_points.append(points)
            indices=np.asarray(mesh.GetFaceVertexIndicesAttr().Get())
            assert indices.min()>=0 and indices.max()<len(points)
            normals=np.asarray(mesh.GetNormalsAttr().Get());assert np.isfinite(normals).all()
            for uv in UsdGeom.PrimvarsAPI(mesh).GetPrimvars():
                if 'UV' in uv.GetPrimvarName():assert np.isfinite(np.asarray(uv.Get())).all()
            if prim.GetName().startswith('ReliefFront_'):
                back=UsdGeom.Mesh(stage.GetPrimAtPath(str(prim.GetPath()).replace('ReliefFront_','ReliefBack_')))
                expected=points*[-1,1,-1]+[0,0,-.33]
                assert np.allclose(np.asarray(back.GetPointsAttr().Get()),expected,atol=1e-6)
        if prim.IsA(UsdShade.Shader):
            sh=UsdShade.Shader(prim)
            if sh.GetInput('file'):
                asset=sh.GetInput('file').Get();assert asset.resolvedPath,str(asset)
    points=np.concatenate(all_points)
    assert points[:,1].min()>=-2.895001 and points[:,1].max()<=3.015001
    assert points[:,0].min()>=-3.35 and points[:,0].max()<=3.35
    check=subprocess.run(['/usr/bin/usdchecker','--arkit',str(path)],capture_output=True,text=True)
    assert check.returncode==0,check.stdout+check.stderr
    result=json.loads((ROOT/name/'model.json').read_text())
    result.update({'usdchecker':'Success!','identity_transforms':True,'textures_resolve':True,
                   'matching_back':True,'bounds_min':points.min(0).tolist(),'bounds_max':points.max(0).tolist()})
    results.append(result)
    print(name+': USD/ARKit check passed; frozen shell and matching back verified.',flush=True)
(ROOT/'validation.json').write_text(json.dumps(results,indent=2))
