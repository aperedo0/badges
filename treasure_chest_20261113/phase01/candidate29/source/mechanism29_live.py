assert 'Status: APPROVED (round 2 numeric build gates).' in (P/'mechanism29/PLAN.md').read_text()
exec(compile((P/'tools/mechanism28_live.py').read_text(),'mechanism28_live.py','exec'))
KY29=-.536
# Stage one: the real keyed cam and its front supported, axially capturing bearing.
cam=cylinder25('Chest Rotating Keyed Cam',(0,KY29,(1.875+1.970)/2),.175,1.970-1.875,axis='Z',bevel=.006)
for name,rad,z0,z1 in [('Cam rotating hub',.055,1.960,2.035),('Cam front axial flange',.090,2.025,2.035)]:
 operand=cylinder25(name,(0,KY29,(z0+z1)/2),rad,z1-z0,axis='Z',bevel=.002);union_handle21(cam,operand,name+' actual union')
bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,segments=192,radius1=.025,radius2=.025,depth=.060)
for v in bm.verts:v.co+=Vector((.140,KY29,(1.835+1.895)/2))
for f in bm.faces:f.smooth=len(f.verts)==4
crank=finish(bm,'Cam actual rear crank pin',hardware,.002);union_handle21(cam,crank,'Cam rear crank physical union')
cut25(cam,cylinder25('Blind key shaft pocket',(0,KY29,(1.910+2.060)/2),.038,2.060-1.910,axis='Z'),'Cam actual blind shaft pocket',[2])
cut25(cam,box('Blind key bit pocket',[-.033,KY29-.135,1.910],[.033,KY29-.020,2.060],hardware,0),'Cam actual blind radial key bit pocket',[2])
# The C bearing has a real insertion opening and a top connection to the cover.
bearing=cylinder25('Chest Fixed Cam C Bearing',(0,KY29,(1.980+2.015)/2),.120,2.015-1.980,axis='Z',bevel=.003)
cut25(bearing,cylinder25('Cam bearing real bore',(0,KY29,(1.970+2.025)/2),.062,2.025-1.970,axis='Z'),'Actual front cam bearing bore',[0])
cut25(bearing,box('Cam bearing upright key bit passage',[-.040,KY29-.200,1.970],[.040,KY29,2.030],hardware,0),'Actual C bearing key insertion opening',[2])
bridge=box('Cam bearing fixed top bridge',[-.280,KY29+.105,2.005],[.280,KY29+.135,2.045],hardware,.003);union_handle21(bearing,bridge,'Cam bearing actual fixed top attachment');bearing['allowed_euler']=[2];prove_part(bearing,'Fixed C bearing connected assembly')
# Cylindrical faces receive actual radial normals after all Boolean rewrites.
for target in [cam,bearing]:
 me=target.data;me.update();v=coords25(target);norm=[]
 for face in me.polygons:
  q=v[list(face.vertices)];cyl=None
  tests=[(0,KY29,.175,1),(0,KY29,.055,1),(0,KY29,.090,1),(.140,KY29,.025,1),(0,KY29,.038,-1)] if target==cam else [(0,KY29,.120,1),(0,KY29,.062,-1)]
  if np.ptp(q[:,2])<.000001:tests=[]
  for cx,cy,rad,sign in tests:
   if np.max(abs(np.linalg.norm(q[:,:2]-[cx,cy],axis=1)-rad))<.00002:cyl=(cx,cy,sign);break
  for li in face.loop_indices:
   if cyl:
    p=v[me.loops[li].vertex_index];n=yaw@Vector(((p[0]-cyl[0])*cyl[2],(p[1]-cyl[1])*cyl[2],0)).normalized();norm.append((n.x,-n.z,n.y))
   else:norm.append(tuple(face.normal))
 me.normals_split_custom_set(norm);prove_part(target,target.name+' finished stage one')
assert not bvh(cam).overlap(bvh(bearing)),'Cam meets its fixed bearing'
# A complete catch is not claimed until slider, guides, key and driven motion exist.
(C/'internal_stage.json').write_text(json.dumps(dict(stage='Cam and front bearing built; carrier, retaining pin, guides, key and controls pending',complete_lock=False,cam=cam.name,fixed_bearing=bearing.name,actual_crank_segments=192,cam_bearing_intersections=0,remaining=['Receiver cheek rear depth correction','Slider frame, bridge and actual retaining pin','Fixed beam guides','Actual key and insertion path','Contact driven cam and slider controls','Whole relative motion and keyhole appearance proof']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True)
print('Saved actual blind keyed cam, rear crank and front C bearing. Internal catch stage one only.')
