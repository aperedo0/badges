import bpy
s = bpy.context.scene
print('SCENE', s.name, 'camera', s.camera.name if s.camera else None, 'res', s.render.resolution_x, s.render.resolution_y, 'engine', s.render.engine, 'view', s.view_settings.view_transform, s.view_settings.look, 'compositing', s.render.use_compositing, 'film_transparent', s.render.film_transparent)
for o in s.objects:
    print('OBJ', o.type, repr(o.name), 'hide_render', o.hide_render, 'parent', o.parent.name if o.parent else None)
