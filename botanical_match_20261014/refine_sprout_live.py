from pathlib import Path
import bpy,json,numpy as np
R=Path('/Users/antonioperedo/Desktop/badges/botanical_match_20261014')
helpers={'__file__':str(R/'blender_workbench.py')}
source=(R.parent/'achievement_coins_refine_20261014/blender_workbench.py').read_text().split('LIVE=globals()')[0]
source=source.replace("heights.append(max([hit.z for hit in hits if hit is not None] or [.16])+.028)","heights.append(max([hit.z for hit in hits if hit is not None] or [float('nan')])+.028)")
source=source.replace("else:heights=[definition['z']]*len(points)","""    h=np.asarray(heights);valid=np.isfinite(h)
            if valid.any():h=np.interp(np.arange(len(h)),np.flatnonzero(valid),h[valid])
            else:h[:]=.26
            heights=np.convolve(np.pad(h,4,mode='edge'),np.ones(9)/9,mode='valid')
        else:heights=[definition['z']]*len(points)""")
exec(source,helpers)
s=bpy.data.scenes['sprout_matched'];bpy.context.window.scene=s
helpers['build_curved_borders'](s,'sprout')
bpy.data.libraries.write(str(R/'sprout/sprout.blend'),{s},compress=True)
print('Sprout gold borders raised to one continuous clean plane; vein heights smoothed.')
