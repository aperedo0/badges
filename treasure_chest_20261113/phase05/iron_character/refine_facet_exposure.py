import bpy,json,shutil
from pathlib import Path
D=Path(__file__).resolve().parent;A=D/'11_restored_pigment';C=D/'12_exposed_facets';C.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(A/'master.blend'));sc=bpy.data.scenes['Test plank master'];obj=sc.objects['Lab Chest Lower Rim'];obj.data=obj.data.copy();mat=obj.data.materials[0].copy();mat.name='Forged iron localized exposed bevel facets';obj.data.materials[0]=mat
for name in ['Lab Chest Rail Rivet 1 3','Lab Chest Rail Rivet 1 4']:sc.objects[name].data.materials[0]=mat
nt=mat.node_tree;attr=next(n for n in nt.nodes if n.type=='ATTRIBUTE' and n.attribute_name=='Damaged bevel facet wear');links=list(attr.outputs['Fac'].links)
r=nt.nodes.new('ShaderNodeMapRange');r.name='Localized damaged facet exposure';r.label='Exposed iron on existing damaged facets';r.interpolation_type='SMOOTHSTEP';r.inputs['From Min'].default_value=.06;r.inputs['From Max'].default_value=.58;r.inputs['To Min'].default_value=0;r.inputs['To Max'].default_value=.98;nt.links.new(attr.outputs['Fac'],r.inputs['Value'])
for link in links:nt.links.new(r.outputs['Result'],link.to_socket)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);a=json.loads((A/'design.json').read_text());a.update(mesh=obj.data.name,material=mat.name,source='11_restored_pigment',only_existing_damaged_facet_exposure_remapped=True,geometry_and_source_maps_exact=True);(C/'design.json').write_text(json.dumps(a,indent=2));shutil.copy2(A/'edge_geometry.npz',C/'edge_geometry.npz')
