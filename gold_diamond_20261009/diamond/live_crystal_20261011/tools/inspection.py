from pathlib import Path
import sys, shutil, zipfile
import numpy as np
from pxr import Usd, UsdGeom, Sdf
sys.path.insert(0, '/Users/antonioperedo/Desktop/badges/all_sides_20261010/tools')
from model_common import read_mesh, write_mesh, finish
ROOT=Path(__file__).resolve().parents[1]
number=sys.argv[sys.argv.index('--')+1]
source=ROOT/'candidates'/number
unpacked=source/'independent_package'
unpacked.mkdir(exist_ok=True)
with zipfile.ZipFile(source/'diamond_badge_mobile.usdz') as package:
    package.extractall(unpacked)
original=Usd.Stage.Open(str(unpacked/'diamond.usdc'))
for pose,degrees in [('right',-90),('back',180),('left',90)]:
    out=ROOT/'inspection'/number/pose
    out.mkdir(parents=True,exist_ok=True)
    layer=Sdf.Layer.CreateNew(str(out/'diamond.usdc'))
    layer.TransferContent(original.GetRootLayer())
    stage=Usd.Stage.Open(layer)
    for prim in stage.Traverse():
        for a in prim.GetAttributes():
            if a.GetTypeName()==Sdf.ValueTypeNames.Asset:
                value=a.Get()
                if value and value.path:
                    file=unpacked/value.path
                    assert file.exists(),file
                    shutil.copyfile(file,out/file.name)
                    a.Set(Sdf.AssetPath(file.name))
    angle=np.deg2rad(degrees)
    rot=np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]])
    for prim in [q for q in stage.Traverse() if q.IsA(UsdGeom.Mesh)]:
        p,f,n,m,uv=read_mesh(prim)
        write_mesh(stage,prim.GetPath(),p@rot.T,f,n@rot.T,m,uv)
    finish('diamond',ROOT,out,stage,[{'inspection_only':True,'angle_degrees':degrees,'candidate':number,'purpose':'Full-size pose in app for four-times edge inspection. Actual continuous scroll is checked independently.'}])
