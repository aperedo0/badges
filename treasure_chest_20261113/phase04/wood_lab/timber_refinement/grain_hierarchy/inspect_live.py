import bpy,json
print(json.dumps(dict(filepath=bpy.data.filepath,dirty=bpy.data.is_dirty,scene=bpy.context.scene.name)))
