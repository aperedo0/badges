"""Apply the app's actual Swift convexity and plane packing checks to both exported rubies."""
import json, subprocess, tempfile, sys
from pathlib import Path
from pxr import Usd,UsdGeom,UsdShade
import numpy as np
root=Path(__file__).resolve().parents[1]
repo=root.parent
harness=(repo/'stair_ruby_20261029/check_runtime_gems.py').read_text()
# Share the native validator and its existing reflection/half precision test verbatim.
body=harness.split("source.read_text()+'''",1)[1].split("'''",1)[0]
body=body.replace(chr(92)*2,chr(92))
native=repo/'emerald_trophy_20261025/preview/ScreenTime/Sources/App/Features/Badges/GemFacetPlanes.swift'
scene=Usd.Stage.Open(str(root/'mobile/ruby_hourglass.usdz'))
fixtures={}
for prim in scene.Traverse():
    if not prim.IsA(UsdGeom.Mesh):continue
    mat=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
    if mat.GetPrim().GetName()!='CrestGem_Ruby':continue
    mesh=UsdGeom.Mesh(prim)
    p=np.asarray(mesh.GetPointsAttr().Get())
    indices=np.asarray(mesh.GetFaceVertexIndicesAttr().Get())
    fixtures[prim.GetName()]=p[indices].tolist()
assert len(fixtures)==2
with tempfile.TemporaryDirectory() as folder:
    folder=Path(folder);runner=folder/'check.swift';runner.write_text(native.read_text()+body)
    verts=folder/'fixtures.json';verts.write_text(json.dumps(fixtures))
    proc=subprocess.run(['/usr/bin/swift','-module-cache-path','/private/tmp/rubyhourglass_swift',str(runner),str(verts)],text=True,capture_output=True)
    if proc.returncode:raise RuntimeError(proc.stderr)
    result=json.loads(proc.stdout)
    (root/(sys.argv[1] if len(sys.argv)>1 else json.loads((root/'design.json').read_text())['candidate'])/'runtime_gems.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result)
