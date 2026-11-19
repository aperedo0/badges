# Point the 3D viewport at the heart: VIEW = (yaw degrees, pitch degrees)
import bpy, math, mathutils
YAW, PITCH, SHADING = 35, 12, 'MATERIAL'
for win in bpy.context.window_manager.windows:
    for area in win.screen.areas:
        if area.type != 'VIEW_3D': continue
        sp = area.spaces.active; r3 = sp.region_3d
        sp.shading.type = SHADING
        sp.overlay.show_overlays = False
        r3.view_perspective = 'ORTHO'
        # front view looks along +Y in Blender (sees the -Y side = model +Z)
        q = mathutils.Euler((math.radians(90 - PITCH), 0, math.radians(YAW)), 'XYZ').to_quaternion()
        r3.view_rotation = q
        r3.view_location = (0, 0, 0.27)
        r3.view_distance = 7.2
print('view set')
