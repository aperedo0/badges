"""Native Blender sculpture for the owner's torch and radial sunburst."""

def torch_xy(points):
    return (np.asarray(points,float)-[626,581])*[2.42/477,-2.42/477]

def bezier_outline(start,segments,steps=16):
    points=[];p=np.array(start,float)
    for c1,c2,end in segments:
        c1,c2,end=map(lambda q:np.array(q,float),(c1,c2,end))
        for t in np.linspace(0,1,steps,endpoint=False):
            points.append((1-t)**3*p+3*(1-t)**2*t*c1+3*(1-t)*t*t*c2+t**3*end)
        p=end
    return torch_xy(points)

def sculpted_plate(name,outline,base,relief):
    from mathutils.geometry import delaunay_2d_cdt
    from collections import Counter
    outline=np.asarray(outline,float)
    if np.cross(outline,np.roll(outline,-1,axis=0)).sum()<0:outline=outline[::-1]
    # Uniform triangles prevent stretched faces from corrugating reflections.
    gx,gy=np.meshgrid(np.arange(outline[:,0].min(),outline[:,0].max(),.028),
                      np.arange(outline[:,1].min(),outline[:,1].max(),.028))
    grid=np.c_[gx.ravel(),gy.ravel()];inside=np.zeros(len(grid),bool)
    for a,b in zip(outline,np.roll(outline,-1,axis=0)):
        if abs(b[1]-a[1])<1e-10:continue
        inside^=((a[1]>grid[:,1])!=(b[1]>grid[:,1])) & (grid[:,0]<(b[0]-a[0])*(grid[:,1]-a[1])/(b[1]-a[1])+a[0])
    coords=np.concatenate([outline,grid[inside]])
    result=delaunay_2d_cdt([Vector(v) for v in coords],[],[list(range(len(outline)))],1,1e-6,False)
    edges=np.roll(outline,-1,axis=0)-outline
    lengths=np.sum(edges*edges,axis=1)
    points=[]
    for v in result[0]:
        p=np.array(v[:]);t=np.clip(np.sum((p-outline)*edges,axis=1)/lengths,0,1)
        distance=np.sqrt(np.min(np.sum((p-(outline+t[:,None]*edges))**2,axis=1)))
        # Broad real curvature across the ribbon, with a short rolled edge.
        points.append([*p,base+relief*math.sin(min(distance/.24,1)*math.pi/2)])
    faces=[tuple(f) for f in result[2]];count=len(points)
    edges=Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3))
    boundary=[(f[i],f[(i+1)%3]) for f in faces for i in range(3)
              if edges[tuple(sorted((f[i],f[(i+1)%3])))]==1]
    # Extrude directly backward. Normal-based solidification pushes grazing
    # vertices sideways and makes a serrated lip outside the flame silhouette.
    points.extend([[p[0],p[1],base-.060] for p in points.copy()])
    front_count=len(faces)
    faces.extend(tuple(i+count for i in reversed(f)) for f in faces.copy())
    faces.extend((i,i+count,j+count,j) for i,j in boundary)
    obj=mesh_object(name,points,faces,'bronze',True)
    for polygon in obj.data.polygons:
        if polygon.index>=front_count:polygon.use_smooth=False
    return obj

def torch_stem():
    profile=[(845,61),(851,72),(857,71),(861,57),(867,57),(871,54),
             (879,53),(884,39),(893,35),(928,30),(977,30),(1014,34),
             (1031,41),(1035,51),(1044,51),(1049,43)]
    points=[];count=64
    for y,r in profile:
        cy=torch_xy([[626,y]])[0,1];radius=r*2.42/477
        for a in np.linspace(0,math.tau,count,endpoint=False):
            points.append([radius*math.cos(a),cy,.125+radius*.43*math.sin(a)])
    faces=[]
    for j in range(len(profile)-1):
        for i in range(count):
            k=(i+1)%count;faces.append((j*count+k,(j+1)*count+k,(j+1)*count+i,j*count+i))
    faces.extend([tuple(range(count-1,-1,-1)),tuple((len(profile)-1)*count+i for i in range(count))])
    mesh_object('Turned bronze torch handle and collars',points,faces,'bronze',True)

def torch():
    disk('Recessed warm charcoal torch backing',2.445,.044,'backdrop')
    for i in range(24):
        a=i*math.tau/24
        radial=np.array([math.cos(a),math.sin(a)]);tangent=np.array([-radial[1],radial[0]])
        # The gap between the two flames must not reveal disconnected roots.
        inner=1.06 if i in [1,2,3,4] else .78
        tip=radial*2.19;left=radial*inner+tangent*.050;right=radial*inner-tangent*.050
        ridge=radial*(inner+.06)
        points=[[*tip,.081],[*left,.081],[*right,.081],[*ridge,.094]]
        mesh_object('Faceted sunburst ray '+str(i+1),points,
                    [(0,1,3),(0,3,2),(1,2,3),(0,2,1)],'bronze')
    main=bezier_outline((624,147),[
        ((606,192),(645,263),(600,339)),
        ((573,390),(519,433),(482,488)),
        ((444,540),(431,595),(456,650)),
        ((463,671),(473,686),(486,700)),
        ((517,705),(552,706),(587,700)),
        ((556,663),(560,618),(591,574)),
        ((627,529),(675,492),(704,445)),
        ((733,389),(725,319),(697,271)),
        ((671,226),(632,202),(624,147))])
    sculpted_plate('Large curling bronze flame',main,.125,.162)
    small=bezier_outline((750,437),[
        ((795,492),(825,608),(746,700)),
        ((699,704),(645,704),(597,700)),
        ((569,662),(587,615),(616,579)),
        ((636,555),(649,535),(661,512)),
        ((644,556),(645,602),(669,625)),
        ((716,613),(760,559),(762,511)),
        ((766,481),(756,453),(750,437))])
    sculpted_plate('Small returning bronze flame',small,.160,.153)
    torch_stem()
    bowl=bezier_outline((423,756),[
        ((529,756),(719,756),(818,756)),
        ((781,815),(716,845),(625,845)),
        ((533,845),(470,816),(423,756))])
    sculpted_plate('Rounded torch bowl',bowl,.135,.150)
    bevel_solid('Broad beveled torch lip',torch_xy([[359,700],[891,700],[835,756],[413,756]]),.185,.337)
