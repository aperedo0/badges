from pathlib import Path
import sys,numpy as np
from pxr import Usd,UsdGeom
sys.path.insert(0,'/Users/antonioperedo/Desktop/badges/all_sides_20261010/tools')
from model_common import read_mesh
root=Path(__file__).resolve().parents[1]
source='/Users/antonioperedo/Desktop/badges/gold_diamond_20261009/diamond/all_sides_20261010/candidates/04/usd/compacted.usdc'
stage=Usd.Stage.Open(source)
prim=next(p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh))
p,f,n,m,uv=read_mesh(prim)
np.savez(root/'source/round_geometry.npz',points=p,faces=f,normals=n,uv=uv['BadgeUV'])
print('Round positions, facets, normals and UVs exported.')
