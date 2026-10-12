"""Independent packaged-file and Blender reimport validation."""
from pathlib import Path
import sys,json,zipfile,hashlib
import numpy as np
import bpy
from pxr import Usd,UsdGeom,UsdShade,UsdUtils
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/sys.argv[sys.argv.index('--')+1]
file=OUT/'copper_flame.usdz';stage=Usd.Stage.Open(str(file))
assert UsdGeom.GetStageUpAxis(stage)=='Y' and UsdGeom.GetStageMetersPerUnit(stage)==1
meshes=[];readers=[];assets=[];transforms=[]
for p in stage.Traverse():
    assert p.GetTypeName() not in ['Camera','SphereLight','DistantLight','RectLight','DomeLight','DiskLight','CylinderLight']
    assert p.GetName() not in ['Casing___smooth_rounded_outer_edge_mobile_geometry','Silver___circumferential_brushed_steel']
    if p.IsA(UsdGeom.Xformable):assert not UsdGeom.Xformable(p).GetOrderedXformOps()
    if p.IsA(UsdGeom.Mesh):
        m=UsdGeom.Mesh(p);norm=np.array(m.GetNormalsAttr().Get());pts=np.array(m.GetPointsAttr().Get());uv=UsdGeom.PrimvarsAPI(p).GetPrimvar('FlameUV')
        assert len(norm)==len(pts)==len(uv.Get());assert np.isfinite(norm).all()
        meshes.append({'name':p.GetName(),'vertices':len(pts),'triangles':len(m.GetFaceVertexCountsAttr().Get()),'uv':'FlameUV'})
    if p.IsA(UsdShade.Shader):
        shader=UsdShade.Shader(p);sid=shader.GetIdAttr().Get()
        if sid=='UsdPrimvarReader_float2':assert shader.GetInput('varname').Get()=='FlameUV'
        if shader.GetInput('file'):assets.append(shader.GetInput('file').Get().path)
checker=UsdUtils.ComplianceChecker(arkit=True);checker.CheckCompliance(str(file));assert not checker.GetErrors() and not checker.GetFailedChecks()
with zipfile.ZipFile(file) as z:
    textures=[]
    for path in assets:
        assert path in z.namelist()
        data=z.read(path);external=(OUT/'textures'/Path(path).name).read_bytes();assert data==external
        textures.append({'member':path,'sha256':hashlib.sha256(data).hexdigest()})
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.usd_import(filepath=str(file),import_materials=True,import_cameras=False,import_lights=False,import_textures_mode='IMPORT_PACK')
imported=[o for o in bpy.data.objects if o.type=='MESH'];assert len(imported)==3
tris=0
for o in imported:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
assert tris==40812
images=[{'name':im.name,'dimensions':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.name.startswith('copper_')]
assert len(images)==2 and all(i['packed'] and i['dimensions']==[1024,1024] for i in images)
report={'arkit_compliance':'PASS','meshes':meshes,'textures_match_package':textures,'reimport_triangles':tris,'reimport_images':images,'no_transforms_or_scene_items':True}
(OUT/'independent_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
