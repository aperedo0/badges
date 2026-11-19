import bpy
sc = bpy.data.scenes.get('Emerald Stag v4')
if sc:
    sc.name = 'Emerald Stag'
    for win in bpy.context.window_manager.windows:
        win.scene = sc
bpy.ops.wm.save_as_mainfile(filepath='/Users/antonioperedo/Desktop/badges/emerald_stag_claude_20261108/live/emerald_stag_live.blend')
print('saved', bpy.data.filepath, [s.name for s in bpy.data.scenes])
