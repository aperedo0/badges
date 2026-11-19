import bpy,sys,math,json,numpy as np
from pathlib import Path
from mathutils import Matrix
D=Path(__file__).resolve().parent;key=sys.argv[sys.argv.index('--')+1];C=D/key;C.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(D/'baseline.blend'));sc=bpy.data.scenes['Test plank master'];o=sc.objects['Lab Chest Lower Rim'];o.data=o.data.copy();
rest=None
if key.startswith(('03','04','05','06','07','09')):
 exec(compile((D/'sculpt_rim.py').read_text(),'local_rim_sculpt','exec'));rest=sculpt_rim(o,C)
me=o.data;R=np.array(Matrix.Rotation(math.radians(32),3,'Y'));a=rest if rest is not None else np.array([tuple(v.co) for v in me.vertices]);q=np.c_[a[:,0],a[:,2],-a[:,1]]@R;uv=me.uv_layers.new(name='LowerIronAtlas');physical=me.uv_layers.new(name='LowerIronPhysical')
for poly in me.polygons:
 center=q[list(poly.vertices)].mean(0);normal=np.array(poly.normal);n=np.array([normal[0],normal[2],-normal[1]])@R
 axis=2 if abs(n[2])>abs(n[0]) else 0
 if abs(n[1])>.85:axis=2 if 1.78-abs(center[2])<2.73-abs(center[0]) else 0
 for li in poly.loop_indices:
  x,y,z=q[me.loops[li].vertex_index]
  if axis==2:u=x+2.73 if center[2]>=0 else 5.46+3.56+2.73-x
  else:u=5.46+1.78-z if center[0]>=0 else 2*5.46+3.56+z+1.78
  v=y+2.2175
  if abs(n[1])>.85:v+=.35*(min(1.78-abs(z),2.73-abs(x)))
  uv.data[li].uv=(u/18.04,v/.5035);physical.data[li].uv=(u,v)
mat=bpy.data.materials.new('Lower iron '+key);mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled');nt.links.new(bs.outputs['BSDF'],out.inputs['Surface']);bs.inputs['Base Color'].default_value=(.058,.052,.047,1);bs.inputs['Metallic'].default_value=.95;bs.inputs['Roughness'].default_value=.50
uvn=nt.nodes.new('ShaderNodeUVMap');uvn.uv_map='LowerIronAtlas';uvp=nt.nodes.new('ShaderNodeUVMap');uvp.uv_map='LowerIronPhysical'
def image(path,color,coord=uvn):
 im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='sRGB' if color else 'Non-Color';im.pack();n=nt.nodes.new('ShaderNodeTexImage');n.image=im;n.interpolation='Linear';nt.links.new(coord.outputs['UV'],n.inputs['Vector']);return n
if key.startswith('01'):
 source=D/'resources/Metal055A';col=image(next(source.glob('*Color.png')),True,uvp);mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(.18,.18,.18,1);nt.links.new(col.outputs['Color'],mul.inputs[1]);nt.links.new(mul.outputs[0],bs.inputs['Base Color']);r=image(next(source.glob('*Roughness.png')),False,uvp);mapping=nt.nodes.new('ShaderNodeMapRange');mapping.inputs['To Min'].default_value=.33;mapping.inputs['To Max'].default_value=.68;nt.links.new(r.outputs['Color'],mapping.inputs['Value']);nt.links.new(mapping.outputs['Result'],bs.inputs['Roughness']);n=image(next(source.glob('*NormalGL.png')),False,uvp);normal=nt.nodes.new('ShaderNodeNormalMap');normal.uv_map='LowerIronPhysical';normal.inputs['Strength'].default_value=.7;nt.links.new(n.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
elif key.startswith('07'):
 source=D/'resources/Hammered0009'
 def native(role):return next(p for p in source.iterdir() if not p.name.startswith('._') and role in p.name)
 scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=1/1.6;nt.links.new(uvp.outputs['UV'],scale.inputs[0])
 def channel(role,color):
  node=image(native(role),color,uvp)
  for link in list(node.inputs['Vector'].links):nt.links.remove(link)
  nt.links.new(scale.outputs['Vector'],node.inputs['Vector']);return node
 col=channel('_color_',True);black=nt.nodes.new('ShaderNodeMixRGB');black.name='Blackened iron pigment';black.blend_type='MULTIPLY';black.inputs[0].default_value=1;black.inputs[2].default_value=(.20,.20,.20,1);nt.links.new(col.outputs['Color'],black.inputs[1])
 wear=image(D/'surface04/wear.png',False);mix=nt.nodes.new('ShaderNodeMixRGB');mix.name='Locally exposed neutral iron';mix.inputs[2].default_value=(.31,.285,.25,1);nt.links.new(wear.outputs['Color'],mix.inputs[0]);nt.links.new(black.outputs[0],mix.inputs[1]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
 rough=channel('_roughness_',False);range=nt.nodes.new('ShaderNodeMapRange');range.inputs['To Min'].default_value=.35;range.inputs['To Max'].default_value=.67;nt.links.new(rough.outputs['Color'],range.inputs['Value']);nt.links.new(range.outputs['Result'],bs.inputs['Roughness'])
 metal=channel('_metallic_',False);range=nt.nodes.new('ShaderNodeMapRange');range.inputs['To Min'].default_value=.82;range.inputs['To Max'].default_value=1;nt.links.new(metal.outputs['Color'],range.inputs['Value']);nt.links.new(range.outputs['Result'],bs.inputs['Metallic'])
 normal=channel('_normal_opengl_',False);nm=nt.nodes.new('ShaderNodeNormalMap');nm.name='Professional hammered OpenGL normal';nm.uv_map='LowerIronPhysical';nm.inputs['Strength'].default_value=.65;nt.links.new(normal.outputs['Color'],nm.inputs['Color']);nt.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
elif key.startswith(('02','03','04','05','06','09')):
 for file,socket,color in [('albedo.png','Base Color',True),('roughness.png','Roughness',False),('metallic.png','Metallic',False)]:nt.links.new(image(D/('surface09' if key.startswith('09') else 'surface06' if key.startswith('06') else 'surface05' if key.startswith('05') else 'surface04' if key.startswith('04') else 'surface03' if key.startswith('03') else 'surface')/file,color).outputs['Color'],bs.inputs[socket])
 height=image(D/('surface09' if key.startswith('09') else 'surface06' if key.startswith('06') else 'surface05' if key.startswith('05') else 'surface04' if key.startswith('04') else 'surface03' if key.startswith('03') else 'surface')/'height16.png',False);bump=nt.nodes.new('ShaderNodeBump');bump.name='Calibrated forging height';bump.inputs['Strength'].default_value=1;bump.inputs['Distance'].default_value=.016;nt.links.new(height.outputs['Color'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
me.materials.clear();me.materials.append(mat)
for p in me.polygons:p.material_index=0
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True);(C/'design.json').write_text(json.dumps(dict(target=o.name,material=mat.name,vertices=len(me.vertices),polygons=len(me.polygons),scope='Existing bottom rim only',geometry_unchanged=not key.startswith(('03','04','05','06','07','09'))),indent=2));print('Saved',key,flush=True)
