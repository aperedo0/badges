"""Apply the measured relief maps to the editable complete Blender scene."""
from pathlib import Path
import bpy
ROOT=Path('/Users/antonioperedo/Desktop/badges/emerald_archer_20261023')
scene=bpy.data.scenes['emerald_archer'];bpy.context.window.scene=scene
for role in ['gold','field','emerald','emerald_light','emerald_dark']:
    objects=[o for o in scene.objects if o.type=='MESH' and o.get('new_emblem')]
    materials={m for o in objects for m in o.data.materials if m and (m.name=='Archer_'+role or m.name.startswith('Archer_'+role+'.'))}
    for mat in materials:
        nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
        uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='CoinReliefUV'
        for suffix,socket,space in [('color','Base Color','sRGB'),('emission','Emission Color','sRGB')]:
            file=ROOT/'candidate02/textures'/(role+'_'+suffix+'.png')
            if not file.exists():continue
            tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(file),check_existing=False)
            tex.image.colorspace_settings.name=space;tex.image.pack()
            nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs[socket])
            if suffix=='emission':bs.inputs['Emission Strength'].default_value=1
bpy.data.libraries.write(str(ROOT/'candidate02/emerald_archer.blend'),{scene},compress=True)
print('Measured relief materials saved in complete editable Blender scene')
