import bpy,json,hashlib,numpy as np
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/lookdev_evidence');sc=bpy.context.scene;assert sc.name=='Test plank master';body=sc.objects['Master Chest Body Envelope'];mat=next(m for m in body.data.materials if m and m.name.startswith('Wood Lab '));p=Path(bpy.data.filepath)
def digest(a):return hashlib.sha256(a.tobytes()).hexdigest()
a=np.empty(len(body.data.vertices)*3,dtype=np.float32);body.data.vertices.foreach_get('co',a)
r=dict(source_file=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),live_was_dirty=bpy.data.is_dirty,frame=sc.frame_current,scene=sc.name,vertices=len(body.data.vertices),geometry_sha256=digest(a),material=mat.name,nodes=[],lights=[],render=dict(engine=sc.render.engine,samples=sc.cycles.samples,device=sc.cycles.device,denoise=sc.cycles.use_denoising,adaptive=sc.cycles.use_adaptive_sampling,threshold=sc.cycles.adaptive_threshold,resolution=[sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage],filter_width=sc.cycles.filter_width),color=dict(view=sc.view_settings.view_transform,look=sc.view_settings.look,exposure=sc.view_settings.exposure,gamma=sc.view_settings.gamma),camera=dict(name=sc.camera.name,matrix=[list(row) for row in sc.camera.matrix_world],type=sc.camera.data.type,ortho=sc.camera.data.ortho_scale,lens=sc.camera.data.lens),layout=[a.type for a in bpy.context.screen.areas])
for n in mat.node_tree.nodes:
 d=dict(name=n.name,type=n.type)
 if n.type=='TEX_IMAGE':d.update(image=n.image.name,path=n.image.filepath,resolution=list(n.image.size),colorspace=n.image.colorspace_settings.name,interpolation=n.interpolation,extension=n.extension)
 if n.type=='NORMAL_MAP':d.update(space=n.space,uv=n.uv_map,strength=n.inputs['Strength'].default_value)
 if n.type=='BSDF_PRINCIPLED':d.update(inputs={k:n.inputs[k].default_value for k in ['Metallic','IOR','Specular IOR Level','Anisotropic','Coat Weight']})
 r['nodes'].append(d)
for o in sc.objects:
 if o.type=='LIGHT':r['lights'].append(dict(name=o.name,matrix=[list(row) for row in o.matrix_world],location=list(o.location),energy=o.data.energy,color=list(o.data.color),size=o.data.size,shape=o.data.shape,hide_render=o.hide_render,data=o.data.name))
(D/'baseline_inventory.json').write_text(json.dumps(r,indent=2));old=bpy.context.preferences.filepaths.save_version;bpy.context.preferences.filepaths.save_version=0
try:bpy.ops.wm.save_as_mainfile(filepath=str(D/'baseline_live.blend'),compress=True)
finally:bpy.context.preferences.filepaths.save_version=old
print(json.dumps({k:r[k] for k in ['source_file','live_was_dirty','material','render','color','layout']}))
