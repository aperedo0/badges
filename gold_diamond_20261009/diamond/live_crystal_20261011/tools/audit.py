from pathlib import Path
import sys, json, zipfile
import numpy as np
from pxr import Usd, UsdGeom, UsdShade, UsdUtils, Sdf
sys.path.insert(0,'/Users/antonioperedo/Desktop/badges/all_sides_20261010/tools')
from model_common import read_mesh
ROOT=Path(__file__).resolve().parents[1]
number=sys.argv[sys.argv.index('--')+1]
candidate=ROOT/'candidates'/number
for label,file in [('prior',ROOT/'source/proposed.usdz'),('new',candidate/'diamond_badge_mobile.usdz')]:
    destination=candidate/'audit'/label
    destination.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(file) as z:
        names=z.namelist()
        z.extractall(destination)
    stage=Usd.Stage.Open(str(destination/names[0]))
    meshes=[p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)]
    assert len(meshes)==1
    arrays=read_mesh(meshes[0])
    if label=='prior':old=arrays;continue
    p,f,n,m,uv=arrays
    assert np.array_equal(p,old[0]) and np.array_equal(f,old[1]) and np.array_equal(n,old[2])
    assert all(np.array_equal(v,old[4][k]) for k,v in uv.items())
    assert UsdGeom.GetStageUpAxis(stage)=='Y' and UsdGeom.GetStageMetersPerUnit(stage)==1
    edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1)
    _,count=np.unique(edges,axis=0,return_counts=True)
    assert np.all(count==2)
    assert np.max(np.abs(n-n[:,0:1]))<1e-6
    textures=[]
    for prim in stage.Traverse():
        assert 'Light' not in prim.GetTypeName() and prim.GetTypeName()!='Camera'
        if prim.IsA(UsdGeom.Xformable):assert not UsdGeom.Xformable(prim).GetOrderedXformOps()
        for a in prim.GetAttributes():
            if a.GetTypeName()==Sdf.ValueTypeNames.Asset:
                asset=a.Get()
                if asset and asset.path:
                    assert (destination/asset.path).exists(),asset.path
                    textures.append(asset.path)
    surfaces=[UsdShade.Shader(q) for q in stage.Traverse() if q.IsA(UsdShade.Shader) and UsdShade.Shader(q).GetIdAttr().Get()=='UsdPreviewSurface']
    assert len(surfaces)==1
    surface=surfaces[0]
    assert surface.GetInput('diffuseColor').HasConnectedSource()
    assert not surface.GetInput('emissiveColor').HasConnectedSource()
    uniform_em=list(surface.GetInput('emissiveColor').Get())
    assert max(uniform_em)<.04
    reader=[UsdShade.Shader(q).GetInput('varname').Get() for q in stage.Traverse() if q.IsA(UsdShade.Shader) and UsdShade.Shader(q).GetIdAttr().Get()=='UsdPrimvarReader_float2']
    assert reader==['BadgeUV'] and 'BadgeUV' in uv
    radius=np.linalg.norm(p[:,[0,2]],axis=1).max()
    assert radius*2<=6.7 and p[:,1].max()<=3.015 and p[:,1].min()>=-2.895
    checker=UsdUtils.ComplianceChecker(arkit=True)
    checker.CheckCompliance(str(file))
    assert not checker.GetErrors() and not checker.GetFailedChecks()
    report={'geometry_unchanged':True,'normals_unchanged':True,'uv_unchanged':True,'closed_mesh':True,'triangles':len(f),'vertices':len(p),'flat_facet_normals':True,'no_transforms_or_lights':True,'bounds':[p.min(0).tolist(),p.max(0).tolist()],'maximum_spin_width':float(2*radius),'textures_resolve_after_independent_unpack':textures,'color_uv':reader,'emission_is_uniform_only':uniform_em,'metallic':float(surface.GetInput('metallic').Get()),'roughness':float(surface.GetInput('roughness').Get()),'clearcoat':float(surface.GetInput('clearcoat').Get()),'ior':float(surface.GetInput('ior').Get()),'opacity':float(surface.GetInput('opacity').Get()),'arkit_errors':checker.GetErrors(),'arkit_failed_checks':checker.GetFailedChecks()}
    (candidate/'package_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
