"""Reference-sized, closed bronze sun and beveled silver double chevron."""
from pathlib import Path
import numpy as np,json,math
ROOT=Path(__file__).resolve().parents[1]
class Mesh:
    def __init__(self,name,smooth=False):self.name=name;self.smooth=smooth;self.p=[];self.f=[];self.roles=[]
    def point(self,p):self.p.append(list(p));return len(self.p)-1
    def face(self,*idx,role=0):
        for j in range(1,len(idx)-1):self.f.append([idx[0],idx[j],idx[j+1]]);self.roles.append(role)
    def finish(self,kind,mapping):
        p=np.asarray(self.p,float);f=np.asarray(self.f,int);t=p[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-12)
        if self.smooth:
            normal=np.zeros_like(p)
            area=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
            for k in range(3):np.add.at(normal,f[:,k],area)
            normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-12)
            normal=normal[f]
        else:normal=np.repeat(n[:,None,:],3,axis=1)
        s=mapping['scale'];cx=mapping['center_x'];bottom=mapping['reference_bottom']
        original=p-np.array(mapping.get('world_offset',[0,0,0]));plane=original.copy();plane[:,0]=original[:,0]*23/(23-original[:,2]);plane[:,1]=1.8+(original[:,1]-1.8)*23/(23-original[:,2]);uv=np.stack([(plane[:,0]/s+cx)/1254,1-(bottom-(plane[:,1]+2.455)/s)/1254],-1)
        if self.name=='GoldCrown_ScallopedShell':
            # Smooth normals from the actual wall curve, independent of the
            # uneven row spacing caused by the five different peak heights.
            sx=uv[:,0]*1254;sy=(1-uv[:,1])*1254;step=.05
            for role in [0,1]:
                back=.115 if role else 0.
                def surface(x,y):return point_from_reference(x,y,wall_z(x,y,mapping)-back,mapping)
                normals=[]
                for x,y in zip(sx,sy):
                    dx=surface(x+step,y)-surface(x-step,y);dy=surface(x,y+step)-surface(x,y-step)
                    q=np.cross(dy,dx);q/=np.linalg.norm(q);normals.append(q if role==0 else -q)
                normals=np.array(normals);idx=(np.asarray(self.roles)==role)&(np.arange(len(f))<self.analytical_face_limit);normal[idx]=normals[f[idx]]
        np.savez_compressed(ROOT/kind/'source'/f'{self.name}.npz',points=p,faces=f,normals=normal,uv=uv,roles=np.asarray(self.roles))
        return {'name':self.name,'triangles':len(f),'smooth':self.smooth,'bounds':[p.min(0).tolist(),p.max(0).tolist()]}
def triangulate(poly):
    """Ear clipping, preserving concave outlines and all boundary vertices."""
    p=np.asarray(poly);idx=list(range(len(p)));faces=[]
    area=np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1));sign=np.sign(area)
    def cross(a,b):return a[0]*b[1]-a[1]*b[0]
    for _ in range(len(p)*len(p)):
        if len(idx)==3:faces.append(idx.copy());return faces
        found=False
        for j,b in enumerate(idx):
            a=idx[j-1];c=idx[(j+1)%len(idx)]
            if cross(p[b]-p[a],p[c]-p[b])*sign<=1e-9:continue
            inside=False
            for k in idx:
                if k in [a,b,c]:continue
                q=p[k]
                if min(cross(p[b]-p[a],q-p[a])*sign,cross(p[c]-p[b],q-p[b])*sign,cross(p[a]-p[c],q-p[c])*sign)>=-1e-9:inside=True;break
            if inside:continue
            faces.append([a,b,c]);idx.pop(j);found=True;break
        if not found:raise RuntimeError('Could not triangulate polygon')
    raise RuntimeError('Ear clipping did not finish')
def point_from_reference(x,y,z,M):
    x0=(x-M['center_x'])*M['scale'];y0=-2.455+(M['reference_bottom']-y)*M['scale']
    return np.array([x0*(1-z/23),1.8+(y0-1.8)*(1-z/23),z])
def wall_z(x,y,M):
    xx=x-M['center_x'];yb=817-75*np.sqrt(max(0,1-(xx/488)**2));height=yb-y
    t=np.clip(height/290,0,1);radius=488+60*t*t*(3-2*t)
    return .70*np.sqrt(max(0,1-(xx/radius)**2))-.16*height*M['scale']
def orient_and_save(mesh,kind,M):
    # Propagate oriented faces around every closed shell; positive volume is outward.
    f=np.asarray(mesh.f);p=np.asarray(mesh.p);edges={}
    for i,tri in enumerate(f):
        for a,b in zip(tri,np.roll(tri,-1)):edges.setdefault(tuple(sorted((int(a),int(b)))),[]).append((i,int(a),int(b)))
    assert all(len(v)==2 for v in edges.values()),(mesh.name,'open edges')
    signs=np.zeros(len(f),int);signs[0]=1;stack=[0]
    while stack:
        i=stack.pop()
        for a,b in zip(f[i],np.roll(f[i],-1)):
            pair=edges[tuple(sorted((int(a),int(b))))];j,c,d=pair[0] if pair[1][0]==i else pair[1]
            required=signs[i]*(-1 if a==c and b==d else 1)
            if not signs[j]:signs[j]=required;stack.append(j)
            else:assert signs[j]==required,(mesh.name,'inconsistent winding')
    assert (signs!=0).all();f[signs<0]=f[signs<0,::-1]
    volume=np.einsum('ij,ij->i',p[f[:,0]],np.cross(p[f[:,1]],p[f[:,2]])).sum()/6
    if volume<0:f=f[:,::-1]
    mesh.f=f.tolist();return mesh.finish(kind,M)
def fit(meshes,M):
    p=np.concatenate([m.p for m in meshes]);lo=p.min(0);hi=p.max(0)
    offset=np.array([-(lo[0]+hi[0])/2,-2.455-lo[1],-(lo[2]+hi[2])/2]);M['world_offset']=offset.tolist()
    for m in meshes:m.p=(np.asarray(m.p)+offset).tolist()
def weld(m):
    p=np.round(m.p,10);unique,inv=np.unique(p,axis=0,return_inverse=True);f=inv[np.array(m.f)];q=unique[f]
    keep=np.linalg.norm(np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]),axis=1)>1e-12
    m.p=unique.tolist();m.f=f[keep].tolist();m.roles=np.array(m.roles)[keep].tolist()
def sphere(name,cx,cy,r,zcenter,M):
    m=Mesh(name,True);N=64;J=30
    front=m.point(point_from_reference(cx,cy,zcenter+r*M['scale']*.78,M));rings=[]
    for j in range(1,J):
        phi=np.pi*j/J;rr=r*np.sin(phi);z=zcenter+r*M['scale']*.78*np.cos(phi)
        rings.append([m.point(point_from_reference(cx+rr*np.cos(a),cy+rr*np.sin(a),z,M)) for a in np.arange(N)*2*np.pi/N])
    back=m.point(point_from_reference(cx,cy,zcenter-r*M['scale']*.78,M))
    for k in range(N):m.face(front,rings[0][k],rings[0][(k+1)%N],role=0)
    for j in range(len(rings)-1):
        for k in range(N):m.face(rings[j][k],rings[j+1][k],rings[j+1][(k+1)%N],rings[j][(k+1)%N],role=0 if j<J//2-1 else 1)
    for k in range(N):m.face(rings[-1][k],back,rings[-1][(k+1)%N],role=1)
    return m
def tube(name,path,r,M,sections=8,closed=False):
    m=Mesh(name,True);p=np.array(path);world=np.array([point_from_reference(*v,M) for v in p]);N=len(p)
    for j in range(N):
        tangent=world[(j+1)%N]-world[j-1] if closed else world[min(j+1,N-1)]-world[max(j-1,0)]
        tangent/=np.linalg.norm(tangent);side=np.cross(tangent,[0,0,1]);side/=np.linalg.norm(side);up=np.cross(side,tangent)
        for a in np.arange(sections)*2*np.pi/sections:m.point(world[j]+r*(np.cos(a)*up+np.sin(a)*side))
    for j in range(N if closed else N-1):
        for k in range(sections):
            a=j*sections+k;b=((j+1)%N)*sections+k;c=j*sections+(k+1)%sections;d=((j+1)%N)*sections+(k+1)%sections
            m.face(a,b,d,c,role=0 if np.cos((k+.5)*2*np.pi/sections)>-.1 else 1)
    if not closed:
        start=m.point(world[0]);end=m.point(world[-1])
        for k in range(sections):m.face(start,(k+1)%sections,k,role=2);m.face(end,(N-1)*sections+k,(N-1)*sections+(k+1)%sections,role=2)
    return m
def gold():
    kind='gold';M={'scale':6.40/1180,'center_x':627.5,'reference_bottom':1000.,'reference_top':206.,'reference_bounds':[38,206,1218,1000],'roughness':.32,'image_size':[1254,1254],'projection':'camera reference plane at Z=0'}
    meshes=[];cx=M['center_x'];R=488.;angles=np.arange(128)*2*np.pi/128
    # A real closed annular band, with a visible inner wall and an open center.
    m=Mesh('GoldCrown_HollowBand',True);rows=6
    for inner in [False,True]:
        for j in range(rows+1):
            v=j/rows
            for a in angles:
                rr=452 if inner else R;z=(.65 if inner else .70)*np.cos(a)
                x=cx+rr*np.sin(a);yt=817-75*np.cos(a)+18*max(0,-np.cos(a))**2;yb=937-63*np.cos(a)
                m.point(point_from_reference(x,(1-v)*yt+v*yb,z,M))
    size=(rows+1)*128
    for inside in [0,1]:
        for j in range(rows):
            for k,a in enumerate(angles):
                q=(k+1)%128;o=inside*size;m.face(o+j*128+k,o+j*128+q,o+(j+1)*128+q,o+(j+1)*128+k,role=0 if (np.cos(a)>0) != bool(inside) else 1)
    for k in range(128):
        q=(k+1)%128;m.face(k,size+k,size+q,q,role=0)
        m.face(rows*128+k,rows*128+q,size+rows*128+q,size+rows*128+k,role=0)
    meshes.append(m)
    # Five peaks joined by smooth asymmetric scallops, matching the reference.
    curves=[[(79,527),(147,638),(242,802),(287,435)],[(303,435),(335,627),(486,817),(611,334)],[(644,334),(761,811),(916,623),(948,435)],[(969,435),(1015,803),(1107,638),(1175,527)]]
    upper=[]
    for curve in curves:
        p=np.array(curve,float)
        for t in np.linspace(0,1,70,endpoint=False):upper.append((1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3])
    upper.append(np.array(curves[-1][-1],float));upper=np.array(upper);N=len(upper);rows=5
    # Curved front shell with a plain closed back; the band continues all around.
    m=Mesh('GoldCrown_ScallopedShell',True);trim=[]
    for back in [False,True]:
        for j in range(rows+1):
            v=j/rows
            for x,y in upper:
                xb=139+(x-79)/(1175-79)*(1115-139);yb=817-75*np.sqrt(max(0,1-((xb-cx)/R)**2))
                xx=(1-v)*xb+v*x;yy=(1-v)*yb+v*y
                z=wall_z(xx,yy,M)
                if back:z-=.115
                m.point(point_from_reference(xx,yy,z,M))
                if not back and j==rows:trim.append((xx,yy,z+.018))
    size=(rows+1)*N
    for back in [0,1]:
        o=back*size
        for j in range(rows):
            for k in range(N-1):m.face(o+j*N+k,o+j*N+k+1,o+(j+1)*N+k+1,o+(j+1)*N+k,role=back)
    m.analytical_face_limit=len(m.f)
    for k in range(N-1):
        m.face(k,k+1,size+k+1,size+k,role=2)
        a=rows*N+k;m.face(a,size+a,size+a+1,a+1,role=0)
    for j in range(rows):
        for k in [0,N-1]:a=j*N+k;b=(j+1)*N+k;m.face(a,b,size+b,size+a,role=2)
    meshes.append(m);meshes.append(tube('GoldCrown_RoundedScallopLip',trim,.025,M))
    # Broad rolled upper flanges rise behind the fine front lip in each valley.
    outercurves=[[(79,527),(147,602),(242,749),(287,435)],[(303,435),(335,580),(486,765),(611,334)],[(644,334),(761,765),(916,580),(948,435)],[(969,435),(1015,749),(1107,602),(1175,527)]]
    for i,(innercurve,outercurve) in enumerate(zip(curves,outercurves)):
        m=Mesh('GoldCrown_ValleyFlange'+str(i+1),True);N=71;pa=np.array(innercurve,float);pb=np.array(outercurve,float)
        paths=[]
        for p in [pb,pa]:
            a=[]
            for t in np.linspace(0,1,N):a.append((1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t*t*p[2]+t**3*p[3])
            paths.append(np.array(a))
        for back in [False,True]:
            for edge in [0,1]:
                for j,((x,y),(xi,yi)) in enumerate(zip(paths[edge],paths[1])):
                    xb=139+(xi-79)/(1175-79)*(1115-139);yb=817-75*np.sqrt(max(0,1-((xb-cx)/R)**2))
                    z=wall_z(xi,yi,M)
                    z-=.10*(yi-y)/50
                    if back:z-=.04
                    m.point(point_from_reference(x,y,z,M))
        for back in [0,1]:
            o=back*2*N
            for j in range(N-1):m.face(o+j,o+j+1,o+N+j+1,o+N+j,role=back)
        for j in range(N-1):
            m.face(j,2*N+j,2*N+j+1,j+1,role=0)
            m.face(N+j,N+j+1,3*N+j+1,3*N+j,role=1)
        for j in [0,N-1]:m.face(j,N+j,3*N+j,2*N+j,role=2)
        weld(m);meshes.append(m)
    for name,v in [('Upper',0),('Lower',1)]:
        path=[]
        for a in angles:
            y=(817-75*np.cos(a)+18*max(0,-np.cos(a))**2) if v==0 else (937-63*np.cos(a));path.append((cx+R*np.sin(a),y,.70*np.cos(a)))
        meshes.append(tube('GoldCrown_'+name+'BandLip',path,.021,M,closed=True))
    balls=[(82,492,43,.03),(302,385,58,.27),(627.5,275,68,.34),(953,385,58,.27),(1173,492,43,.03)]
    for i,(x,y,r,z) in enumerate(balls):
        meshes.append(sphere('GoldCrown_Finial'+str(i+1),x,y,r,z,M))
        # Small closed collars join each finial to the scalloped shell.
        a=np.arange(48)*2*np.pi/48;path=[(x+(.31*r)*np.cos(t),y+r*.88+(.06*r)*np.sin(t),z+.025*np.sin(t)) for t in a]
        meshes.append(tube('GoldCrown_Collar'+str(i+1),path,.019,M,sections=6,closed=True))
    fit(meshes,M);records=[orient_and_save(m,kind,M) for m in meshes];M['meshes']=records
    (ROOT/kind/'source/mapping.json').write_text(json.dumps(M,indent=2)+'\n');print('GOLD',sum(r['triangles'] for r in records))
def diamond():
    from scipy.spatial import Delaunay
    kind='diamond';M={'scale':6.40/1043,'center_x':626.5,'reference_bottom':984.,'reference_top':202.,'reference_bounds':[105,202,1148,984],'roughness':.32,'image_size':[1254,1254],'projection':'camera reference plane at Z=0'}
    rows=[[(401,206),(496,203),(627,202),(752,202),(851,206)],[(325,239),(359,239),(479,239),(627,239),(773,239),(897,239),(930,239)],[(231,324),(359,324),(530,320),(719,320),(894,324),(1028,324)],[(105,440),(210,437),(360,436),(496,435),(627,436),(759,435),(893,436),(1036,437),(1148,440)],[(195,534),(412,533),(521,535),(733,535),(845,532),(1057,534)],[(334,678),(498,678),(627,674),(754,678),(918,678)],[(446,795),(568,795),(627,795),(684,795),(807,795)],[(624,984)]]
    pts=np.array([p for row in rows for p in row],float);D=Delaunay(pts);faces=D.simplices
    m=Mesh('DiamondCrystal_CutFacets');z=[]
    for x,y in pts:
        if y<=440:
            depth=.06+.38*np.maximum(0,1-abs(x-626.5)/522)*min(1,(y-202)/150+.25)
            depth+=.035*np.sin((x-105)*.023)*np.sin((y-202)*.019)
        else:
            depth=max(.008,.46*(984-y)/544-.40*abs(x-624)/522)
            depth+=.028*np.sin((x-105)*.017)*np.sin((y-440)*.021)*(984-y)/544
        z.append(depth)
    for back in [False,True]:
        for (x,y),zz in zip(pts,z):m.point(point_from_reference(x,y,-zz if back else zz,M))
    N=len(pts)
    for f in faces:m.face(*f,role=0);m.face(*(f[::-1]+N),role=1)
    for a,b in D.convex_hull:m.face(int(a),int(b),int(b+N),int(a+N),role=2)
    fit([m],M);records=[orient_and_save(m,kind,M)];M['meshes']=records
    (ROOT/kind/'source/mapping.json').write_text(json.dumps(M,indent=2)+'\n');print('DIAMOND',sum(r['triangles'] for r in records))
if __name__=='__main__':gold();diamond()
