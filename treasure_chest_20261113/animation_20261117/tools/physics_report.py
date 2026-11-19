# blender -b --factory-startup --python-expr ... : print per-frame roll/pitch/yaw, COM height, corner heights
import json, sys, math
from mathutils import Matrix, Quaternion, Vector
path = sys.argv[sys.argv.index("--") + 1]
d = json.load(open(path)); st = int(d["params"]["steps"])
B, D, C = 2.775, 1.865, d["params"]["com"]
cs = [Vector((sx * B, sy * D, -C)) for sx in (-1, 1) for sy in (-1, 1)]
for i in range(0, len(d["frames"]), st):
    fr = d["frames"][i]
    if fr["t"] < 0.5 or fr["t"] > 1.6: continue
    q = Quaternion(fr["quat"]); M = Matrix.Translation(fr["loc"]) @ q.to_matrix().to_4x4()
    e = q.to_euler("XYZ")
    print(f"f{i//st+1:3d} t={fr['t']:.3f} roll={math.degrees(e.y):6.2f} pitch={math.degrees(e.x):5.2f} yaw={math.degrees(e.z):5.2f} comz={fr['loc'][2]:5.2f} x={fr['loc'][0]:5.2f} corners=" + " ".join(f"{(M@c).z:5.2f}" for c in cs))
