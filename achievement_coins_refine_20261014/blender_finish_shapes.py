"""Native smooth lathed reliefs and beveled bars in the open Blender scenes."""
from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parent

def lathe(definition):
    profile=np.asarray(definition['profile'])
    y,c,r=profile.T;segments=25
    theta=np.linspace(0,np.pi,segments)
    scale=definition['zscale'];base=definition['base']
    dr=np.gradient(r,y);dc=np.gradient(c,y)
    vertices=np.stack([c[:,None]+r[:,None]*np.cos(theta),
                      np.broadcast_to(y[:,None],(len(y),segments)),
                      base+scale*r[:,None]*np.sin(theta)],-1).reshape(-1,3)
    normals=np.stack([np.broadcast_to(scale*np.cos(theta),(len(y),segments)),
                     -scale*(dr[:,None]+dc[:,None]*np.cos(theta)),
                     np.broadcast_to(np.sin(theta),(len(y),segments))],-1).reshape(-1,3)
    normals/=np.linalg.norm(normals,axis=1,keepdims=True)
    faces=[]
    for i in range(len(y)-1):
        for j in range(segments-1):
            a=i*segments+j;b=a+1;d=a+segments;e=d+1
            faces.extend([(a,d,e),(a,e,b)])
    front_count=len(faces)
    boundary=(list(range(0,len(vertices),segments))+
              list(range((len(y)-1)*segments+1,len(vertices)))+
              list(range((len(y)-2)*segments+segments-1,segments-2,-segments))+
              list(range(segments-2,0,-1)))
    start=len(vertices)
    rear=vertices[boundary].copy();rear[:,2]=.02
    vertices=np.concatenate([vertices,rear])
    for i,a in enumerate(boundary):
        j=(i+1)%len(boundary);b=boundary[j]
        faces.extend([(a,start+j,b),(a,start+i,start+j)])
    faces.append(tuple(reversed(range(start,start+len(boundary)))))
    mesh=bpy.data.meshes.new('Smooth_lathed_relief');mesh.from_pydata(vertices.tolist(),[],faces);mesh.update();mesh.calc_loop_triangles()
    triangles=np.asarray([t.vertices[:] for t in mesh.loop_triangles])
    front=np.asarray([t.polygon_index<front_count for t in mesh.loop_triangles])
    front_tri=triangles[front];wall_tri=triangles[~front]
    walls=vertices[wall_tri]
    wn=np.cross(walls[:,1]-walls[:,0],walls[:,2]-walls[:,0]);wn/=np.maximum(np.linalg.norm(wn,axis=1,keepdims=True),1e-9)
    wn=.3*wn+.7*np.array([0,0,1]);wn/=np.maximum(np.linalg.norm(wn,axis=1,keepdims=True),1e-9)
    corner=np.concatenate([normals[front_tri],np.repeat(wn[:,None],3,axis=1)])
    triangles=np.concatenate([front_tri,wall_tri])
    bpy.data.meshes.remove(mesh)
    return vertices,triangles,corner,len(front_tri)

def bar(definition):
    width,height,depth=definition['dimensions'];ry=height/2;rz=depth/2
    cap=min(ry,width/4)
    angles=np.linspace(.01,np.pi/2,10)
    left=-width/2+cap*(1-np.cos(angles));right=-left[::-1]
    x=np.r_[left,np.linspace(left[-1],right[0],8)[1:-1],right]
    s=np.sqrt(np.maximum(1e-6,1-(np.maximum(0,np.abs(x)-(width/2-cap))/cap)**2))
    derivative=np.gradient(s,x);theta=np.linspace(0,2*np.pi,32,endpoint=False)
    vertices=np.stack([np.broadcast_to(x[:,None],(len(x),len(theta))),ry*s[:,None]*np.cos(theta),rz*s[:,None]*np.sin(theta)],-1).reshape(-1,3)
    vertices+=np.asarray(definition['center'])
    normals=np.stack([np.broadcast_to((-ry*rz*derivative)[:,None],(len(x),len(theta))),
                      np.broadcast_to(rz*np.cos(theta),(len(x),len(theta))),
                      np.broadcast_to(ry*np.sin(theta),(len(x),len(theta)))],-1).reshape(-1,3)
    normals/=np.linalg.norm(normals,axis=1,keepdims=True)
    triangles=[]
    for i in range(len(x)-1):
        for j in range(len(theta)):
            a=i*len(theta)+j;b=i*len(theta)+(j+1)%len(theta);d=a+len(theta);e=b+len(theta)
            triangles.extend([(a,b,e),(a,e,d)])
    triangles=np.asarray(triangles)
    corner=normals[triangles]
    cap_tri=[];cap_normals=[]
    for end,row,direction in [(0,0,-1),(1,len(x)-1,1)]:
        center=len(vertices)
        v=np.array(definition['center'],float);v[0]+=x[row]
        vertices=np.concatenate([vertices,v[None]])
        for j in range(len(theta)):
            a=row*len(theta)+j;b=row*len(theta)+(j+1)%len(theta)
            cap_tri.append((center,b,a) if direction<0 else (center,a,b))
            cap_normals.append([[direction,0,0]]*3)
    triangles=np.concatenate([triangles,np.asarray(cap_tri)])
    corner=np.concatenate([corner,np.asarray(cap_normals)])
    front=corner.mean(1)[:,2]>.001
    triangles=np.concatenate([triangles[front],triangles[~front]])
    corner=np.concatenate([corner[front],corner[~front]])
    return vertices,triangles,corner,int(front.sum())

for name in ['hourglass_teal','hourglass_gold','sunrise']:
    scene=bpy.data.scenes[name];bpy.context.window.scene=scene
    base=ROOT/name;design=json.loads((base/'design.json').read_text());loaded=np.load(base/'reliefs.npz')
    arrays={key:loaded[key] for key in loaded.files}
    for i,feature in enumerate(design['features']):
        if 'blender_lathe' in feature:values=lathe(feature['blender_lathe'])
        elif 'blender_bar' in feature:values=bar(feature['blender_bar'])
        else:continue
        p,t,n,fc=values
        arrays[f'{i}_points']=p;arrays[f'{i}_triangles']=t;arrays[f'{i}_normals']=n
        feature['front_count']=fc;feature['triangles']=len(t)
        for side in ['Front','Back']:
            prefix=f'Relief{side}_{i}_{feature["role"]}'
            obj=next(o for o in scene.objects if o.name.startswith(prefix))
            materials=list(obj.data.materials)
            vertices=p if side=='Front' else p*[-1,1,-1]+[0,0,-.33]
            mesh=bpy.data.meshes.new(prefix+'_Lathed');mesh.from_pydata(vertices.tolist(),[],t.tolist());mesh.update()
            obj.data=mesh
            for mat in materials:mesh.materials.append(mat)
            for polygon in mesh.polygons:polygon.use_smooth=True
            obj['authored_in_blender']='Smooth lathe or beveled solid bar'
    np.savez_compressed(base/'reliefs.npz',**arrays)
    (base/'design.json').write_text(json.dumps(design,indent=2))
bpy.context.window.scene=bpy.data.scenes['hourglass_teal']
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'coins.blend'),compress=True)
