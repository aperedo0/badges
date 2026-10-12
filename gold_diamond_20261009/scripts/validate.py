"""Independent packaged USDZ, texture and fresh Blender reimport checks."""
from pathlib import Path
import sys,json,zipfile,hashlib
import numpy as np
import bpy
from pxr import Usd,UsdGeom,UsdShade,UsdUtils
ROOT=Path(__file__).resolve().parents[1]
kind,folder=sys.argv[sys.argv.index('--')+1:sys.argv.index('--')+3]
OUT=ROOT/kind/folder;file=OUT/'badge.usdz';stage=Usd.Stage.Open(str(file))
expected=json.loads((OUT/'build.json').read_text())
assert UsdGeom.GetStageUpAxis(stage)=='Y' and UsdGeom.GetStageMetersPerUnit(stage)==1
meshes=[];assets=[];allpts=[]
for p in stage.Traverse():
    assert 'Light' not in p.GetTypeName() and p.GetTypeName()!='Camera'
    assert p.GetName() not in ['Casing___smooth_rounded_outer_edge_mobile_geometry','Silver___circumferential_brushed_steel']
    if p.IsA(UsdGeom.Xformable):assert not UsdGeom.Xformable(p).GetOrderedXformOps()
    if p.IsA(UsdGeom.Mesh):
        m=UsdGeom.Mesh(p);pts=np.array(m.GetPointsAttr().Get());counts=np.array(m.GetFaceVertexCountsAttr().Get());indices=np.array(m.GetFaceVertexIndicesAttr().Get());norm=np.array(m.GetNormalsAttr().Get());uv=UsdGeom.PrimvarsAPI(p).GetPrimvar('BadgeUV')
        assert np.all(counts==3) and len(norm)==len(indices)==len(uv.Get())
        assert np.isfinite(norm).all() and np.allclose(np.linalg.norm(norm,axis=1),1,atol=1e-5)
        assert m.GetNormalsInterpolation()=='faceVarying' and uv.GetInterpolation()=='faceVarying'
        f=indices.reshape(-1,3);e=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,c=np.unique(e,axis=0,return_counts=True);assert np.all(c==2)
        assert np.all(np.linalg.norm(np.cross(pts[f[:,1]]-pts[f[:,0]],pts[f[:,2]]-pts[f[:,0]]),axis=1)>1e-12)
        allpts.append(pts);meshes.append({'name':p.GetName(),'vertices':len(pts),'triangles':len(f),'uv':'BadgeUV','closed':True})
    if p.IsA(UsdShade.Shader):
        sh=UsdShade.Shader(p);sid=sh.GetIdAttr().Get()
        assert sid in ['UsdPreviewSurface','UsdUVTexture','UsdPrimvarReader_float2']
        if sid=='UsdPrimvarReader_float2':assert sh.GetInput('varname').Get()=='BadgeUV'
        if sh.GetInput('file'):assets.append(sh.GetInput('file').Get().path)
points=np.concatenate(allpts);lo=points.min(0);hi=points.max(0)
assert lo[1]>=-2.895 and hi[1]<=3.015 and max(abs(lo[0]),abs(hi[0]))<=3.35
assert abs(lo[1]+2.455)<1e-6 and abs(lo[0]+hi[0])<.01 and abs(lo[2]+hi[2])<1e-5
checker=UsdUtils.ComplianceChecker(arkit=True);checker.CheckCompliance(str(file));assert not checker.GetErrors() and not checker.GetFailedChecks()
with zipfile.ZipFile(file) as z:
    textures=[]
    for path in assets:
        assert path in z.namelist();data=z.read(path);assert data==(OUT/'textures'/Path(path).name).read_bytes()
        textures.append({'member':path,'sha256':hashlib.sha256(data).hexdigest()})
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.usd_import(filepath=str(file),import_materials=True,import_cameras=False,import_lights=False,import_textures_mode='IMPORT_PACK')
imported=[o for o in bpy.data.objects if o.type=='MESH'];assert len(imported)==len(meshes)
tris=0
for o in imported:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
assert tris==expected['triangles']
images=[{'name':im.name,'dimensions':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.packed_file]
assert len(images)==2 and all(i['dimensions']==[1024,1024] for i in images)
master=OUT/f'{kind}_badge_master.blend';bpy.ops.wm.open_mainfile(filepath=str(master))
assert len([o for o in bpy.data.objects if o.type=='MESH'])==len(meshes)
assert len([im for im in bpy.data.images if im.packed_file and list(im.size)==[1024,1024]])==2
report={'arkit_compliance':'PASS','meshes':meshes,'textures_match_package':textures,'reimport_triangles':tris,'reimport_images':images,'editable_master_packed_textures':True,'no_transforms_or_scene_items':True,'bounds':[lo.tolist(),hi.tolist()]}
(OUT/'independent_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
