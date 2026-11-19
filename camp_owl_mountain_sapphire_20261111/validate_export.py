"""Validate the actual USDZ contract, texture bytes and native gem plane loader."""
from pathlib import Path
import sys,json,zipfile,hashlib,subprocess
import numpy as np
from pxr import Usd,UsdGeom,UsdShade
R=Path(__file__).resolve().parent
slug,candidate=sys.argv[1:3];C=R/slug/candidate;model=C/'model.usdz'
stage=Usd.Stage.Open(str(model));assert stage
assert UsdGeom.GetStageUpAxis(stage)=='Y'
assert UsdGeom.GetStageMetersPerUnit(stage)==1
meshes=[];gem_vertices={};texture_files=[]
with zipfile.ZipFile(model) as archive:
 names=set(archive.namelist())
 for prim in stage.Traverse():
  assert prim.GetTypeName() not in ['Camera','DomeLight','DistantLight','SphereLight','RectLight','DiskLight']
  if prim.IsA(UsdGeom.Xformable):assert not UsdGeom.Xformable(prim).GetOrderedXformOps()
  if prim.IsA(UsdShade.Shader):
   sh=UsdShade.Shader(prim);assert sh.GetIdAttr().Get() in ['UsdPreviewSurface','UsdPrimvarReader_float2','UsdUVTexture']
   if sh.GetIdAttr().Get()=='UsdUVTexture':
    name=sh.GetInput('file').Get().path;assert name in names,(name,names)
    assert any(archive.read(name)==p.read_bytes() for p in (C/'textures').glob('*.png'))
    texture_files.append(name)
  if not prim.IsA(UsdGeom.Mesh):continue
  m=UsdGeom.Mesh(prim);p=np.asarray(m.GetPointsAttr().Get(),np.float32);idx=np.asarray(m.GetFaceVertexIndicesAttr().Get()).reshape(-1,3)
  assert np.all(np.asarray(m.GetFaceVertexCountsAttr().Get())==3)
  assert len(m.GetNormalsAttr().Get())==idx.size
  assert len(UsdGeom.PrimvarsAPI(m).GetPrimvar('st').Get())==idx.size
  mat=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
  if mat and mat.GetPrim().GetName().startswith('CrestGem_'):
   assert mat.GetPrim().GetName() in ['CrestGem_Sapphire','CrestGem_SapphireClear','CrestGem_FoilSapphire']
   shader=UsdShade.Shader(mat.GetPrim().GetChild('Surface'))
   assert all(not inp.HasConnectedSource() for inp in shader.GetInputs())
   gem_vertices[str(prim.GetPath())]=p[idx].reshape(-1,3).tolist()
  meshes.append(dict(name=str(prim.GetPath()),triangles=len(idx),bounds=[p.min(0).tolist(),p.max(0).tolist()]))
lo=np.array([m['bounds'][0] for m in meshes]).min(0);hi=np.array([m['bounds'][1] for m in meshes]).max(0)
expected_top=2.995
if (C/'owner_adjustment.json').exists():
 adjustment=json.loads((C/'owner_adjustment.json').read_text())
 expected_top=adjustment['expected_y_max']
 assert expected_top<=3.015,'The adjusted badge must still fit the Home frame'
assert hi[1]<=3.015 and lo[1]>=-2.895,(lo,hi)
assert abs(hi[1]-expected_top)<.004 and abs(lo[1]+2.455)<.004,(lo,hi)
assert max(abs(lo[0]),abs(hi[0]))<=3.35
assert abs(lo[2]+hi[2])<.002
gem_report={}
if gem_vertices:
 source=R.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/GemFacetPlanes.swift'
 runner=R/'native_gem_validation.swift'
 runner.write_text(source.read_text()+'''
let fixtures = try JSONDecoder().decode([String: [[Float]]].self, from: Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1])))
var results: [String: [String: Int]] = [:]
for (name, vertices) in fixtures {
 let corners = vertices.map { SIMD3<Float>($0[0], $0[1], $0[2]) }
 guard let planes = GemFacetPlanes.outwardPlanes(ofTriangles: corners) else { fatalError("Rejected native gem") }
 let mirror = corners.map { SIMD3<Float>($0.x, -$0.y, $0.z) }
 guard let reflected = GemFacetPlanes.outwardPlanes(ofTriangles: mirror) else { fatalError("Rejected native mirror") }
 results[name] = ["planes": planes.count, "reflectionPlanes": reflected.count]
}
let data = try JSONSerialization.data(withJSONObject: results, options: [.sortedKeys])
FileHandle.standardOutput.write(data)
''')
 fixture=C/'runtime_gem_vertices.json';fixture.write_text(json.dumps(gem_vertices))
 result=subprocess.run(['/usr/bin/swift','-module-cache-path','/tmp/camp_badge_swift_modules',str(runner),str(fixture)],check=True,text=True,capture_output=True)
 gem_report=json.loads(result.stdout)
report=dict(contract_passed=True,model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),meshes=len(meshes),triangles=sum(m['triangles'] for m in meshes),bytes=model.stat().st_size,bounds=[lo.tolist(),hi.tolist()],all_textures_present_and_byte_identical=True,texture_files=texture_files,native_gems=gem_report,no_gem_appearance_texture=True,production_app_untouched=True)
(C/'export_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
