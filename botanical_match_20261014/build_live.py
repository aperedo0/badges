"""Complete working coins, using native Blender curves and solid beveled plates."""
from pathlib import Path
import bpy,json,numpy as np
from mathutils import Matrix,Vector
ROOT=Path('/Users/antonioperedo/Desktop/badges/botanical_match_20261014')
original=ROOT.parent/'achievement_coins_refine_20261014'
helpers={'__file__':str(ROOT/'blender_workbench.py')}
exec((original/'blender_workbench.py').read_text().split('LIVE=globals()')[0],helpers)
for name in ['sunrise','sprout']:
    scene=bpy.data.scenes.new(name+'_matched');scene.world=bpy.data.scenes[name].world.copy();scene.render.engine='BLENDER_WORKBENCH'
    for old in bpy.data.scenes[name].objects:
        if old.type=='MESH' and old.name.startswith(('Casing___','Inner_channel___','Inner_edge___','Rim_inner_lip___','Rear_Inner_edge___')):continue
        obj=old.copy()
        if old.data:obj.data=old.data.copy()
        scene.collection.objects.link(obj)
    rim=next(o for o in bpy.data.scenes['water_match'].objects if o.name.startswith('Casing___'))
    obj=rim.copy();obj.data=rim.data.copy();scene.collection.objects.link(obj)
    bpy.context.window.scene=scene;helpers['build_curved_borders'](scene,name)
    meta=json.loads((ROOT/name/'design.json').read_text());a=np.load(ROOT/name/'reliefs.npz')
    for i,f in enumerate(meta['features']):
        p=a[f'{i}_points']
        for side in ['Front','Back']:
            obj=next(o for o in scene.objects if o.name.startswith(f'Relief{side}_{i}_{f["role"]}'))
            uv=obj.data.uv_layers.get('CoinReliefUV') or obj.data.uv_layers.new(name='CoinReliefUV')
            for loop in obj.data.loops:
                q=p[loop.vertex_index];uv.data[loop.index].uv=((q[0]+3.015)/6.03,(q[1]+3.015)/6.03)
    for obj in scene.objects:
        if obj.type=='EMPTY' and 'reference' in obj.name:
            obj.data.filepath=meta['reference'];obj.data.reload();obj.empty_image_depth='FRONT';obj.show_in_front=True;obj.hide_set(False);obj.hide_viewport=False
    scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    bpy.data.libraries.write(str(ROOT/name/(name+'.blend')),{scene},compress=True)
    print(name,'complete native Blender working coin saved')
bpy.context.window.scene=bpy.data.scenes['sunrise_matched']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_rotation=Matrix.Identity(3).to_quaternion();area.spaces.active.region_3d.view_location=Vector((-3.3,0,0));area.spaces.active.region_3d.view_distance=11;area.spaces.active.region_3d.view_perspective='ORTHO'
