"""Author complete new hourglass working coins in the connected Blender."""
from pathlib import Path
import json,numpy as np,bpy
from mathutils import Matrix,Vector
ROOT=Path('/Users/antonioperedo/Desktop/badges/hourglass_match_20261014')
OLD=ROOT.parent/'achievement_coins_refine_20261014'
helpers={'__file__':str(OLD/'blender_finish_shapes.py')}
exec((OLD/'blender_finish_shapes.py').read_text().split("for name in ['hourglass_teal'")[0],helpers)
for name in ['hourglass_teal','hourglass_gold']:
    scene=bpy.data.scenes.new(name+'_matched')
    source=bpy.data.scenes[name]
    scene.world=source.world.copy();scene.render.engine='BLENDER_WORKBENCH'
    for old in source.objects:
        if old.type=='MESH' and old.name.startswith(('Casing___','Inner_channel___','Inner_edge___','Rim_inner_lip___','Rear_Inner_edge___')):continue
        obj=old.copy()
        if old.data:obj.data=old.data.copy()
        scene.collection.objects.link(obj)
    rim=next(o for o in bpy.data.scenes['water_match'].objects if o.name.startswith('Casing___'))
    obj=rim.copy();obj.data=rim.data.copy();scene.collection.objects.link(obj)
    bpy.context.window.scene=scene
    root=ROOT/name;meta=json.loads((root/'design.json').read_text());loaded=np.load(root/'reliefs.npz');arrays={k:loaded[k] for k in loaded.files}
    for i,feature in enumerate(meta['features']):
        if 'blender_lathe' in feature:
            p,t,n,fc=helpers['lathe'](feature['blender_lathe'])
            arrays[f'{i}_points']=p;arrays[f'{i}_triangles']=t;arrays[f'{i}_normals']=n
            feature['front_count']=fc;feature['triangles']=len(t)
        else:p,t,n=(arrays[f'{i}_{k}'] for k in ['points','triangles','normals'])
        for side in ['Front','Back']:
            obj=next(o for o in scene.objects if o.name.startswith(f'Relief{side}_{i}_{feature["role"]}'))
            mats=list(obj.data.materials)
            points=p if side=='Front' else p*[-1,1,-1]+[0,0,-.33]
            normals=n if side=='Front' else n*[-1,1,-1]
            mesh=bpy.data.meshes.new(name+f'_{side}_{i}_clean');mesh.from_pydata(points.tolist(),[],t.tolist());mesh.update()
            for face in mesh.polygons:face.use_smooth=True
            mesh.normals_split_custom_set(normals.reshape(-1,3).tolist())
            for mat in mats:mesh.materials.append(mat)
            uv=mesh.uv_layers.new(name='CoinReliefUV')
            for loop in mesh.loops:
                q=p[loop.vertex_index];uv.data[loop.index].uv=((q[0]+3.015)/6.03,(q[1]+3.015)/6.03)
            obj.data=mesh
    np.savez_compressed(root/'reliefs.npz',**arrays);(root/'design.json').write_text(json.dumps(meta,indent=2))
    scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_rotation=Matrix.Identity(3).to_quaternion()
                area.spaces.active.region_3d.view_location=Vector((-3.3,0,0));area.spaces.active.region_3d.view_distance=11
                area.spaces.active.region_3d.view_perspective='ORTHO'
    bpy.data.libraries.write(str(root/(name+'.blend')),{scene},compress=True)
    print(name,'complete Blender coin saved')
bpy.context.window.scene=bpy.data.scenes['hourglass_teal_matched']
