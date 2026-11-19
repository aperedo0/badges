assert 'Status: APPROVED (review round 1).' in (P/'thickness24/PLAN.md').read_text()
proof24=[]
def probe24(name,point,direction,axis,expected):
 ob=sc.objects[name];q=yaw@Vector(point);d=yaw@Vector(direction);q=Vector((q.x,-q.z,q.y));d=Vector((d.x,-d.z,d.y));ok,p,n,idx=ob.ray_cast(q,d)
 assert ok,(name,'miss',point)
 v=yaw.inverted()@Vector((p.x,p.z,-p.y));got=float(v[axis]);assert abs(got-expected)<2e-5,(name,got,expected)
 proof24.append(dict(part=name,point=list(point),axis=axis,actual=got,expected=expected));return got
for sx in (-1,1):
 probe24('Chest Body Envelope',(sx*3,-1,0),(-sx,0,0),0,sx*2.55)
 probe24(f'Chest Handle Mount {sx}',(sx*2.50,-.3,.80),(sx,0,0),0,sx*2.545)
for sz in (-1,1):
 probe24('Chest Body Envelope',(0,-1,sz*2),(0,0,-sz),2,sz*1.60)
 for name,y in [('Chest Body Upper Rim',.30),('Chest Lower Rim',-1.9)]:
  probe24(name,(1,y,0),(0,0,sz),2,sz*1.59)
  probe24(name,(1,y,sz*2.1),(0,0,-sz),2,sz*1.78)
 for sx in (-1,1):
  name=f'Chest Corner Upright {sx} {sz}'
  probe24(name,(sx*2.40,-.8,sz*1.50),(0,0,sz),2,sz*1.59)
  probe24(name,(sx*2.40,-.8,sz*1.95),(0,0,-sz),2,sz*1.77)
  probe24(name,(sx*2.4,-.8,sz*1.45),(sx,0,0),0,sx*2.54)
for sx in (-1,1):
 for name,y in [('Chest Body Upper Rim',.3),('Chest Lower Rim',-1.9)]:
  probe24(name,(0,y,.5),(sx,0,0),0,sx*2.54)
probe24('Chest Central Lock Strap',(0,-1.2,1.50),(0,0,1),2,1.595)
(C/'thickness_contact.json').write_text(json.dumps(dict(checks=proof24,body_half_width=2.55,body_half_depth=1.60,rail_front_projection=.18,upright_front_projection=.17,handle_plate_wood_overlap=.005,wood_recess=.050),indent=2))
print('Verified actual recessed wood, thicker metal backs, retained face projection and attachment overlaps.')
