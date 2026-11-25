"""Upgrade the dedicated Blender file to the chosen crystal facing and inset core."""
from pathlib import Path
import json,bpy,sys
root=Path(bpy.data.filepath).parent
directory=root/globals().get('CANDIDATE',json.loads((root/'design.json').read_text())['candidate'])
params=json.loads((directory/'facing.json').read_text())
g=json.loads((directory/'geometry.json').read_text())
scene=bpy.context.scene
assert scene.name=='Ruby Hourglass Studio'
mat=bpy.data.materials.get('Polished Ruby Facing') or bpy.data.materials.new('Polished Ruby Facing')
mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(*params['color'],1);bs.inputs['Metallic'].default_value=params['metallic']
bs.inputs['Roughness'].default_value=params['roughness'];bs.inputs['Alpha'].default_value=params['opacity'];bs.inputs['IOR'].default_value=1.77
mat.diffuse_color=(*params['color'],1)
for name in ['Upper_Ruby','Lower_Ruby']:
    core=scene.objects[name];facing=scene.objects.get(name+'_Facing')
    if not facing:
        facing=core.copy();facing.data=core.data.copy();facing.name=name+'_Facing';core.users_collection[0].objects.link(facing)
    facing.data.materials.clear();facing.data.materials.append(mat)
    for ob,coords in [(facing,g[name+'_Facing']['points']),(core,g[name]['points'])]:
        for v,(x,y,z) in zip(ob.data.vertices,coords):v.co=(x,-z,y)
        ob.data.update()
bpy.context.preferences.filepaths.save_version=0
if directory.name in ('candidate04','candidate05'):
    for name in ['Left_Bronze_Rail','Right_Bronze_Rail']:
        obj=scene.objects[name];geom=g[name]
        for v,(x,y,z) in zip(obj.data.vertices,geom['points']):v.co=(x,-z,y)
        obj.data.update()
        obj.data.normals_split_custom_set_from_vertices([(x,-z,y) for x,y,z in geom['normals']])
    bronze=scene.objects['Left_Bronze_Rail'].active_material
    shader=bronze.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*params['bronze'],1)
    texture=next(node for node in bronze.node_tree.nodes if node.type=='TEX_IMAGE')
    texture.image=bpy.data.images.load(str(directory/'BronzeBrush.png'));texture.image.colorspace_settings.name='Non-Color';texture.image.pack()
if params.get('polished_border'):
    import importlib.util
    path=root/'tools/girdle.py';spec=importlib.util.spec_from_file_location('girdle',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    girdle=mat.copy();girdle.name='Ruby Polished Girdle'
    girdle.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=1
    for key in ('Upper_Ruby_Facing','Lower_Ruby_Facing'):
        surf=scene.objects[key];surf.data.materials.append(girdle)
        borders=set(module.polished_border(key,g[key]))
        for poly in surf.data.polygons:poly.material_index=1 if poly.index in borders else 0
scene['candidate']=directory.name
scene.render.filepath='//'+directory.name+'/studio_front.png'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
