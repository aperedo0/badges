import bpy,numpy as np,math,json
from mathutils import Matrix

def sculpt_rim(obj,D):
 old=obj.data;verts=np.array([tuple(v.co) for v in old.vertices],np.float64);faces=[list(p.vertices) for p in old.polygons];edgepairs=[tuple(e.vertices) for e in old.edges];edgeid={tuple(sorted(e)):i for i,e in enumerate(edgepairs)};parent=list(range(len(edgepairs)))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 def union(a,b):parent[find(a)]=find(b)
 for f in faces:
  es=[edgeid[tuple(sorted((f[i],f[(i+1)%len(f)])))] for i in range(len(f))]
  if len(f)==4:union(es[0],es[2]);union(es[1],es[3])
  else:union(es[0],es[1]);union(es[1],es[2])
 lengths={}
 for i,(a,b) in enumerate(edgepairs):root=find(i);lengths[root]=max(lengths.get(root,0),float(np.linalg.norm(verts[a]-verts[b])))
 counts={i:max(1,int(math.ceil(lengths[find(i)]/.018))) for i in range(len(edgepairs))};cache={};points=[];newfaces=[];smooth=[]
 def add(key,p):
  if key not in cache:cache[key]=len(points);points.append(p)
  return cache[key]
 def edge(a,b,t,n):
  if t==0:return add(('v',a),verts[a])
  if t==n:return add(('v',b),verts[b])
  if a>b:a,b=b,a;t=n-t
  return add(('e',a,b,t,n),verts[a]*(1-t/n)+verts[b]*(t/n))
 for fi,f in enumerate(faces):
  if len(f)==4:
   a,b,c,d=f;nu=counts[edgeid[tuple(sorted((a,b)))]];nv=counts[edgeid[tuple(sorted((b,c)))]];grid={}
   for j in range(nv+1):
    for i in range(nu+1):
     if j==0:k=edge(a,b,i,nu)
     elif i==nu:k=edge(b,c,j,nv)
     elif j==nv:k=edge(d,c,i,nu)
     elif i==0:k=edge(a,d,j,nv)
     else:
      u,v=i/nu,j/nv;k=add(('f',fi,i,j),verts[a]*(1-u)*(1-v)+verts[b]*u*(1-v)+verts[c]*u*v+verts[d]*(1-u)*v)
     grid[i,j]=k
   for j in range(nv):
    for i in range(nu):newfaces.append([grid[i,j],grid[i+1,j],grid[i+1,j+1],grid[i,j+1]]);smooth.append(old.polygons[fi].use_smooth)
  else:
   a,b,c=f;n=counts[edgeid[tuple(sorted((a,b)))]];grid={}
   for i in range(n+1):
    for j in range(n+1-i):
     if j==0:k=edge(a,b,i,n)
     elif i==0:k=edge(a,c,j,n)
     elif i+j==n:k=edge(b,c,j,n)
     else:k=add(('f',fi,i,j),verts[a]*(1-(i+j)/n)+verts[b]*(i/n)+verts[c]*(j/n))
     grid[i,j]=k
   for i in range(n):
    for j in range(n-i):
     newfaces.append([grid[i,j],grid[i+1,j],grid[i,j+1]]);smooth.append(old.polygons[fi].use_smooth)
     if i+j<n-1:newfaces.append([grid[i+1,j],grid[i+1,j+1],grid[i,j+1]]);smooth.append(old.polygons[fi].use_smooth)
 rest=np.asarray(points,np.float64);rot=np.array(Matrix.Rotation(math.radians(32),3,'Y'));q=np.c_[rest[:,0],rest[:,2],-rest[:,1]]@rot;baseline=q.copy();x,y,z=q.T;front=np.clip((z-1.69)/.05,0,1);back=np.clip((-z-1.69)/.05,0,1);right=np.clip((x-2.64)/.05,0,1);left=np.clip((-x-2.64)/.05,0,1)
 def ss(a,b,v):t=np.clip((v-a)/(b-a),0,1);return t*t*(3-2*t)
 guard=(1-ss(2.25,2.58,np.abs(x)))
 # Retain the original front and rear rail rivet seating regions exactly.
 for xc in [-1.1277,1.1234]:guard*=ss(.105,.17,np.hypot(x-xc,y+1.96575))
 mid=ss(-2.205,-2.15,y)*(1-ss(-1.78,-1.73,y));dents=np.zeros(len(q))
 for xc,yc,rx,ry,depth in [(-1.72,-1.98,.18,.13,.004),(-.72,-1.91,.23,.16,.003),(1.35,-2.00,.19,.14,.0045)]:dents-=depth*np.exp(-((x-xc)/rx)**2-((y-yc)/ry)**2)
 q[:,2]+=dents*front*guard*mid;q[:,2]-=dents*back*guard*mid
 chips=np.zeros(len(q))
 for xc,width,depth in [(-1.97,.045,.016),(-1.18,.030,.010),(-.68,.065,.022),(.55,.035,.013),(1.42,.055,.020),(1.88,.032,.012)]:chips+=depth*np.maximum(1-np.abs((x-xc)/width),0)**1.25
 top=np.exp(-((y+1.714)/.035)**2);q[:,1]-=chips*top*front*guard*.78;q[:,2]-=.45*chips*top*front*guard*.78
 bottom=np.zeros(len(q))
 for xc,width,depth in [(-1.65,.06,.010),(-.95,.045,.008),(.8,.07,.014),(1.9,.045,.008)]:bottom+=depth*np.maximum(1-np.abs((x-xc)/width),0)**1.4
 fade=np.exp(-((y+2.2175)/.034)**2);q[:,1]+=bottom*fade*front*guard*.82;q[:,2]-=.4*bottom*fade*front*guard*.82
 transformed=(q-baseline)@rot.T;world=rest+np.c_[transformed[:,0],-transformed[:,2],transformed[:,1]];mesh=bpy.data.meshes.new('Locally forged lower rim');mesh.from_pydata(world.tolist(),[],newfaces);mesh.update()
 for p,v in zip(mesh.polygons,smooth):p.use_smooth=v
 loop_edges=np.empty(len(mesh.loops),np.int32);mesh.loops.foreach_get('edge_index',loop_edges);assert np.all(np.bincount(loop_edges,minlength=len(mesh.edges))==2),'Unstitched adaptive surface'
 obj.data=mesh;np.savez_compressed(D/'sculpt_fields.npz',rest=rest,local_rest=baseline,local_deformed=q,faces=np.array([len(f) for f in newfaces],np.int32));print('Adaptive closed rim',len(mesh.vertices),len(mesh.polygons),flush=True);return rest
