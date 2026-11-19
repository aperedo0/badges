import bpy, math, mathutils
YAW, PITCH, SHADING, DIST = __VIEW__
for win in bpy.context.window_manager.windows:
    for area in win.screen.areas:
        if area.type != 'VIEW_3D': continue
        sp = area.spaces.active; r3 = sp.region_3d
        sp.shading.type = SHADING; sp.overlay.show_overlays = False
        r3.view_perspective = 'PERSP'
        q = mathutils.Euler((math.radians(90 - PITCH), 0, math.radians(YAW)), 'XYZ').to_quaternion()
        r3.view_rotation = q; r3.view_location = (0, 0, 0.25); r3.view_distance = DIST
print('view set')
