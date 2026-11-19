assert 'Status: APPROVED (review round 1).' in (P/'mechanism26/PLAN.md').read_text()
assert 'Status: APPROVED (review round 2).' in (P/'mechanism25/PLAN.md').read_text()
S25=lambda y:.95*y-.12275
inv25=yaw.inverted();CY25=S25(.64);CZ25=2.;created25=[]
def coords25(ob):
 return np.array([tuple(inv25@Vector((v.co.x,v.co.z,-v.co.y))) for v in ob.data.vertices])
def write25(ob,v):
 for vv,q in zip(ob.data.vertices,v):
  q=yaw@Vector(q);vv.co=(q.x,-q.z,q.y)
 ob.data.update()
def cylinder25(name,c,r,length,axis='X',bevel=0):
 bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,segments=64,radius1=r,radius2=r,depth=length)
 rot=Matrix.Rotation(math.pi/2,3,'Y') if axis=='X' else Matrix.Identity(3)
 for v in bm.verts:v.co=rot@v.co+Vector(c)
 for f in bm.faces:f.smooth=len(f.verts)==4
 return finish(bm,name,hardware,bevel)
def annular25(name,a,b,R,r,bev=.006,profile_override=None):
 profile=np.array(profile_override if profile_override is not None else [(a+bev,R),(a,R-bev),(a,r+bev),(a+bev,r),(b-bev,r),(b,r+bev),(b,R-bev),(b-bev,R)])
 V=[];F=[];N=64
 for x,rho in profile:
  for j in range(N):u=j*2*math.pi/N;V.append((x,CY25+rho*math.cos(u),CZ25+rho*math.sin(u)))
 for k in range(len(profile)):
  for j in range(N):F.append([k*N+j,k*N+(j+1)%N,((k+1)%len(profile))*N+(j+1)%N,((k+1)%len(profile))*N+j])
 ob=solid(name,V,F,hardware,0,True);ob['allowed_euler']=[0];prove_part(ob,name);created25.append(name)
 normals=[];sgn=np.sign(np.cross(profile,np.roll(profile,-1,axis=0)).sum())
 for face in ob.data.polygons:
  k=face.index//N;dx,dr=profile[(k+1)%len(profile)]-profile[k];nn=np.array([dr,-dx])*sgn;nn/=np.linalg.norm(nn)
  for li in face.loop_indices:
   j=ob.data.loops[li].vertex_index%N;u=j*2*math.pi/N;n=yaw@Vector((nn[0],nn[1]*math.cos(u),nn[1]*math.sin(u)));normals.append((n.x,-n.z,n.y))
 ob.data.normals_split_custom_set(normals);return ob

def cut25(ob,cutter,label,allowed):
 prior=list(ob.get('allowed_euler',[2]));ob['allowed_euler']=sorted(set(prior+allowed));union_handle21(ob,cutter,label,'DIFFERENCE');ob['allowed_euler']=allowed;prove_part(ob,label)

# Rebuild the hinge as independent true circular solids after height correction.
center=annular25('Chest Front Hasp Barrel',-.240,.240,.168,.086)
for sx in (-1,1):
 a,b=sorted([sx*.250,sx*.360]);annular25(f'Chest Fixed Front Hinge Knuckle {sx}',a,b,.190,.086)
pin=cylinder25('Chest Front Hinge Pin',(0,CY25,2),.078,.800,bevel=.008);prove_part(pin,pin.name);created25.append(pin.name)
mount=sc.objects['Chest Hasp Mount'];cut25(mount,cylinder25('Hinge mount moving sleeve relief',(0,CY25,2),float(globals().get('hinge_relief_radius',.188)),.496),'Mount circular sleeve clearance',[2])
cut25(sc.objects['Chest Upper Lid Rim'],cylinder25('Hidden upper rail sleeve seat',(0,CY25,2),float(globals().get('hinge_relief_radius',.188)),.496),'Hidden lid rail sleeve clearance',[0])
# Narrow the existing measured latch without altering its centerline or height.
for name in ['Chest Curved Hasp Tongue','Chest Hasp Edge Rail -1','Chest Hasp Edge Rail 1']:
 ob=sc.objects[name];v=coords25(ob)
 if 'Edge Rail' in name:
  side=int(name.split()[-1]);v[:,0]+=side*(.2085-.2335)
 else:v[:,0]*=.455/.505
 write25(ob,v)
 # Exact pin clearance is needed only if its root crosses the circular bore.
 cutter=cylinder25('Moving latch pin clearance '+name,(0,CY25,2),.086,.800)
 cut25(ob,cutter,name+' pin clearance',[2,0])
 if name=='Chest Curved Hasp Tongue':
  cut25(ob,cylinder25('Latch real retaining pin bore',(0,S25(-.025),1.970),.032,.800),name+' retaining bore',[0,-2])
 created25.append(name)
for sx in (-1,1):
 ob=sc.objects[f'Chest Hasp Pivot Dome {sx}'];v=coords25(ob);v[:,0]+=sx*.040;write25(ob,v)
# Actual case surfaces, using the original outlined shapes and aligned keyhole.
hole[:,1]=S25(hole[:,1]);back25=back.copy();back25[:,1]=S25(back25[:,1]);inner25=offset_outline(back25,.065)
caseback=shield('Chest Case Back With Key Bore',back25,1.780,1.815,.008);caseback['allowed_euler']=[0];prove_part(caseback,caseback.name)
N=len(back25);V=np.vstack([np.c_[q,np.full(N,z)] for q,z in [(back25,1.810),(back25,2.045),(inner25,2.045),(inner25,1.810)]]);F=[]
for k in range(4):
 for j in range(N):n=(k+1)%4;nj=(j+1)%N;F.append([k*N+j,k*N+nj,n*N+nj,n*N+j])
walls=solid('Chest Hollow Lock Case Walls',V,F,hardware,0);walls['allowed_euler']=[0];prove_part(walls,walls.name)
for sx in (-1,1):
 a,b=sorted([sx*.245,sx*.360]);cheek=box(f'Case receiver cheek {sx}',[a,-.250,float(globals().get('receiver_cheek_rear_z',1.830))],[b,-.040,2.080],hardware,.006);union_handle21(walls,cheek,'Attached receiver cheek '+str(sx));walls['allowed_euler']=[0];prove_part(walls,walls.name)
cut25(walls,box('Case receiver open pocket',[-.240,-.245,1.830],[.240,-.065,2.250],hardware,0),'Actual case receiver opening',[0])
cut25(walls,cylinder25('Receiver supported pin guides',(0,S25(-.025),1.970),.033,1.2),'Actual supported receiver guide bores',[-4])
cover=shield('Chest Lock Backing With Bore',back25,2.040,2.080,.008);cover['allowed_euler']=[0]
cut25(cover,box('Front cover actual receiver opening',[-.240,-.245,1.830],[.240,-.065,2.250],hardware,0),'Front cover receiver mouth',[0])
# Restore the raised decorative shield without creating a second floating plate.
for name in ['Chest Lock Border With Bore','Chest Shield Lock Plate With Bore']:
 ob=sc.objects[name];v=coords25(ob);z=1.88+(v[:,2]-1.88)*2
 if 'Border' in name:z=np.interp(z,[1.975,2.015,2.115],[2.040,2.075,2.115])
 else:z=2.080+(z-2.020)*(.027/.087)
 v[:,2]=z;write25(ob,v);ob['allowed_euler']=[0];prove_part(ob,name)
 cut25(ob,box('Raised face receiver clearance '+name,[-.240,-.245,1.830],[.240,-.065,2.250],hardware,0),name+' receiver clearance',[0])
for j in range(7):
 ob=sc.objects[f'Chest Lock Rivet {j}'];v=coords25(ob);old=1.88+.5*((2.0 if j<2 else 2.108)-1.88);new=2.085 if j<2 else 2.112;v[:,2]+=new-old;write25(ob,v)
# Source ownership is explicit, even before the animation controls are added.
moving=['Chest Front Hasp Barrel','Chest Curved Hasp Tongue','Chest Hasp Edge Rail -1','Chest Hasp Edge Rail 1']
fixed=['Chest Hasp Mount','Chest Front Hinge Pin','Chest Fixed Front Hinge Knuckle -1','Chest Fixed Front Hinge Knuckle 1']
(C/'mechanism_parts.json').write_text(json.dumps(dict(stage='Front hinge and hollow case constructed, clearance proof pending',moving_hasp=moving,lid_fixed=fixed,case_support='Chest Central Lock Strap',body_fixed_case=[caseback.name,walls.name,cover.name,'Chest Lock Border With Bore','Chest Shield Lock Plate With Bore'],actual_euler_proof=proof[-30:],complete_lock=False,opening_rig_complete=False),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True)
print('Saved actual front pin, knuckles, sleeve, bored latch and hollow shield case. Continuous motion certification remains pending.')
