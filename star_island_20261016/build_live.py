"""Author complete new badge scenes in the connected Blender application."""
from pathlib import Path
import bpy, math, json
import numpy as np
from mathutils import Vector, Quaternion

ROOT=Path('/Users/antonioperedo/Desktop/badges/star_island_20261016')
TEMP=Path('/tmp/star_island_20261016');TEMP.mkdir(exist_ok=True)
design=json.loads((ROOT/'design.json').read_text())
leaf_geometry=np.load(ROOT/'leaf_geometry.npz')
sea_geometry=np.load(ROOT/'sea_geometry.npz')
PALETTE={'silver':((.52,.50,.47),1,.31),'cloud':((.26,.25,.24),1,.43),
 'gold':((.78,.47,.065),1,.28),'leaf':((.008,.155,.026),.45,.22),
 'charcoal':((.005,.006,.007),0,.89),'sky':((.25,.02,.1),0,.76),
 'sea':((.006,.205,.255),.35,.28),'sun':((1,.48,.015),.2,.30)}

def material(role):
    name=badge+'_'+role
    mat=bpy.data.materials.new(name);mat.use_nodes=True
    color,metal,rough=PALETTE[role];mat.diffuse_color=(*color,1)
    node=mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value=(*color,1);node.inputs['Metallic'].default_value=metal;node.inputs['Roughness'].default_value=rough
    fitted=ROOT/badge/'textures'/(role+'_color.png')
    scales_path=ROOT/badge/'texture_scales.json'
    scales=json.loads(scales_path.read_text()).get(role,{}) if scales_path.exists() else {}
    texname='silver' if role=='cloud' else role
    file=fitted if fitted.exists() else ROOT/'textures'/(texname+'.png')
    if file.exists():
        uv=mat.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map='CoinReliefUV'
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(file),check_existing=False);tex.image.colorspace_settings.name='sRGB';tex.image.pack()
        mat.node_tree.links.new(uv.outputs['UV'],tex.inputs['Vector'])
        if role!='cloud' or fitted.exists():
            color_output=tex.outputs['Color']
            if scales and fitted.exists():
                mul=mat.node_tree.nodes.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=scales['color'];mat.node_tree.links.new(color_output,mul.inputs[0]);color_output=mul.outputs['Vector']
            mat.node_tree.links.new(color_output,node.inputs['Base Color'])
        glowfile=ROOT/badge/'textures'/(role+'_emission.png')
        if fitted.exists() and role in ['sky','sea','sun','leaf'] and glowfile.exists():
            glow=mat.node_tree.nodes.new('ShaderNodeTexImage');glow.image=bpy.data.images.load(str(glowfile),check_existing=False);glow.image.colorspace_settings.name='sRGB';glow.image.pack()
            mat.node_tree.links.new(uv.outputs['UV'],glow.inputs['Vector'])
            glow_output=glow.outputs['Color']
            if scales:
                mul=mat.node_tree.nodes.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=scales['emission'];mat.node_tree.links.new(glow_output,mul.inputs[0]);glow_output=mul.outputs['Vector']
            mat.node_tree.links.new(glow_output,node.inputs['Emission Color']);node.inputs['Emission Strength'].default_value=1 if scales else 4
    mat['role']=role
    return mat

def finish(obj,role,smooth=False):
    obj['new_emblem']=True;obj['role']=role
    obj.data.materials.clear();obj.data.materials.append(mats[role])
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    if obj.type=='CURVE':bpy.ops.object.convert(target='MESH')
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    for p in obj.data.polygons:p.use_smooth=smooth
    obj.data.update()
    uv=obj.data.uv_layers.get('CoinReliefUV') or obj.data.uv_layers.new(name='CoinReliefUV')
    for loop in obj.data.loops:
        p=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((p.x+3.015)/6.03,(p.y+3.015)/6.03)
    return obj

def mesh_object(name,points,faces,role,smooth=False):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(points,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
    return finish(obj,role,smooth)

def disk(name,radius,z,role,center=(0,0),half=False,dome=0):
    count=96 if not half else 48
    angles=np.linspace(0,math.pi if half else math.tau,count+1)
    # A center ring keeps the disk's gently raised surface genuinely curved.
    points=[[*center,z+dome]]
    for theta in angles:points.append([center[0]+radius*math.cos(theta),center[1]+radius*math.sin(theta),z])
    faces=[(0,i+1,i+2) for i in range(count)]
    return mesh_object(name,points,faces,role,True)

def tube(name,points,role,radius=.025,closed=False):
    points=np.asarray(points)
    # Thin borders do not need subpixel-long curve segments.
    take=[0]
    for i in range(1,len(points)-1):
        if np.linalg.norm(points[i]-points[take[-1]])>.035:take.append(i)
    take.append(len(points)-1);points=points[take]
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1;c.bevel_depth=radius;c.bevel_resolution=1;c.use_fill_caps=True
    spline=c.splines.new('POLY');spline.points.add(len(points)-1)
    for p,q in zip(spline.points,points):p.co=(*q,1)
    spline.use_cyclic_u=closed
    obj=bpy.data.objects.new(name,c);scene.collection.objects.link(obj)
    return finish(obj,role,True)

def xy_tube(name,points,z,role,radius=.025,closed=False):
    return tube(name,[[p[0],p[1],z] for p in points],role,radius,closed)

def block(name,center,size,role,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center);obj=bpy.context.object;obj.name=name;obj.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=obj.modifiers.new('Machined short bevel','BEVEL');mod.width=bevel;mod.segments=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=obj.modifiers.new('Weighted machined normals','WEIGHTED_NORMAL');mod.keep_sharp=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return finish(obj,role,False)

def plate(name,points,z,role):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='2D';curve.fill_mode='BOTH';curve.extrude=.006
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for p,(x,y) in zip(spline.points,points):p.co=(x,y,0,1)
    spline.use_cyclic_u=True
    obj=bpy.data.objects.new(name,curve);obj.location.z=z;scene.collection.objects.link(obj)
    return finish(obj,role)

def ellipsoid(name,center,scale,role,segments=24,rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=center)
    obj=bpy.context.object;obj.name=name;obj.scale=scale
    return finish(obj,role,True)

def staircase():
    disk('Recessed charcoal face',2.445,.044,'charcoal')
    # The clouds are behind the steps, with individual overlapping lobes.
    clouds=[(-2.30,.12,.29),(-2.12,-.28,.40),(-2.10,-.78,.49),(-1.65,-.65,.32),(-1.38,-1.02,.32),(-1.84,-1.27,.42),(-1.47,-1.62,.43),(-1.10,-1.45,.32)]
    for side in [-1,1]:
        for i,(x,y,r) in enumerate(clouds):
            ellipsoid('Cloud_'+str(side)+'_'+str(i),(side*abs(x),y,.072),(r,r*.92,.075),'cloud')
    # Reference proportions: five progressively narrower solid steps.
    specs=[(3.02,-1.96,1.28,.265),(2.10,-1.035,.57,.235),(1.66,-.56,.38,.205),(1.28,-.175,.39,.175),(.99,.18,.32,.145)]
    for i,(width,y,height,front) in enumerate(specs):block('Step_'+str(i+1),(0,y,(.045+front)/2),(width,height,front-.045),'silver',.023)
    cy=.90;outer=.67;inner=.294
    boundary=[]
    for i in range(10):
        a=math.pi/2+i*math.pi/5;r=outer if i%2==0 else inner
        boundary.append([r*math.cos(a),cy+r*math.sin(a),.23 if i%2==0 else .27])
    points=[[0,cy,.43]]+boundary+[[x,y,.16] for x,y,_ in boundary]
    faces=[]
    for i in range(10):
        j=(i+1)%10;faces.append((0,i+1,j+1));faces.append((i+1,11+i,11+j,j+1))
    mesh_object('Five point faceted star',points,faces,'silver')
    rays=[((0,1.65),(0,2.18)),((-.55,1.28),(-.94,1.67)),((.55,1.28),(.94,1.67)),((-.83,.97),(-1.48,1.06)),((.83,.97),(1.48,1.06)),((-.75,.59),(-1.24,.31)),((.75,.59),(1.24,.31))]
    for i,(a,b) in enumerate(rays):xy_tube('Ray_'+str(i),[a,b],.145,'silver',.032)

def sunset():
    disk('Purple orange sunset enamel',2.445,.044,'sky')
    # Sea is the bottom circular segment, exactly behind the raised horizon.
    hy=design['horizon'][0][1];rad=2.445;a=math.asin(hy/rad)
    arc=np.linspace(math.pi-a,math.tau+a,100)
    pts=[[rad*math.cos(t),rad*math.sin(t),.078] for t in arc]
    center=np.array(pts).mean(0);points=[center.tolist()]+pts
    faces=[(0,i+1,i+2) for i in range(len(pts)-1)]+[(0,len(pts),1)]
    mesh_object('Teal sea',sea_geometry['points'].tolist(),sea_geometry['triangles'].tolist(),'sea',True)
    disk('Sun disc',design['sun_radius'],.105,'sun',design['sun_center'],True,.055)
    c=design['sun_center'];r=design['sun_radius']
    xy_tube('Sun raised gold arc',[[c[0]+r*math.cos(t),c[1]+r*math.sin(t)] for t in np.linspace(0,math.pi,64)],.17,'gold',.028)
    xy_tube('Gold horizon',design['horizon'],.14,'gold',.026)
    for j,p in enumerate(design['leaves']+design['small_leaves']):
        plate('Solid green frond base_'+str(j),p,.162,'leaf')
        points=leaf_geometry[str(j)+'_points'];tris=leaf_geometry[str(j)+'_triangles']
        mesh_object('Palm green frond_'+str(j),points.tolist(),tris.tolist(),'leaf',True)
        xy_tube('Continuous gold frond edge_'+str(j),p,.182,'gold',.021,True)
    for tree,key in enumerate(['trunk','small_trunk']):
        start,end=np.asarray(design[key]);axis=end-start;perp=np.array([-axis[1],axis[0]]);perp/=np.linalg.norm(perp)
        for k in range(6):
            t0=k/6;t1=(k+1)/6-.018;a=start+axis*t0;b=start+axis*t1
            w0=(.145 if tree==0 else .105)*(1-.58*t0);w1=(.145 if tree==0 else .105)*(1-.58*t1)
            p=[[*q,.23] for q in [a-perp*w0,a+perp*w0,b+perp*w1,b-perp*w1]]
            mesh_object('Gold trunk segment_'+str(tree)+'_'+str(k),p,[(0,3,2,1)],'gold')
            xy_tube('Trunk segment bevel_'+str(tree)+'_'+str(k),[a-perp*w0,a+perp*w0,b+perp*w1,b-perp*w1],.23,'gold',.018,True)
        ellipsoid('Palm gold hub_'+str(tree),(*end,.25),(.12 if tree==0 else .085,)*3,'gold',20,10)
    points=leaf_geometry['12_points'].copy();points[:,2]+=.025
    plate('Solid island base',design['island'],.183,'gold')
    mesh_object('Golden island',points.tolist(),leaf_geometry['12_triangles'].tolist(),'gold',True)
    xy_tube('Island shore gold border',design['island'],.23,'gold',.026,True)
    for i,key in enumerate(['wave1','wave2']):xy_tube('Gold edged ocean swell_'+str(i),design[key],.15+i*.008,'gold',.025)
    for i,(px,py,rx,ry) in enumerate([(856,789,147,10),(856,823,101,9),(856,851,55,7)]):
        x=(px-626)*2.42/485;y=(613-py)*2.42/480
        ellipsoid('Sun reflection_'+str(i),(x,y,.125),(rx*2.42/485,ry*2.42/480,.018),'gold',32,8)

for badge,base in [('star_ascent','clean'),('island_sunset','sprout')]:
    for old_scene in list(bpy.data.scenes):
        if old_scene.name==badge or old_scene.name.startswith(badge+'.'):
            bpy.data.scenes.remove(old_scene)
    source=ROOT/badge/(badge+'.blend')
    with bpy.data.libraries.load(str(source),link=False) as (available,loaded):loaded.scenes=[available.scenes[0]]
    scene=loaded.scenes[0];scene.name=badge;bpy.context.window.scene=scene
    for obj in list(scene.objects):
        if not (obj.type=='MESH' and obj.name.startswith('Casing___')):bpy.data.objects.remove(obj,do_unlink=True)
    for obj in scene.objects:
        if obj.type=='MESH':
            for mat in obj.data.materials:
                if mat and mat.use_nodes:
                    for node in mat.node_tree.nodes:
                        if node.type=='TEX_IMAGE' and node.image:node.image.pack()
    mats={role:material(role) for role in PALETTE}
    if badge=='star_ascent':staircase()
    else:sunset()
    # Export front relief arrays before making the genuine mirrored back.
    arrays={};groups=[]
    for obj in list(scene.objects):
        if not obj.get('new_emblem'):continue
        obj.data.calc_loop_triangles();mesh=obj.data
        p=np.array([v.co[:] for v in mesh.vertices]);t=np.array([tri.vertices[:] for tri in mesh.loop_triangles])
        n=np.array([[mesh.corner_normals[l].vector[:] for l in tri.loops] for tri in mesh.loop_triangles])
        i=len(groups);arrays[str(i)+'_points']=p;arrays[str(i)+'_triangles']=t;arrays[str(i)+'_normals']=n
        groups.append({'name':obj.name,'role':obj['role']})
        back=obj.copy();back.data=obj.data.copy();back.name='Back_'+obj.name
        for v in back.data.vertices:v.co=(-v.co.x,v.co.y,-v.co.z-.33)
        scene.collection.objects.link(back)
    np.savez_compressed(TEMP/(badge+'_geometry.npz'),**arrays)
    (ROOT/badge/'design.json').write_text(json.dumps({'groups':groups,'palette':PALETTE,'source_shell':base},indent=2))
    ref=bpy.data.objects.new(badge+'_reference',None);ref.empty_display_type='IMAGE';ref.data=bpy.data.images.load(str(ROOT/'references'/(badge+'.png')),check_existing=True);ref.data.pack();ref.empty_display_size=6.03;ref.location=(-7,0,0);scene.collection.objects.link(ref)
    for a in bpy.context.screen.areas:
        if a.type=='VIEW_3D':
            s=a.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,0,0));s.region_3d.view_distance=9;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
    bpy.data.libraries.write(str(ROOT/badge/(badge+'.blend')),{scene},compress=True)
    print(badge,': complete working scene,',len(groups),'raised objects')
