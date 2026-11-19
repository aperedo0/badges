from pathlib import Path
import bpy,json,numpy as np,time
R=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106');key=(R/'active.txt').read_text().strip();C=R/key/'candidate20';state=C/'ao_bake_state.json'
state.write_text(json.dumps(dict(status='baking',started=time.time())))
scene=bpy.context.scene
ob=next(o for o in scene.objects if o.type=='MESH' and 'velvet cushion' in o.name)
mat=ob.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');original=output.inputs['Surface'].links[0].from_socket
image=bpy.data.images.new(key+' geometric cloth occlusion',width=1024,height=1024,alpha=False,float_buffer=True);image.colorspace_settings.name='Non-Color';image.filepath_raw=str(C/'textures/velvet_occlusion.png');image.file_format='PNG'
tex=nodes.new('ShaderNodeTexImage');tex.name='Native geometric ambient occlusion';tex.image=image
for n in nodes:n.select=False
tex.select=True;nodes.active=tex
ao=nodes.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.60;ao.samples=32
emission=nodes.new('ShaderNodeEmission');links.new(ao.outputs['Color'],emission.inputs['Color']);links.new(emission.outputs[0],output.inputs['Surface'])
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
scene.render.engine='CYCLES';scene.cycles.samples=32
bpy.ops.object.bake(type='EMIT',use_clear=True,margin=16)
links.new(original,output.inputs['Surface']);nodes.remove(ao);nodes.remove(emission)
pixels=np.array(image.pixels[:]).reshape(1024,1024,4)[:,:,:3];assert pixels.std()>.01
image.save();image.pack();ob['native_ambient_occlusion']='velvet_occlusion.png from actual hemisphere visibility, radius 0.60 scene units'
bpy.data.libraries.write(str(C/'source'/(key+'.blend')),{scene},compress=True)
state.write_text(json.dumps(dict(status='complete',completed=time.time(),minimum=float(pixels.min()),maximum=float(pixels.max()),standard_deviation=float(pixels.std()),only_geometry_visibility=True,lights_baked=False),indent=2)+'\n')
print(key,'geometric ambient occlusion saved',float(pixels.min()),float(pixels.std()))
