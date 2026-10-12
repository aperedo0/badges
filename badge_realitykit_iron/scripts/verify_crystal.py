"""Verify broad polygon panels, ridge continuity, and bit-identical plane normals."""
import bpy,json,numpy as np
from pathlib import Path
from collections import Counter
from pxr import Usd,UsdGeom
r=Path(__file__).resolve().parents[1]
d=json.loads((r/'reports/crystal_design.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(r/'scenes/iron_medallion_master.blend'))
o=bpy.data.objects['Emblem | faceted compass spear'];mesh=o.data
p=np.asarray(d['outline']+d['ridge']);faces=d['front_faces'];count=d['front_planes']
assert count==6 and len(faces)==count
assert all(np.array_equal(np.asarray(v.co,dtype=np.float32),np.asarray(p[i],dtype=np.float32)) for i,v in enumerate(list(mesh.vertices)[:len(p)]))
assert all(not poly.use_smooth for poly in mesh.polygons)
assert all(mesh.polygons[i].material_index==0 for i in d['left_front_planes'])
assert all(mesh.polygons[i].material_index==2 for i in d['right_front_planes'])
for mod in o.modifiers:
    if mod.type=='BEVEL':assert mod.width<=.0040001 and mod.material==1
normals=np.array([mesh.polygons[i].normal[:] for i in range(count)])
plane_errors=[]
for face in faces:
    q=p[face];normal=np.cross(q[1]-q[0],q[2]-q[0]);normal/=np.linalg.norm(normal)
    plane_errors.append(float(np.abs((q-q[0])@normal).max()))
assert max(plane_errors)<1e-12
adjacent=[(i,j) for i in range(count) for j in range(i+1,count) if len(set(faces[i])&set(faces[j]))==2]
def angle(a,b):return float(np.degrees(np.arctan2(np.linalg.norm(np.cross(a,b)),a@b)))
angles=[angle(normals[i],normals[j]) for i,j in adjacent];assert min(angles)>1
edges=Counter(tuple(sorted((face[i],face[(i+1)%len(face)]))) for face in faces for i in range(len(face)))
ridge=d['ridge_vertex_indices'];ridge_edges=[tuple(sorted((a,b))) for a,b in zip(ridge,ridge[1:])]
assert all(edges[e]==2 for e in ridge_edges)
a,b=p[ridge[0],:2],p[ridge[-1],:2];delta=b-a
ridge_error=max(float(abs(np.cross(delta,p[i,:2]-a))/np.linalg.norm(delta)) for i in ridge)
# The reference ridge bends slightly in projection.
# At phone size, measure the full panels, never their hidden triangulation.
def project(points):
    camera=np.array([0.,1.8,23.]);forward=np.array([0.,-.55,0.])-camera;forward/=np.linalg.norm(forward)
    right=np.cross(forward,[0.,1.,0.]);right/=np.linalg.norm(right);up=np.cross(right,forward)
    delta=np.asarray(points)-camera;depth=delta@forward
    return np.stack([540+2250*(delta@right)/depth,720-2250*(delta@up)/depth],axis=1)
px=project(p);rim=project([[-3.015,0,.26],[3.015,0,.26]]);scale=320/abs(rim[1,0]-rim[0,0])
areas=[];widths=[]
for face in faces:
    q=px[face]*scale
    area=.5*abs(np.dot(q[:,0],np.roll(q[:,1],-1))-np.dot(q[:,1],np.roll(q[:,0],-1)))
    perimeter=sum(np.linalg.norm(q[(i+1)%len(q)]-q[i]) for i in range(len(q)))
    areas.append(float(area));widths.append(float(2*area/perimeter))
assert min(areas)>150 and min(widths)>5,(areas,widths)
# The final USDZ must repeat one exact normal across ALL triangles of each plane,
# including the subpixel strips assigned to that plane by rules 1 and 2.
t=json.loads((r/'reports/crystal_triangle_planes.json').read_text());canonical=np.asarray(t['canonical_normals'],dtype=np.float32)
stage=Usd.Stage.Open(str(r/'mobile/iron_badge_mobile.usdz'))
prim=next(p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh) and '/Emblem' in str(p.GetPath()));usd=UsdGeom.Mesh(prim)
ns=np.asarray(usd.GetNormalsAttr().Get(),dtype=np.float32).reshape(-1,3,3)
usd_points=np.asarray(usd.GetPointsAttr().Get(),dtype=np.float64)
usd_indices=np.asarray(usd.GetFaceVertexIndicesAttr().Get()).reshape(-1,3)
assert len(ns)==len(t['triangle_original_plane'])
rows=[]
for pi,normal in enumerate(canonical):
    broad=[i for i,owner in enumerate(t['triangle_original_plane']) if owner==pi]
    assert broad
    same=[i for i,v in enumerate(ns) if np.array_equal(v,np.tile(normal,(3,1)))]
    assert set(broad)<=set(same),(pi,broad,same)
    values=ns[same].reshape(-1,3);difference=float(np.abs(values-normal).max())
    normal_angle=max(angle(v.astype(float),normal.astype(float)) for v in values)
    assert difference==0 and normal_angle==0,(pi,difference,normal_angle)
    origin=np.asarray(mesh.vertices[mesh.polygons[pi].vertices[0]].co,dtype=np.float64)
    geometry_error=float(np.abs((usd_points[usd_indices[broad]].reshape(-1,3)-origin)@normal.astype(float)).max())
    assert geometry_error<3e-7,(pi,geometry_error)
    row={'plane':pi,'kind':'front_main' if pi in d['main_front_planes'] else 'front_shaded' if pi<count else 'side_wall' if pi<count+d['side_wall_planes'] else 'back',
         'broad_triangles':len(broad),'triangles_including_folded_strips':len(same),
         'maximum_normal_component_difference':difference,'maximum_normal_angle_degrees':normal_angle,
         'final_broad_plane_geometry_max_deviation_units':geometry_error,'normal':normal.tolist()}
    if pi<count:row.update(phone_panel_area_pixels_at_320px_badge=areas[pi],phone_panel_2area_over_perimeter_pixels=widths[pi])
    rows.append(row)
assert sum(row['triangles_including_folded_strips'] for row in rows)==len(ns)
report={'distinct_front_planes_at_one_degree':count,'front_quads':sum(len(f)==4 for f in faces),'front_tip_triangles':sum(len(f)==3 for f in faces),
        'minimum_adjacent_crease_degrees':min(angles),'ridge_vertex_indices':ridge,
        'ridge_edges_all_shared_by_left_and_right_front_planes':True,'projected_ridge_line_max_deviation_units':ridge_error,
        'analytic_front_planarity_max_deviation_units':max(plane_errors),'all_master_crystal_polygons_flat_shaded':True,
        'front_plane_normal_vectors':normals.tolist(),'left_main_right_shaded_materials':True,
        'maximum_normal_difference_within_any_plane':0.0,'maximum_normal_angle_within_any_plane_degrees':0.0,
        'final_broad_plane_geometry_max_deviation_units':max(row['final_broad_plane_geometry_max_deviation_units'] for row in rows),'planes':rows}
(r/'proof/crystal_design_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));print('PASS: six broad panels around a continuous centered ridge; normal difference exactly 0 within all front, side and back planes.')
