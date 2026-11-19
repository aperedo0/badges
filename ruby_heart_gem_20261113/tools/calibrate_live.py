import bpy,numpy as np
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/ruby_heart_gem_20261113');sc=bpy.context.scene;mat=sc.objects['Ruby Heart gem'].data.materials[0];script=next(n for n in mat.node_tree.nodes if n.bl_idname=='ShaderNodeScript')
debug=R/'optics/ray_probe.osl';debug.write_text('shader ray_probe(output closure color BSDF=0){vector d=normalize(I);BSDF=emission()*color(.5+.5*d[0],.5+.5*d[1],.5+.5*d[2]);}')
script.filepath=str(debug);script.update();sc.render.resolution_percentage=25;sc.cycles.samples=1;sc.cycles.use_denoising=False;sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.render.filepath=str(R/'optics/ray_probe.png');bpy.ops.render.render(write_still=True)
im=bpy.data.images['Render Result'];im.save_render(str(R/'optics/ray_probe.exr'),scene=sc)
print('Ray probe rendered. Global OSL I encoded as color.')
# Return the complete scene to its actual optical shader, without rendering again yet.
script.filepath=str(R/'optics/ruby_foil.osl');script.update()
for lv in (1,2,3,8):script.inputs['Mip'+str(lv)].default_value=str(R/'optics'/f'studio_linear_mip{lv}.exr')
sc.render.resolution_percentage=100;sc.cycles.samples=64;sc.cycles.use_denoising=True;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
