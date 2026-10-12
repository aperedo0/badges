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
        uv=np.stack([(p[:,0]/s+cx)/1254,1-(bottom-(p[:,1]+2.455)/s)/1254],-1)
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
def bronze():
    kind='bronze';s=5.30/1017;cx=626.5;bottom=1098.
    mapping={'scale':s,'center_x':cx,'reference_bottom':bottom,'reference_top':81.,'image_size':[1254,1254]}
    cy=-2.455+(bottom-584)*s
    meshes=[]
    # Closed ellipsoid: true domed front and back, smooth analytic silhouette.
    m=Mesh('BronzeSun_Dome',True);sectors=160;r=208*s
    north=m.point((0,cy,.325));rings=[];latitudes=100
    for j in range(1,latitudes):
        phi=np.pi*j/latitudes;rr=r*np.sin(phi);z=.325*np.cos(phi)
        rings.append([m.point((rr*np.cos(a),cy+rr*np.sin(a),z)) for a in np.arange(sectors)*2*np.pi/sectors])
    south=m.point((0,cy,-.325))
    for k in range(sectors):m.face(north,rings[0][k],rings[0][(k+1)%sectors],role=0)
    for j in range(len(rings)-1):
        role=0 if j<latitudes//2-1 else 1
        for k in range(sectors):
            a,b=rings[j][k],rings[j][(k+1)%sectors];c,d=rings[j+1][k],rings[j+1][(k+1)%sectors]
            m.face(a,c,d,b,role=role)
    for k in range(sectors):m.face(rings[-1][k],south,rings[-1][(k+1)%sectors],role=1)
    meshes.append(m)
    # Two rounded lips separated by a real dark circumferential channel.
    for name,radius,minor,z in [('BronzeSun_OuterLip',230*s,6.8*s,.10),('BronzeSun_InnerLip',218*s,4.2*s,.075)]:
        m=Mesh(name,True);cross=10
        for j in range(sectors):
            a=j*2*np.pi/sectors
            for k in range(cross):
                b=k*2*np.pi/cross;rr=radius+minor*np.cos(b)
                m.point((rr*np.cos(a),cy+rr*np.sin(a),z+minor*np.sin(b)))
        for j in range(sectors):
            for k in range(cross):
                a=j*cross+k;b=((j+1)%sectors)*cross+k;c=j*cross+(k+1)%cross;d=((j+1)%sectors)*cross+(k+1)%cross
                m.face(a,b,d,c,role=0 if np.sin((k+.5)*2*np.pi/cross)>-.1 else 1)
        meshes.append(m)
    # Under the lips a closed annular channel. Front cap is physical geometry.
    m=Mesh('BronzeSun_Channel',True);r0=211*s;r1=237*s
    for z in [.035,-.12]:
        for rr in [r0,r1]:
            for k in range(sectors):
                a=k*2*np.pi/sectors;m.point((rr*np.cos(a),cy+rr*np.sin(a),z))
    for k in range(sectors):
        q=(k+1)%sectors
        m.face(k,sectors+k,sectors+q,q,role=2)
        m.face(2*sectors+k,2*sectors+q,3*sectors+q,3*sectors+k,role=1)
        m.face(k,q,2*sectors+q,2*sectors+k,role=2)
        m.face(sectors+k,3*sectors+k,3*sectors+q,sectors+q,role=2)
    meshes.append(m)
    # Actual triangular wedges. The long four rays alternate with shorter diagonals.
    rays=[[(627,81),(716,380),(538,380)],[(1139,583),(841,497),(841,676)],[(627,1098),(540,802),(714,802)],[(114,583),(410,677),(410,497)],[(924,291),(836,470),(751,393)],[(941,873),(753,780),(839,706)],[(312,873),(414,706),(498,781)],[(329,291),(501,393),(418,470)]]
    for i,tri in enumerate(rays):
        m=Mesh('BronzeSun_Ray'+str(i+1));p=np.asarray(tri,float)
        xy=np.stack([(p[:,0]-cx)*s,-2.455+(bottom-p[:,1])*s],-1)
        if np.cross(xy[1]-xy[0],xy[2]-xy[0])<0:xy=xy[[0,2,1]]
        front=[m.point((*xy[k],-.075 if k else .015)) for k in range(3)]
        # Ray crests stay behind the entire rim so the two lips are continuous.
        mid=m.point((*(xy[1]+xy[2])/2,.025))
        m.face(front[0],front[1],mid,role=0);m.face(front[0],mid,front[2],role=0);m.face(front[1],front[2],mid,role=0)
        back=[m.point((*xy[k],-.22)) for k in range(3)]
        m.face(back[0],back[2],back[1],role=1)
        for k in range(3):q=(k+1)%3;m.face(front[k],back[k],back[q],front[q],role=2)
        meshes.append(m)
    records=[m.finish(kind,mapping) for m in meshes];mapping['meshes']=records
    (ROOT/kind/'source/mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
    print('BRONZE',sum(m['triangles'] for m in records))
def offset_polygon(p,width):
    # Image coordinates have +Y down; this outline is clockwise in image space.
    p=np.asarray(p,float);lines=[]
    for j in range(len(p)):
        v=p[(j+1)%len(p)]-p[j];v/=np.linalg.norm(v);n=np.array([-v[1],v[0]])
        lines.append((n,float(n@p[j]+width[j])))
    out=[]
    for j in range(len(p)):
        n0,b0=lines[j-1];n1,b1=lines[j];out.append(np.linalg.solve(np.stack([n0,n1]),[b0,b1]))
    return np.asarray(out)
def rounded(p,amount=2.,steps=6):
    p=np.asarray(p);out=[]
    for j in range(len(p)):
        v=p[j];a=p[j-1]-v;b=p[(j+1)%len(p)]-v
        a=v+a/np.linalg.norm(a)*amount;b=v+b/np.linalg.norm(b)*amount
        for t in np.linspace(0,1,steps,endpoint=False):out.append((1-t)**2*a+2*t*(1-t)*v+t*t*b)
    return np.asarray(out)
def silver():
    kind='silver';s=5.30/778;cx=627.
    # Source vertices follow the visible beveled outer silhouette.
    polys=[np.array([(214,253),(627,518),(1040,253),(1040,464),(627,741),(214,464)],float),np.array([(214,542),(627,807),(1040,542),(1040,752),(627,1030),(214,752)],float)]
    # Source outline is counterclockwise in image coordinates; reverse for inset.
    polys=[p if np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))>0 else p[::-1] for p in polys]
    widths=[45,45,26,18,18,26]
    cores=[np.array([(270,337),(627,571),(984,337),(1019,461),(627,719),(235,461)],float),np.array([(270,626),(627,860),(984,626),(1019,749),(627,1008),(235,749)],float)]
    contours=[(rounded(p),rounded(q)) for p,q in zip(polys,cores)]
    bottom=max(p[:,1].max() for p,q in contours)
    mapping={'scale':s,'center_x':cx,'reference_bottom':float(bottom),'reference_top':253.,'image_size':[1254,1254]}
    meshes=[]
    for i,(outer,inner) in enumerate(contours):
        m=Mesh('SilverChevron_'+('Upper' if i==0 else 'Lower'))
        def xy(p):return np.stack([(p[:,0]-cx)*s,-2.455+(bottom-p[:,1])*s],-1)
        outerxy=xy(outer);innerxy=xy(inner)
        # A mild real center ridge divides the two broad planes. Each half's
        # normal is constant; all bevel strips have the corresponding geometry.
        frontz=.30-.012*np.abs(innerxy[:,0]);edgez=.015+np.zeros(len(outerxy))
        fi=[m.point((*p,z)) for p,z in zip(innerxy,frontz)]
        oi=[m.point((*p,z)) for p,z in zip(outerxy,edgez)]
        bi=[m.point((*p,-.30)) for p in outerxy]
        # Core includes both planar halves, separated exactly at X=0.
        for face in triangulate(innerxy):
            # Split any triangle crossing the crest at X=0, maintaining flat normals.
            verts=np.array([m.p[fi[k]] for k in face])
            for side in [-1,1]:
                clipped=[]
                for j,a in enumerate(verts):
                    b=verts[(j+1)%3];ina=side*a[0]>=-1e-10;inb=side*b[0]>=-1e-10
                    if ina:clipped.append(a)
                    if ina!=inb:
                        t=-a[0]/(b[0]-a[0]);q=a+t*(b-a);q[0]=0;q[2]=.30;clipped.append(q)
                if len(clipped)>=3:
                    ids=[m.point(p) for p in clipped]
                    for k in range(1,len(ids)-1):
                        a,b,c=ids[0],ids[k],ids[k+1]
                        if np.cross(np.array(m.p[b])-m.p[a],np.array(m.p[c])-m.p[a])[2]<0:b,c=c,b
                        m.face(a,b,c,role=0)
        # Smooth rounding is confined to the small corner facets.
        for j in range(len(outer)):
            k=(j+1)%len(outer)
            m.face(oi[j],fi[j],fi[k],oi[k],role=0)
            m.face(oi[j],oi[k],bi[k],bi[j],role=2)
        for tri in triangulate(outerxy):
            ids=[bi[k] for k in tri]
            if np.cross(np.array(m.p[ids[1]])-m.p[ids[0]],np.array(m.p[ids[2]])-m.p[ids[0]])[2]>0:ids=ids[::-1]
            m.face(*ids,role=1)
        # Merge exact coincident core/boundary vertices to close the shell.
        pts=np.round(m.p,10);unique,inv=np.unique(pts,axis=0,return_inverse=True);m.p=unique.tolist();m.f=inv[np.array(m.f)].tolist()
        ff=np.asarray(m.f);tt=unique[ff];good=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)>1e-12
        m.f=ff[good].tolist();m.roles=np.asarray(m.roles)[good].tolist()
        # Consistent front-facing orientation for every upper surface triangle.
        for j,face in enumerate(m.f):
            q=unique[face];n=np.cross(q[1]-q[0],q[2]-q[0])
            if m.roles[j]==0 and n[2]<0:m.f[j]=face[::-1]
        meshes.append(m)
    records=[m.finish(kind,mapping) for m in meshes];mapping['meshes']=records
    (ROOT/kind/'source/mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
    print('SILVER',sum(m['triangles'] for m in records))
if __name__=='__main__':bronze();silver()
