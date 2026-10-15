"""Complete, editable coin scenes. Inspection cameras stay out of the USDZs."""
from pathlib import Path
import bpy, json, math
import numpy as np
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parent
TEMP = Path('/tmp/achievement_coins_20261014')
NAMES = ['clean', 'hourglass_teal', 'hourglass_gold', 'sunrise', 'sprout']
COLORS = {
    'water': (.02, .35, .55, 1), 'glass': (.04, .11, .15, 1),
    'silver': (.55, .57, .60, 1), 'bronze': (.65, .30, .08, 1),
    'gold': (.75, .52, .13, 1), 'emerald': (.015, .27, .10, 1),
    'soil': (.22, .065, .015, 1), 'sand': (.14, .40, .43, 1),
    'background': (.035, .04, .045, 1),
    'emerald_background': (.012, .15, .055, 1),
}

def point_camera(camera):
    forward=(-camera.location).normalized()
    right=forward.cross(Vector((0.,1.,0.))).normalized()
    up=right.cross(forward)
    camera.rotation_euler=Matrix((right,up,-forward)).transposed().to_euler()

def build_curved_borders(scene,name):
    """Author continuous round borders in Blender around the existing relief."""
    base=ROOT/name
    design=json.loads((base/'design.json').read_text())
    loaded=np.load(base/'reliefs.npz')
    arrays={key:loaded[key] for key in loaded.files}
    for i,feature in enumerate(design['features']):
        if 'blender_curve' not in feature and 'blender_plate' not in feature:continue
        plate='blender_plate' in feature
        definition=feature['blender_plate'] if plate else feature['blender_curve']
        points=definition['points']
        if np.linalg.norm(np.asarray(points[0])-points[-1])<.001:points=points[:-1]
        if definition.get('conform'):
            from mathutils.bvhtree import BVHTree
            trees=[]
            for j,leaf in enumerate(design['features']):
                if leaf['role']==definition['conform']:
                    trees.append(BVHTree.FromPolygons(arrays[f'{j}_points'].tolist(),arrays[f'{j}_triangles'][:leaf['front_count']].tolist(),all_triangles=True))
            dense=[]
            for a,b in zip(np.asarray(points[:-1]),np.asarray(points[1:])):
                count=max(2,int(np.linalg.norm(b-a)/.025))
                dense.extend((a*(1-t)+b*t).tolist() for t in np.linspace(0,1,count,endpoint=False))
            points=dense+[points[-1]]
            heights=[]
            for x,y in points:
                hits=[tree.ray_cast(Vector((x,y,5.)),Vector((0.,0.,-1.)))[0] for tree in trees]
                heights.append(max([hit.z for hit in hits if hit is not None] or [.16])+.028)
        else:heights=[definition['z']]*len(points)
        curve=bpy.data.curves.new(name+'_round_border_'+str(i),'CURVE')
        curve.dimensions='2D' if plate else '3D';curve.resolution_u=1
        if plate:curve.extrude=definition['extrude'];curve.fill_mode='BOTH'
        curve.bevel_depth=definition['radius'];curve.bevel_resolution=3
        spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
        for p,(x,y),z in zip(spline.points,points,heights):p.co=(x,y,0. if plate else z,1.)
        spline.use_cyclic_u=definition.get('closed',True)
        curve.use_fill_caps=True
        obj=bpy.data.objects.new(name+'_round_border_'+str(i),curve)
        if plate:obj.location.z=definition['z']
        scene.collection.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.convert(target='MESH')
        if plate:bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)
        mesh=obj.data
        for polygon in mesh.polygons:polygon.use_smooth=True
        mesh.update();mesh.calc_loop_triangles()
        vertices=np.asarray([v.co[:] for v in mesh.vertices])
        triangles=np.asarray([t.vertices[:] for t in mesh.loop_triangles])
        normals=np.asarray([v.normal[:] for v in mesh.vertices])
        front=normals[triangles].mean(1)[:,2]>=0
        triangles=np.concatenate([triangles[front],triangles[~front]])
        corner_normals=normals[triangles]
        arrays[f'{i}_points']=vertices
        arrays[f'{i}_triangles']=triangles
        arrays[f'{i}_normals']=corner_normals
        feature['front_count']=int(front.sum());feature['triangles']=len(triangles)
        # Replace both faces in the complete working coin, leaving its shell.
        for side in ['Front','Back']:
            prefix=f'Relief{side}_{i}_{feature["role"]}'
            old=next(o for o in scene.objects if o.name.startswith(prefix))
            materials=list(old.data.materials)
            old_mesh=old.data
            p=vertices if side=='Front' else vertices*np.array([-1,1,-1])+np.array([0,0,-.33])
            new=bpy.data.meshes.new(prefix+'_Blender')
            new.from_pydata(p.tolist(),[],triangles.tolist());new.update()
            old.data=new
            for mat in materials:new.materials.append(mat)
            for polygon in new.polygons:polygon.use_smooth=True
            old['authored_in_blender']='Continuous round border curve'
            if old_mesh.users==0:bpy.data.meshes.remove(old_mesh)
        bpy.data.objects.remove(obj,do_unlink=True)
    np.savez_compressed(base/'reliefs.npz',**arrays)
    (base/'design.json').write_text(json.dumps(design,indent=2))

LIVE=globals().get('LIVE',False)
if not LIVE:bpy.ops.wm.read_factory_settings(use_empty=True)
for name in NAMES:
    scene = bpy.data.scenes.new(name)
    bpy.context.window.scene = scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = 700
    scene.render.resolution_y = 700
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.studiolight_rotate_z = .3
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = 'BOTH'
    scene.display.shading.cavity_ridge_factor = .6
    scene.display.shading.cavity_valley_factor = .7
    scene.display.shading.curvature_ridge_factor = .4
    scene.display.shading.curvature_valley_factor = .6
    scene.display.shading.background_type = 'WORLD'
    scene.world = bpy.data.worlds.new(name + '_inspection_world')
    scene.world.color = (.025, .025, .025)
    bpy.ops.wm.usd_import(filepath=str(ROOT / name / 'pkg/coin.usdc'))
    build_curved_borders(scene,name)
    # The imported whole coin retains its rim, inset, wall and relief meshes.
    for obj in scene.objects:
        if obj.type == 'MESH':
            obj['frozen_shell'] = not obj.name.startswith(('Relief', 'Rear_'))
    scene_materials={mat for obj in scene.objects if obj.type=='MESH' for mat in obj.data.materials if mat}
    for mat in scene_materials:
        if mat.name.startswith('Coin_'):
            role = mat.name.removeprefix('Coin_').split('_Face')[0].split('_Wall')[0]
            if role in COLORS:
                mat.diffuse_color = COLORS[role]
                if role == 'sand' and name == 'hourglass_gold':
                    mat.diffuse_color = COLORS['gold']
        elif name == 'sunrise':
            mat.diffuse_color = COLORS['bronze']
        elif name == 'sprout':
            mat.diffuse_color = COLORS['gold']
        else:
            mat.diffuse_color = COLORS['silver']
    # A reference beside the complete coin for hands-on Blender development.
    reference = bpy.data.objects.new(name + '_reference', None)
    reference.empty_display_type = 'IMAGE'
    reference.data = bpy.data.images.load(json.loads((ROOT / name / 'design.json').read_text())['reference'], check_existing=True)
    reference.empty_display_size = 6.6
    reference.location = (-7., 0., 0.)
    reference.rotation_euler = (0., 0., 0.)
    scene.collection.objects.link(reference)
    camera_data = bpy.data.cameras.new(name + '_inspection_camera')
    camera = bpy.data.objects.new(name + '_inspection_camera', camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 7.2
    scene.camera = camera
    for label, angle in ([] if LIVE else [('front', 0.), ('oblique', math.pi / 6), ('side', math.pi / 2), ('back', math.pi)]):
        camera.location = (18 * math.sin(angle), 2.0 if label == 'oblique' else 0., 18 * math.cos(angle))
        point_camera(camera)
        scene.render.filepath = str(TEMP / (name + '_blender_' + label + '.png'))
        bpy.ops.render.render(write_still=True)
    # Leave a useful three-quarter working view rather than the rear pose.
    camera.location = (9., 2., 15.6)
    point_camera(camera)
    scene['purpose'] = 'Blender geometry development; final appearance must be checked in Home.'
bpy.context.window.scene = bpy.data.scenes['clean']
if LIVE:
    from mathutils import Quaternion
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.shading.type='SOLID';space.shading.color_type='MATERIAL'
            space.shading.show_cavity=True;space.shading.cavity_type='BOTH'
            space.overlay.show_floor=False;space.overlay.show_axis_x=False;space.overlay.show_axis_y=False
            space.region_3d.view_rotation=Quaternion((1.,0.,0.,0.))
            space.region_3d.view_location=Vector((-3.3,0.,0.))
            space.region_3d.view_distance=11.
            space.region_3d.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'coins.blend'), compress=True)
