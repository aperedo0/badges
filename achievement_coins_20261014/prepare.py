"""Reference-traced reliefs, authored on the unchanged shipped silver coin."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/achievement_coin_mpl')
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_closing, binary_fill_holes, distance_transform_edt, gaussian_filter, label, map_coordinates
from scipy.spatial import Delaunay,cKDTree
from matplotlib.figure import Figure
from matplotlib.path import Path as PolygonPath

ROOT = Path(__file__).resolve().parent
TEMP = Path('/tmp/achievement_coins_20261014')
TEMP.mkdir(exist_ok=True)
REFS = {
    'clean': ('ChatGPT Image Oct 13, 2026, 06_56_52 PM.png', (624, 609, 517)),
    'hourglass_teal': ('ChatGPT Image Oct 13, 2026, 08_20_22 PM.png', (623, 606, 537)),
    'hourglass_gold': ('ChatGPT Image Oct 13, 2026, 08_21_10 PM.png', (623, 606, 537)),
    'sunrise': ('ChatGPT Image Oct 13, 2026, 11_39_55 AM.png', (625, 612, 507)),
    'sprout': ('Polished Emerald Sprout Medallion.png', (625, 599, 575)),
}

def bezier(start, sections, samples=18):
    points = [np.asarray(start, float)]
    for c1, c2, end in sections:
        p = points[-1]; a,b,c = map(lambda q: np.asarray(q, float), (c1,c2,end))
        for t in np.linspace(0,1,samples+1)[1:]:
            points.append((1-t)**3*p+3*(1-t)**2*t*a+3*(1-t)*t*t*b+t**3*c)
    return np.array(points)

def polygon_mask(points, shape):
    im=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(im).polygon([tuple(p) for p in points],fill=255)
    return np.asarray(im)>0

def circle_mask(x,y,r,shape):
    yy,xx=np.indices(shape);return (xx-x)**2+(yy-y)**2 <= r*r

def world(xy, circle):
    x,y,r=circle
    return np.stack([(xy[...,0]-x)*3.015/r,(y-xy[...,1])*3.015/r],-1)

def relief(mask, circle, depth=.22, base=.09, step=12, flat=False, dome=False, glass=False, analytic=False):
    """A solid embossed face, with a closed wall and actual curved height."""
    # Closed strokes are rings, not filled plates. Preserve their inner holes.
    mask=np.asarray(mask,bool)
    dist=gaussian_filter(distance_transform_edt(mask),1.2)
    fig=Figure();ax=fig.subplots();cs=ax.contour(mask.astype(float),levels=[.5])
    edges=[]
    for contour in cs.allsegs[0]:
        if len(contour)<8:continue
        length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(contour,axis=0),axis=1))]
        d=np.arange(0,length[-1],max(2,step/3))
        edges.append(np.stack([np.interp(d,length,contour[:,i]) for i in range(2)],-1))
    if not edges:return None
    yy,xx=np.meshgrid(np.arange(0,mask.shape[0],step),np.arange(0,mask.shape[1],step),indexing='ij')
    inside=mask[yy,xx]
    inner=np.stack([xx[inside],yy[inside]],-1)
    # Fine samples only in the bevel where curvature needs them.
    sy,sx=np.meshgrid(np.arange(0,mask.shape[0],7),np.arange(0,mask.shape[1],7),indexing='ij')
    near=mask[sy,sx]&(dist[sy,sx]<12)
    points=np.unique(np.round(np.concatenate(edges+[inner,np.stack([sx[near],sy[near]],-1)]),5),axis=0)
    tri=Delaunay(points).simplices
    samples=points[tri].mean(1)
    keep=map_coordinates(mask.astype(float),[samples[:,1],samples[:,0]],order=0,mode='constant')>.5
    for a,b in [(0,1),(1,2),(2,0)]:
        mid=(points[tri[:,a]]+points[tri[:,b]])/2
        keep &= map_coordinates(mask.astype(float),[mid[:,1],mid[:,0]],order=1,mode='constant')>.2
    tri=tri[keep]
    xy=world(points,circle)
    d=map_coordinates(dist,[points[:,1],points[:,0]],order=1,mode='nearest')*3.015/circle[2]
    if dome:
        height=depth*np.sqrt(np.clip(d/max(d.max(),.001),0,1))
    else:
        reach=min(.085,max(.008,float(np.quantile(d[d>0],.995))))
        u=np.clip(d/reach,0,1)
        height=depth*np.sqrt(np.maximum(0,2*u-u*u))
    if glass:
        center=(mask.shape[1]-1)/2
        rows=mask.any(1)
        l=np.argmax(mask,axis=1);rr=mask.shape[1]-1-np.argmax(mask[:,::-1],axis=1)
        yc=np.clip(points[:,1].round().astype(int),0,len(rows)-1)
        widths=np.maximum(1,(rr[yc]-l[yc])/2);center=(rr[yc]+l[yc])/2
        height=.48*world(np.stack([widths+circle[0],np.full(len(points),circle[1])],-1),circle)[:,0]*np.sqrt(np.maximum(0,1-((points[:,0]-center)/widths)**2))
    if analytic:
        l=np.argmax(mask,axis=1);rr=mask.shape[1]-1-np.argmax(mask[:,::-1],axis=1)
        valid=mask.any(1)
        width=np.where(valid,(rr-l)/2,0.)
        center=np.where(valid,(rr+l)/2,circle[0])
        width=gaussian_filter(width,2.)
        center=np.interp(np.arange(len(valid)),np.flatnonzero(valid),center[valid])
        center=gaussian_filter(center,2.)
        row=np.clip(points[:,1],0,len(valid)-1)
        wr=np.interp(row,np.arange(len(width)),width)
        cr=np.interp(row,np.arange(len(center)),center)
        height=depth*np.sqrt(np.maximum(0,wr*wr-(points[:,0]-cr)**2))/max(width.max(),1.)
    p=np.c_[xy,base+height]
    # Delaunay is counter-clockwise in image coordinates, opposite to world Y.
    cross=np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]])
    flip=cross[:,2]<0;tri[flip]=tri[flip][:,[0,2,1]]
    from collections import Counter
    count=Counter(tuple(sorted(e)) for f in tri for e in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])])
    directed={tuple(sorted((a,b))):(a,b) for f in tri for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]}
    boundary=[directed[e] for e,n in count.items() if n==1]
    n=len(p);back=p.copy();back[:,2]=base-.02
    wall=[]
    for a,b in boundary:
        for f in [[a,n+a,n+b],[a,n+b,b]]:wall.append(np.array(f))
    # The reverse of each raised piece is buried in the inset, not rendered.
    alltri=np.concatenate([tri,np.array(wall)])
    allpoints=np.concatenate([p,back])
    normals=np.zeros_like(p)
    fn=np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]])
    for j in range(3):np.add.at(normals,tri[:,j],fn)
    normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12)
    if not flat:
        distances,neighbors=cKDTree(xy).query(xy,k=min(24,len(xy)))
        weights=np.exp(-.5*(distances/.032)**2)*(distances<.075)
        normals=(normals[neighbors]*weights[:,:,None]).sum(1)/np.maximum(weights.sum(1)[:,None],1e-12)
        normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12)
    # Rounded relief edges continue the nearby face, avoiding a thin mirrored rim.
    weight=.65*np.clip(1-d/.07,0,1)
    normals=normals*(1-weight[:,None])+np.array([0,0,1])*weight[:,None]
    normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12)
    corner=normals[tri] if not flat else np.repeat((fn/np.maximum(np.linalg.norm(fn,axis=1,keepdims=True),1e-12))[:,None],3,axis=1)
    backs=np.repeat(np.array([[[0,0,-1.]]]),len(tri),axis=0);backs=np.repeat(backs,3,axis=1)
    wp=allpoints[np.array(wall)]
    wn=np.cross(wp[:,1]-wp[:,0],wp[:,2]-wp[:,0]);wn/=np.maximum(np.linalg.norm(wn,axis=1,keepdims=True),1e-12)
    wn=.3*wn+.7*np.array([0,0,1]);wn/=np.linalg.norm(wn,axis=1,keepdims=True)
    walln=np.repeat(wn[:,None],3,axis=1)
    return {'points':allpoints,'triangles':alltri,'normals':np.concatenate([corner,walln]),'front_count':len(tri)}

def prepare(name):
    filename,circle=REFS[name];src=Path('/Users/antonioperedo/Downloads')/filename
    image=np.asarray(Image.open(src).convert('RGB'),float)/255
    shape=image.shape[:2];yy,xx=np.indices(shape)
    cx,cy,rad=circle;disk=(xx-cx)**2+(yy-cy)**2< (rad*2.505/3.015)**2
    features=[]
    def add(role,mask,curve=None,curve_radius=None,curve_z=None,**kwargs):
        m=relief(mask&disk,circle,**kwargs)
        if m is None:return
        m['role']=role
        if curve is not None:
            m['blender_curve']={'points':world(np.asarray(curve),circle).tolist(),
                                'radius':curve_radius,'z':curve_z}
        features.append(m)
    if name=='clean':
        drop=bezier((627,276),[
            ((647,277),(668,391),(724,464)),((783,545),(839,607),(836,702)),
            ((833,814),(756,891),(639,897)),((514,898),(418,813),(414,703)),
            ((403,608),(475,523),(530,453)),((591,369),(605,277),(627,276))])
        add('water',polygon_mask(drop,shape),depth=.57,dome=True,analytic=True,step=12)
        add('water',circle_mask(401,429,77,shape),depth=.31,dome=True,analytic=True,step=10)
        add('water',circle_mask(335,613,47,shape),depth=.20,dome=True,analytic=True,step=8)
        star=bezier((875,341),[
            ((888,440),(889,452),(982,469)),((889,484),(889,495),(879,609)),
            ((865,500),(861,487),(771,469)),((860,453),(862,441),(875,341))])
        add('silver',polygon_mask(star,shape),depth=.24,dome=True,step=8)
    elif name.startswith('hourglass'):
        glass=bezier((508,318),[
            ((555,308),(704,308),(747,318)),((794,324),(787,419),(750,461)),
            ((715,502),(638,538),(629,582)),((619,626),(692,676),(739,724)),
            ((784,770),(780,833),(749,846)),((695,853),(559,853),(507,846)),
            ((474,832),(477,770),(521,723)),((568,674),(624,630),(615,587)),
            ((612,544),(552,510),(510,466)),((473,427),(465,326),(508,318))])
        gm=polygon_mask(glass,shape)
        add('glass',gm,base=.09,glass=True,step=12)
        # Frame follows the glass outline with actual round metal.
        stroke=Image.new('L',(shape[1],shape[0]));dr=ImageDraw.Draw(stroke)
        dr.line([tuple(p) for p in glass],fill=255,width=18,joint='curve')
        add('silver',np.asarray(stroke)>0,base=.12,depth=.17,step=7,
            curve=glass,curve_radius=.054,curve_z=.175)
        for bounds in [(373,246,874,302),(373,873,874,936)]:
            box=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(box).rounded_rectangle(bounds,radius=23,fill=255)
            add('silver',np.asarray(box)>0,base=.15,depth=.19,step=12)
        for x in (428,817):
            ys=np.array([309,327,354,440,477,503,556,568,599,610,675,704,825,844,861])
            radii=np.array([21,16,9,16,21,18,9,26,26,9,21,18,9,21,27])
            dense=np.arange(309,862,3);r=np.interp(dense,ys,radii)
            r=gaussian_filter(r,1.2)
            poly=np.concatenate([np.c_[x-r,dense],np.c_[x+r,dense][::-1]])
            add('silver',polygon_mask(poly,shape),base=.14,depth=.19,dome=True,analytic=True,step=10)
        upper=bezier((494,421),[
            ((585,414),(694,413),(762,417)),((744,467),(689,511),(650,550)),
            ((631,570),(629,595),(626,610)),((622,576),(610,550),(591,530)),
            ((550,497),(512,462),(494,421))])
        lower=bezier((487,830),[
            ((543,812),(585,781),(625,737)),((667,783),(720,814),(766,832)),
            ((683,849),(562,848),(487,830))])
        # Sand is real relief in the two bulbs, and the stream has its own mesh.
        add('sand',polygon_mask(upper,shape)&gm,base=.39,depth=.025,step=13)
        add('sand',polygon_mask(lower,shape)&gm,base=.40,depth=.025,step=13)
        stream=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(stream).line([(626,586),(626,743)],fill=255,width=3)
        add('sand',np.asarray(stream)>0,base=.13,depth=.04,step=3)
        # Emboss the sand on the curved glass face so the opaque coin relief
        # cannot cover it. This is a relief medallion, not a separate vessel.
        left=np.argmax(gm,axis=1);right=gm.shape[1]-1-np.argmax(gm[:,::-1],axis=1)
        for feature in features:
            if feature['role']!='sand':continue
            points=feature['points'];front_vertices=len(points)//2
            pixels_x=cx+points[:,0]*rad/3.015
            pixels_y=cy-points[:,1]*rad/3.015
            rows=np.clip(np.rint(pixels_y).astype(int),0,gm.shape[0]-1)
            half=np.maximum(1,(right[rows]-left[rows])/2)
            center=(right[rows]+left[rows])/2
            glass_z=.09+.48*half*3.015/rad*np.sqrt(np.maximum(0,1-((pixels_x-center)/half)**2))
            points[:front_vertices,2]=glass_z[:front_vertices]+.018
            points[front_vertices:,2]=glass_z[front_vertices:]+.004
            triangles=feature['triangles']
            face_normals=np.cross(points[triangles[:,1]]-points[triangles[:,0]],points[triangles[:,2]]-points[triangles[:,0]])
            face_normals/=np.maximum(np.linalg.norm(face_normals,axis=1,keepdims=True),1e-12)
            normals=np.zeros_like(points)
            for corner in range(3):np.add.at(normals,triangles[:,corner],face_normals)
            normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12)
            feature['normals']=normals[triangles]
    elif name=='sunrise':
        for ray in [
            [(627,241),(593,508),(657,508)],
            [(407,344),(499,549),(550,529)],
            [(293,484),(420,598),(468,569)],
            [(294,618),(429,660),(433,635)],
            [(850,344),(705,529),(754,549)],
            [(962,484),(793,569),(835,598)],
            [(962,618),(821,635),(826,660)],
        ]:
            add('bronze',polygon_mask(ray,shape),base=.105,depth=.155,step=14)
            features[-1]['blender_plate']={'points':world(np.asarray(ray),circle).tolist(),
                'radius':.018,'z':.11,'extrude':.065}
        phi=np.linspace(np.pi,0,100)
        sun=np.c_[627+182*np.cos(phi),704-182*np.sin(phi)]
        sunmask=polygon_mask(sun,shape)&(yy<=672)
        add('bronze',sunmask,base=.10,depth=.25,dome=True,analytic=True,step=16)
        horizon=bezier((211,716),[((449,657),(796,657),(1036,716))],samples=100)
        im=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(im).line([tuple(p) for p in horizon],fill=255,width=13,joint='curve')
        add('bronze',np.asarray(im)>0,base=.31,depth=.055,step=9)
        hw=world(horizon,circle)
        features[-1]['blender_curve']={'points':hw[np.linalg.norm(hw,axis=1)<=2.46].tolist(),
            'radius':.035,'z':.32,'closed':False}
        road=bezier((560,672),[
            ((646,669),(751,688),(725,727)),((701,762),(554,787),(551,829)),
            ((545,871),(732,925),(885,947)),((800,1021),(622,1056),(497,989)),
            ((435,956),(400,917),(414,870)),((430,824),(531,784),(598,752)),
            ((641,731),(680,706),(646,695)),((621,686),(583,681),(560,672))])
        add('bronze',polygon_mask(road,shape),base=.13,depth=.13,step=17)
        rw=world(road,circle);radii=np.linalg.norm(rw,axis=1)
        rw*=np.minimum(1,2.47/np.maximum(radii,1e-8))[:,None]
        features[-1]['blender_plate']={'points':rw.tolist(),'radius':.024,'z':.13,'extrude':.08}
    elif name=='sprout':
        left=bezier((267,420),[
            ((413,414),(536,497),(579,617)),((590,653),(581,680),(573,695)),
            ((430,684),(309,598),(267,420))])
        right=bezier((637,663),[
            ((619,509),(756,352),(945,328)),((954,499),(876,637),(651,687)),
            ((645,681),(640,672),(637,663))])
        for leaf in [left,right]:
            add('emerald',polygon_mask(leaf,shape),base=.13,depth=.25,step=58,flat=True,dome=True)
            im=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(im).line([tuple(p) for p in leaf],fill=255,width=14,joint='curve')
            add('gold',np.asarray(im)>0,base=.15,depth=.17,step=9,
                curve=leaf,curve_radius=.038,curve_z=.19)
        stem=bezier((568,687),[
            ((594,731),(605,737),(605,775)),((607,796),(592,807),(569,812)),
            ((602,810),(632,810),(661,817)),((635,802),(626,795),(630,772)),
            ((640,722),(646,700),(653,676)),((641,675),(633,680),(625,695)),
            ((611,718),(606,739),(600,718)),((590,699),(581,691),(568,687))])
        add('gold',polygon_mask(stem,shape),base=.14,depth=.15,step=9)
        features[-1]['blender_plate']={'points':world(stem,circle).tolist(),
            'radius':.018,'z':.225,'extrude':.025}
        for line in [[(284,437),(412,530),(569,687)],[(932,346),(770,508),(649,677)]]:
            im=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(im).line(line,fill=255,width=9,joint='curve')
            add('gold',np.asarray(im)>0,base=.30,depth=.045,step=6)
            features[-1]['blender_curve']={'points':world(np.asarray(line),circle).tolist(),
                'radius':.022,'z':.19,'closed':False,'conform':'emerald'}
        soil=bezier((275,956),[
            ((347,901),(388,886),(426,886)),((488,810),(526,797),(605,802)),
            ((689,801),(739,840),(792,884)),((854,887),(908,918),(948,951)),
            ((864,1123),(369,1130),(275,956))])
        add('soil',polygon_mask(soil,shape),base=.115,depth=.11,step=65,flat=True,dome=True)
        im=Image.new('L',(shape[1],shape[0]));ImageDraw.Draw(im).line([tuple(p) for p in soil[:4*18+1]],fill=255,width=13,joint='curve')
        add('gold',np.asarray(im)>0,base=.19,depth=.10,step=10,
            curve=soil[:4*18+1],curve_radius=.033,curve_z=.235)
        features[-1]['blender_curve']['closed']=False
    # A new face laid just above the original inset. Its geometry is untouched.
    angles=np.linspace(0,2*np.pi,256,endpoint=False)
    points=np.r_[[[0.,0.,.044]],np.c_[2.507*np.cos(angles),2.507*np.sin(angles),np.full(256,.044)]]
    triangles=np.array([[0,k+1,(k+1)%256+1] for k in range(256)])
    if name=='sprout':
        parts=[np.array([[0.,0.,.095]])]
        for ring,radius in enumerate([.83,1.67,2.507]):
            a=np.linspace(0,2*np.pi,20,endpoint=False)+(ring%2)*np.pi/20
            z=.044+.058*(1-radius/2.507)+.011*np.sin(3*a+ring)
            if ring==2:z[:]=.044
            parts.append(np.c_[radius*np.cos(a),radius*np.sin(a),z])
        points=np.concatenate(parts);triangles=Delaunay(points[:,:2]).simplices
        normals=np.cross(points[triangles[:,1]]-points[triangles[:,0]],points[triangles[:,2]]-points[triangles[:,0]])
        flip=normals[:,2]<0;triangles[flip]=triangles[flip][:,[0,2,1]];normals[flip]*=-1
        normals/=np.linalg.norm(normals,axis=1,keepdims=True)
        normals=np.repeat(normals[:,None],3,axis=1)
        role='emerald_background'
    else:
        normals=np.tile([0.,0.,1.],(256,3,1));role='background'
    features.append({'role':role,'points':points,'triangles':triangles,
                     'normals':normals,'front_count':len(triangles)})
    out=ROOT/name;out.mkdir(exist_ok=True)
    metadata={'name':name,'reference':str(src),'circle':circle,'features':[]}
    arrays={}
    for i,m in enumerate(features):
        feature={'role':m['role'],'front_count':m['front_count'],'triangles':len(m['triangles'])}
        if 'blender_curve' in m:feature['blender_curve']=m['blender_curve']
        if 'blender_plate' in m:feature['blender_plate']=m['blender_plate']
        metadata['features'].append(feature)
        for key in ['points','triangles','normals']:arrays[f'{i}_{key}']=m[key]
    np.savez_compressed(out/'reliefs.npz',**arrays)
    (out/'design.json').write_text(json.dumps(metadata,indent=2))
    # A compact geometry mask for development only.
    view=Image.fromarray((image*.28*255).astype('uint8'))
    for i,m in enumerate(features[:-1]):
        pts=np.array(m['points']);xy=np.c_[cx+pts[:,0]*rad/3.015,cy-pts[:,1]*rad/3.015]
        draw=ImageDraw.Draw(view)
        for t in m['triangles'][:m['front_count']]:
            if i%2==0:draw.line([tuple(xy[j]) for j in list(t)+[t[0]]],fill=(100,160,180),width=1)
    view.resize((480,480)).save(TEMP/(name+'_geometry.png'))
    print(name,len(features),'reliefs',sum(len(m['triangles']) for m in features),'front solid triangles',flush=True)

if __name__=='__main__':
    import sys
    for name in sys.argv[1:] or REFS:prepare(name)
