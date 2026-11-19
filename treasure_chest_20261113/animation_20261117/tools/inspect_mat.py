import bpy
sc=bpy.data.scenes['Full chest material evaluation']
print("CYC", sc.cycles.samples, sc.cycles.device, sc.render.film_transparent, sc.view_settings.view_transform, sc.view_settings.look, sc.world.name if sc.world else None)
for o in sc.objects:
    if o.type=='MESH' and (o.modifiers or o.name.startswith('Claude') or o.name.startswith('Simple')):
        print(o.name, [(m.type, getattr(m,'levels',None), getattr(m,'render_levels',None)) for m in o.modifiers])
for m in bpy.data.materials:
    if m.name.startswith('Simple') or m.name.startswith('Claude'):
        print("MAT", m.name, getattr(m,'displacement_method',None), m.cycles.displacement_method if hasattr(m,'cycles') else None)
for o in sc.objects:
    if o.type=='LIGHT': print("LIGHT", o.name, o.data.type, o.data.energy, tuple(o.data.color), o.location[:])
    if o.type=='CAMERA': print("CAM", o.name, o.data.lens, o.data.sensor_width)
