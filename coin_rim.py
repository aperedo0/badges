"""Physical brushed metal on the complete raised rim; never painted lighting.

A shared metal binding lets the app restore directional brushing on the face,
bevel and outer wall. The inner bevel has its own less peaky satin finish.
"""
from pathlib import Path
import math,struct,zlib
import numpy as np

COLORS={
 'clean':(.57,.59,.62),'hourglass_teal':(.36,.38,.41),
 'hourglass_gold':(.61,.59,.54),'sunrise':(.66,.32,.16),'sprout':(.80,.58,.23),
}
SHELL_PATH='/Badge/Casing___smooth_rounded_outer_edge/Casing___smooth_rounded_outer_edge_mobile_geometry'
BRUSHED='Silver___circumferential_brushed_steel_Mobile_Casing'
FRONT_Z=.300
CENTER_Z=-.165
# UV charts have generous gutters to keep mipmaps from mixing finishes.
CHARTS={'face':(.02,.48),'side':(.54,.73),'bevel':(.79,.86),'inner':(.91,.98)}
# Bevel/inner atlas charts are unused by the restored border shaders below.
FINISH={'face':(.33,.012),'side':(.38,.014),'bevel':(.24,.006),'inner':(.32,.002)}

def write_gray_png(path,values):
 pixels=np.uint8(np.clip(np.rint(values*255),0,255));h,w=pixels.shape
 def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
 raw=b''.join(b'\0'+row.tobytes() for row in pixels)
 Path(path).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))

def write_rgb_png(path,values):
 pixels=np.uint8(np.clip(np.rint(values*255),0,255));h,w,_=pixels.shape
 def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
 raw=b''.join(b'\0'+row.tobytes() for row in pixels)
 Path(path).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))

def sample_field(field,u,v):
 h,w=field.shape;x=(u%1)*w;y=np.clip(v,0,1)*(h-1)
 ix=np.floor(x).astype(int);iy=np.floor(y).astype(int);dx=x-ix;dy=y-iy
 return ((1-dy)*((1-dx)*field[iy,ix%w]+dx*field[iy,(ix+1)%w])+dy*((1-dx)*field[np.minimum(iy+1,h-1),ix%w]+dx*field[np.minimum(iy+1,h-1),(ix+1)%w]))

def finish_atlases(folder,name):
 """Only the reference's high-frequency grain; its lighting was removed.

 The grain source is mean-free, exposure-normalized and high-passed at 12
 source pixels. A small neutral reflectance grain is intrinsic surface detail;
 no broad light bands, normal map or emission are present.
 """
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
 grain=np.load(Path(__file__).with_name('coin_brush_grain.npz'))['grain']
 # Mirror joins have matching values and no hard tile edge.
 grain=np.concatenate([grain,grain[:,::-1]],axis=1)
 grain=np.concatenate([grain,grain[::-1]],axis=0)
 size=1024;atlas=np.full((size,size),.36);reflectance=np.ones((size,size))
 for role,(bottom,top) in CHARTS.items():
  # Include gutters. The UVs stay well inside these chart rectangles.
  lo=max(0,int((bottom-.014)*size));hi=min(size,int((top+.014)*size)+1)
  u,v=np.meshgrid((np.arange(size)+.5)/size,(np.arange(lo,hi)+.5)/size)
  t=np.clip((v-bottom)/(top-bottom),0,1)
  # Match the visible grain density, rather than squeezing the entire photo
  # across the coin or its much narrower outer wall.
  fine=sample_field(grain,u*(.35 if role=='face' else 1.),.13+t*(.35 if role=='face' else .12))
  mean,variation=FINISH[role]
  # PNG row zero is UV top, hence reverse these rows when writing.
  atlas[lo:hi]=mean+variation*fine
  reflectance[lo:hi]=1+(.12 if role in ['face','side'] else .025)*fine
 out=folder/'Rim_brushed_reference_roughness.png';write_gray_png(out,atlas[::-1])
 linear=np.clip(reflectance[::-1,:,None]*np.array(COLORS[name]),0,1)
 srgb=np.where(linear<=.0031308,12.92*linear,1.055*linear**(1/2.4)-.055)
 color=folder/'Rim_brushed_reference_color.png';write_rgb_png(color,srgb)
 return out,color

def raise_points(points):
 points=np.array(points,copy=True);current=float(points[:,2].max())
 if abs(current-FRONT_Z)<1e-6:return points
 assert abs(current-.215)<1e-6,current
 points[:,2]+=np.where(points[:,2]>CENTER_Z,.085,-.085);return points

def brush_uv(points,triangles,planar_uv):
 q=points[triangles];radius=np.linalg.norm(q[:,:,:2],axis=2);mean=radius.mean(axis=1)
 roles=np.where(mean>3.014,'side',np.where(mean>2.945,'bevel',np.where(mean<2.485,'inner','face')))
 angle=np.arctan2(q[:,:,1],q[:,:,0])/math.tau+.5
 seam=np.ptp(angle,axis=1)>.5;angle[seam]=np.where(angle[seam]<.5,angle[seam]+1,angle[seam])
 uv=np.zeros((*triangles.shape,2))
 for role,(bottom,top) in CHARTS.items():
  mask=roles==role
  if role=='face':
   u=planar_uv[mask,:,0];v=planar_uv[mask,:,1]
  else:
   u=angle[mask]
   if role=='side':v=(q[mask,:,2]+.56)/.79
   elif role=='bevel':v=(radius[mask]-2.945)/.07
   else:v=(q[mask,:,2]+.52)/.71
  uv[mask,:,0]=u;uv[mask,:,1]=bottom+np.clip(v,0,1)*(top-bottom)
 return uv,roles

def apply(stage,name,package,raise_geometry=True):
 from pxr import UsdGeom,UsdShade,Sdf,Gf,Vt
 package=Path(package);atlas,color_atlas=finish_atlases(package/'textures',name)
 mesh=UsdGeom.Mesh(stage.GetPrimAtPath(SHELL_PATH));assert mesh,'Coin casing missing'
 points=np.asarray(mesh.GetPointsAttr().Get())
 if raise_geometry:
  points=raise_points(points);mesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(points.astype(np.float32)))
  mesh.GetExtentAttr().Set([Gf.Vec3f(*points.min(0).tolist()),Gf.Vec3f(*points.max(0).tolist())])
 triangles=np.asarray(mesh.GetFaceVertexIndicesAttr().Get()).reshape(-1,3)
 source_uv=UsdGeom.PrimvarsAPI(mesh).GetPrimvar('USDZ_UV')
 planar=np.asarray(source_uv.ComputeFlattened()).reshape(-1,2)
 if source_uv.GetInterpolation()=='vertex':planar=planar[triangles]
 else:planar=planar.reshape(-1,3,2)
 uv,roles=brush_uv(points,triangles,planar)
 UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('RimBrushUV',Sdf.ValueTypeNames.TexCoord2fArray,'faceVarying').Set(Vt.Vec2fArray.FromNumpy(uv.reshape(-1,2).astype(np.float32)))
 materials={}
 for matname in [BRUSHED,'Shell_inner']:
  path='/Badge/_materials/'+matname;stage.RemovePrim(path)
  mat=UsdShade.Material.Define(stage,path);sh=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('Surface'));sh.CreateIdAttr('UsdPreviewSurface')
  for key,value,typ in [('diffuseColor',Gf.Vec3f(*COLORS[name]),Sdf.ValueTypeNames.Color3f),('metallic',1.,Sdf.ValueTypeNames.Float),('emissiveColor',Gf.Vec3f(0),Sdf.ValueTypeNames.Color3f),('clearcoat',0.,Sdf.ValueTypeNames.Float),('opacity',1.,Sdf.ValueTypeNames.Float)]:sh.CreateInput(key,typ).Set(value)
  reader=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('BrushUV'));reader.CreateIdAttr('UsdPrimvarReader_float2');reader.CreateInput('varname',Sdf.ValueTypeNames.String).Set('RimBrushUV');reader.CreateOutput('result',Sdf.ValueTypeNames.Float2)
  tex=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('RoughnessMap'));tex.CreateIdAttr('UsdUVTexture')
  tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+atlas.name));tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('raw');tex.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('repeat');tex.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp');tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result');tex.CreateOutput('r',Sdf.ValueTypeNames.Float)
  sh.CreateInput('roughness',Sdf.ValueTypeNames.Float).ConnectToSource(tex.ConnectableAPI(),'r');sh.CreateOutput('surface',Sdf.ValueTypeNames.Token);mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(),'surface');materials[matname]=mat
  color=UsdShade.Shader.Define(stage,mat.GetPath().AppendChild('MetalReflectance'));color.CreateIdAttr('UsdUVTexture');color.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+color_atlas.name));color.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB');color.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(reader.ConnectableAPI(),'result');color.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('repeat');color.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp');color.CreateOutput('rgb',Sdf.ValueTypeNames.Float3);sh.GetInput('diffuseColor').ConnectToSource(color.ConnectableAPI(),'rgb')
 UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(materials[BRUSHED])
 for subset in UsdGeom.Subset.GetGeomSubsets(mesh,UsdGeom.Tokens.face,'materialBind'):
  role=subset.GetPrim().GetName();UsdShade.MaterialBindingAPI.Apply(subset.GetPrim()).Bind(materials['Shell_inner' if role=='inner' else BRUSHED])
 for unused in ['Shell_bevel','Shell_side']:stage.RemovePrim('/Badge/_materials/'+unused)
 for image in (package/'textures').glob('Rim_*.png'):
  if image not in [atlas,color_atlas]:image.unlink()
 restore_glint_borders(stage,name,package)
 return mesh

def apply_blender(scene,name):
 import bpy
 rim=next(o for o in scene.objects if o.type=='MESH' and o.name.startswith('Casing___'));mesh=rim.data
 points=raise_points(np.asarray([v.co[:] for v in mesh.vertices]))
 for vertex,point in zip(mesh.vertices,points):vertex.co=point
 mesh.update();triangles=np.asarray([p.vertices[:] for p in mesh.polygons]);assert triangles.shape[1]==3
 planar=np.asarray([x.uv[:] for x in mesh.uv_layers['USDZ_UV'].data]).reshape(-1,3,2)
 coords,roles=brush_uv(points,triangles,planar)
 uv=mesh.uv_layers.get('RimBrushUV') or mesh.uv_layers.new(name='RimBrushUV')
 for polygon,face_uv in zip(mesh.polygons,coords):
  for i,loop in enumerate(polygon.loop_indices):uv.data[loop].uv=face_uv[i]
 atlas,color_atlas=finish_atlases(Path('/tmp/coin_rim_reference')/name,name);image=bpy.data.images.load(str(atlas),check_existing=True);image.reload();image.colorspace_settings.name='Non-Color';image.pack()
 color_image=bpy.data.images.load(str(color_atlas),check_existing=True);color_image.reload();color_image.colorspace_settings.name='sRGB';color_image.pack()
 mesh.materials.clear()
 for label in [BRUSHED,'Shell_inner']:
  mat=bpy.data.materials.new(name+'_'+label);mat.use_nodes=True;mat.diffuse_color=(*COLORS[name],1)
  nodes=mat.node_tree.nodes;links=mat.node_tree.links;sh=nodes.get('Principled BSDF');sh.inputs['Base Color'].default_value=(*COLORS[name],1);sh.inputs['Metallic'].default_value=1;sh.inputs['Emission Color'].default_value=(0,0,0,1)
  anisotropic=next((s for s in sh.inputs if 'Anisotrop' in s.name and 'Rotation' not in s.name),None)
  if anisotropic is not None:anisotropic.default_value=.4 if label==BRUSHED else 0
  if label==BRUSHED and sh.inputs.get('Tangent') is not None:
   tangent=nodes.new('ShaderNodeTangent');tangent.direction_type='RADIAL';tangent.axis='Z';links.new(tangent.outputs['Tangent'],sh.inputs['Tangent'])
  coord=nodes.new('ShaderNodeUVMap');coord.uv_map='RimBrushUV';tex=nodes.new('ShaderNodeTexImage');tex.image=image;links.new(coord.outputs['UV'],tex.inputs['Vector']);links.new(tex.outputs['Color'],sh.inputs['Roughness']);mesh.materials.append(mat)
  color=nodes.new('ShaderNodeTexImage');color.image=color_image;links.new(coord.outputs['UV'],color.inputs['Vector']);links.new(color.outputs['Color'],sh.inputs['Base Color'])
 for polygon,role in zip(mesh.polygons,roles):polygon.material_index=int(role=='inner')
 restore_glint_borders_blender(rim,name,roles)
 return rim


def glint_texture(folder):
 import zipfile
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
 out=folder/'Rim_glint_reference_roughness.png'
 with zipfile.ZipFile(Path(__file__).with_name('coin_glint_reference.usdz')) as archive:
  out.write_bytes(archive.read('textures/'+out.name))
 return out


def restore_glint_borders(stage,name,package):
 """Restore the two actual border shaders, not a guessed roughness value."""
 from pxr import Usd,UsdGeom,UsdShade,Sdf,Gf
 reference=Usd.Stage.Open(str(Path(__file__).with_name('coin_glint_reference.usdz')))
 glint_texture(Path(package)/'textures')
 for role in ['inner','bevel']:
  path=Sdf.Path('/Badge/_materials/Shell_'+role);stage.RemovePrim(path)
  assert Sdf.CopySpec(reference.GetRootLayer(),path,stage.GetRootLayer(),path)
  surface=UsdShade.Shader(stage.GetPrimAtPath(path.AppendChild('Surface')))
  surface.GetInput('diffuseColor').Set(Gf.Vec3f(*(np.array(COLORS[name])*(.94 if role=='inner' else 1.)).tolist()))
  subset=stage.GetPrimAtPath(SHELL_PATH+'/'+role)
  UsdShade.MaterialBindingAPI.Apply(subset).Bind(UsdShade.Material(stage.GetPrimAtPath(path)))


def restore_glint_borders_blender(rim,name,roles):
 import bpy
 mesh=rim.data;file=glint_texture(Path('/tmp/coin_rim_reference')/name)
 image=bpy.data.images.load(str(file),check_existing=True);image.reload();image.colorspace_settings.name='Non-Color';image.pack()
 mesh.materials.pop(index=1)
 for role,scale,bias,tint in [('inner',.25,.240,.94),('bevel',.12,.146,1.)]:
  mat=bpy.data.materials.new(name+'_original_glint_'+role);mat.use_nodes=True;mat.diffuse_color=(*[c*tint for c in COLORS[name]],1)
  nodes=mat.node_tree.nodes;links=mat.node_tree.links;sh=nodes.get('Principled BSDF');sh.inputs['Base Color'].default_value=mat.diffuse_color;sh.inputs['Metallic'].default_value=1;sh.inputs['Emission Color'].default_value=(0,0,0,1)
  uv=nodes.new('ShaderNodeUVMap');uv.uv_map='USDZ_UV';tex=nodes.new('ShaderNodeTexImage');tex.image=image;links.new(uv.outputs['UV'],tex.inputs['Vector'])
  multiply=nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY_ADD';multiply.inputs[1].default_value=scale;multiply.inputs[2].default_value=bias;links.new(tex.outputs['Color'],multiply.inputs[0]);links.new(multiply.outputs[0],sh.inputs['Roughness']);mesh.materials.append(mat)
 for polygon,role in zip(mesh.polygons,roles):polygon.material_index=1 if role=='inner' else 2 if role=='bevel' else 0
