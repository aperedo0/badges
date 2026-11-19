import bpy,ast,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');C=R/'phase01/candidate27';source=(R/'phase01/tools/certify_motion27_live.py').read_text();node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='inside');ns={'Vector':Vector};exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual containment source>','exec'),ns)
yaw=Matrix.Rotation(math.radians(32),3,'Y')
def point(q):
 p=yaw@Vector(q);return Vector((p.x,-p.z,p.y))
def tree(name):
 m=bpy.context.scene.objects[name].data;m.calc_loop_triangles();return BVHTree.FromPolygons([v.co.copy() for v in m.vertices],[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True,epsilon=1e-8)
roof=tree('Chest Barrel Lid Envelope');pin=tree('Chest Front Hinge Pin');sleeve=tree('Chest Front Hasp Barrel');result={}
for name,pt,tr,want in [('roof_inside',point((0,1,0)),roof,True),('roof_outside_front',point((0,.5,2.3)),roof,False),('tongue_vertex_outside_roof',bpy.context.scene.objects['Chest Curved Hasp Tongue'].data.vertices[0].co,roof,False),('pin_center_inside_pin',point((0,.48525,2)),pin,True),('sleeve_bore_is_empty',point((0,.48525,2)),sleeve,False)]:
 got=ns['inside'](pt,tr);assert got==want,(name,got,want);result[name]=got
(C/'containment_validation.json').write_text(json.dumps({'actual_source_function_tested':True,'tests':result},indent=2));print(result)
