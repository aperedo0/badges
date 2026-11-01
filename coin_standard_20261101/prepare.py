"""Snapshot only Emerald Sprout and prepare its complete Blender import."""
from pathlib import Path
import shutil,json,hashlib,zipfile
from pxr import Usd,UsdGeom
import numpy as np
R=Path(__file__).resolve().parent;P=R.parent/'emerald_trophy_20261025/preview';S=P/'ScreenTime/SupportingFiles/Assets.xcassets/Badge3DPreviewEmeraldSprout.dataset/coin.usdz'
O=R/'original';C=R/'candidate01'
for p in [O/'mobile',O/'source',O/'review',C/'mobile',C/'source',C/'review',R/'work']:p.mkdir(parents=True,exist_ok=True)
copy=O/'mobile/emerald_sprout_original.usdz'
if not copy.exists():shutil.copyfile(S,copy)
pkg=R/'work/original';pkg.mkdir(exist_ok=True)
with zipfile.ZipFile(copy) as z:
 z.extractall(pkg);names=z.namelist()
usd=next(n for n in names if n.endswith(('.usdc','.usda','.usd')));stage=Usd.Stage.Open(str(pkg/usd));UsdGeom.SetStageUpAxis(stage,'Z');stage.GetRootLayer().Export(str(pkg/'blender_import.usdc'))
meta={'active_candidate':'candidate01','scope':'Emerald Sprout only','status':'draft for owner review','radial_rim_width_factor':.65,'whole_coin_thickness_factor':.65,'inner_radius':2.420,'old_outer_radius':3.015,'new_outer_radius':2.80675,'old_rim_width':.595,'new_rim_width':.38675,'old_shell_depth':.930,'new_shell_depth':.6045,'old_center_z':-.165,'new_center_z':-.10725,'old_front_rim_z':.300,'new_front_rim_z':.195,'front_recess':.1664,'preview_size':.96,'preview_lift':.35175,'lowest_world_y':-2.455,'original_sha256':hashlib.sha256(copy.read_bytes()).hexdigest(),'original_preview_asset':str(S),'source_usd':usd,'archive_files':names}
if not (R/'draft_design.json').exists():(R/'draft_design.json').write_text(json.dumps(meta,indent=2)+'\n')
# Snapshot the private preview source for a scoped integration patch.
p=P/'ScreenTime/Sources/App/Features/Badges/Badge3DLiveBadge.swift';before=R/'preview_before.swift'
if not before.exists():shutil.copyfile(p,before)
print(json.dumps({k:meta[k] for k in ['scope','new_outer_radius','new_rim_width','new_shell_depth','preview_lift']},indent=2))
