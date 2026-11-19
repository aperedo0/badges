import bpy,numpy as np,json,math,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
P=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab');src=bpy.context.scene;assert src.name=='Chest Complete Form Phase 1'
lab=bpy.data.scenes.new('Wood surface comparison');lab.render.engine='CYCLES';lab.world=src.world.copy();lab.view_settings.view_transform=src.view_settings.view_transform;lab.view_settings.look=src.view_settings.look;lab.view_settings.exposure=src.view_settings.exposure;lab.render.image_settings.file_format='PNG';lab.render.film_transparent=False;lab.cycles.samples=32;lab.cycles.use_denoising=True
copies={}
for o in src.objects:
 if not(o.get('full_form') or o.type in {'CAMERA','LIGHT'} or o.name=='Development floor'):continue
 q=o.copy();q.name='Lab '+o.name;q.parent=None;q.matrix_world=o.matrix_world.copy();q.hide_render=o.hide_render;lab.collection.objects.link(q);copies[o.name]=q
 if o.type in {'CAMERA','LIGHT'}:q.data=o.data.copy()
lab.camera=copies[src.camera.name];lab['source_scene']=src.name;lab['source_file']=str(P/'baseline_live.blend');lab['comparison_only']=True
body=copies['Chest Body Envelope'];body.name='Lab body A baseline';base=body.data;slot=[i for i,m in enumerate(base.materials) if m and 'Sample45' in m.name][0];old=base.materials[slot]
# Exact clipped front boundary, with recess fading to zero at its perimeter.
ymin=-2.1605000495910645;ymax=-.862500011920929;xb=2.49114990234375;xt=2.3499999046325684
W=801;H=217;t=np.linspace(0,1,H);Y=np.broadcast_to((ymin+t*(ymax-ymin))[:,None],(H,W));half=xb+(xt-xb)*t;X=half[:,None]*np.linspace(-1,1,W)[None,:]
bounds=json.loads((P/'candidate_design.json').read_text())['bounds'];pad=16;uw=2048;uh=768
U=pad/uw+(X-bounds['xmin'])/5.1*(uw-2*pad)/uw;V=pad/uh+(Y-bounds['ymin'])/1.3775*(uh-2*pad)/uh
idx=np.arange(W*H).reshape(H,W);F=np.stack([idx[:-1,:-1],idx[:-1,1:],idx[1:,1:],idx[1:,:-1]],axis=2).reshape(-1,4)
rot=Matrix.Rotation(math.radians(32),3,'Y');RM=np.array(rot)
def world(a):
 q=a@RM.T;return np.c_[q[:,0],-q[:,2],q[:,1]]
def interp(a):
 hh,ww=a.shape;uu=np.clip((X-bounds['xmin'])/5.1,0,1)*(ww-1);vv=np.clip(1-(Y-bounds['ymin'])/1.3775,0,1)*(hh-1);ix=uu.astype(int);iy=vv.astype(int);fx=uu-ix;fy=vv-iy
 return a[iy,ix]*(1-fx)*(1-fy)+a[iy,np.minimum(ix+1,ww-1)]*fx*(1-fy)+a[np.minimum(iy+1,hh-1),ix]*(1-fx)*fy+a[np.minimum(iy+1,hh-1),np.minimum(ix+1,ww-1)]*fx*fy
edge=np.minimum.reduce([half[:,None]-abs(X),Y-ymin,ymax-Y]);fade=np.clip(edge/.045,0,1);fade=fade*fade*(3-2*fade)
for key,folder in [('B','B_true_relief'),('C','C_scan')]:
 mat=old.copy();mat.name='Wood Lab '+key;nodes=mat.node_tree.nodes
 for role in ['albedo','roughness','normal']:
  im=bpy.data.images.load(str(P/folder/(role+'.png')),check_existing=False);im.colorspace_settings.name='sRGB' if role=='albedo' else 'Non-Color';im.pack();nodes['Single plank '+role].image=im
 nodes['Single plank physical tangent normal'].inputs['Strength'].default_value=1.0
 bs=nodes.get('Principled BSDF');bs.inputs['IOR'].default_value=1.46;bs.inputs['Specular IOR Level'].default_value=.5
 q=body.copy();q.data=base.copy();q.name='Lab body '+key;lab.collection.objects.link(q);q.data.materials[slot]=mat
 bm=bmesh.new();bm.from_mesh(q.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i] for i in [354,356,357]],context='FACES');bm.to_mesh(q.data);bm.free()
 a=np.load(P/folder/'surface.npz')['height'];z=1.6+interp(a)*fade;points=world(np.stack([X,Y,z],axis=2).reshape(-1,3));me=bpy.data.meshes.new('Wood '+key+' displaced grid');me.from_pydata(points.tolist(),[],F.tolist());me.update();me.materials.append(mat);uv=me.uv_layers.new(name='ChestWoodUV_Sample44');uvs=np.c_[U.ravel(),V.ravel()];ids=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',ids);uv.data.foreach_set('uv',uvs[ids].ravel());me.polygons.foreach_set('use_smooth',np.ones(len(F),dtype=bool))
 ob=bpy.data.objects.new('Lab relief '+key,me);lab.collection.objects.link(ob);ob['actual_geometry']=True;ob['depth_min']=float(z.min()-1.6);ob['grid']=[W,H];q.hide_render=ob.hide_render=True
# Keep the owner scene active; render work uses a separate saved comparison scene.
bpy.ops.wm.save_as_mainfile(filepath=str(P/'comparisons.blend'),compress=True)
print(json.dumps(dict(scene=lab.name,source_untouched=True,grid=[W,H],quad_count=len(F),normal_strength=old.node_tree.nodes['Single plank physical tangent normal'].inputs['Strength'].default_value)))
