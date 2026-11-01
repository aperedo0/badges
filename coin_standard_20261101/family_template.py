"""Save the approved bare casing and inset as the new reusable template."""
from pathlib import Path
import json, tempfile, zipfile, subprocess, shutil
import numpy as np
from pxr import Usd, UsdGeom, UsdShade
R=Path(__file__).resolve().parent;F=R/'family';T=F/'template';T.mkdir(exist_ok=True)
source=R/'candidate03/mobile/emerald_sprout_badge_mobile.usdz'
with tempfile.TemporaryDirectory(prefix='approved_coin_template_',dir='/tmp') as tmp:
    pkg=Path(tmp)
    with zipfile.ZipFile(source) as archive:
        archive.extractall(pkg);names=archive.namelist()
    usd=next(n for n in names if n.endswith(('.usd','.usda','.usdc')))
    stage=Usd.Stage.Open(str(pkg/usd))
    remove=[p.GetPath() for p in stage.Traverse() if p.IsA(UsdGeom.Mesh) and not ('Casing___' in p.GetName() or 'Inset___' in p.GetName())]
    for path in remove:stage.RemovePrim(path)
    used=set()
    for p in stage.Traverse():
        if p.IsA(UsdGeom.Mesh) or p.IsA(UsdGeom.Subset):
            m,_=UsdShade.MaterialBindingAPI(p).ComputeBoundMaterial()
            if m:used.add(m.GetPath())
    remove=[p.GetPath() for p in stage.Traverse() if p.IsA(UsdShade.Material) and p.GetPath() not in used]
    for path in remove:stage.RemovePrim(path)
    assets=set()
    for p in stage.Traverse():
        for a in p.GetAttributes():
            v=a.Get()
            if a.GetTypeName()=='asset' and v and v.path:assets.add(v.path.removeprefix('./'))
    stage.GetRootLayer().Save()
    compact=pkg/'compact.usdc';stage.GetRootLayer().Export(str(compact));compact.replace(pkg/usd)
    out=T/'shell_template.usdz'
    subprocess.run(['/usr/bin/usdzip',str(out),usd]+sorted(assets),cwd=pkg,check=True,capture_output=True)
    check=subprocess.run(['/usr/bin/usdchecker','--arkit',str(out)],text=True,capture_output=True)
    (T/'usdchecker.txt').write_text(check.stdout+check.stderr);assert check.returncode==0
    shell=next(UsdGeom.Mesh(p) for p in stage.Traverse() if p.IsA(UsdGeom.Mesh) and 'Casing___' in p.GetName())
    np.savez_compressed(T/'shell_geometry.npz',points=np.asarray(shell.GetPointsAttr().Get()),normals=np.asarray(shell.GetNormalsAttr().Get()),face_counts=np.asarray(shell.GetFaceVertexCountsAttr().Get()),face_indices=np.asarray(shell.GetFaceVertexIndicesAttr().Get()))
design=dict(status='owner approved',rim_reduction_from_original=.20,whole_coin_depth_reduction_from_original=.30,
            outer_radius=2.896,inner_radius=2.420,band_width=.476,shell_depth=.651,center_z=-.1155,
            front_rim_z=.210,front_plain_background_z=.0308,front_recess=.1792,
            closed_circular_bottom=True,preview_size=.96,preview_lift=.441,lowest_world_y=-2.455,
            casing_name='Casing___smooth_rounded_outer_edge_mobile_geometry',
            brushed_material_name='Silver___circumferential_brushed_steel',
            source='Emerald Sprout candidate03',notes='Keep each badge finish. Template gold is only a starter finish. Never apply the reductions twice.')
(T/'shell_design.json').write_text(json.dumps(design,indent=2)+'\n')
print('Saved validated approved shell template.')
