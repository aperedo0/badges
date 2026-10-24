"""Build both complete bronze coins inside the connected Blender application."""
from pathlib import Path
import bpy,math,json,zipfile
import numpy as np
from mathutils import Vector,Quaternion

ROOT=Path('/Users/antonioperedo/Desktop/badges/bronze_coins_20261018')
TEMP=Path('/tmp/bronze_coins_20261018');TEMP.mkdir(exist_ok=True)
SOURCE=ROOT.parent/'botanical_match_20261014/sunrise/mobile/sunrise_badge_mobile.usdz'
(TEMP/'rim').mkdir(exist_ok=True)
with zipfile.ZipFile(SOURCE) as archive:
    for filename in archive.namelist():
        if filename.startswith('textures/Rim_'):
            (TEMP/'rim'/Path(filename).name).write_bytes(archive.read(filename))
PALETTE={'bronze':((.66,.32,.16),1,.30),'backdrop':((.003,.0025,.0022),1,.90)}
# Reuse only the existing native Blender helper definitions, not its builders.
helper=ROOT.parent/'star_island_20261016/build_live.py'
text=helper.read_text();definitions=text[text.index('def material('):text.index('\ndef staircase(')]
exec(compile(definitions,str(helper),'exec'),globals())
exec(compile((ROOT/'torch_geometry.py').read_text(),str(ROOT/'torch_geometry.py'),'exec'),globals())

def pixel_xy(points,center=(623,576)):
    return (np.asarray(points,float)-center)*[2.42/455,-2.42/455]

def bevel_solid(name,outline,base=.065,front=.245):
    p=np.asarray(outline,float)
    area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))
    if area<0:p=p[::-1]
    n=len(p);points=[[*q,front] for q in p]+[[*q,base] for q in p]
    faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
    faces += [(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
    obj=mesh_object(name,points,faces,'bronze')
    bpy.context.view_layer.objects.active=obj
    bevel=obj.modifiers.new('Solid machined bronze bevel','BEVEL');bevel.width=.040;bevel.segments=3
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    normal=obj.modifiers.new('Weighted flat face normals','WEIGHTED_NORMAL');normal.keep_sharp=True
    bpy.ops.object.modifier_apply(modifier=normal.name)
    return finish(obj,'bronze')

def compass():
    disk('Recessed warm charcoal',2.445,.044,'backdrop')
    for quarter in range(4):
        a=np.linspace(quarter*math.pi/2+.065,(quarter+1)*math.pi/2-.065,40)
        xy_tube('Compass quarter '+str(quarter),np.c_[1.49*np.cos(a),1.49*np.sin(a)],.087,'bronze',.014)
    for i in range(4):
        a=i*math.pi/2;axis=np.array([math.cos(a),math.sin(a)]);side=np.array([-axis[1],axis[0]])
        perimeter=[axis*2.24,axis*.82+side*.041,axis*.16,axis*.82-side*.041]
        points=[[*p,.078] for p in perimeter]+[[*(axis*.82),.100]]
        mesh_object('Tapered cardinal needle '+str(i),points,[(j,(j+1)%4,4) for j in range(4)],'bronze')
    outline=pixel_xy([[813,230],[656,534],[799,532],[451,926],[600,618],[449,626]])
    bevel_solid('Raised solid lightning bolt',outline)

def pebble(name,shape,base=.068):
    outline=pixel_xy(shape['outline_pixels'])
    center=pixel_xy([shape['center_pixels']])[0]
    if np.cross(outline,np.roll(outline,-1,axis=0)).sum()<0:outline=outline[::-1]
    count=len(outline);depth=shape['depth']
    points=[[*center,base+depth]]
    for latitude in range(1,24):
        phi=latitude*math.pi/24
        for xy in center+(outline-center)*math.sin(phi):
            points.append([*xy,base+depth*math.cos(phi)])
    points.append([*center,base-depth]);end=len(points)-1
    faces=[(0,1+i,1+(i+1)%count) for i in range(count)]
    for ring in range(22):
        a=1+ring*count;b=a+count
        for i in range(count):
            j=(i+1)%count
            faces.extend([(a+i,b+i,b+j),(a+i,b+j,a+j)])
    a=1+22*count
    faces.extend((a+i,end,a+(i+1)%count) for i in range(count))
    return mesh_object(name,points,faces,'bronze',True)

def balance():
    disk('Recessed dark charcoal',2.445,.044,'backdrop')
    shapes=json.loads((ROOT/'zen_balance/stone_outlines.json').read_text())
    for name,shape in shapes.items():pebble(name,shape)

def bronze_casing(scene):
    """Keep the full round source mesh and approved roughness/glint graphs."""
    rim=next(o for o in scene.objects if o.type=='MESH' and o.name.startswith('Casing___'))
    for mat in rim.data.materials:
        if not mat or not mat.use_nodes:continue
        mat.diffuse_color=(.66,.32,.16,1)
        for node in mat.node_tree.nodes:
            if node.type=='BSDF_PRINCIPLED':
                tint=.94 if 'inner' in mat.name.lower() else 1.
                node.inputs['Base Color'].default_value=(.66*tint,.32*tint,.16*tint,1)
            if node.type=='TEX_IMAGE' and node.image:
                filename=Path(node.image.filepath).name
                if filename=='Rim_brushed_reference_color.png':
                    node.image=bpy.data.images.load(str(TEMP/'rim'/filename),check_existing=False)
                    node.image.colorspace_settings.name='sRGB'
                node.image.pack()
    return rim

for badge in globals().get('BADGE_NAMES',['lightning_compass','zen_balance','torch_sunburst']):
    for old in list(bpy.data.scenes):
        if old.name==badge or old.name.startswith(badge+'.'):bpy.data.scenes.remove(old)
    own=ROOT/badge/(badge+'.blend')
    source=own if own.exists() else ROOT.parent/'star_island_20261016/star_ascent/star_ascent.blend'
    with bpy.data.libraries.load(str(source),link=False) as (available,loaded):loaded.scenes=[available.scenes[0]]
    scene=loaded.scenes[0];scene.name=badge;bpy.context.window.scene=scene
    for obj in list(scene.objects):
        if not (obj.type=='MESH' and obj.name.startswith('Casing___')):bpy.data.objects.remove(obj,do_unlink=True)
    bronze_casing(scene)
    mats={role:material(role) for role in PALETTE}
    if badge in ['zen_balance','torch_sunburst']:
        mat=mats['bronze'];nodes=mat.node_tree.nodes
        rough=nodes.new('ShaderNodeTexImage')
        rough.image=bpy.data.images.load(str(ROOT/badge/'textures/bronze_roughness.png'),check_existing=False)
        rough.image.colorspace_settings.name='Non-Color';rough.image.pack()
        uv=next(n for n in nodes if n.type=='UVMAP')
        mat.node_tree.links.new(uv.outputs['UV'],rough.inputs['Vector'])
        mat.node_tree.links.new(rough.outputs['Color'],nodes.get('Principled BSDF').inputs['Roughness'])
    if badge=='lightning_compass':compass()
    elif badge=='zen_balance':balance()
    else:torch()
    arrays={};groups=[]
    for obj in list(scene.objects):
        if not obj.get('new_emblem'):continue
        mesh=obj.data;mesh.calc_loop_triangles()
        p=np.array([v.co[:] for v in mesh.vertices]);t=np.array([tri.vertices[:] for tri in mesh.loop_triangles])
        n=np.array([[mesh.corner_normals[l].vector[:] for l in tri.loops] for tri in mesh.loop_triangles])
        i=len(groups);arrays[str(i)+'_points']=p;arrays[str(i)+'_triangles']=t;arrays[str(i)+'_normals']=n
        groups.append({'name':obj.name,'role':obj['role']})
        back=obj.copy();back.data=obj.data.copy();back.name='Back_'+obj.name
        for v in back.data.vertices:v.co=(-v.co.x,v.co.y,-v.co.z-.33)
        back.data.update()
        if mesh.has_custom_normals:
            back.data.normals_split_custom_set([(-v.vector.x,v.vector.y,-v.vector.z) for v in mesh.corner_normals])
        scene.collection.objects.link(back)
    np.savez_compressed(TEMP/(badge+'_geometry.npz'),**arrays)
    (ROOT/badge/'design.json').write_text(json.dumps({'groups':groups,'palette':PALETTE,'source_shell':'sunrise'},indent=2))
    ref=bpy.data.objects.new(badge+'_reference',None);ref.empty_display_type='IMAGE';ref.data=bpy.data.images.load(str(ROOT/'references'/(badge+'.png')),check_existing=True);ref.data.pack();ref.empty_display_size=6.03;ref.location=(-7,0,0);scene.collection.objects.link(ref)
    for area in bpy.context.screen.areas:
        if area.type=='VIEW_3D':
            s=area.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,0,0));s.region_3d.view_distance=9;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
    bpy.data.libraries.write(str(own),{scene},compress=True)
    print(badge,'complete,',len(groups),'front relief objects',flush=True)
