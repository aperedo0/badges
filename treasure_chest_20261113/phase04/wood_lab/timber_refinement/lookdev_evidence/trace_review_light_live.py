import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/lookdev_evidence');sc=bpy.context.scene;assert sc.name=='Test plank master';dg=bpy.context.evaluated_depsgraph_get();R=Matrix.Rotation(math.radians(32),3,'Y')
def world(q):
 p=R@Vector(q);return Vector((p.x,-p.z,p.y))
N=world((0,0,1));rows=[]
for x in [-1.7,-1.2,1.0,1.6,2.0]:
 p=world((x,-1.45,1.604))
 for tag in ['Key','Fill']:
  light=sc.objects['Lab Chest Development '+tag];d=light.location-p;direction=d.normalized();hits=[]
  for u,v in [(0,0),(-.4,-.4),(-.4,.4),(.4,-.4),(.4,.4)]:
   q=light.matrix_world@Vector((u*light.data.size,v*light.data.size,0));ray=q-p;hit=sc.ray_cast(dg,p,ray.normalized(),distance=ray.length-.01)
   hits.append(hit[4].name if hit[0] else None)
  rows.append(dict(local_x=x,light=tag,hardware_blockers=hits,distance=d.length,incidence_from_flat_front_normal=math.degrees(math.acos(max(-1,min(1,N.dot(direction)))))))
(D/'hardware_light_paths.json').write_text(json.dumps(dict(method='Five visibility rays per light from the original front datum. This tests hardware occlusion, not fine grain self shadow or total rendered irradiance.',samples=rows),indent=2));print(json.dumps(rows))
