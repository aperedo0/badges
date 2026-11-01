"""Copy a reviewed candidate into its final model and source folders."""
from pathlib import Path
import sys,json,shutil,datetime
ROOT=Path(__file__).resolve().parent;key=sys.argv[1];R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip();cfg=json.loads((R/'design.json').read_text());model=json.loads((C/'validation.json').read_text())
required=['comparison.jpg','every_side.jpg','app_front.png','app_back.png','app_side_left.png','app_side_right.png','full_turn.mp4','runtime_gem_validation.json','runtime_attachment.txt','outline_front_4x.png','outline_back_4x.png','outline_side_left_4x.png','outline_side_right_4x.png',key+'.blend']
for f in required:assert (C/f).is_file(),f
source=C/'mobile'/(key+'_badge_mobile.usdz');target=R/'mobile'/source.name;target.parent.mkdir(exist_ok=True)
if target.exists():
 old=R/'previous'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S');old.mkdir(parents=True);shutil.copyfile(target,old/target.name)
shutil.copyfile(source,target);(R/'source').mkdir(exist_ok=True);shutil.copyfile(C/(key+'.blend'),R/'source'/(key+'.blend'));shutil.copyfile(R/'design.json',C/'design.json')
report='''# {name}

Reference matched sculpture with a complete matching rear, continuous side walls and independently closed central details. Inspected in the connected Blender application and the separate Badge Studio simulator. The original studio lights, stage and production app are unchanged.

[Reference and simulator](./{candidate}/comparison.jpg) | [Every side](./{candidate}/every_side.jpg) | [Slow full turn](./{candidate}/full_turn.mp4)

## Reference details

{details}

## Files

Final model: `mobile/{key}_badge_mobile.usdz`. Editable complete Blender scene: `source/{key}.blend`. Rebuild blueprint: `design.json`. Native captures and outline crops are in `{candidate}`.

## Dynamic gemstones

Every stone is an independent closed convex cut. Its color absorption, reflections, refraction and internal light paths respond to rotation under the fixed studio. No gemstone appearance photograph or fixed emission image is bound to it. The preview restores its named crest material with the runtime optics described in [RUNTIME.md](../RUNTIME.md). The USDZ by itself retains a plain fallback material.

Resting facet highlights differ from the static reference because they now come from actual light directions. Frostwing uses two convex sections under the center setting to retain its pinched long outline. The stairway's concave guiding star uses four separately cut stones. The editable scene retains ordinary fallback materials; final optical review takes place in the simulator.

## Checks and limits

Reviewed the front, rear, both side poses, slow full turn, reflection and outline crops. The model is closed, Y up, one meter per unit, has identity transforms, fits the shared floating height and has no coin material names, cameras, lights or floor objects. ARKit USD validation passes.

This custom framed shape follows the reference outline rather than the frozen coin casing. Detailed contours and matching rear use {triangles:,} triangles and {mb:.1f} MB, above the usual mobile size guidance. The extra geometry preserves the small contour details. Fine surface marks are carried by color and roughness maps on the actual relief. A measured front appearance fill preserves the non gemstone reference finish, while physical metal reflections change during rotation. The gemstones use the separate runtime optical path instead of that appearance fill. It is a close reference interpretation under the fixed app lighting, not a claim of pixel identity at every angle.
'''.format(name=cfg['name'],candidate=C.name,details='\n'.join('* '+x for x in cfg['details']),key=key,triangles=model['triangles'],mb=model['bytes']/1e6)
(R/'REPORT.md').write_text(report);print(target)
