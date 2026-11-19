assert 'Status: APPROVED (review round 1).' in (P/'mechanism28/PLAN.md').read_text()
hinge_relief_radius=.180
exec(compile((P/'tools/mechanism27_live.py').read_text(),'mechanism27_live.py','exec'))
outer28=np.array([[.254,.168],[.260,.168],[.270,.190],[.290,.190],[.298,.180],[.306,.180],[.314,.190],[.334,.190],[.344,.170],[.356,.170]])
profile28=np.vstack([outer28[0],[[.250,.164],[.250,.092],[.256,.086],[.354,.086],[.360,.092],[.360,.166]],outer28[:0:-1]])
old_outer=np.array([[.250,.184],[.256,.190],[.354,.190],[.360,.184]])
knots=np.unique(np.r_[old_outer[:,0],outer28[:,0],.250,.360]);new_outer=np.vstack([[[.250,.164]],outer28,[[.360,.166]]]);excess=np.interp(knots,new_outer[:,0],new_outer[:,1])-np.interp(knots,old_outer[:,0],old_outer[:,1]);assert excess.max()<1e-9
for sx in (-1,1):
 prof=profile28.copy();prof[:,0]*=sx
 a,b=sorted([sx*.250,sx*.360]);ob=annular25(f'Chest Fixed Front Hinge Knuckle {sx}',a,b,.190,.086,profile_override=prof);prove_part(ob,ob.name+' paired narrow collars')
(C/'collar_profile.json').write_text(json.dumps(dict(positive_outer_profile=new_outer.tolist(),inner_radius=.086,radial_segments=64,old_outer_profile=old_outer.tolist(),maximum_radius_excess=float(excess.max()),collar_material_subset=True,hinge_relief_radius=.180,minimum_inscribed_relief_radius=.180*math.cos(math.pi/64),radial_sleeve_clearance=.180*math.cos(math.pi/64)-.168,axial_sleeve_gap=.010),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'treasure_chest.blend'),compress=True)
print('Saved paired narrow collar ridges and tighter hidden hinge seat. New motion certification pending.')
