"""Reference-derived sculpted geometry, authored in the app's raw Y-up space."""
import math
from pathlib import Path
import numpy as np

FLOOR = -2.895
MESH_IDS = [f'Part{i}' for i in range(6)]  # Internal keys; USD uses tier/part/finish names.

class Mesh:
    def __init__(self):
        self.points=[];self.faces=[];self.normals=[];self.materials=[];self.regions=[];self.lookup={}
    def vertex(self, point):
        point=tuple(float(x) for x in np.asarray(point,np.float32));key=tuple(round(x,7) for x in point)
        if key not in self.lookup:
            self.lookup[key]=len(self.points);self.points.append(point)
        return self.lookup[key]
    def triangle(self, points, material, normals=None, region='surface'):
        points=np.asarray(points,float);raw=np.cross(points[1]-points[0],points[2]-points[0])
        if np.linalg.norm(raw)<1e-11:return
        if normals is None:normals=np.repeat((raw/np.linalg.norm(raw))[None,:],3,axis=0)
        normals=np.asarray(normals,float);normals/=np.linalg.norm(normals,axis=1,keepdims=True)
        if raw@normals.mean(0)<0:points=points[[0,2,1]];normals=normals[[0,2,1]]
        self.faces.append([self.vertex(p) for p in points]);self.normals.extend(normals.astype(np.float32));self.materials.append(material);self.regions.append(region)
    def quad(self, points, material, normals=None, region='surface'):
        if normals is None:
            raw=np.cross(np.asarray(points[1])-points[0],np.asarray(points[2])-points[0]);raw/=np.linalg.norm(raw)
            normals=np.repeat(raw[None,:],4,axis=0)
        for ids in [[0,1,2],[0,2,3]]:self.triangle([points[i] for i in ids],material,[normals[i] for i in ids],region)

def bezier(a,b,c,d,count):
    return np.array([(1-t)**3*np.array(a)+3*(1-t)**2*t*np.array(b)+3*(1-t)*t*t*np.array(c)+t**3*np.array(d) for t in np.linspace(0,1,count,endpoint=False)])

def silver_geometry(settings):
    meshes={key:Mesh() for key in MESH_IDS};scale=6.03/1002
    def world(pixel,z):return np.array([(pixel[0]-628)*scale,(1052-pixel[1])*scale-3.015,z],float)
    # The five-point star has ten real planar faces, with a single central apex.
    outline=[(627,237),(718,435),(898,478),(771,613),(801,801),(627,701),(453,800),(482,614),(351,478),(535,436)]
    boundary=[world(p,settings.get(f'star_tip_{i}_z',settings['star_boundary_z'])) for i,p in enumerate(outline)];center=world((627,553),settings['star_apex_z']);star=meshes[MESH_IDS[3]]
    star_normals=[]
    for i,p in enumerate(boundary):
        q=boundary[(i+1)%10];normal=np.cross(p-center,q-center);normal/=np.linalg.norm(normal)
        if normal[2]<0:normal=-normal
        material=3 if normal[0]<0 else 4
        star.triangle([center,p,q],material,[normal]*3,f'star plane {i}');star_normals.append(normal.tolist())
        backp=p.copy();backq=q.copy();backp[2]=backq[2]=.035
        star.quad([p,backp,backq,q],4,region='star extruded sidewall')
        star.triangle([world((627,553),.035),backq,backp],4,[[0,0,-1]]*3,'star back')
    # Reference leaf axes and widths, including the inward-facing and crossed-base leaves.
    leaves=[((282,403),(416,255),48,10),((262,518),(391,397),41,-5),((245,529),(221,319),42,-10),((226,676),(142,477),46,-10),((272,731),(327,522),43,7),((310,813),(127,657),49,-6),((402,863),(353,672),42,-5),((421,913),(194,829),43,-6),((565,943),(422,797),42,8),((562,977),(332,969),42,0)]
    along=32;across=12
    for mirror in [False,True]:
        for number,(base,tip,halfwidth,bend) in enumerate(leaves):
            base=np.array(base,float);tip=np.array(tip,float)
            if mirror:base[0]=1256-base[0];tip[0]=1256-tip[0];bend=-bend
            direction=tip-base;perp=np.array([-direction[1],direction[0]])/np.linalg.norm(direction)
            target=meshes[MESH_IDS[[0,1,4,5][number%4]]]
            def surface(t,s,back=False):
                shape=max(0,math.sin(math.pi*t));axis=base+t*direction+perp*bend*shape
                xy=axis+perp*halfwidth*shape**.72*s
                edge=.145+.014*shape
                z=edge-.052 if back else edge+settings['leaf_ridge_height']*shape**.65*(1-abs(s))**.70
                return world(xy,z)
            def normal(t,s,side,back=False):
                t=np.clip(t,1e-5,1-1e-5);s=side*1e-5 if abs(s)<1e-8 else s;h=1e-5
                dt=surface(min(1,t+h),s,back)-surface(max(0,t-h),s,back)
                ds=surface(t,min(1,s+h),back)-surface(t,max(-1,s-h),back)
                n=np.cross(dt,ds);n/=np.linalg.norm(n)
                if n[2]<0:n=-n
                return -n if back else n
            for back in [False,True]:
                for ti in range(along):
                    for si in range(across):
                        ts=[ti/along,(ti+1)/along];ss=[-1+2*si/across,-1+2*(si+1)/across];side=-1 if sum(ss)<0 else 1
                        params=[(ts[0],ss[0]),(ts[1],ss[0]),(ts[1],ss[1]),(ts[0],ss[1])]
                        points=[surface(t,s,back) for t,s in params];normals=[normal(t,s,side,back) for t,s in params]
                        target.quad(points,4 if back else (0 if side<0 else 8),normals,f'leaf {mirror}-{number} '+('back' if back else 'folded curved face'))
            for side in [-1,1]:
                for ti in range(along):
                    t0,t1=ti/along,(ti+1)/along
                    target.quad([surface(t0,side),surface(t0,side,True),surface(t1,side,True),surface(t1,side)],8,region='leaf edge thickness')
    # Two gently curving cylindrical stems cross like the photograph, with actual solid ends.
    paths=[bezier((278,392),(164,670),(300,855),(493,925),80),bezier((493,925),(560,955),(634,996),(690,1038),80)]
    path=np.vstack(paths+[np.array([[690,1038]])]);casing=meshes[MESH_IDS[2]]
    for mirrored in [False,True]:
        pixels=path.copy()
        if mirrored:pixels[:,0]=1256-pixels[:,0]
        axis=np.array([world(p,.075+(0.008 if mirrored else 0)) for p in pixels]);rings=[];norms=[]
        for i,p in enumerate(axis):
            tangent=axis[min(len(axis)-1,i+1)]-axis[max(0,i-1)];tangent/=np.linalg.norm(tangent)
            u=np.array([-tangent[1],tangent[0],0]);u/=np.linalg.norm(u);v=np.array([0,0,1.])
            ring=[];ns=[]
            for j in range(16):
                angle=2*math.pi*j/16;n=math.cos(angle)*u+math.sin(angle)*v
                ring.append(p+settings['stem_radius']*n);ns.append(n)
            rings.append(ring);norms.append(ns)
        for i in range(len(rings)-1):
            for j in range(16):
                k=(j+1)%16;material=2 if j<8 else 5
                casing.quad([rings[i][j],rings[i+1][j],rings[i+1][k],rings[i][k]],material,[norms[i][j],norms[i+1][j],norms[i+1][k],norms[i][k]],'curved stem')
        for end in [0,len(axis)-1]:
            tangent=axis[1]-axis[0] if end==0 else axis[-1]-axis[-2];tangent/=np.linalg.norm(tangent);n=-tangent if end==0 else tangent
            for j in range(16):casing.triangle([axis[end],rings[end][j],rings[end][(j+1)%16]],5,[n]*3,'stem end')
    return meshes,{'kind':'standalone ten-plane star, twenty folded sculpted leaves, two crossed cylindrical stems','star_plane_normals':star_normals,'reference_scale':scale,'star_apex_z':settings['star_apex_z'],'curved_surface_exception':'Leaf blades and stems intentionally use smooth continuous custom normals, matching curved foliage in the reference; the star alone is faceted and perfectly planar.'}

def shield_outline():
    center=628.;top=(628,60);shoulder=(1069,232);lower=(1002,857);tip=(628,1156)
    right=np.vstack([bezier(top,(750,147),(920,205),shoulder,64),bezier(shoulder,(1090,470),(1052,745),lower,80),bezier(lower,(959,962),(795,1085),tip,80),np.array([tip])])
    left=right[-2:0:-1].copy();left[:,0]=2*center-left[:,0]
    raw=np.vstack([right,left]);scale=6.03/(1156-60)
    xy=np.column_stack([(raw[:,0]-center)*scale,3.015-(raw[:,1]-60)*scale])
    # CCW front contour.
    if np.cross(xy,np.roll(xy,-1,axis=0)).sum()<0:xy=xy[::-1]
    return xy,raw,scale

def iron_geometry(settings):
    meshes={key:Mesh() for key in MESH_IDS};outline,raw,scale=shield_outline();count=len(outline)
    # A real curved, layered shield profile. Insets scale around its vertical center.
    profiles=[(1.,-.345,'back'),(1.,.035,'outer sidewall'),(.994,.087,'outer rounded edge'),(.986,.119,'outer rounded edge'),(.978,.139,'outer rounded edge'),(.963,.153,'raised satin rim'),(.930,.153,'raised satin rim'),(.901,.153,'raised satin rim'),(.884,.122,'rim inner lip'),(.879,.078,'inner reveal'),(.872,.053,'dark inner channel'),(.868,.036,'plate perimeter')]
    rings=[np.column_stack([outline*s,np.full(count,z)]) for s,z,_ in profiles]
    for pi in range(len(rings)-1):
        role=profiles[pi+1][2]
        target=meshes[MESH_IDS[2 if pi<7 else 5 if pi==7 else 1 if pi==8 else 4]]
        material=5 if pi==0 else 6 if pi<4 else 2 if pi<7 else 8 if pi==7 else 1 if pi==8 else 7
        for i in range(count):
            j=(i+1)%count
            # Rounded outer shoulders interpolate normals in both contour/profile directions.
            def normal_at(profile,index):
                contour=rings[profile][(index+1)%count]-rings[profile][(index-1)%count]
                sweep=rings[min(profile+1,len(rings)-1)][index]-rings[max(profile-1,0)][index]
                n=np.cross(contour,sweep);n/=np.linalg.norm(n)
                expected=np.array([outline[index,0],outline[index,1],.1])
                if n@expected<0:n=-n
                return n
            points=[rings[pi][i],rings[pi][j],rings[pi+1][j],rings[pi+1][i]]
            ns=[normal_at(pi,i),normal_at(pi,j),normal_at(pi+1,j),normal_at(pi+1,i)] if pi<4 else None
            target.quad(points,material,ns,role)
    # Closed back: this floating shape requires no floor cut.
    casing=meshes[MESH_IDS[2]]
    for i in range(count):casing.triangle([[0,0,-.345],rings[0][(i+1)%count],rings[0][i]],5,[[0,0,-1]]*3,'shield back')
    inner=outline*.868
    field=np.load(Path(__file__).resolve().parents[1]/'source/shield_plate_field.npz');heightmap=field['height'];x0,x1,y0,y1=field['bounds']
    def sample(array,x,y):
        fx=np.clip((x-x0)/(x1-x0)*(array.shape[1]-1),0,array.shape[1]-1-1e-5);fy=np.clip((y-y0)/(y1-y0)*(array.shape[0]-1),0,array.shape[0]-1-1e-5);ix=int(fx);iy=int(fy);tx=fx-ix;ty=fy-iy
        return (1-ty)*((1-tx)*array[iy,ix]+tx*array[iy,ix+1])+ty*((1-tx)*array[iy+1,ix]+tx*array[iy+1,ix+1])
    def z_and_gradient(x,y):
        return .036+settings['plate_bow']*sample(heightmap,x,y)
    radial=32
    front=[];front_normals=[]
    for ri in range(radial+1):
        ring=[];ns=[];fraction=ri/radial
        for x,y in inner*fraction:
            z=.036 if ri==radial else z_and_gradient(x,y);h=1e-4;side=-1 if x<0 else 1
            evalx=side*1e-5 if abs(x)<1e-5 else x
            dx=settings['plate_bow']*sample(field['gx'],x,y);dy=settings['plate_bow']*sample(field['gy'],x,y)
            n=np.array([-dx,-dy,1.]);n/=np.linalg.norm(n)
            ring.append([x,y,z]);ns.append(n)
        front.append(ring);front_normals.append(ns)
    # Continuous front plate split at the center ridge.
    for ri in range(radial):
        for i in range(count):
            j=(i+1)%count;points=[front[ri][i],front[ri+1][i],front[ri+1][j],front[ri][j]]
            normals=[front_normals[ri][i],front_normals[ri+1][i],front_normals[ri+1][j],front_normals[ri][j]]
            left=np.mean(points,axis=0)[0]<0;target=meshes[MESH_IDS[0 if left else 3]]
            target.quad(points,0 if left else 3,normals,'bowed shield plate')
    for i in range(count):
        j=(i+1)%count
        left=inner[i,0]+inner[j,0]<0
        meshes[MESH_IDS[0 if left else 3]].quad([front[-1][i], rings[-1][i], rings[-1][j],front[-1][j]],0 if left else 3,region='plate seated edge')
    return meshes,{'kind':'full shield with bowed metal plate, smooth dome, raised satin border, inner reveal and recessed channel','outline_world':outline.tolist(),'reference_outline_pixels':raw.tolist(),'reference_scale':scale,'plate_bow':settings['plate_bow'],'curved_surface_exception':'Shield plate and rounded shoulder are intentionally smoothly curved; no triangular faceted patchwork or added center emblem.'}
