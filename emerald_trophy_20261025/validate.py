"""Check the app contract and exact preservation of the approved gold shell."""
from pathlib import Path
import json,zipfile,hashlib,sys
from collections import Counter
import numpy as np
from pxr import Usd,UsdGeom,UsdShade,Sdf
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'botanical_match_20261014/sprout/mobile/sprout_badge_mobile.usdz'
NAME=next((a for a in sys.argv[1:] if a.startswith('candidate')),'candidate01')
MODEL=ROOT/NAME/'mobile/emerald_trophy_badge_mobile.usdz'
a=Usd.Stage.Open(str(SOURCE));b=Usd.Stage.Open(str(MODEL))
SHELL='/Badge/Casing___smooth_rounded_outer_edge/Casing___smooth_rounded_outer_edge_mobile_geometry'
def attributes(prim):
    return {str(p.GetPath()):{x.GetName():((x.Get().path if isinstance(x.Get(),Sdf.AssetPath) else repr(x.Get())),[str(c) for c in x.GetConnections()]) for x in p.GetAttributes()} for p in Usd.PrimRange(prim)}
assert attributes(a.GetPrimAtPath(SHELL))==attributes(b.GetPrimAtPath(SHELL))
for material in ['Silver___circumferential_brushed_steel_Mobile_Casing','Shell_inner','Shell_bevel']:
    p='/Badge/_materials/'+material
    expected=attributes(a.GetPrimAtPath(p));actual=attributes(b.GetPrimAtPath(p))
    if NAME in ['candidate06','candidate07']:
        # The owner explicitly requested this trophy's rim finish change.
        for values in [expected,actual]:values[p+'/Surface'].pop('inputs:diffuseColor',None)
    assert expected==actual
with zipfile.ZipFile(SOURCE) as za,zipfile.ZipFile(MODEL) as zb:
    for p in b.Traverse():
        if p.IsA(UsdShade.Shader) and 'New_' not in str(p.GetPath()):
            f=UsdShade.Shader(p).GetInput('file')
            if f:
                allowed=NAME in ['candidate06','candidate07'] and f.Get().path in ['textures/Rim_brushed_reference_color.png','textures/Rim_brushed_reference_roughness.png']
                if not allowed:assert za.read(f.Get().path)==zb.read(f.Get().path)
assert UsdGeom.GetStageUpAxis(b)=='Y' and UsdGeom.GetStageMetersPerUnit(b)==1
positions=[];degenerate=0;zero_normals=0;triangles=0
for prim in b.Traverse():
    assert prim.GetTypeName() not in ['Camera','DomeLight','DistantLight','SphereLight','RectLight']
    if prim.HasAttribute('xformOpOrder'):assert not prim.GetAttribute('xformOpOrder').Get()
    if not prim.IsA(UsdGeom.Mesh):continue
    m=UsdGeom.Mesh(prim);v=np.asarray(m.GetPointsAttr().Get());positions.append(v)
    assert np.isfinite(v).all()
    counts=np.asarray(m.GetFaceVertexCountsAttr().Get());assert (counts==3).all()
    t=np.asarray(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3);triangles+=len(t)
    q=v[t];degenerate+=int((np.linalg.norm(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]),axis=1)<1e-12).sum())
    n=np.asarray(m.GetNormalsAttr().Get());assert np.isfinite(n).all()
    zero_normals+=int((np.linalg.norm(n,axis=-1)<.01).sum())
    if str(prim.GetPath())==SHELL:
        _,w=np.unique(np.round(v/1e-5).astype(np.int64),axis=0,return_inverse=True)
        edges=Counter(tuple(sorted(e)) for f in w[t] for e in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])])
        assert all(c==2 for c in edges.values())
    if prim.GetName().startswith('Front_'):
        back=UsdGeom.Mesh(b.GetPrimAtPath('/Badge/'+prim.GetName().replace('Front_','Back_',1)))
        bv=np.asarray(back.GetPointsAttr().Get());assert np.allclose(bv,v*[-1,1,-1]+[0,0,-.33],atol=1e-6)
        assert np.allclose(np.asarray(back.GetNormalsAttr().Get()),n*[-1,1,-1],atol=1e-6)
# A recessed field must cover the full disk, including every annular sector.
field=b.GetPrimAtPath('/Badge/Front_field')
if field:
    fm=UsdGeom.Mesh(field);fv=np.asarray(fm.GetPointsAttr().Get());ft=np.asarray(fm.GetFaceVertexIndicesAttr().Get()).reshape(-1,3)
    fq=fv[ft];area=float(np.linalg.norm(np.cross(fq[:,1]-fq[:,0],fq[:,2]-fq[:,0]),axis=1).sum()/2)
    radius=float(np.linalg.norm(fv[:,:2],axis=1).max())
    assert area/(np.pi*radius*radius)>.995,('incomplete recessed field',area,radius)
v=np.concatenate(positions);assert abs(v[:,1].max()-3.015)<1e-5 and abs(v[:,1].min()+3.015)<1e-5
assert abs(v[:,0].min()+3.015)<1e-5 and abs(v[:,0].max()-3.015)<1e-5
assert degenerate==0 and zero_normals==0,(degenerate,zero_normals)
result={'shell_geometry_materials_and_maps':('geometry preserved; owner requested matching rim finish' if NAME in ['candidate06','candidate07'] else 'exactly preserved'),'round_shell_closed':True,
 'Y_up_meters':True,'identity_transforms':True,'no_lights_or_cameras':True,
 'matching_sculpted_back':True,'degenerate_triangles':degenerate,'zero_normals':zero_normals,
 'triangles':triangles,'bytes':MODEL.stat().st_size,'bounds':[v.min(0).tolist(),v.max(0).tolist()],
 'required_preview_size':.96,'required_preview_lift':.56,'lowest_world_y':-2.455,
 'sha256':hashlib.sha256(MODEL.read_bytes()).hexdigest()}
(ROOT/NAME/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
