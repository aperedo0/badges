import bpy,json
ng=bpy.data.node_groups.new('Temporary output item schema','CompositorNodeTree');fo=ng.nodes.new('CompositorNodeOutputFile');i=fo.file_output_items.new('RGBA','raw');r={}
for p in i.bl_rna.properties:
 if p.identifier=='rna_type':continue
 v=getattr(i,p.identifier)
 r[p.identifier]=dict(type=p.type,value=str(v),enums=list(p.enum_items.keys()) if p.type=='ENUM' else None)
r['format_type']=str(fo.format.bl_rna);r['format_properties']=[p.identifier for p in fo.format.bl_rna.properties]
bpy.data.node_groups.remove(ng);print(json.dumps(r))
