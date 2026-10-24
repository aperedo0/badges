"""Construct and inspect the complete shield in the live Blender scene."""
from pathlib import Path
import bpy,json,math
import numpy as np
from mathutils import Vector,Quaternion
from mathutils.geometry import delaunay_2d_cdt
ROOT=Path('/Users/antonioperedo/Desktop/badges/crimson_shield_20261019')
TEMP=Path('/tmp/crimson_shield_20261019')
D=json.loads((ROOT/'design.json').read_text());P=json.loads((ROOT/'palette.json').read_text())
for s in list(bpy.data.scenes):
    if s.name=='crimson_shield':bpy.data.scenes.remove(s)
scene=bpy.data.scenes.new('crimson_shield');bpy.context.window.scene=scene
M={}
for role,(col,metal,rough) in P.items():
    m=bpy.data.materials.new('CrimsonShield_BrushedField' if role=='field' else 'Shield_'+role);m.use_nodes=True
    nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=metal
    bs.inputs['Roughness'].default_value=rough
    if role in ['red','gem']:
        bs.inputs['Coat Weight'].default_value=.18 if role=='red' else .65
        bs.inputs['Coat Roughness'].default_value=.24 if role=='red' else .13
    uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='ShieldUV'
    if role=='field':
        bs.inputs['Anisotropic'].default_value=.55
        tangent=nt.nodes.new('ShaderNodeTangent');tangent.direction_type='UV_MAP';tangent.uv_map='ShieldUV'
        nt.links.new(tangent.outputs['Tangent'],bs.inputs['Tangent'])
    for suffix,socket,space in [('color','Base Color','sRGB'),('roughness','Roughness','Non-Color')]:
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures'/f'{role}_{suffix}.png'),check_existing=True)
        if tex.image.packed_file:tex.image.unpack(method='REMOVE')
        tex.image.reload();tex.image.colorspace_settings.name=space;tex.image.pack()
        nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs[socket])
    M[role]=m
objects=[]
def obj(name,v,f,role,smooth=False,mirror=True):
    v=np.array(v,float);f=[tuple(q) for q in f]
    if mirror:
        n=len(v);v=np.vstack([v,v*[-1,1,-1]]);f+= [tuple(i+n for i in q) for q in f.copy()]
    me=bpy.data.meshes.new(name);me.from_pydata(v.tolist(),[],f);me.update()
    ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);me.materials.append(M[role]);ob['role']=role
    uv=me.uv_layers.new(name='ShieldUV')
    for poly in me.polygons:
        poly.use_smooth=smooth
        for li in poly.loop_indices:
            index=me.loops[li].vertex_index;co=me.vertices[index].co
            u=-co.x if mirror and index>=n else co.x
            if role=='field':
                uv.data[li].uv=((.840*u+.543*co.y+3.015)/6.03,(-.543*u+.840*co.y+2.455)/5.47)
            else:
                uv.data[li].uv=((u+3.015)/6.03,(co.y+2.455)/5.47)
    objects.append(ob);return ob
outer=np.array(D['outer'])
def offset(p,d):
    # Nested contours retain the traced silhouette without offset loops at corners.
    center=np.array([0.,.2425]);half=np.array([2.104631,2.6975])
    return center+(p-center)*(1-d/half)

profile=[(0,.140),(.013,.205),(.030,.280),(.047,.286),(.060,.255),(.075,.252),(.205,.305),(.232,.130),(.246,.100),(.262,.135),(.279,.125),(.419,.125),(.435,.205),(.458,.228),(.482,.185),(.514,.095)]
roles=['edge','steel','steel','channel','steel','steel','steel','channel','steel','channel','red','channel','steel','steel','edge']
# Insert exact intersections with the two diagonal metal join details.
raw=outer.copy();parameters=[(0,0.)]
for i,(a,b) in enumerate(zip(raw,np.roll(raw,-1,axis=0))):
    fractions={0.}
    for d,z in [profile[2],profile[5],profile[6],profile[8]]:
        aa,bb=offset(np.array([a,b]),d)
        sa=aa[1]-abs(aa[0])+.84;sb=bb[1]-abs(bb[0])+.84
        for level in [-.025,0,.025,.055,.080]:
            if (sa-level)*(sb-level)<0:
                fractions.add(float((level-sa)/(sb-sa)))
    for f in sorted(fractions):
        if i==0 and f==0:continue
        parameters.append((i,f))
outer=np.array([raw[i]*(1-f)+raw[(i+1)%len(raw)]*f for i,f in parameters]);n=len(outer)
def frame_depth(p,z,d):
    # A recessed diagonal join and its small machined shoulders are real geometry.
    if d>.262:return np.full(len(p),z)
    along=p[:,1]-np.abs(p[:,0])+.84
    groove=np.maximum(0,1-np.abs(along)/.025)
    shoulder=np.maximum(0,1-np.abs(along-.055)/.025)
    return z+np.clip(d/.055,0,1)*(-.055*groove+.018*shoulder)
for k,role in enumerate(roles):
    a,z=profile[k];b,zz=profile[k+1];aa=offset(outer,a);bb=offset(outer,b)
    if role=='red':
        rings=[]
        for t,rise in [(0,0),(.18,.010),(.50,.018),(.82,.010),(1,0)]:
            p=aa*(1-t)+bb*t;rings.append(np.c_[p,np.full(n,z+rise)])
        v=np.vstack(rings);f=[]
        for j in range(4):f += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for i in range(n)]
        obj('Smooth deep red mineral inlay',v,f,role,True)
    else:
        v=np.vstack([np.c_[aa,frame_depth(aa,z,a)],np.c_[bb,frame_depth(bb,zz,b)]])
        obj('Frame section '+str(k),v,[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)],role,True)

obj('Solid shield edge',[[*p,.14] for p in outer]+[[*p,-.14] for p in outer],[(i,n+i,n+(i+1)%n,(i+1)%n) for i in range(n)],'edge',True,False)
def inside(p,poly):
    x,y=p;result=False
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:result=not result
    return result
def sculpt(name,poly,base,rise,role,spacing=.065,ridge=None):
    poly=np.array(poly,float)
    if np.cross(poly,np.roll(poly,-1,axis=0)).sum()<0:poly=poly[::-1]
    p=poly.tolist();constraints=[]
    if ridge is not None:
        ridge=np.array([q for q in ridge if inside(q,poly)])
        first=len(p);p+=ridge.tolist();constraints=[(first+i,first+i+1) for i in range(len(ridge)-1)]
    for x in np.arange(poly[:,0].min()+spacing/2,poly[:,0].max(),spacing):
        for y in np.arange(poly[:,1].min()+spacing/2,poly[:,1].max(),spacing):
            if inside((x,y),poly):p.append([x,y])
    r=delaunay_2d_cdt([Vector(q) for q in p],constraints,[list(range(len(poly)))],1,1e-6,False)
    xy=np.array(r[0]);faces=[tuple(q) for q in r[2] if len(q)==3]
    # Distance to the boundary makes a continuous low rounded relief.
    dist=[]
    for q in xy:
        a=poly;b=np.roll(poly,-1,axis=0);ab=b-a
        t=np.clip(((q-a)*ab).sum(axis=1)/(ab*ab).sum(axis=1),0,1)
        dist.append(np.linalg.norm(q-a-t[:,None]*ab,axis=1).min())
    if role=='field':
        # A shallow cylindrical shield spreads the highlight along its face.
        across=.840*xy[:,0]-.543*(xy[:,1]-.24)
        dome=np.maximum(.012,rise-.035*across**2)
        t=np.clip(np.array(dist)/.20,0,1);blend=t*t*(3-2*t)
        z=base+dome*blend
    elif ridge is not None:
        a=ridge[:-1];b=ridge[1:];ab=b-a;rd=[]
        for q in xy:
            t=np.clip(((q-a)*ab).sum(axis=1)/np.maximum((ab*ab).sum(axis=1),1e-12),0,1)
            rd.append(np.linalg.norm(q-a-t[:,None]*ab,axis=1).min())
        z=base+rise*np.array(dist)/np.maximum(np.array(dist)+np.array(rd),1e-12)
    else:
        z=base+rise*(1-np.exp(-np.array(dist)/.075))
    v=np.c_[xy,z];count=len(v)
    from collections import Counter
    edges=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,np.roll(f,-1)))
    directed=[(a,b) for f in faces for a,b in zip(f,np.roll(f,-1)) if edges[tuple(sorted((a,b)))]==1]
    front_count=len(faces)
    v=np.vstack([v,np.c_[xy,np.full(count,base-.045)]])
    faces += [tuple(i+count for i in f[::-1]) for f in faces.copy()]
    faces += [(a,a+count,b+count,b) for a,b in directed]
    ob=obj(name,v,faces,role,True)
    # Keep wall and buried reverse triangles flat.
    for k,p in enumerate(ob.data.polygons):p.use_smooth=(k%(len(faces)))<front_count
    if ridge is not None:
        crest=set(np.where(z>base+rise-1e-5)[0].tolist());crest|={i+2*count for i in crest.copy()}
        for edge in ob.data.edges:
            if all(i in crest for i in edge.vertices):edge.use_edge_sharp=True
        ob.data.update()
    return ob
sculpt('Curved brushed dark shield',offset(raw,.509),.095,.110,'field',.085)
for key in ['upper_left','lower_left']:
    p=np.array(D[key]);ridge=np.array(D[key.replace('_left','_ridge')]);sculpt('Creased silver '+key,p,.225,.075,'steel',.035,ridge)
    p=p*[-1,1];sculpt('Creased silver '+key.replace('left','right'),p,.225,.075,'steel',.035,ridge*[-1,1])
for end in ['top','bottom']:
    a=np.array(D[end+'_holder']);b=np.array(D[end+'_window']);n=len(a)
    rings=[(a,.235),(a*.90+b*.10,.285),(a*.62+b*.38,.365),(a*.26+b*.74,.285),(b,.320)]
    for k in range(len(rings)-1):
        v=np.vstack([np.c_[rings[k][0],np.full(n,rings[k][1])],np.c_[rings[k+1][0],np.full(n,rings[k+1][1])]])
        obj(end+' swept ruby setting '+str(k),v,[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)],'steel',True)
    p=np.array(D[end+'_gem'])
    if np.cross(p,np.roll(p,-1,axis=0)).sum()<0:p=p[::-1]
    center=p.mean(axis=0);inner=center+(p-center)*.58
    v=[[*q,.308] for q in p]+[[*q,.385] for q in inner]+[[*center,.450]]
    f=[(i,(i+1)%4,4+(i+1)%4,4+i) for i in range(4)]+[(4+i,4+(i+1)%4,8) for i in range(4)]
    obj(end+' ruby crown facets',v,f,'gem',False)
# Import a full native copy of the previous shield as hidden working context.
from pxr import Usd,UsdGeom
source=Usd.Stage.Open(str(ROOT/'previous/crimson_shield_before_brushing.usdz'));context=bpy.data.collections.new('Previous Crimson source copy');scene.collection.children.link(context)
for prim in source.Traverse():
    if prim.IsA(UsdGeom.Mesh):
        mesh=UsdGeom.Mesh(prim);v=np.array(mesh.GetPointsAttr().Get());indices=list(mesh.GetFaceVertexIndicesAttr().Get());counts=list(mesh.GetFaceVertexCountsAttr().Get());f=[];i=0
        for c in counts:f.append(indices[i:i+c]);i+=c
        me=bpy.data.meshes.new('Source '+prim.GetName());me.from_pydata(v.tolist(),[],f)
        ob=bpy.data.objects.new('Source '+prim.GetName(),me);context.objects.link(ob)
context.hide_render=True;context.hide_viewport=True
# Export model data from Blender's actual mesh and corner normals.
arrays={};manifest=[]
for k,ob in enumerate(objects):
    me=ob.data;me.calc_loop_triangles()
    prefix='m'+str(k);arrays[prefix+'_v']=np.array([v.co[:] for v in me.vertices],np.float32)
    arrays[prefix+'_f']=np.array([t.vertices[:] for t in me.loop_triangles],np.int32)
    arrays[prefix+'_n']=np.array([me.corner_normals[li].vector[:] for t in me.loop_triangles for li in t.loops],np.float32)
    arrays[prefix+'_uv']=np.array([me.uv_layers['ShieldUV'].data[li].uv[:] for t in me.loop_triangles for li in t.loops],np.float32)
    manifest.append({'prefix':prefix,'name':ob.name,'role':ob['role']})
np.savez_compressed(TEMP/'meshes.npz',**arrays);(TEMP/'meshes.json').write_text(json.dumps(manifest,indent=2))
scene.world=bpy.data.worlds.new('Shield working studio');scene.world.color=(.10,.10,.10)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.shading.type='MATERIAL'
            region=area.spaces.active.region_3d;region.view_rotation=Quaternion((1,0,0,0));region.view_location=(0,.24,0);region.view_distance=8.2;region.view_perspective='ORTHO'
bpy.data.libraries.write(str(ROOT/'crimson_shield.blend'),{scene},compress=True)
print(json.dumps({'objects':len(objects),'triangles':sum(len(ob.data.loop_triangles) for ob in objects),'scene':scene.name}))
