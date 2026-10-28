"""Build a complete sculpted Emerald Archer in the live Blender application."""
from pathlib import Path
import bpy, math, json, zipfile
import numpy as np
from mathutils import Vector, Quaternion
from mathutils.geometry import tessellate_polygon

ROOT=Path('/Users/antonioperedo/Desktop/badges/emerald_archer_20261023')
OUT=ROOT/'candidate01';TEMP=Path('/tmp/emerald_archer_20261023');TEMP.mkdir(exist_ok=True)
SOURCE=ROOT.parent/'botanical_match_20261014/sprout/mobile/sprout_badge_mobile.usdz'
PALETTE={
 'gold':((.73,.365,.065),1,.265),
 'gold_edge':((.40,.175,.028),1,.44),
 'gold_vein':((.22,.080,.014),.65,.55),
 'field':((.004,.075,.025),.72,.32),
 'emerald':((.0015,.19,.075),.50,.14),
 'emerald_light':((.014,.36,.18),.45,.14),
 'emerald_dark':((.001,.042,.019),.65,.19),
 'setting_shadow':((.008,.023,.012),.8,.30)}

# Keep the complete approved source available while constructing the new face.
old=bpy.context.scene
for s in list(bpy.data.scenes):
    if s.name=='emerald_archer':bpy.data.scenes.remove(s)
source_scene=ROOT.parent/'star_island_20261016/island_sunset/island_sunset.blend'
with bpy.data.libraries.load(str(source_scene),link=False) as (available,loaded):loaded.scenes=[available.scenes[0]]
scene=loaded.scenes[0];scene.name='emerald_archer';bpy.context.window.scene=scene
context=bpy.data.collections.new('Complete previous coin working context');scene.collection.children.link(context)
for ob in list(scene.objects):
    if ob.type=='MESH' and ob.name.startswith('Casing___'):continue
    for c in list(ob.users_collection):c.objects.unlink(ob)
    context.objects.link(ob)
context.hide_viewport=True;context.hide_render=True

M={}
for role,(color,metal,rough) in PALETTE.items():
    mat=bpy.data.materials.new('Archer_'+role);mat.use_nodes=True;mat.diffuse_color=(*color,1)
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    if role.startswith('emerald'):
        bs.inputs['Coat Weight'].default_value=.35;bs.inputs['Coat Roughness'].default_value=.12
    M[role]=mat

def xy(p):return (np.asarray(p,float)-[627,566])*[2.42/458,-2.42/458]
def bez(p,n=25):
    p=np.asarray(p,float);t=np.linspace(0,1,n)[:,None]
    if len(p)==4:return (1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3]
    raise ValueError('Four control points required')
def chain(curves,n=20):return np.vstack([bez(p,n)[:-1] for p in curves]+[np.asarray(curves[-1][-1:])])
objects=[]
def mesh(name,v,f,role='gold',smooth=False):
    v=np.asarray(v,float);f=[tuple(q) for q in f]
    me=bpy.data.meshes.new(name);me.from_pydata(v.tolist(),[],f);me.update()
    ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);me.materials.append(M[role])
    ob['role']=role;ob['new_emblem']=True
    for p in me.polygons:p.use_smooth=smooth
    uv=me.uv_layers.new(name='CoinReliefUV')
    for li,l in enumerate(me.loops):
        c=me.vertices[l.vertex_index].co;uv.data[li].uv=((c.x+3.015)/6.03,(c.y+3.015)/6.03)
    objects.append(ob);return ob

def tube(name,p,r=.012,role='gold',sides=6):
    p=np.asarray(p,float);verts=[]
    if r<=.013:
        keep=[0]
        for i in range(1,len(p)-1):
            if np.linalg.norm(p[i]-p[keep[-1]])>=.045:keep.append(i)
        keep.append(len(p)-1);p=p[keep]
    for i,q in enumerate(p):
        axis=p[min(len(p)-1,i+1)]-p[max(0,i-1)];axis/=max(np.linalg.norm(axis),1e-10)
        a=np.cross(axis,[0,0,1])
        if np.linalg.norm(a)<.01:a=np.cross(axis,[0,1,0])
        a/=np.linalg.norm(a);b=np.cross(axis,a)
        for theta in np.arange(sides)*math.tau/sides:verts.append(q+r*(a*math.cos(theta)+b*math.sin(theta)))
    faces=[]
    for i in range(len(p)-1):
        for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
    faces += [tuple(range(sides-1,-1,-1)),tuple((len(p)-1)*sides+j for j in range(sides))]
    return mesh(name,verts,faces,role,True)
def line(name,p,z=.15,r=.012,role='gold',sides=6):
    return tube(name,np.c_[xy(p),np.full(len(p),z)],r,role,sides)
def curve(name,p,z=.15,r=.012,role='gold',n=25):return line(name,bez(p,n),z,r,role)

def solid(name,p,z=.20,base=.08,bevel=.013,role='gold'):
    p=xy(p)
    if np.cross(p,np.roll(p,-1,axis=0)).sum()<0:p=p[::-1]
    n=len(p);v=np.vstack([np.c_[p,np.full(n,z)],np.c_[p,np.full(n,base)]])
    # Native tessellation handles the concave notch in an arrow feather.
    poly=[Vector((*q,z)) for q in p];lookup={tuple(q):i for i,q in enumerate(poly)}
    tri=tessellate_polygon([poly]);f=[tuple(q if isinstance(q,int) else lookup[tuple(q)] for q in t) for t in tri]
    f += [tuple(i+n for i in t[::-1]) for t in f.copy()]
    f += [(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
    ob=mesh(name,v,f,role)
    if bevel:
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
        mod=ob.modifiers.new('Jeweller bevel','BEVEL');mod.width=bevel;mod.segments=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=ob.modifiers.new('Weighted face normals','WEIGHTED_NORMAL');mod.keep_sharp=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
        uv=ob.data.uv_layers['CoinReliefUV']
        for li,l in enumerate(ob.data.loops):
            c=ob.data.vertices[l.vertex_index].co;uv.data[li].uv=((c.x+3.015)/6.03,(c.y+3.015)/6.03)
    return ob

# Recessed green metal field with a very shallow radial crown.
verts=[[0,0,.056]];faces=[];N=96
for radius in [.80,1.60,2.445]:
    for a in np.arange(N)*math.tau/N:verts.append([radius*math.cos(a),radius*math.sin(a),.044+.012*(1-(radius/2.445)**2)])
faces += [(0,1+i,1+(i+1)%N) for i in range(N)]
for k in range(2):
    a=1+k*N;b=a+N
    faces += [(a+i,b+i,b+(i+1)%N,a+(i+1)%N) for i in range(N)]
mesh('Recessed emerald green field',verts,faces,'field',True)

# Fine intrinsic metal grain, without broad light bands or painted highlights.
field=M['field'];nt=field.node_tree;bs=nt.nodes.get('Principled BSDF')
for suffix,socket,space in [('color','Base Color','sRGB'),('roughness','Roughness','Non-Color')]:
    path=OUT/'textures'/('field_'+suffix+'.png')
    tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(path),check_existing=False)
    tex.image.colorspace_settings.name=space;tex.image.pack()
    uv=nt.nodes.get('Archer UV')
    if uv is None:uv=nt.nodes.new('ShaderNodeUVMap');uv.name='Archer UV';uv.uv_map='CoinReliefUV'
    nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs[socket])

# Laurel leaves have raised center creases, curved shoulders, and gold veins.
def leaf(name,a,b,width,bend=0,z=.115,rise=.075,veins=True):
    a=np.array(a,float);b=np.array(b,float);axis=b-a;L=np.linalg.norm(axis);perp=np.array([-axis[1],axis[0]])/L
    def at(t,s):
        w=width*math.sin(math.pi*t)**.82
        p=a+axis*t+perp*(bend*math.sin(math.pi*t)+s*w)
        zz=z+rise*math.sin(math.pi*t)**.55*(1-abs(s)**.72)
        return [*xy(p),zz]
    strips=[-1,-.78,-.40,0,.40,.78,1];K=len(strips);N=12
    v=[at(0,0)]
    for i in range(1,N):
        for s in strips:v.append(at(i/N,s))
    end=len(v);v.append(at(1,0));f=[]
    f += [(0,1+j,1+j+1) for j in range(K-1)]
    for i in range(N-2):
        start=1+i*K;nextrow=start+K
        f += [(start+j,nextrow+j,nextrow+j+1,start+j+1) for j in range(K-1)]
    f += [(1+(N-2)*K+j,end,1+(N-2)*K+j+1) for j in range(K-1)]
    f=[q[::-1] for q in f]
    boundary=[0]+[1+i*K for i in range(N-1)]+[end]+[1+i*K+K-1 for i in range(N-2,-1,-1)]
    base=len(v);center=(a+b)/2;v.append([*xy(center),z-.025])
    f += [(boundary[i],base,boundary[(i+1)%len(boundary)]) for i in range(len(boundary))]
    ob=mesh(name,v,f,'gold',True)
    # A split along the crest gives the paired polished leaf faces a crisp seam.
    crest={0,end}|{1+i*K+3 for i in range(N-1)}
    for e in ob.data.edges:
        if all(i in crest for i in e.vertices):e.use_edge_sharp=True
    if veins:
        for t in [.28,.48,.68]:
            for side in [-1,1]:
                points=[]
                for u in np.linspace(0,1,5):
                    q=np.array(at(t+.20*u,side*.91*u));q[2]+=.0015;points.append(q)
                tube(name+' engraved vein',points,.0034,'gold_vein',4)
        points=[np.array(at(t,0))+[0,0,.001] for t in np.linspace(.05,.96,13)]
        tube(name+' center rib',points,.0045,'gold_edge',4)
    return ob

# The four sprays are traced separately, preserving the gaps around the arrow.
sprays=[
 ('Upper left',[[224,553],[220,410],[334,247],[482,189]],[
 ((211,541),(204,461),13,-4),((232,479),(240,360),20,0),((237,488),(326,412),20,-6),
 ((268,405),(303,274),22,-4),((272,401),(373,342),21,-7),((318,322),(382,210),22,-4),
 ((325,324),(445,286),22,-6),((387,258),(508,172),23,-5),((390,258),(498,234),21,-9)]),
 ('Upper right',[[1030,553],[1039,413],[923,247],[772,190]],[
 ((1040,541),(1049,462),13,4),((1019,478),(1013,360),20,0),((1015,489),(934,413),20,6),
 ((988,404),(953,274),22,4),((984,402),(885,342),21,7),((937,322),(875,210),22,4),
 ((930,324),(823,286),22,6),((870,257),(750,172),23,5),((865,258),(775,234),21,9)]),
 ('Lower left',[[574,975],[404,902],[260,810],[222,620]],[
 ((261,741),(204,650),18,4),((269,774),(227,638),19,4),((310,810),(225,743),21,-5),
 ((325,823),(310,693),25,1),((390,882),(368,797),20,-1),((392,881),(277,828),20,-3),
 ((454,932),(436,830),22,-1),((455,932),(336,892),20,-3),((525,955),(499,888),16,-2),
 ((527,958),(415,943),18,-7)]),
 ('Lower right',[[684,975],[852,903],[998,806],[1031,620]],[
 ((999,742),(1033,641),18,-4),((996,774),(1050,651),19,-4),((932,820),(1026,742),22,5),
 ((930,819),(942,692),24,-1),((862,886),(864,806),21,2),((865,885),(979,830),20,3),
 ((787,930),(801,885),19,2),((790,931),(915,892),20,3),((732,960),(835,943),18,7)])]
for title,path,leaves in sprays:
    line(title+' curved gold stem',bez(path,48),.115,.0095)
    for i,(a,b,w,bend) in enumerate(leaves):leaf(title+' leaf '+str(i+1),a,b,w,bend)

# Three small faceted buds stand on their own fine stems.
def bud(name,center,rx,ry):
    cx,cy=center;p=[[cx,cy-ry],[cx+rx,cy],[cx,cy+ry],[cx-rx,cy]]
    v=[[*q,.145] for q in xy(p)]+[[*xy([cx,cy]),.22]]
    mesh(name,v,[(4,(i+1)%4,i) for i in range(4)])
curve('Upper left bud stem',[[354,356],[364,348],[371,346],[382,353]],.12,.007)
bud('Upper left pointed bud',(386,356),22,11)
curve('Lower left bud stem',[[352,840],[334,809],[343,784],[365,761]],.12,.008)
bud('Lower left pointed bud',(365,762),18,23)
curve('Lower right bud stem',[[892,865],[907,840],[899,821],[899,804]],.12,.008)
bud('Lower right pointed bud',(899,802),12,25)

# Two swept bow limbs. The cross section is modeled, including the feather cuts.
outer=chain([[[636,209],[654,271],[704,274],[767,316]],[[767,316],[829,357],[856,430],[875,474]]],33)
inner=chain([[[632,226],[645,285],[688,319],[718,343]],[[718,343],[764,384],[785,441],[760,475]]],33)
def limb(name,flip=False):
    v=[];f=[];K=9;N=len(outer)
    for i,(a,b) in enumerate(zip(inner,outer)):
        t=i/(N-1)
        for j in range(K):
            s=j/(K-1);p=a*(1-s)+b*s
            if flip:p=p*[1,-1]+[0,1138]
            crown=math.sin(math.pi*s)**.65
            zz=.142+.095*crown
            # Sweeping repeated feather grooves are actual shallow recesses.
            v.append([*xy(p),zz])
    for i in range(N-1):
        for j in range(K-1):
            a=i*K+j;f.append((a,a+K,a+K+1,a+1))
    border=list(range(K))+[i*K+K-1 for i in range(1,N)]+list(range((N-1)*K+K-2,(N-1)*K-1,-1))+[i*K for i in range(N-2,0,-1)]
    n=len(v)
    for i in border:v.append([v[i][0],v[i][1],.09])
    f += [(border[i],n+i,n+(i+1)%len(border),border[(i+1)%len(border)]) for i in range(len(border))]
    if flip:f=[q[::-1] for q in f]
    mesh(name,v,f,'gold',True)
    for label,points in [('outside',outer),('inside',inner)]:
        p=points.copy()
        if flip:p=p*[1,-1]+[0,1138]
        line(name+' '+label+' bead',p,.154,.0085,'gold_edge')
    # The long feather rachis divides the carved shoulder into overlapping panels.
    p=inner*.34+outer*.66
    if flip:p=p*[1,-1]+[0,1138]
    line(name+' sweeping central ridge',p,.235,.0085,'gold')
    for cut in np.arange(.29,.88,.078):
        points=[]
        for s in np.linspace(.04,.96,13):
            t=cut+.105*s-.035*s*s
            a=np.array([np.interp(t,np.linspace(0,1,N),inner[:,k]) for k in range(2)])
            b=np.array([np.interp(t,np.linspace(0,1,N),outer[:,k]) for k in range(2)])
            q=a*(1-s)+b*s
            if flip:q=q*[1,-1]+[0,1138]
            z=.142+.095*math.sin(math.pi*s)**.65+.001
            points.append([*xy(q),z])
        tube(name+' swept feather engraving',points,.0042,'gold_vein',4)
limb('Upper carved recurve bow limb')
limb('Lower carved recurve bow limb',True)

# Sculpted bridges between the limbs and central setting.
for flip in [False,True]:
    p=chain([[[762,475],[790,482],[788,509],[775,529]],[[775,529],[767,541],[749,550],[739,557]],[[739,557],[770,565],[814,541],[838,513]],[[838,513],[832,494],[851,485],[873,475]]],14)
    if flip:p=p*[1,-1]+[0,1138]
    solid(('Lower' if flip else 'Upper')+' sculpted grip shoulder',p,.205,.09,.012)

# Thin gold drawstring and vertical construction line, behind the arrow.
line('Upper diagonal taut bowstring',[[601,214],[337,564]],.146,.010)
line('Lower diagonal taut bowstring',[[337,576],[600,904]],.146,.010)
line('Fine vertical gold sight line',[[627,250],[627,892]],.095,.0035,'gold_edge',4)
line('Polished horizontal arrow shaft',[[251,570],[944,570]],.260,.040)
# A lower shoulder under the shaft gives its cylindrical edge a real shadow.
line('Arrow shaft lower warm edge',[[259,576],[938,576]],.237,.012,'gold_edge')

# Paired diagonal feather barbs, with real open cuts between each plate.
for i in range(6):
    x=247+i*28
    top=[[x,513],[x+24,516],[x+81,559],[x+49,559]]
    solid('Upper arrow feather '+str(i+1),top,.284,.17,.007)
    lower=[[x+49,582],[x+81,582],[x+24,626],[x,629]]
    solid('Lower arrow feather '+str(i+1),lower,.284,.17,.007)
    line('Upper feather fine cut '+str(i+1),[[x+4,516],[x+53,557]],.289,.0038,'gold_edge',4)
    line('Lower feather fine cut '+str(i+1),[[x+53,584],[x+4,625]],.289,.0038,'gold_edge',4)

# Arrow collars are lathed rings, rather than painted bands.
def collar(name,cx,cy,r=.062,width=.042):
    c=xy([cx,cy]);verts=[];faces=[];N=20
    for x,rr in [(-width*.5,r*.82),(-width*.34,r),(width*.34,r),(width*.5,r*.82)]:
        for t in np.arange(N)*math.tau/N:verts.append([c[0]+x,c[1]+rr*math.cos(t),.260+rr*math.sin(t)])
    for i in range(3):
        for j in range(N):faces.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
    mesh(name,verts,faces,'gold',True)
for i,x in enumerate([443,735,898,918]):collar('Turned gold arrow collar '+str(i+1),x,570,.067 if x!=918 else .057,.052 if x in [443,735] else .038)

# Jewelled curved lozenges. Their gold frames have a peaked polished section.
def setting(name,cx,cy,rx,ry,kind='diamond',gem_scale=.68):
    if kind=='swept':
        contours=[[[cx,cy-ry],[cx+rx*.10,cy-ry*.48],[cx+rx*.58,cy-ry*.10],[cx+rx,cy]],
                  [[cx+rx,cy],[cx+rx*.5,cy+ry*.12],[cx+rx*.16,cy+ry*.48],[cx,cy+ry]],
                  [[cx,cy+ry],[cx-rx*.16,cy+ry*.48],[cx-rx*.5,cy+ry*.12],[cx-rx,cy]],
                  [[cx-rx,cy],[cx-rx*.58,cy-ry*.10],[cx-rx*.10,cy-ry*.48],[cx,cy-ry]]]
        p=chain(contours,12)[:-1]
    else:p=np.array([[cx,cy-ry],[cx+rx,cy],[cx,cy+ry],[cx-rx,cy]])
    center=np.array([cx,cy]);N=len(p);v=[]
    for scale,z in [(1,.240),(.90,.295),(.78,.335),(gem_scale,.285)]:
        for q in center+(p-center)*scale:v.append([*xy(q),z])
    faces=[]
    for k in range(3):faces += [(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for i in range(N)]
    ob=mesh(name+' raised curved gold frame',v,[q[::-1] for q in faces],'gold',kind=='swept')
    # The low black green bed separates the stone from the metal prongs.
    q=np.array([[cx,cy-ry*gem_scale],[cx+rx*gem_scale,cy],[cx,cy+ry*gem_scale],[cx-rx*gem_scale,cy]])
    solid(name+' dark stone seat',q,.280,.21,.003,'setting_shadow')
    q=center+(q-center)*.91
    table=center+(q-center)*.54
    vv=[[*xy(a),.295] for a in q]+[[*xy(a),.360] for a in table]+[[*xy(center+[0,-ry*.08]),.399]]
    ff=[(i,(i+1)%4,4+(i+1)%4,4+i) for i in range(4)]+[(4+i,4+(i+1)%4,8) for i in range(4)]
    ob=mesh(name+' emerald cut facets',vv,[q[::-1] for q in ff],'emerald')
    ob.data.materials.append(M['emerald_light']);ob.data.materials.append(M['emerald_dark'])
    for i,p in enumerate(ob.data.polygons):p.material_index=[1,0,2,0,1,0,2,0][i]
    # Export separate material groups later without disturbing facet normals.
    return ob
setting('Upper bow tip',627,193,42,69,'swept',.61)
setting('Lower bow tip',626,933,44,74,'swept',.61)
setting('Upper grip',818,470,37,41,'swept',.69)
setting('Lower grip',818,671,38,43,'swept',.69)
setting('Central emerald',817,570,76,63,'swept',.76)

# Broad ornate arrowhead with a swept notch and triangular emerald inlay.
arrow=chain([[[938,510],[969,532],[1016,553],[1058,570]],[[1058,570],[1014,582],[970,608],[938,632]],[[938,632],[951,597],[955,586],[935,578]],[[935,578],[960,565],[952,545],[938,510]]],12)[:-1]
solid('Swept gold arrowhead',arrow,.305,.19,.012)
inlay=[[958,541],[1023,570],[958,603],[969,575]]
solid('Arrowhead emerald seat',inlay,.312,.28,.005,'setting_shadow')
p=xy([[961,547],[1014,570],[961,596],[974,571]])
v=[[*a,.323] for a in p]+[[*xy([975,568]),.395]]
ob=mesh('Arrowhead emerald facets',v,[(4,(i+1)%4,i) for i in range(4)],'emerald')
ob.data.materials.append(M['emerald_light']);ob.data.materials.append(M['emerald_dark'])
for i,p in enumerate(ob.data.polygons):p.material_index=[1,0,2,0][i]
setting('Small arrow nock',233,570,43,30,'diamond',.35)
# The nock is all gold, as in the reference.
for ob in objects:
    if ob.name.startswith('Small arrow nock'):
        ob.data.materials.clear();ob.data.materials.append(M['gold'])
        ob['role']='gold'
        for p in ob.data.polygons:p.material_index=0
bud('Faceted arrow draw grip',(627,569),31,28)

# Split by actual material while extracting Blender evaluated corner normals.
groups=[];arrays={}
for ob in objects:
    me=ob.data;me.calc_loop_triangles()
    for mi,mat in enumerate(me.materials):
        tris=[t for t in me.loop_triangles if t.material_index==mi]
        if not tris:continue
        role=next(r for r,m in M.items() if m==mat)
        index=len(groups);arrays[str(index)+'_points']=np.array([v.co[:] for v in me.vertices],np.float32)
        arrays[str(index)+'_triangles']=np.array([t.vertices[:] for t in tris],np.int32)
        arrays[str(index)+'_normals']=np.array([[me.corner_normals[l].vector[:] for l in t.loops] for t in tris],np.float32)
        groups.append({'name':ob.name,'role':role})
    back=ob.copy();back.data=ob.data.copy();back.name='Back '+ob.name
    for v in back.data.vertices:v.co=(-v.co.x,v.co.y,-v.co.z-.33)
    if me.has_custom_normals:back.data.normals_split_custom_set([(-n.vector.x,n.vector.y,-n.vector.z) for n in me.corner_normals])
    scene.collection.objects.link(back)
np.savez_compressed(TEMP/'emerald_archer_geometry.npz',**arrays)
(OUT/'design.json').write_text(json.dumps({'groups':groups,'palette':PALETTE,'source_shell':'sprout','reference_center':[627,566],'reference_inner_radius':458},indent=2))

ref=bpy.data.objects.new('Owner reference',None);ref.empty_display_type='IMAGE'
ref.data=bpy.data.images.load(str(ROOT/'reference.png'),check_existing=True);ref.data.pack()
ref.empty_display_size=6.63;ref.location=(-7,0,0);scene.collection.objects.link(ref)
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        s=area.spaces.active;s.region_3d.view_rotation=Quaternion((1,0,0,0));s.region_3d.view_location=Vector((0,0,0))
        s.region_3d.view_distance=8.8;s.region_3d.view_perspective='ORTHO';s.shading.type='MATERIAL';s.overlay.show_overlays=False
bpy.data.libraries.write(str(OUT/'emerald_archer.blend'),{scene},compress=True)
print('Emerald Archer built:',len(objects),'front objects,',len(groups),'material groups')
