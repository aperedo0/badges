assert 'Status: APPROVED (review round 1).' in (P/'mechanism30/PLAN.md').read_text()
receiver_cheek_rear_z=1.865
exec(compile((P/'tools/mechanism28_live.py').read_text(),'mechanism28_live.py','exec'))
# Build the real quarter turn yoke, bridge and retaining pin as one solid.
O=chamfer_rect(.065,.135,.004)+[-.010,-.606];I=chamfer_rect(.035,.105,.004)+[-.010,-.606];K=8
V=np.vstack([np.c_[q,np.full(K,z)] for q,z in [(O,1.830),(O,1.855),(I,1.855),(I,1.830)]]);F=[]
for k in range(4):
 for j in range(K):n=(k+1)%4;nj=(j+1)%K;F.append([k*K+j,k*K+nj,n*K+nj,n*K+j])
slider=solid('Chest Key Driven Slider',V,F,hardware,0);slider['allowed_euler']=[0];prove_part(slider,'Actual quarter turn yoke')
for name,lo,hi in [('Slider vertical stem',[-.035,-.490,1.830],[.015,-.185,1.855]),('Slider horizontal beam',[-.450,-.225,1.830],[.250,-.185,1.855]),('Slider retaining pin bridge',[-.435,-.225,1.830],[-.385,-.1265,1.990])]:
 part=box(name,lo,hi,hardware,.002);union_handle21(slider,part,name+' real connection')
pin=cylinder25('Actual short retaining pin',((-.500-.1475)/2,-.1465,1.970),.028,.500-.1475,axis='X',bevel=.001);union_handle21(slider,pin,'Retaining pin actual attachment')
bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,segments=int(globals().get('detent_pocket_segments',64)),radius1=.010,radius2=.010,depth=.050)
for v in bm.verts:v.co+=Vector((.100,float(globals().get('detent_pocket_center_y',-.187)),1.845))
pocket=finish(bm,'Beam rounded detent pocket',hardware,0);cut25(slider,pocket,'Actual shallow detent pocket',[0])
# Both rails have actual back plate support and leave the moving bridges clear.
caseback=sc.objects['Chest Case Back With Key Bore'];caseback['allowed_euler']=[0]
for name,lo,hi in [('Upper slider guide',[-.375,-.175,1.810],[.050,-.160,1.870]),('Lower slider guide',[-.760,-.250,1.810],[-.165,-.235,1.870])]:
 rail=box(name,lo,hi,hardware,.002);union_handle21(caseback,rail,name+' actual back attachment')
prove_part(slider,'Complete short slider stage one');prove_part(caseback,'Case back with attached guides')
assert not bvh(slider).overlap(bvh(caseback)),'Slider meets fixed guide or case back at rest'
assert not bvh(slider).overlap(bvh(sc.objects['Chest Hollow Lock Case Walls'])),'Slider meets cheek or wall at rest'
parts=json.loads((C/'mechanism_parts.json').read_text());parts.update(moving_slider=[slider.name],permanent_cam_removed=True,complete_lock=False,stage='Direct key catch stage one: slider and guides built; removable key and spring detent pending');(C/'mechanism_parts.json').write_text(json.dumps(parts,indent=2))
(C/'internal_stage.json').write_text(json.dumps(dict(stage='Real connected slider, retaining pin and attached guide rails saved',complete_lock=False,permanent_cam_and_bearing_hidden=True,retaining_pin_locked_span=[-.500,-.1475],stroke=.120,retracted_span=[-.620,-.2675],receiver_cheek_rear_z=1.865,remaining=['Actual removable key and pilot passage','Real spring detent and compliant contact','Quarter turn contact controls','Actual complete relative motion and insertion proofs','Closed keyhole comparison with28']),indent=2))
if not globals().get('DEFER_CHEST_SAVE',False):bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True)
print('Saved direct key slider, real short retaining pin and supported guides. Removable key, detent and controls pending.')

exec(compile((P/'tools/key30_live.py').read_text(),'key30_live.py','exec'))
