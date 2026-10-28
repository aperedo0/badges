"""Sculpt the complete trophy badge in the connected Blender application."""
from pathlib import Path
import bpy,math,json
import numpy as np
from mathutils import Vector,Quaternion
from mathutils.geometry import tessellate_polygon,delaunay_2d_cdt
ROOT=Path('/Users/antonioperedo/Desktop/badges/emerald_trophy_20261025')
CANDIDATE=globals().get('TROPHY_CANDIDATE','candidate01')
OUT=ROOT/CANDIDATE;TEMP=Path('/tmp/emerald_trophy_20261025');TEMP.mkdir(exist_ok=True)
EMISSION={'emerald':(0,.010,.001),'emerald_light':(.010,.10,.025)} if CANDIDATE in ['candidate02','candidate03'] else {}
PALETTE={'gold':((.78,.39,.065),1,.25),'gold_edge':((.50,.22,.025),1,.34),
 'gold_vein':((.28,.10,.012),.85,.48),'field':((.001,.020,.0042),.62,.44),
 'ribbon':((.001,.055,.014),.85,.27),'emerald':((.001,.15,.025),.25,.15),
 'emerald_light':((.025,.40,.09),.20,.14),'emerald_dark':((.0003,.018,.002),.35,.19),
 'setting_shadow':((.001,.008,.001),.8,.35)}
if CANDIDATE=='candidate03':PALETTE['field']=((.0005,.026,.0022),1.,.44)
for old in list(bpy.data.scenes):
    if old.name=='emerald_trophy':bpy.data.scenes.remove(old)
source=ROOT.parent/'star_island_20261016/island_sunset/island_sunset.blend'
with bpy.data.libraries.load(str(source),link=False) as (available,loaded):loaded.scenes=[available.scenes[0]]
scene=loaded.scenes[0];scene.name='emerald_trophy';bpy.context.window.scene=scene
context=bpy.data.collections.new('Trophy complete source context');scene.collection.children.link(context)
for ob in list(scene.objects):
    if ob.type=='MESH' and ob.name.startswith('Casing___'):continue
    for c in list(ob.users_collection):c.objects.unlink(ob)
    context.objects.link(ob)
context.hide_render=True;context.hide_viewport=True
M={}
for role,(color,metal,rough) in PALETTE.items():
    m=bpy.data.materials.new('Trophy_'+role);m.use_nodes=True;m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    if role in EMISSION:
        bs.inputs['Emission Color'].default_value=(*EMISSION[role],1);bs.inputs['Emission Strength'].default_value=1
    if role.startswith('emerald'):
        bs.inputs['Coat Weight'].default_value=.35;bs.inputs['Coat Roughness'].default_value=.12
    M[role]=m

# Native mesh, bevel, and tube operations previously used for the complete coins.
helper=ROOT.parent/'emerald_archer_20261023/build_live.py'
source_text=helper.read_text()
exec(compile(source_text[source_text.index('def xy('):source_text.index('# Recessed green metal field')],str(helper),'exec'),globals())
def xy(p):return (np.asarray(p,float)-[627,590])*[2.42/490,-2.42/490]
native_tube=tube
def tube(name,p,r=.012,role='gold',sides=6):
    return native_tube(name,p,r,role,min(sides,4) if r<=.013 else sides)
leaf_text=source_text[source_text.index('def leaf('):source_text.index('# The four sprays')]
leaf_text=leaf_text.replace('N=12','N=10').replace('for t in [.28,.48,.68]','for t in [.32,.61]')
exec(compile(leaf_text,str(helper),'exec'),globals())

def orient(v,faces):
    v=np.asarray(v);p=faces[0]
    nz=np.cross(v[p[1]]-v[p[0]],v[p[2]]-v[p[0]])[2]
    return [tuple(reversed(f)) for f in faces] if nz<0 else faces

def surface_strip(name,left,right,zfun,role='gold',steps=9,closed=True):
    left=np.asarray(left);right=np.asarray(right);n=len(left);v=[];f=[]
    for i,(a,b) in enumerate(zip(left,right)):
        for j in range(steps):
            s=j/(steps-1);p=a*(1-s)+b*s
            v.append([*xy(p),zfun(i/(n-1),s,p)])
    for i in range(n-1):
        for j in range(steps-1):
            a=i*steps+j;f.append((a,a+steps,a+steps+1,a+1))
    f=orient(v,f)
    if closed:
        boundary=list(range(steps))+[i*steps+steps-1 for i in range(1,n)]+list(range(n*steps-2,(n-1)*steps-1,-1))+[i*steps for i in range(n-2,0,-1)]
        # A low closed back has the same planar contour and stays inside the shell.
        base=len(v)
        v += [[v[i][0],v[i][1],min(.075,v[i][2]-.025)] for i in boundary]
        f += [(boundary[i],base+i,base+(i+1)%len(boundary),boundary[(i+1)%len(boundary)]) for i in range(len(boundary))]
    return mesh(name,v,f,role,True)

def swept_band(name,path,width,z=.18,rise=.055,role='gold',border=False):
    path=np.asarray(path,float);tangent=np.gradient(path,axis=0)
    tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-8)
    side=np.c_[-tangent[:,1],tangent[:,0]]
    w=np.array([width(t) if callable(width) else width for t in np.linspace(0,1,len(path))])
    a=path-side*w[:,None];b=path+side*w[:,None]
    def depth(t,s,p):return (z(t,s,p) if callable(z) else z)+rise*math.sin(math.pi*s)**.7
    ob=surface_strip(name,a,b,depth,role,5)
    if border:
        for label,edge in [('left',a),('right',b)]:
            p=[[ *xy(q),depth(i/(len(path)-1),0 if label=='left' else 1,q)+.004] for i,q in enumerate(edge)]
            tube(name+' '+label+' gold binding',p,.008,'gold',6)
    return ob

def ellipse_lathe(name,cx,profile,zcenter=.13,depth_ratio=.28,role='gold',segments=48):
    # Profiles are radius in reference pixels and height in reference pixels.
    v=[];f=[];scale=2.42/490
    for r,y in profile:
        for a in np.arange(segments)*math.tau/segments:
            v.append([*xy([cx+r*math.cos(a),y]),zcenter+r*scale*depth_ratio*math.sin(a)])
    for j in range(len(profile)-1):
        for i in range(segments):
            a=j*segments+i;b=j*segments+(i+1)%segments
            f.append((a,b,b+segments,a+segments))
    # Winding follows the profile's vertical direction.
    if profile[-1][1]<profile[0][1]:f=[q[::-1] for q in f]
    f += [tuple(range(segments-1,-1,-1)),tuple((len(profile)-1)*segments+i for i in range(segments))]
    return mesh(name,v,f,role,True)

def sphere(name,p,r,z=.18,role='gold',segments=8,rings=4):
    x,y=xy(p);v=[[x,y,z+r]]
    for j in range(1,rings):
        a=math.pi*j/rings
        for k in range(segments):
            b=math.tau*k/segments;v.append([x+r*math.sin(a)*math.cos(b),y+r*math.sin(a)*math.sin(b),z+r*math.cos(a)])
    bottom=len(v);v.append([x,y,z-r]);f=[(0,1+i,1+(i+1)%segments) for i in range(segments)]
    for j in range(rings-2):
        a=1+j*segments;b=a+segments
        f += [(a+i,b+i,b+(i+1)%segments,a+(i+1)%segments) for i in range(segments)]
    a=1+(rings-2)*segments;f += [(a+i,bottom,a+(i+1)%segments) for i in range(segments)]
    return mesh(name,v,f,role,True)

# A complete recessed field. Its only texture is subdued intrinsic mineral grain.
n=128;v=[[0,0,.051]]+[[2.445*math.cos(a),2.445*math.sin(a),.044] for a in np.arange(n)*math.tau/n]
mesh('Recessed deep emerald field',v,[(0,1+i,1+(i+1)%n) for i in range(n)],'field',True)

# Large laurel sprays, including the fine joining branches and small gold berries.
lower_path=chain([[[498,962],[462,903],[414,875],[371,831]],[[371,831],[286,754],[224,654],[230,501]],[[230,501],[231,463],[227,428],[224,411]]],23)
lower_leaves=[((230,525),(223,402),22,-2),((235,578),(175,468),24,-7),
 ((244,606),(277,515),24,5),((270,672),(157,555),27,-5),((304,729),(169,656),28,-6),
 ((319,751),(294,594),29,-1),((358,807),(350,651),29,1),((372,826),(201,754),30,-8),
 ((404,864),(252,832),23,-5),((412,852),(392,708),24,3)]
top_path=chain([[[383,336],[424,284],[477,225],[552,182]]],35)
top_leaves=[((478,235),(555,178),22,-4),((477,254),(574,268),19,5),
 ((424,297),(460,212),19,-2),((429,304),(493,310),15,4)]
for side in [0,1]:
    flip=lambda p:np.asarray(p,float)*([-1,1] if side else [1,1])+([1254,0] if side else [0,0])
    for title,path,specs in [('Lower laurel',lower_path,lower_leaves),('Upper laurel',top_path,top_leaves)]:
        q=flip(path);line(title+' main stem '+str(side),q,.102,.010)
        for i,(a,b,w,bend) in enumerate(specs):
            aa,bb=flip(a),flip(b)
            leaf(title+' leaf '+str(side)+' '+str(i),aa,bb,w,-bend if side else bend,.102,.061)
            near=q[np.argmin(np.linalg.norm(q-aa,axis=1))]
            if np.linalg.norm(near-aa)>2:line(title+' leaf stalk '+str(i),[near,aa],.105,.0055)
    for i,(center,stem) in enumerate([((407,273),(395,314)),((472,282),(443,287)),
       ((244,532),(231,550)),((216,580),(238,606)),((256,626),(254,651)),
       ((234,665),(271,699)),((308,730),(327,761)),((273,747),(315,784)),((365,783),(367,816))]):
        p,s=flip(center),flip(stem);line('Laurel berry stem',[p,s],.11,.0055)
        sphere('Gold laurel berry '+str(side)+' '+str(i),p,.026 if i<2 else .023,.12)

# Torch shafts and collars sit behind the front laurel leaves.
for side,cx in enumerate([319,935]):
    ellipse_lathe('Torch fluted shaft '+str(side),cx,[(17,476),(17,485),(15,490),(15,711),(20,718)],.14,.70,segments=24)
    for k in [-2,-1,0,1,2]:
        px=cx+k*6;zz=.14+.052*math.sqrt(max(0,1-(k/3)**2))
        line('Torch long raised flute '+str(side)+' '+str(k),[[px,486],[px,715]],zz,.006,'gold_edge',6)
    ellipse_lathe('Torch shaped capital '+str(side),cx,[(21,478),(25,476),(26,470),(22,466),(22,459),(28,454),(27,448),(41,421),(49,414),(50,408),(55,405),(55,396),(51,392)],.14,.34,segments=28)
    for y,r in [(399,54),(413,47),(456,27),(475,25)]:
        ellipse_lathe('Torch turned collar '+str(side)+' '+str(y),cx,[(r-2,y-3),(r,y-1),(r,y+3),(r-2,y+5)],.14,.45,segments=24)
    for i in range(7):
        x=cx+(i-3)*9;w=6 if i in [0,6] else 7
        leaf('Torch capital petal '+str(side)+' '+str(i),(cx+(i-3)*5,450),(x,419),w,0,.207,.025,False)
    # Six flowing metal tongues. Their curves and central creases are physical relief.
    flames=[([[313,389],[274,354],[341,299],[332,235]],23,.15),
            ([[317,388],[299,352],[364,313],[344,267]],18,.19),
            ([[303,390],[264,358],[280,331],[296,284]],17,.13),
            ([[296,390],[252,374],[251,345],[263,323]],13,.12),
            ([[329,389],[369,360],[373,335],[372,306]],16,.14),
            ([[329,387],[349,362],[336,332],[340,304]],13,.22)]
    for i,(controls,width,z) in enumerate(flames):
        p=bez(controls,21)
        if side:p=p*[-1,1]+[1254,0]
        swept_band('Flowing gold flame '+str(side)+' '+str(i),p,lambda t,w=width:w*math.sin(math.pi*t)**.72,z,.055,'gold')

# The trophy foot and stem have closed elliptical sections and turned shoulders.
pedestal_profile=[(151,997),(153,994),(153,988),(148,986),(146,968),(140,961),
 (127,958),(126,951),(120,948),(108,875),(108,867),(113,865),(113,856),
 (109,852),(105,850),(106,843),(100,837),(91,834),(91,824),(80,821),(80,812),(68,809)]
ellipse_lathe('Trophy stepped pedestal and plinth',627,pedestal_profile,.14,.24,segments=40)
stem_profile=[(66,805),(62,799),(45,790),(29,770),(19,747),(17,721),(27,716),(39,714),(44,709),(43,702),(36,698),(34,687),(25,677)]
ellipse_lathe('Trophy curved stem and collars',627,stem_profile,.15,.40,segments=32)

# A broad curved cup rather than a flat emblem. Horizontal sections narrow into a rounded heel.
cup_edge=bez([[488,408],[483,562],[514,654],[627,681]],33)
width_by_y=lambda y:np.interp(y,cup_edge[:,1],627-cup_edge[:,0])
def cup_z(p):
    x,y=p;w=max(float(width_by_y(y)),1)
    return .13+.235*max(0,1-((x-627)/w)**2)**.60
left=cup_edge[:-1];right=np.c_[1254-left[:,0],left[:,1]]
surface_strip('Trophy rounded cup',left,right,lambda t,s,p:cup_z(p),'gold',19)

# Three raised elliptical lip bands wrap the mouth of the cup.
for j,(top,bottom,z) in enumerate([(366,381,.22),(379,399,.245),(398,411,.23)]):
    a=bez([[475,top+9],[536,top-7],[716,top-7],[779,top+9]],33)
    b=bez([[479,bottom+5],[538,bottom-1],[716,bottom-1],[775,bottom+5]],33)
    surface_strip('Trophy mouth band '+str(j),a,b,lambda t,s,p,z=z:z+.030*math.sin(math.pi*s),'gold',5)
    line('Trophy mouth lip '+str(j),a,z+.010,.008)

# The two curled handles have solid, rounded metal cross sections.
handle=chain([[[439,426],[450,447],[477,423],[455,389]],
 [[455,389],[429,364],[402,380],[392,405]],
 [[392,405],[365,457],[410,541],[450,575]],
 [[450,575],[479,602],[504,624],[488,640]],
 [[488,640],[477,652],[462,637],[478,629]]],15)
for side in [0,1]:
    p=handle.copy()
    if side:p=p*[-1,1]+[1254,0]
    swept_band('Trophy curled handle '+str(side),p,lambda t:12.5*(1-.45*t)+2*math.sin(t*math.pi),.15,.07,'gold')
    sphere('Handle cup joining stud '+str(side),[783 if side else 471,451],.038,.24)

# Fine raised acanthus branches follow the cup's curved surface.
def cup_line(name,p,r=.006,role='gold_edge'):
    tube(name,[[*xy(q),cup_z(q)+.012] for q in p],r,role,6)
for side in [0,1]:
    flip=lambda p:np.asarray(p)*([-1,1] if side else [1,1])+([1254,0] if side else [0,0])
    p=chain([[[627,663],[568,598],[565,541],[556,492]],[[556,492],[550,453],[538,437],[525,433]]],23)
    cup_line('Trophy acanthus main stem '+str(side),flip(p),.0065)
    scrolls=[[[556,495],[541,463],[546,438],[575,433]],[[553,480],[565,442],[572,430],[583,429]],
       [[568,547],[548,508],[535,491],[521,498]],[[578,579],[564,555],[580,543],[570,511]],
       [[590,607],[574,587],[592,575],[585,555]],[[611,641],[586,618],[606,606],[597,591]],
       [[548,468],[531,446],[526,462],[515,460]]]
    for i,c in enumerate(scrolls):
        q=flip(bez(c,19));cup_line('Trophy curled acanthus '+str(side)+' '+str(i),q,.006)
    for i,(a,b,w) in enumerate([((546,458),(519,429),6),((550,444),(546,417),5),((565,438),(578,423),5),
       ((565,553),(575,524),5),((578,590),(587,565),5),((594,621),(602,596),4)]):
        a,b=flip(np.array(a)),flip(np.array(b));p=bez([a,a+(b-a)*.25+[(-7 if side else 7),0],a+(b-a)*.75,b],15)
        swept_band('Trophy acanthus leaf '+str(side)+' '+str(i),p,lambda t,w=w:w*math.sin(math.pi*t)**.8,
                   lambda t,s,q:cup_z(q)+.010,.012,'gold',False)
for i,controls in enumerate([[[627,472],[623,446],[616,431],[607,429]],
 [[627,472],[629,446],[638,431],[649,433]],[[627,472],[619,437],[625,424],[627,411]],
 [[627,472],[635,439],[628,426],[627,411]]]):
    cup_line('Trophy center crest '+str(i),bez(controls,20),.007,'gold')

# The lower ribbon has real rolled folds, with a separate green reverse.
for side in [0,1]:
    flip=lambda p:np.asarray(p)*([-1,1] if side else [1,1])+([1254,0] if side else [0,0])
    tail=chain([[[412,867],[365,863],[326,889],[286,898]],[[286,898],[330,922],[346,917],[341,969]],
                [[341,969],[365,943],[403,949],[445,927]]],17)
    tail=flip(tail)
    # A pointed cut is modeled into the broad loose ribbon end.
    tail_outline=chain([[[394,850],[361,860],[322,889],[286,898]],[[286,898],[307,914],[333,921],[337,922]],
      [[337,922],[329,943],[329,958],[341,970]],[[341,970],[364,946],[403,949],[445,927]],
      [[445,927],[428,901],[409,879],[394,850]]],12)[:-1]
    if CANDIDATE=='candidate01':solid('Ribbon loose tail '+str(side),flip(tail_outline),.115,.07,.006,'ribbon')
    else:
        def inside(q,poly):
            x,y=q;result=False
            for a,b in zip(poly,np.roll(poly,-1,axis=0)):
                if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:result=not result
            return result
        points=tail_outline.tolist()
        for x in np.arange(tail_outline[:,0].min()+5,tail_outline[:,0].max(),10):
            for y in np.arange(tail_outline[:,1].min()+5,tail_outline[:,1].max(),10):
                if inside((x,y),tail_outline):points.append([x,y])
        result=delaunay_2d_cdt([Vector(q) for q in points],[],[list(range(len(tail_outline)))],1,1e-5,False)
        q=np.array(result[0]);faces=[tuple(p) for p in result[2]]
        def fold_z(p):
            x,y=p;return max(.075,.11+.10*math.sin(((x-280)+(y-850)*.45)*math.pi/140)+.025*math.sin((y-850)/27))
        v=[[*xy(flip(p)),fold_z(p)] for p in q]
        mesh('Ribbon curved loose tail '+str(side),v,orient(v,faces),'ribbon',True)
        tube('Ribbon tail gold binding '+str(side),[[*xy(flip(p)),fold_z(p)+.003] for p in np.vstack([tail_outline,tail_outline[:1]])],.006,'gold_edge',6)
    path=chain([[[566,833],[515,827],[475,796],[437,805]],[[437,805],[388,810],[377,829],[389,861]],
       [[389,861],[400,888],[404,909],[437,899]]],24)
    path=flip(path)
    def ribbon_z(t,s,p):return .22+.08*math.sin(t*math.pi)+.033*math.cos(t*math.pi*3)*(2*s-1)
    swept_band('Folded emerald ribbon '+str(side),path,lambda t:31*(1-.55*t**4),ribbon_z,.022,'ribbon',True)

# Faceted emeralds in deep beveled gold diamond settings.
def jewel(name,cx,cy,rx,ry,base=.25):
    c=np.array([cx,cy]);outline=np.array([[cx,cy-ry],[cx+rx,cy],[cx,cy+ry],[cx-rx,cy]])
    n=4;v=[]
    for scale,z in [(1,base),(.92,base+.042),(.78,base+.070),(.68,base+.035)]:
        v += [[*xy(p),z] for p in c+(outline-c)*scale]
    f=[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for k in range(3) for i in range(n)]
    mesh(name+' bevelled gold setting',v,[q[::-1] for q in f],'gold')
    solid(name+' dark stone seat',c+(outline-c)*.675,base+.035,base-.01,.002,'setting_shadow')
    outer=c+(outline-c)*.64;table=c+(outline-c)*.29
    # An eight sided table splits each broad crown into clean triangle facets.
    outer8=np.array([outer[i]*(1-t)+outer[(i+1)%4]*t for i in range(4) for t in [0,.5]])
    inner8=c+(outer8-c)*.43
    v=[[*xy(p),base+.043] for p in outer8]+[[*xy(p),base+.112] for p in inner8]+[[*xy(c+[0,-ry*.10]),base+.140]]
    f=[(i,(i+1)%8,8+(i+1)%8,8+i) for i in range(8)]+[(8+i,8+(i+1)%8,16) for i in range(8)]
    ob=mesh(name+' emerald crown facets',v,[q[::-1] for q in f],'emerald')
    ob.data.materials.append(M['emerald_light']);ob.data.materials.append(M['emerald_dark'])
    for i,p in enumerate(ob.data.polygons):p.material_index=[1,0,0,2,2,0,1,1][i%8]
jewel('Upper emerald',627,206,65,87,.22)
jewel('Pedestal emerald',627,907,40,51,.31)

# Small matching laurel engraving on the front of the pedestal.
for side in [0,1]:
    flip=lambda p:np.asarray(p)*([-1,1] if side else [1,1])+([1254,0] if side else [0,0])
    p=bez([[514,944],[540,933],[565,909],[580,883]],23)
    line('Pedestal laurel stem '+str(side),flip(p),.293,.005)
    for i,(a,b,w) in enumerate([((536,932),(528,911),6),((544,923),(544,899),6),((554,912),(560,891),6),
        ((542,928),(565,932),6),((555,915),(580,918),6),((568,900),(580,885),5)]):
        leaf('Pedestal laurel leaf '+str(side)+' '+str(i),flip(a),flip(b),w,0,.295,.020,False)

# Attach the field's low contrast intrinsic texture in Blender.
for role in ['field']:
    mat=M[role];nt=mat.node_tree;uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='CoinReliefUV'
    for suffix,socket,space in [('color','Base Color','sRGB'),('roughness','Roughness','Non-Color')]:
        path=OUT/'textures'/(role+'_'+suffix+'.png')
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(path),check_existing=False)
        tex.image.colorspace_settings.name=space;tex.image.pack()
        nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],nt.nodes.get('Principled BSDF').inputs[socket])

# Export actual Blender triangle normals, combine materials later, and build a full sculpted back.
arrays={};groups=[]
for ob in objects:
    me=ob.data;me.calc_loop_triangles()
    p=np.array([v.co[:] for v in me.vertices],float)
    for mi,mat in enumerate(me.materials):
        tris=[t for t in me.loop_triangles if t.material_index==mi]
        tris=[t for t in tris if np.linalg.norm(np.cross(p[t.vertices[1]]-p[t.vertices[0]],p[t.vertices[2]]-p[t.vertices[0]]))>1e-10]
        if not tris:continue
        role=next(r for r,m in M.items() if mat==m);i=len(groups)
        arrays[str(i)+'_points']=p;arrays[str(i)+'_triangles']=np.array([t.vertices[:] for t in tris],np.int32)
        arrays[str(i)+'_normals']=np.array([[me.corner_normals[l].vector[:] for l in t.loops] for t in tris],float)
        groups.append({'name':ob.name,'role':role})
    back=ob.copy();back.data=ob.data.copy();back.name='Back '+ob.name
    for v in back.data.vertices:v.co=(-v.co.x,v.co.y,-v.co.z-.33)
    if me.has_custom_normals:back.data.normals_split_custom_set([(-v.vector.x,v.vector.y,-v.vector.z) for v in me.corner_normals])
    scene.collection.objects.link(back)
np.savez_compressed(TEMP/(CANDIDATE+'_geometry.npz'),**arrays)
(OUT/'design.json').write_text(json.dumps({'groups':groups,'palette':PALETTE,'emission':EMISSION,'source_shell':'sprout','reference_center':[627,590],'reference_inner_radius':490},indent=2))
reference=bpy.data.objects.new('Trophy owner reference',None);reference.empty_display_type='IMAGE'
reference.data=bpy.data.images.load(str(ROOT/'reference.png'),check_existing=True);reference.data.pack()
reference.empty_display_size=6.2;reference.location=(-7,0,0);scene.collection.objects.link(reference)
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        s=a.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,0,0))
        s.region_3d.view_distance=8.8;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
bpy.data.libraries.write(str(OUT/'emerald_trophy.blend'),{scene},compress=True)
print('Complete Emerald Trophy:',len(objects),'front objects,',len(groups),'material groups')
