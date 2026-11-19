import bpy,json
ng=bpy.data.node_groups.new('Temporary output schema','CompositorNodeTree');fo=ng.nodes.new('CompositorNodeOutputFile')
f=fo.file_output_items.bl_rna.functions['new']
r=dict(new_parameters=[dict(id=p.identifier,type=p.type,required=p.is_required) for p in f.parameters],default_items=[dict(name=i.name,props=[p.identifier for p in i.bl_rna.properties]) for i in fo.file_output_items],inputs=[s.name for s in fo.inputs]);bpy.data.node_groups.remove(ng);print(json.dumps(r))
