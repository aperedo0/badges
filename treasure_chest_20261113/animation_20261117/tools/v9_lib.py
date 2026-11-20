"""Shared helpers for the version 9 temple scripts (run inside Blender with exec). No deletes: objects are
reused by name and get fresh mesh data; materials are rebuilt in place."""
import bpy, math
from mathutils import Matrix, Vector

SCN = bpy.data.scenes["Chest Reveal"]
HERE = bpy.path.abspath("//")
RES = HERE + "temple/resources/cache/"


def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
    par = parent or SCN.collection
    if c.name not in [x.name for x in par.children]:
        par.children.link(c)
    return c


def temple_root():
    """Empty that carries the chest's frame (x right, y away from the camera, z up from the chest's floor)."""
    c = coll("Reveal Temple", bpy.data.collections["Reveal"])
    e = bpy.data.objects.get("Temple Root")
    if e is None:
        e = bpy.data.objects.new("Temple Root", None)
        c.objects.link(e)
        e.empty_display_size = 2.0
    e.matrix_world = bpy.data.objects["Reveal Chest Root"].matrix_world.copy()
    return e


def mesh_from(name, verts, faces, uvs=None, smooth=None, mat_idx=None, sharp_deg=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    n_loops = len(me.loops)
    vi = [0] * n_loops
    me.loops.foreach_get("vertex_index", vi)
    for uvname, vals in (uvs or {}).items():
        layer = me.uv_layers.new(name=uvname)
        data = [0.0] * (2 * n_loops)
        for li, v in enumerate(vi):
            data[2 * li], data[2 * li + 1] = vals[v]
        layer.data.foreach_set("uv", data)
    if smooth is not None:
        if isinstance(smooth, bool):
            smooth = [smooth] * len(me.polygons)
        me.polygons.foreach_set("use_smooth", smooth)
    if mat_idx is not None:
        me.polygons.foreach_set("material_index", mat_idx)
    if sharp_deg is not None:
        me.set_sharp_from_angle(angle=math.radians(sharp_deg))
    me.update()
    return me


def put(name, me, collection, mats=(), parent=None):
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, me)
        collection.objects.link(o)
    else:
        o.data = me
        if collection.name not in [c.name for c in o.users_collection]:
            collection.objects.link(o)
    me.name = name
    me.materials.clear()
    for m in mats:
        me.materials.append(m)
    if parent is not None:
        o.parent = parent
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.matrix_basis = Matrix.Identity(4)
    return o


def bevel(o, width, segments=2, angle=30.0, name="Temple Bevel"):
    m = o.modifiers.get(name) or o.modifiers.new(name, "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(angle)
    m.use_clamp_overlap = True
    m.harden_normals = False
    return m


def mat(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    return m


class NT:
    """Tiny node writer: n = NT(material); x = n.node('ShaderNodeMath', operation='MULTIPLY', ins={0: a, 1: 0.5})."""

    def __init__(self, m):
        self.t = m.node_tree
        self.x = 0

    def node(self, kind, ins=None, loc=None, label=None, **props):
        nd = self.t.nodes.new(kind)
        if loc:
            nd.location = loc
        else:
            self.x += 180
            nd.location = (self.x, 0)
        if label:
            nd.label = label
            nd.name = label
        for k, v in props.items():
            setattr(nd, k, v)
        for key, val in (ins or {}).items():
            sock = nd.inputs[key]
            self.set(sock, val)
        return nd

    def set(self, sock, val):
        if isinstance(val, bpy.types.NodeSocket):
            self.t.links.new(val, sock)
        elif isinstance(val, bpy.types.Node):
            self.t.links.new(val.outputs[0], sock)
        else:
            sock.default_value = val

    def link(self, a, b):
        self.t.links.new(a, b)

    # small math helpers returning sockets
    def math(self, op, a, b=None, c=None, clamp=False):
        ins = {0: a}
        if b is not None:
            ins[1] = b
        if c is not None:
            ins[2] = c
        return self.node("ShaderNodeMath", ins=ins, operation=op, use_clamp=clamp).outputs[0]

    def vmath(self, op, a, b=None, scale=None):
        ins = {0: a}
        if b is not None:
            ins[1] = b
        nd = self.node("ShaderNodeVectorMath", ins=ins, operation=op)
        if scale is not None:
            nd.inputs[3].default_value = scale
        return nd.outputs["Vector"] if op not in ("DOT_PRODUCT", "LENGTH", "DISTANCE") else nd.outputs["Value"]

    def mix(self, fac, a, b, kind="RGBA", blend="MIX"):
        nd = self.node("ShaderNodeMix", data_type=kind, blend_type=blend)
        if kind == "RGBA":
            self.set(nd.inputs[0], fac)
            self.set(nd.inputs[6], a)
            self.set(nd.inputs[7], b)
            return nd.outputs[2]
        if kind == "FLOAT":
            self.set(nd.inputs[0], fac)
            self.set(nd.inputs[2], a)
            self.set(nd.inputs[3], b)
            return nd.outputs[0]
        self.set(nd.inputs[0], fac)
        self.set(nd.inputs[4], a)
        self.set(nd.inputs[5], b)
        return nd.outputs[1]

    def ramp(self, fac, stops, interp="LINEAR"):
        nd = self.node("ShaderNodeMapRange", ins={0: fac, 1: stops[0], 2: stops[1], 3: 0.0, 4: 1.0},
                       interpolation_type="SMOOTHSTEP" if interp == "SMOOTH" else "LINEAR")
        nd.clamp = True
        return nd.outputs[0]

    def image(self, path, vec, color=True, proj="FLAT", blend=0.0):
        img = bpy.data.images.load(path, check_existing=True)
        img.colorspace_settings.name = "sRGB" if color else "Non-Color"
        nd = self.node("ShaderNodeTexImage", ins={0: vec})
        nd.image = img
        nd.projection = proj
        nd.projection_blend = blend
        nd.interpolation = "Linear"
        return nd

    def noise(self, vec, scale, detail=2.0, rough=0.5, dims="3D", distortion=0.0):
        nd = self.node("ShaderNodeTexNoise", ins={"Vector": vec, "Scale": scale, "Detail": detail,
                                                  "Roughness": rough, "Distortion": distortion},
                       noise_dimensions=dims)
        return nd

    def coord(self):
        return self.node("ShaderNodeTexCoord")

    def uv(self, name):
        return self.node("ShaderNodeUVMap", uv_map=name).outputs[0]

    def sep(self, v):
        return self.node("ShaderNodeSeparateXYZ", ins={0: v}).outputs

    def comb(self, x, y, z):
        return self.node("ShaderNodeCombineXYZ", ins={0: x, 1: y, 2: z}).outputs[0]

    def out(self, shader):
        o = self.node("ShaderNodeOutputMaterial")
        self.link(shader, o.inputs[0])
        return o
