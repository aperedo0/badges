from pathlib import Path
import sys,json,subprocess
import numpy as np
from pxr import Usd,UsdGeom,UsdShade
ROOT=Path(__file__).resolve().parent
source=ROOT.parent/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/GemFacetPlanes.swift'
runner=Path('/tmp/aurora_runtime_planes.swift');runner.write_text(source.read_text()+'''
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let fixtures = try JSONDecoder().decode([String: [[Float]]].self, from: Data(contentsOf: url))
var result: [String: [String: Int]] = [:]
for (name, vertices) in fixtures {
    let corners = vertices.map { SIMD3<Float>($0[0], $0[1], $0[2]) }
    guard let planes = GemFacetPlanes.outwardPlanes(ofTriangles: corners) else { fatalError("Rejected exported gem: \\(name)") }
    let mirrored = corners.map { SIMD3<Float>($0.x, -$0.y, $0.z) }
    guard let reflection = GemFacetPlanes.outwardPlanes(ofTriangles: mirrored) else { fatalError("Rejected reflection: \\(name)") }
    var maxError: Float = 0
    for p in planes {
        let hi = SIMD4<Float>(Float(Float16(p.x)), Float(Float16(p.y)), Float(Float16(p.z)), Float(Float16(p.w)))
        let residual = (p - hi) * 1024
        let lo = SIMD4<Float>(Float(Float16(residual.x)), Float(Float16(residual.y)), Float(Float16(residual.z)), Float(Float16(residual.w)))
        let difference = p - (hi + lo / 1024)
        maxError = max(maxError, abs(difference.x), abs(difference.y), abs(difference.z), abs(difference.w))
    }
    precondition(maxError < 0.00001, "Plane upload loses tip precision")
    result[name] = ["planes": planes.count, "reflectionPlanes": reflection.count, "maximumCoefficientErrorInNanounits": Int(maxError * 1_000_000_000)]
}
let bytes = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(bytes)
''')
key=sys.argv[1];R=ROOT/key;C=R/'candidate10'
model=Path(sys.argv[2]) if len(sys.argv)>2 else C/'mobile'/(key+'_badge_mobile.usdz');stage=Usd.Stage.Open(str(model));fixtures={}
for prim in stage.Traverse():
 if not prim.IsA(UsdGeom.Mesh):continue
 mat=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
 if not mat.GetPrim().GetName().startswith('CrestGem_'):continue
 assert not any(child.GetTypeName()=='Shader' and UsdShade.Shader(child).GetIdAttr().Get()=='UsdUVTexture' for child in Usd.PrimRange(mat.GetPrim()))
 shader=UsdShade.Shader(mat.GetPrim().GetChild('Surface'))
 for inp in shader.GetInputs():assert not inp.HasConnectedSource()
 mesh=UsdGeom.Mesh(prim);points=np.asarray(mesh.GetPointsAttr().Get());tri=np.asarray(mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1,3)
 fixtures[str(prim.GetPath())]=points[tri].reshape(-1,3).tolist()
assert len(fixtures)==sum(1 for g in json.loads((C/'groups.json').read_text()) if g['mat'].startswith('CrestGem_'))
if not fixtures:
 (C/('runtime_gem_validation_compact.json' if len(sys.argv)>2 else 'runtime_gem_validation.json')).write_text(json.dumps(dict(gem_count=0,no_gems=True)))
 sys.exit(0)
path=C/'runtime_gem_vertices.json';path.write_text(json.dumps(fixtures))
result=subprocess.run(['/usr/bin/swift','-module-cache-path','/tmp/aurora_swift_modules',str(runner),str(path)],capture_output=True,text=True,check=True)
report=json.loads(result.stdout)
(C/('runtime_gem_validation_compact.json' if len(sys.argv)>2 else 'runtime_gem_validation.json')).write_text(json.dumps(dict(gems=report,no_appearance_textures=True,actual_renderer_convexity_passed=True,reflection_convexity_passed=True),indent=2)+'\n')
print(key,len(fixtures),'stones pass actual renderer convexity and plane precision checks.')
