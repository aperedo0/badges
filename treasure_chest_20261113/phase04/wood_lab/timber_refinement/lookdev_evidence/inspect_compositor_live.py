import bpy,json
print(json.dumps(dict(scene_nodes=[p.identifier for p in bpy.types.Scene.bl_rna.properties if 'compos' in p.identifier or 'node' in p.identifier],output_properties=[p.identifier for p in bpy.types.CompositorNodeOutputFile.bl_rna.properties],renderlayer_outputs=[p.identifier for p in bpy.types.CompositorNodeRLayers.bl_rna.properties]),indent=2))
