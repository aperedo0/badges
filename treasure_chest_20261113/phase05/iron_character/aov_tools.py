"""Temporary, socket driven Shader AOV diagnostics using Blender 5.2 native output files."""
import bpy,json,numpy as np
from pathlib import Path

def attach(scene,material,signals):
 layer=scene.view_layers[0];nodes=material.node_tree.nodes;links=material.node_tree.links;records=[];created={}
 for name,kind,socket in signals:
  item=next((a for a in layer.aovs if a.name==name),None) or layer.aovs.add();item.name=name;item.type=kind;n=nodes.new('ShaderNodeOutputAOV');n.aov_name=name;n.name='Diagnostic '+name;dest=n.inputs['Color' if kind=='COLOR' else 'Value'];record=dict(name=name,type=kind,source_node=socket.node.name,source_socket=socket.name)
  source=socket if socket.is_output else socket.links[0].from_socket if socket.is_linked else None
  if source:links.new(source,dest);record['connection']='Actual linked signal'
  else:
   value=socket.default_value
   if kind=='COLOR':dest.default_value=tuple(value) if len(value)==4 else (*value,1)
   else:dest.default_value=float(value)
   record.update(connection='Actual constant input copied without changing the shader',constant=list(value) if hasattr(value,'__len__') else float(value))
  assert item.is_valid,name;records.append(record);created[name]=n
 layer.update_render_passes();return records,created

def configure_files(scene,names,directory):
 directory=Path(directory);scene.use_nodes=True;group=bpy.data.node_groups.new('Temporary material AOV diagnostics','CompositorNodeTree');scene.compositing_node_group=group;group.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');render=group.nodes.new('CompositorNodeRLayers');render.scene=scene;render.layer=scene.view_layers[0].name;output=group.nodes.new('NodeGroupOutput');group.links.new(render.outputs['Image'],output.inputs['Image']);writers={}
 for name in names:
  assert name in render.outputs,list(render.outputs.keys());node=group.nodes.new('CompositorNodeOutputFile');node.directory=str(directory/name);node.file_name='data';node.format.media_type='IMAGE';node.format.file_format='OPEN_EXR';node.format.color_mode='RGB';node.format.color_depth='32';node.format.exr_codec='ZIP';node.save_as_render=False;node.file_output_items.clear();node.file_output_items.new('RGBA',name);group.links.new(render.outputs[name],node.inputs[name]);writers[name]=node
 return writers

def read_outputs(directory,names):
 arrays={}
 for name in names:
  files=sorted((Path(directory)/name).glob('*.exr'));assert files,('Missing AOV file',name);im=bpy.data.images.load(str(files[-1]),check_existing=False);im.colorspace_settings.name='Non-Color';w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a);a=a.reshape(h,w,4)[:,:,:3];assert np.isfinite(a).all(),name;arrays[name]=a;bpy.data.images.remove(im)
 return arrays

def statistics(arrays,scope_name):
 scope=arrays[scope_name][:,:,0]>.999;assert scope.sum()>500,'Missing or empty diagnostic surface scope';result={}
 for name,array in arrays.items():
  a=array[scope].astype(np.float64);result[name]=dict(min=a.min(0).tolist(),max=a.max(0).tolist(),mean=a.mean(0).tolist(),std=a.std(0).tolist(),nonzero_fraction=float(np.mean(abs(a)>1e-7)),scope_pixels=int(scope.sum()))
 return result,scope
