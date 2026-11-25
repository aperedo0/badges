"""Version 19: no sparkle under the chest when the lid opens (owner, 2026-11-24).

Run inside Claude_Temple_Ceiling.blend; safe to run again. Nothing is deleted and no mesh, picture, light or timing
is touched: only the material of the gold ring set into the platform (Temple Gold Inlay). Every node this adds is
named "v19 ...", its one animation curve belongs to a node named "v19 ...", no number of the material is changed,
and V19_UNDO=1 takes everything out again.

The owner, on the reveal: "I am seeing these white specks at the bottom, find out why they are happening". Shown
three kinds and three choices, the owner picked the first: the sparkle under the chest goes, the grit stays.

What the sparkle was. The gold ring runs all the way round the platform, so one stretch of it lies behind the
chest. Through the gap under the chest, between its feet, that stretch shows as a faint gold line. When the lid
opens, the light that bursts out of the chest (Temple Chest Burst) just reaches it over the chest's back wall, at
the edge of the chest's shadow. The ring is shiny and thinner than a pixel there, so a few points flash white and
change every frame: video seconds 13.0 to 13.7 (reveal frames 42 to 63). Tested and ruled out: light leaking
through the chest, the sparks, the falling sand.

What this does. That one stretch of the ring (behind the chest, between its feet) answers no light once the chest
stands in front of it: its colour and the colour of its edge reflection both go to black there. It stays the same
plain metal as the rest of the ring, with the same Metallic and Roughness numbers, because wiring those two changed
the whole ring slightly, and taking the ring out of the burst light's receivers changed a pillar.
  * Before the chest lands that stretch is in plain view (the temple stands empty for a second), so it stays gold
    until the chest is down (scene frame 32) and goes dark over the next frames, under the landing dust
    (scene frames 34 to 46). The arrival's held frames, the waiting and the reveal all sit at frame 49 or later.
  * The faint gold line under the chest goes with it. The rest of the ring, left and right of the chest and in
    front of it, is exactly as it was.
The two other kinds of specks are not touched: the grit the feet kick up on landing (Reveal Dust Grit Boot ...)
and the pale chips in the platform's stone.

    V19 test, saves nothing:  blender -b <file> --python tools/v19_no_sparkle.py --python tools/v12_render.py
V19_SIDE0 (2.2) and V19_SIDE1 (2.5): across the chest, fully dark inside the first, untouched beyond the second.
V19_BACK0 (1.7) and V19_BACK1 (2.0): toward the back, untouched before the first, fully dark beyond the second.
V19_DOWN0 (34) and V19_DOWN1 (46): the scene frames the stretch goes dark between. V19_TURN (0.559): the chest's
turn in the temple. V19_UNDO=1 takes it all out."""
import bpy, os, math

E = os.environ.get
TAG = "v19 "
MAT, RING = "Temple Gold Inlay", "Temple Dais Gold Rings"
SIDE0, SIDE1 = float(E("V19_SIDE0", "2.2")), float(E("V19_SIDE1", "2.5"))
BACK0, BACK1 = float(E("V19_BACK0", "1.7")), float(E("V19_BACK1", "2.0"))
DOWN0, DOWN1 = int(E("V19_DOWN0", "34")), int(E("V19_DOWN1", "46"))
TURN = float(E("V19_TURN", "0.559"))
UNDO = E("V19_UNDO") == "1"
PAINT = ("Base Color", "Specular Tint")      # what answers light on a plain metal: its colour, its edge colour


def add(nt, kind, name, at):
    n = nt.nodes.new(kind)
    n.name = n.label = TAG + name
    n.location = at
    return n


def curves(nt):
    """This script's animation curves on the material's nodes, each with the list it sits in."""
    ad = nt.animation_data
    if ad and ad.action:
        for layer in ad.action.layers:
            for st in layer.strips:
                for cb in st.channelbags:
                    for fc in list(cb.fcurves):
                        if fc.data_path.startswith('nodes["' + TAG):
                            yield cb, fc


def undo(m):
    nt = m.node_tree
    N = nt.nodes
    for n in [n for n in N if n.name.startswith(TAG + "paint ")]:
        was = n.inputs[6].links[0].from_socket if n.inputs[6].links else None
        for to in [l.to_socket for l in n.outputs[2].links]:
            if was:                                     # the socket had a link of its own: give it back
                nt.links.new(was, to)
    for cb, fc in list(curves(nt)):
        cb.fcurves.remove(fc)
    ad = nt.animation_data
    if ad and ad.action and ad.action.name.startswith(TAG):
        act = ad.action
        if not any(len(cb.fcurves) for layer in act.layers for st in layer.strips for cb in st.channelbags):
            nt.animation_data_clear()
            bpy.data.actions.remove(act)
    for n in [n for n in N if n.name.startswith(TAG)]:
        N.remove(n)                                     # its links go with it; the sockets show their own numbers again


def dark(m):
    undo(m)                                             # start from the material as it was
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    pb = next(n for n in N if n.type == "BSDF_PRINCIPLED")
    x0, y0 = pb.location.x - 1500, pb.location.y - 520

    # 1. where a point of the ring lies, seen from the chest: across it, and toward the back of the temple
    geo = add(nt, "ShaderNodeNewGeometry", "place in the temple", (x0, y0))
    xyz = add(nt, "ShaderNodeSeparateXYZ", "place xyz", (x0 + 200, y0))
    L.new(geo.outputs["Position"], xyz.inputs[0])

    def along(name, a, b, row):                         # a*X + b*Y
        m1 = add(nt, "ShaderNodeMath", name + ", x part", (x0 + 400, y0 - row))
        m1.operation = "MULTIPLY"
        L.new(xyz.outputs["X"], m1.inputs[0])
        m1.inputs[1].default_value = a
        m2 = add(nt, "ShaderNodeMath", name, (x0 + 600, y0 - row))
        m2.operation = "MULTIPLY_ADD"
        L.new(xyz.outputs["Y"], m2.inputs[0])
        m2.inputs[1].default_value = b
        L.new(m1.outputs[0], m2.inputs[2])
        return m2.outputs[0]

    c, s = math.cos(TURN), math.sin(TURN)
    across, back = along("across the chest", c, s, 0), along("behind the chest", -s, c, 220)
    side = add(nt, "ShaderNodeMath", "either side", (x0 + 800, y0))
    side.operation = "ABSOLUTE"
    L.new(across, side.inputs[0])

    def ramp(name, sock, lo, hi, a, b, row):
        r = add(nt, "ShaderNodeMapRange", name, (x0 + 1000, y0 - row))
        r.interpolation_type = "SMOOTHSTEP"
        L.new(sock, r.inputs["Value"])
        r.inputs["From Min"].default_value, r.inputs["From Max"].default_value = lo, hi
        r.inputs["To Min"].default_value, r.inputs["To Max"].default_value = a, b
        return r.outputs["Result"]

    between = ramp("between the feet", side.outputs[0], SIDE0, SIDE1, 1.0, 0.0, 0)
    behind = ramp("behind the back wall", back, BACK0, BACK1, 0.0, 1.0, 260)
    stretch = add(nt, "ShaderNodeMath", "stretch behind the chest", (x0 + 1200, y0))
    stretch.operation = "MULTIPLY"
    L.new(between, stretch.inputs[0])
    L.new(behind, stretch.inputs[1])

    # 2. when: only once the chest stands in front of it (before that the stretch is in plain view)
    down = add(nt, "ShaderNodeValue", "chest is down", (x0 + 1000, y0 - 520))
    had = bool(nt.animation_data and nt.animation_data.action)
    for f, v in ((DOWN0, 0.0), (DOWN1, 1.0)):
        down.outputs[0].default_value = v
        down.outputs[0].keyframe_insert("default_value", frame=f)
    if not had:
        nt.animation_data.action.name = TAG + "chest is down"
    for cb, fc in curves(nt):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
        fc.update()
        down.outputs[0].default_value = fc.evaluate(bpy.context.scene.frame_current)
    hidden = add(nt, "ShaderNodeMath", "hidden stretch", (x0 + 1200, y0 - 260))
    hidden.operation = "MULTIPLY"
    L.new(stretch.outputs[0], hidden.inputs[0])
    L.new(down.outputs[0], hidden.inputs[1])

    # 3. there, the metal answers no light: its colour and its edge colour go to black
    for k, name in enumerate(PAINT):
        sock = pb.inputs[name]
        mix = add(nt, "ShaderNodeMix", "paint " + name, (pb.location.x - 220, y0 - 260 * k))
        mix.data_type = "RGBA"
        L.new(hidden.outputs[0], mix.inputs[0])
        if sock.links:
            L.new(sock.links[0].from_socket, mix.inputs[6])
        else:
            mix.inputs[6].default_value = tuple(sock.default_value)
        mix.inputs[7].default_value = (0.0, 0.0, 0.0, 1.0)
        L.new(mix.outputs[2], sock)
    return [(name, tuple(round(v, 3) for v in pb.inputs[name].default_value)) for name in PAINT]


m = bpy.data.materials[MAT]
ring = bpy.data.objects[RING]
assert any(sl.material == m for sl in ring.material_slots), "the ring does not wear " + MAT
wears = sorted(o.name for o in bpy.data.objects if any(sl.material == m for sl in o.material_slots))
if UNDO:
    undo(m)
    print("V19 no sparkle: put back;", MAT, "is worn by", wears, flush=True)
else:
    print("V19 no sparkle:", dark(m), "dark between scene frames", (DOWN0, DOWN1), ";", MAT, "is worn by", wears, flush=True)
bpy.context.view_layer.update()
