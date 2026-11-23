"""Version 14: a great closed door behind the two front pillars, and two stone fire bowls at their feet.
Owner, 2026-11-22, with a picture of the ending made from the scene (the long hall replaced by a wall with an arched
wooden double door, the torches replaced by a fire bowl on a block at each pillar's foot): "I overall wasn't a fan of
the long hall with a bunch of fires. I think we could have collapsed it a little bit. So I want to go with this. The
main things I want you to take from this is ... above the pillars, behind them there's that like brick looking stuff.
That is going to be darkened up for sure. There's going to be a new fire source, and that fire source is visible ...
you're going to create the door and everything. Now, if other things were changed, you don't change them. Like the
pillars were changed, you don't change the pillars ... This is mainly about what's behind the pillars and beyond.
Anything from the pillars to the view doesn't change except for the fire. The fire does change."

Run inside chest_reveal_v12_full.blend, the main file (owner, same day: "I want you to touch the one that codex
duplicated from, which should be the main file"; Codex_Treasure_Chamber.blend is another agent's and is never
touched). The long hall version from before this change is kept as chest_reveal_v12_long_hall.blend.
Safe to run again; nothing is deleted: what is not wanted any more is switched off and kept in the file.

- The wall stands right against the back of the big arch between the two pillars (its face at y 60.9; the arch ends
  at 60.84). Coursed stone like the wall above the arch, much darker (WALL_DARK).
- One short hall leads from the big arch to the door, 14 deep ("there's some depth before the door. That needs to be
  a little longer"; fourth round: "a super mini hallway. We can make that longer ... so that it appears smaller ...
  long to the point where it starts to match the inspiration in terms of size"). It carries the big arch's own
  inner surface straight on, the same radius and the same stones under the same lights (third round: "there's like
  another little layer. It's one tunnel": a tunnel a little narrower than the arch had shown as a ring inside it).
- The door fills the end of the hall: 28.6 wide and 43.3 tall (the chest is 5.5 wide), its round top on the same
  centre as the big arch. Two leaves of four upright planks each; thick iron with real edges: a band round the edge
  and down the middle, four strap hinges with pointed ends and three studs each, two tall pull handles between
  chamfered blocks, big round studs. Fourth round ("the wood is like a different color, the metal's darker, more
  gritty ... it still needs a lot of work"), read off the owner's picture patch by patch: the wood a warm red brown
  with flowing grain cut into it (lines that run up each plank and close into a loop here and there), over the
  chest's own fine fibres; the iron nearly black, beaten, pitted and scuffed, its edges worn bright and coppery; the
  door lit by its own warm light from the upper left, brightest about its middle, so every line, dent, stud and edge
  has a lit and a shaded side.
- The big arch's stones and the wall above it turn darker and warmer as the gold light comes up ("the brick thing
  ... above the arch ... needs to be darkened to match the scene, to match the mock-up"); in the dark part of the
  story they are exactly as before.
- Everything behind the wall is switched off: the small arch and its pillars, the long hall, its lights and the far
  doorway. All twelve slim torches are switched off too.
- The fire: a wide, low eight sided stone bowl with a sunk panel on each side and a thick rim, sitting on a low
  square block, at the foot of each front pillar, full of charcoal to its rim and heaped up in the middle (fourth
  round: "the rocks ... look like they're sitting on top of a plate ... There should be like rocks under those rocks
  ... The shape of the bowl is different and it's also much lower to the ground"; see the notes at the bowls below).
  The fire, its glow, embers, coals and light are the first torch pair's own, moved into the bowls with a wider flame
  ("the flame is fine"), so they still follow lit_0 on Temple Torch Control and catch at the same moment the first
  torches did (the sound of the fire still fits).
- Nothing from the pillars to the camera is touched, except that the loose stones lying where the two blocks stand
  are hidden. The new wall and tunnel throw no shadow for the two cool side lights that stand behind them, so the
  pillars, the floor and the chest are lit as before (measured on stills of the dark wait and of the ending, before
  and after: the chest, the platform and the floor differ by under 1 of 255). The warm edge lights that stood for
  the hall's torches behind the pillars are off, and the two that glowed on the big arch and on the wall above it
  are nearly off and skip the door, as do the hall's cool light from above and its pale top light (they greyed the
  wood).
- The door has its own light (Temple Door Glow, in which only the door's own parts throw shadows, and Temple Door
  Fill) and two far lights seen only as glints in the iron (Temple Door Glint L and R); the fires do not light the
  door's wood and iron (they lit its foot brightest). Each bowl is lit from the firelit floor and the middle of the
  hall (Temple Bowl Fill, Temple Bowl Block Fill); in the dark the moonlight on the wall above the arch reaches the
  door's top.
- Checked with stills only (dark wait, fires catching, ending); no video was rendered."""
import bpy, math, random
from mathutils import Vector, Matrix

exec(open(bpy.path.abspath("//tools/v9_lib.py")).read())
G = globals().get
FLOOR = G("TEMPLE_FLOOR", -0.55)
root = temple_root()
TC = bpy.data.collections["Reveal Temple"]
RECV = bpy.data.collections["Temple Light Receivers"]
BURST = bpy.data.collections["Temple Burst Receivers"]
TORCH = bpy.data.collections["Temple Torches"]
DC = coll("Temple Door", TC)
ctrl = bpy.data.objects["Temple Torch Control"]
story = bpy.data.objects["Temple Story"]
CAM = Vector((0.0, -16.0, 8.0))                  # where the resting camera stands, in the chest's frame
rng = random.Random(G("DOOR_SEED", 14))

# Sizes read off the owner's picture (second round, 2026-11-22: "the metal and the wood are like totally off ... the
# door and the metal just look cheap ... Make it look as close as possible to the inspiration"), as shares of the
# door: four planks to a leaf; the iron band round the edge and the one down the middle about a seventh of a leaf
# wide; strap hinges from the edge to a fifth of the way from the middle, pointed, three studs each; pull handles
# from a fifth to half of the door's height; studs about as wide as two thirds of a band.
YW = G("DOOR_WALL_Y", 60.9)                      # the wall's face: right against the back of the big arch (it ends at 60.84),
                                                 # so no dark gap shows between the two; the pillars' feet stand a little into it
RO = G("DOOR_HALF", 14.36)                       # half the opening's width and the radius of its round top: the big arch's own
                                                 # inner radius, so arch and tunnel are one surface (third round: "there's like
                                                 # another little layer. It's one tunnel"; at 13.9 it showed as a ring inside)
ZS = 28.4                                        # where the round top springs (the big arch springs there too)
ZB = FLOOR - 0.05
# "there's some depth before the door. That needs to be a little longer. The mock-up is longer": the door sits this
# far back in the wall (it was 0.9), so a round tunnel of dark stone leads to it behind the big arch.
# Fourth round: "a super mini hallway. We can make that longer ... so that it appears smaller ... pushed back more.
# Make that little hall ... long to the point where it starts to match the inspiration in terms of size." In the
# With the hall 14 deep behind the big arch (it was 7.1) the door's own parts are the picture's size on the screen:
# the two strap hinges are as far apart and the handles as long as in the picture, to within a hundredth. (The door
# stays a tenth narrower than the picture's: it is a taller, narrower door, shaped by the scene's arch.) At 21 the
# door is 0.72 of its arch across, as in the picture, but an eighth smaller than the picture's door on the screen.
DEPTH = G("DOOR_DEPTH", 14.0)
YD = YW + DEPTH                                  # the planks' face
XW, ZT = 24.0, 47.0                              # the wall reaches past the picture's edges and above the big arch
BAND = 1.8                                       # width of the iron band round the door's edge
MID = 1.0                                        # half the width of the band down the middle
STRAPS = (4.1, 26.5)                             # heights of the strap hinges
HANDLE = (9.4, 21.8)                             # the pull handles: bottom and top
HX = 2.95                                        # and how far they stand from the middle
LT = 24.0                                        # one length of the chest's plank map covers this much of a plank's height


# ------------------------------------------------------------------ small builders (all in the chest's frame)
def prism(poly, y0, y1, uv=None):
    """A flat outline in x and z (counter clockwise seen from the camera), from y0 (toward the camera) back to y1."""
    n = len(poly)
    V = [(x, y0, z) for x, z in poly] + [(x, y1, z) for x, z in poly]
    F = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
    for i in range(n):
        j = (i + 1) % n
        F.append((i, n + i, n + j, j))
    U = None
    if uv:
        U = [uv(x, z) for x, z in poly] * 2
    return V, F, U


def box(x0, x1, y0, y1, z0, z1):
    return prism([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y0, y1)[:2]


def frustum(cx, cy, h0, h1, z0, z1):
    """A square block that narrows upward: half widths h0 below and h1 above."""
    V = [(cx + sx * h, cy + sy * h, z) for z, h in ((z0, h0), (z1, h1)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return V, F


def join(parts):
    V, F = [], []
    for v, f in parts:
        k = len(V)
        V += v
        F += [tuple(i + k for i in face) for face in f]
    return V, F


def arc(r, a0, a1, n, cz=ZS):
    return [(r * math.cos(a0 + (a1 - a0) * k / n), cz + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]


def lathe(profile, n, cx, cy, z0, turn=0.0):
    """Radius and height pairs turned round an upright axis; n sides."""
    V, F = [], []
    for r, z in profile:
        for k in range(n):
            a = turn + 2 * math.pi * k / n
            V.append((cx + r * math.cos(a), cy + r * math.sin(a), z0 + z))
    for i in range(len(profile) - 1):
        for k in range(n):
            a, b = i * n + k, i * n + (k + 1) % n
            F.append((a, b, b + n, a + n))
    F.append(tuple(range(n - 1, -1, -1)))                                    # closed underneath
    F.append(tuple((len(profile) - 1) * n + k for k in range(n)))            # and on top
    return V, F


def dome(x, z, y, r, h, n=14, rings=4):
    """A stud: a round head on the surface at depth y, facing the camera."""
    V, F = [], []
    for i in range(rings):
        a = (math.pi / 2) * i / rings
        for k in range(n):
            t = 2 * math.pi * k / n
            V.append((x + r * math.cos(a) * math.cos(t), y - h * math.sin(a), z + r * math.cos(a) * math.sin(t)))
    V.append((x, y - h, z))
    for i in range(rings - 1):
        for k in range(n):
            a, b = i * n + k, i * n + (k + 1) % n
            F.append((a, b, b + n, a + n))
    top = len(V) - 1
    for k in range(n):
        F.append(((rings - 1) * n + k, (rings - 1) * n + (k + 1) % n, top))
    return V, F


def lump(cx, cy, cz, r):
    """A piece of charcoal: a rough twenty sided stone."""
    t = (1 + 5 ** 0.5) / 2
    P = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t), (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
         (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    sq = (rng.uniform(0.75, 1.2), rng.uniform(0.75, 1.2), rng.uniform(0.55, 0.85))
    V = []
    for x, y, z in P:
        k = r * rng.uniform(0.8, 1.15) / math.sqrt(1 + t * t)
        V.append((cx + x * k * sq[0], cy + y * k * sq[1], cz + z * k * sq[2]))
    return V, F


def place(name, V, F, mats, uvs=None, smooth=False, bevel_w=None, shadow=True, mat_idx=None, sharp_deg=None, segments=2, edge=False):
    o = put(name, mesh_from(name, V, F, uvs=uvs, smooth=smooth, mat_idx=mat_idx, sharp_deg=sharp_deg), DC, mats, root)
    o.visible_shadow = shadow
    if bevel_w:
        bv = bevel(o, bevel_w, segments=segments, angle=30.0)
        bv.material = 1 if edge else -1                                  # the rounded edges take the second material (worn metal)
    for c in (RECV, BURST):
        if o.name not in c.objects:
            c.objects.link(o)
    return o


def drive(idb, path, expr, index=-1, g=0):
    try:
        idb.driver_remove(path, index) if index >= 0 else idb.driver_remove(path)
    except Exception:
        pass
    fcu = idb.driver_add(path, index) if index >= 0 else idb.driver_add(path)
    dr = fcu.driver
    dr.type = "SCRIPTED"
    var = dr.variables.new()
    var.name = "lit"
    var.type = "SINGLE_PROP"
    var.targets[0].id = ctrl
    var.targets[0].data_path = f'["lit_{g}"]'
    dr.expression = expr


# ------------------------------------------------------------------ materials
def darken_node(m):
    """A colour the stone's own colour is multiplied by, just before it is shaded."""
    nt = m.node_tree
    pb = next(nd for nd in nt.nodes if nd.bl_idname == "ShaderNodeBsdfPrincipled")
    dk = nt.nodes.get("v14 darken")
    if dk is None:
        dk = nt.nodes.new("ShaderNodeMix")
        dk.name = dk.label = "v14 darken"
        dk.data_type = "RGBA"
        dk.blend_type = "MULTIPLY"
        dk.inputs[0].default_value = 1.0
        src = pb.inputs["Base Color"].links[0].from_socket
        nt.links.new(src, dk.inputs[6])
        nt.links.new(dk.outputs[2], pb.inputs["Base Color"])
    return dk


def darker(src_name, new_name, k):
    """A copy of a stone the temple already has, with its colour turned down."""
    m = bpy.data.materials.get(new_name)
    if m is None:
        m = bpy.data.materials[src_name].copy()
        m.name = new_name
    darken_node(m).inputs[7].default_value = (k, k, k, 1)
    return m


def img(n, name, vec, color=True):
    nd = n.node("ShaderNodeTexImage", ins={0: vec})
    nd.image = bpy.data.images[name]
    nd.interpolation = "Linear"
    return nd


# "That is going to be darkened up for sure": the wall's stone at a sixth of the colour of the wall above the arch.
# The thin air of the hall glows a little in the firelight in front of the wall, so the stone itself has to be this
# dark to read clearly darker.
m_wall = darker("Temple Wall Masonry", "Temple Door Wall", G("WALL_DARK", 0.16))


def stone(name, tint, scale, shade=0.8):
    """Plain worn stone from the pillars' scan, tinted."""
    m = mat(name)
    n = NT(m)
    p = n.vmath("SCALE", n.coord().outputs["Object"], scale=scale)
    PS = RES + "polyhaven_plastered_stone_wall/plastered_stone_wall_"
    dif = n.image(PS + "diff_2k.jpg", p, proj="BOX", blend=0.25)
    rgh = n.image(PS + "rough_2k.jpg", p, color=False, proj="BOX", blend=0.25)
    dsp = n.image(PS + "disp_2k.png", p, color=False, proj="BOX", blend=0.25)
    ao = n.node("ShaderNodeAmbientOcclusion", ins={"Distance": 0.8})
    bc = n.mix(1.0, dif.outputs["Color"], tint, blend="MULTIPLY")
    bc = n.mix(shade, bc, ao.outputs["Color"], blend="MULTIPLY")      # how much nooks darken
    bump = n.node("ShaderNodeBump", ins={"Strength": 0.5, "Distance": 0.1, "Height": dsp.outputs["Color"]})
    pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": bc, "Roughness": n.math("ADD", 0.45, n.math("MULTIPLY", n.node("ShaderNodeRGBToBW", ins={0: rgh.outputs["Color"]}).outputs[0], 0.5)),
                                                "Normal": bump.outputs[0]})
    n.out(pb.outputs[0])
    return m



# Second round: "the brick thing that goes behind the pillars, like above the arch ... That needs to be darkened to
# match the scene, to match the mock-up." The big arch's stones and the wall above it turn darker and warmer as the
# gold light comes up (in the picture, about 41, 30, 20 of 255; they were about 50, 44, 39). In the dark part of the
# story they are exactly as before: the start the owner approved does not change.
ARCH_END = G("ARCH_END", (0.38, 0.18, 0.08))
for nm in ("Temple Arch Stone High", "Temple Wall Masonry"):
    dk = darken_node(bpy.data.materials[nm])
    for i, k in enumerate(ARCH_END):
        try:
            dk.inputs[7].driver_remove("default_value", i)
        except Exception:
            pass
        d = dk.inputs[7].driver_add("default_value", i).driver
        d.type = "SCRIPTED"
        v = d.variables.new()
        v.name = "gold"
        v.type = "SINGLE_PROP"
        v.targets[0].id = story
        v.targets[0].data_path = '["gold"]'
        d.expression = "1.0 - %.3f * gold" % (1.0 - k)


# The door's wood is the chest's own: the planks the owner approved on the chest (their colour, roughness and relief
# maps, already in this file), set upright, darker and browner, as an old door of the same timber would be.
# (The first try used a scan of grey weathered timber tinted brown: scratched and busy, "cheap".)
def wood(name, tag):
    m = mat(name)
    n = NT(m)
    uv = n.uv("UVMap")
    tone = n.sep(n.uv("Tone"))[0]                                     # each plank a little lighter or darker
    alb = img(n, f"Simple {tag}_albedo.png", uv)
    rgh = img(n, f"Simple {tag}_rough.png", uv)
    hgt = img(n, f"Simple {tag}_height16.png", uv)
    lum = n.node("ShaderNodeRGBToBW", ins={0: alb.outputs["Color"]}).outputs[0]
    fibre = n.ramp(lum, (0.055, 0.105))                               # the chest planks' own fine fibres (measured on the map)
    uvs = n.sep(uv)                                                   # 0 runs up the plank, 1 across it
    # Fourth round ("the wood is like a different color ... it still needs a lot of work"). Read off the picture:
    # its wood is drawn with flowing grain, lines that run up the plank and swing round a knot here and there, cut
    # into the surface so that their ridges catch the light; a warm red brown, brightest about the middle of the
    # door. This is the grain of a board sawn along a trunk: rings round a heart that wanders behind the board,
    # nearer the surface in places (there the lines close into long loops).
    along = n.math("MULTIPLY", uvs[0], LT)                             # units up the plank
    across = n.math("MULTIPLY", n.math("SUBTRACT", uvs[1], 0.5), 3.5)   # units across, nought in its middle
    seed = n.math("MULTIPLY", tone, 57.0)
    h1 = n.noise(n.comb(n.math("MULTIPLY", along, 0.085), seed, 0.0), 1.0, detail=1.0).outputs["Fac"]
    h2 = n.noise(n.comb(n.math("MULTIPLY", along, 0.07), n.math("ADD", seed, 7.3), 3.0), 1.0, detail=1.0).outputs["Fac"]
    dx = n.math("SUBTRACT", across, n.math("MULTIPLY", n.math("SUBTRACT", h1, 0.5), 3.4))
    dz = n.math("MAXIMUM", n.math("MULTIPLY", n.math("SUBTRACT", h2, 0.33), 3.4), 0.07)
    r = n.math("SQRT", n.math("ADD", n.math("MULTIPLY", dx, dx), n.math("MULTIPLY", dz, dz)))
    wob = n.noise(n.comb(n.math("MULTIPLY", across, 0.5), n.math("MULTIPLY", along, 0.11), seed), 1.0, detail=3.0, rough=0.6).outputs["Fac"]
    ph = n.math("MULTIPLY", n.math("ADD", r, n.math("MULTIPLY", n.math("SUBTRACT", wob, 0.5), 1.1)), 2.0 * math.pi * G("WOOD_RINGS", 3.0))
    ring = n.math("ADD", 0.5, n.math("MULTIPLY", n.math("SINE", ph), 0.5))
    # the lines come and go along the plank (drawn at one strength everywhere they read as stripes)
    fade = n.ramp(n.noise(n.comb(n.math("MULTIPLY", across, 0.7), n.math("MULTIPLY", along, 0.16), n.math("ADD", seed, 3.1)), 1.0, detail=2.0).outputs["Fac"], (0.3, 0.7), interp="SMOOTH")
    lines = n.math("ADD", 0.5, n.math("MULTIPLY", n.math("SUBTRACT", n.ramp(ring, (0.2, 0.85), interp="SMOOTH"), 0.5), n.math("ADD", 0.3, n.math("MULTIPLY", fade, 0.7))))
    st = n.noise(n.comb(n.math("MULTIPLY", uvs[1], 9.0), n.math("MULTIPLY", uvs[0], 1.6), n.math("MULTIPLY", tone, 31.0)), 1.0, detail=3.0, rough=0.6)
    streak = n.ramp(st.outputs["Fac"], (0.3, 0.72), interp="SMOOTH")
    k = n.math("ADD", n.math("ADD", n.math("MULTIPLY", lines, 0.42), n.math("MULTIPLY", fibre, 0.26)), n.math("MULTIPLY", streak, 0.32))
    c = n.mix(k, G("WOOD_DARK", (0.022, 0.0060, 0.0014, 1)), G("WOOD_LIGHT", (0.120, 0.035, 0.0080, 1)))
    edge = n.ramp(n.math("MINIMUM", uvs[1], n.math("SUBTRACT", 1.0, uvs[1])), (0.0, 0.09), interp="SMOOTH")
    shade = n.math("MULTIPLY", tone, n.math("ADD", 0.6, n.math("MULTIPLY", edge, 0.4)))
    c = n.mix(1.0, c, n.comb(shade, shade, shade), blend="MULTIPLY")
    ao = n.node("ShaderNodeAmbientOcclusion", ins={"Distance": 0.7})
    c = n.mix(0.85, c, ao.outputs["Color"], blend="MULTIPLY")
    bump = n.node("ShaderNodeBump", ins={"Strength": 0.35, "Distance": 0.1, "Height": hgt.outputs["Color"]})
    bump2 = n.node("ShaderNodeBump", ins={"Strength": G("WOOD_CUT", 0.45), "Distance": 0.1, "Height": lines, "Normal": bump.outputs[0]})
    rough = n.math("ADD", 0.1, n.node("ShaderNodeRGBToBW", ins={0: rgh.outputs["Color"]}).outputs[0])
    pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": c, "Roughness": rough, "Normal": bump2.outputs[0]})
    pb.inputs["Specular IOR Level"].default_value = 0.22              # little sheen: a full one laid a grey veil over the brown
    n.out(pb.outputs[0])
    return m                                                         # (the maps are the chest's own pictures: nothing about them is changed)


m_wood = [wood("Temple Door Wood A", "plank01"), wood("Temple Door Wood B", "plank03")]

m_gap = mat("Temple Door Gap")                                        # what shows between two planks: nothing
n = NT(m_gap)
n.out(n.node("ShaderNodeBsdfDiffuse", ins={"Color": (0.004, 0.003, 0.002, 1)}).outputs[0])

# The door's iron, fourth round ("the metal's darker, more gritty" in the picture). Read off it: nearly black brown
# iron beaten all over in shallow dents the size of a thumb, pitted and scuffed, with its edges worn bright and
# coppery where hands and time have rubbed them. Two materials: the body, and the worn edges (the rounded edges of
# every band, strap and handle take the second one).
m_iron = mat("Temple Door Iron")
n = NT(m_iron)
p = n.coord().outputs["Object"]
patch = n.ramp(n.noise(p, 1.1, detail=6, rough=0.7).outputs["Fac"], (0.38, 0.72), interp="SMOOTH")      # scuffed, lighter patches
dents = n.node("ShaderNodeTexVoronoi", ins={"Vector": p, "Scale": 0.95}, feature="SMOOTH_F1")           # hammer marks
grit = n.noise(p, 13.0, detail=3, rough=0.65).outputs["Fac"]
pits = n.node("ShaderNodeTexVoronoi", ins={"Vector": p, "Scale": 4.2}, feature="F1")
pit = n.math("SUBTRACT", 1.0, n.ramp(pits.outputs["Distance"], (0.05, 0.16), interp="SMOOTH"))           # 1 in a pit
icol = n.mix(patch, G("IRON_DARK", (0.0130, 0.0120, 0.0115, 1)), G("IRON_LIGHT", (0.044, 0.040, 0.038, 1)))
tex = n.math("MULTIPLY", n.math("ADD", 0.78, n.math("MULTIPLY", grit, 0.44)), n.math("SUBTRACT", 1.0, n.math("MULTIPLY", pit, 0.6)))
icol = n.mix(1.0, icol, n.comb(tex, tex, tex), blend="MULTIPLY")
ao = n.node("ShaderNodeAmbientOcclusion", ins={"Distance": 0.6})
icol = n.mix(0.85, icol, ao.outputs["Color"], blend="MULTIPLY")
hgt = n.math("SUBTRACT", n.math("ADD", n.math("MULTIPLY", dents.outputs["Distance"], 1.0), n.math("MULTIPLY", grit, 0.16)), n.math("MULTIPLY", pit, 0.25))
bump = n.node("ShaderNodeBump", ins={"Strength": G("IRON_BEAT", 0.9), "Distance": 0.14, "Height": hgt})
pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": icol, "Roughness": n.math("ADD", 0.44, n.math("MULTIPLY", n.math("ADD", patch, pit), 0.12)), "Metallic": 0.65,
                                            "Normal": bump.outputs[0]})
n.out(pb.outputs[0])
m_edge = mat("Temple Door Iron Edge")
n = NT(m_edge)
p = n.coord().outputs["Object"]
wear = n.ramp(n.noise(p, 2.6, detail=4, rough=0.65).outputs["Fac"], (0.3, 0.75), interp="SMOOTH")       # worn through here, still dark there
ecol = n.mix(wear, (0.030, 0.021, 0.014, 1), G("IRON_EDGE", (0.30, 0.155, 0.065, 1)))
pb = n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": ecol, "Roughness": n.math("SUBTRACT", 0.5, n.math("MULTIPLY", wear, 0.16)), "Metallic": 0.85})
n.out(pb.outputs[0])

# the bowls and their blocks: worn stone from the pillars' scan, warm; the bowl lighter than the block under it
# (no darkening of nooks on the bowl: under the thick rim it turned the whole bowl black)
m_bowl = stone("Temple Bowl Stone", G("BOWL_TINT", (0.58, 0.48, 0.38, 1)), 0.17, shade=0.0)
m_block = stone("Temple Bowl Block Stone", G("BLOCK_TINT", (0.38, 0.31, 0.25, 1)), 0.17, shade=0.6)

m_lump = mat("Temple Coal Lump")                                     # charcoal: nearly black, dull
n = NT(m_lump)
n.out(n.node("ShaderNodeBsdfPrincipled", ins={"Base Color": (0.03, 0.021, 0.016, 1), "Roughness": 0.85}).outputs[0])

# ------------------------------------------------------------------ the wall, and one tunnel from the big arch to the door
ARC_N = 96                                                           # the big arch's own steps round its curve
outline = [(-XW, ZB), (-RO, ZB)] + arc(RO, math.pi, 0.0, ARC_N) + [(RO, ZB), (XW, ZB), (XW, ZT), (-XW, ZT)]
wall = place("Temple Door Wall", [(x, YW, z) for x, z in outline], [tuple(range(len(outline)))], [m_wall])
# The tunnel carries the big arch's own inner surface straight on to the door: the same radius, the same stones (their
# joints run on down the tunnel), lit by the same lights. Below the arch, behind the pillars, its two sides are the
# coursed stone of the wall above the arch. It starts where the arch's rounded back edge begins (y 60.78).
prof = [(-RO, ZB)] + arc(RO, math.pi, 0.0, ARC_N) + [(RO, ZB)]
n_ = len(prof)
V = [(x, 60.78, z) for x, z in prof] + [(x, YD + 0.5, z) for x, z in prof]
F = [(i, n_ + i, n_ + i + 1, i + 1) for i in range(n_ - 1)]
tunnel = place("Temple Door Tunnel", V, F, [bpy.data.materials["Temple Arch Stone High"], bpy.data.materials["Temple Wall Masonry"]],
               mat_idx=[1] + [0] * (n_ - 3) + [1], smooth=True)

# ------------------------------------------------------------------ the two leaves: upright planks
RD = RO - 0.05                                                       # the door's own half width
parts, UV, TONE, MI = [], [], [], []
PT = 0.4                                                             # plank thickness
for side in (-1, 1):
    x = 0.05
    widths = [rng.uniform(0.92, 1.08) for _ in range(4)]
    sc = (RD - x) / sum(widths)
    for w in widths:
        x0, x1 = x + 0.035, x + w * sc - 0.035                        # a dark line between planks
        x = x + w * sc
        yf = YD + rng.uniform(0.0, 0.05)                              # no two planks sit quite flush
        tone_ = rng.uniform(0.82, 1.1)
        cuts = [ZB] + [z + rng.uniform(-0.3, 0.3) for z in STRAPS] + [None]     # boards meet under the straps
        for a, b in zip(cuts[:-1], cuts[1:]):
            if b is not None:
                poly = [(x0, a), (x1, a), (x1, b), (x0, b)]
                top_z = b
            else:
                top = [(xx, ZS + math.sqrt(max(RD * RD - xx * xx, 0.0))) for xx in (x1 - (x1 - x0) * k / 8 for k in range(9))]
                poly = [(x0, a), (x1, a)] + top
                top_z = ZS + RD
            if side < 0:
                poly = [(-px, pz) for px, pz in reversed(poly)]
            u0 = rng.uniform(0.0, max(1.0 - (top_z - a) / LT, 0.0))
            fu, fv = rng.random() < 0.5, rng.random() < 0.5            # each board a different stretch of the map, some turned round
            xa, xb = (x0, x1) if side > 0 else (-x1, -x0)

            def uvf(px, pz, a=a, u0=u0, fu=fu, fv=fv, xa=xa, xb=xb):
                u = u0 + (pz - a) / LT
                v = min(max((px - xa) / (xb - xa), 0.0), 1.0)
                return ((1.0 - u) if fu else u, (1.0 - v) if fv else v)
            v_, f_, u_ = prism(poly, yf, yf + PT, uv=uvf)
            parts.append((v_, f_))
            UV += u_
            TONE += [(tone_, 0.0)] * len(v_)
            MI += [rng.randrange(2)] * len(f_)                         # one of the chest's two wide plank maps
V, F = join(parts)
planks = place("Temple Door Planks", V, F, m_wood, uvs={"UVMap": UV, "Tone": TONE}, bevel_w=0.07, mat_idx=MI)
V, F = box(-RO - 0.3, RO + 0.3, YD + PT - 0.02, YD + PT + 0.3, ZB, ZS + RO + 0.3)
place("Temple Door Backing", V, F, [m_gap])

# ------------------------------------------------------------------ the ironwork: thick, with real edges
iron, studs, grips = [], [], []
PB, PM, PS_ = 0.42, 0.5, 0.36                                        # how far the edge band, the middle band and the straps stand proud
band = [(RD, ZB)] + arc(RD, 0.0, math.pi, 56) + [(-RD, ZB), (-(RD - BAND), ZB)] + arc(RD - BAND, math.pi, 0.0, 56) + [(RD - BAND, ZB)]
iron.append(prism(band, YD - PB, YD + 0.1)[:2])
iron.append(box(-MID, MID, YD - PM, YD + 0.1, ZB, ZS + RD - BAND + 0.2))             # down the middle, where the leaves meet
SR, SH = 0.58, 0.42                                                  # stud: radius and height
rm = RD - BAND / 2
for a in (0.0, 38.0, 90.0, 142.0, 180.0):                            # studs round the top, as in the picture
    a = math.radians(a)
    studs.append(dome(rm * math.cos(a), ZS + rm * math.sin(a), YD - PB, SR, SH))
for z in (19.5, 10.6, 1.9):                                          # down both sides
    for sx in (-1, 1):
        studs.append(dome(sx * rm, z, YD - PB, SR, SH))
for z in (35.0, 26.5, 15.6, 6.4):                                    # down the middle
    studs.append(dome(0.0, z, YD - PM, SR, SH))
for z in STRAPS:                                                     # strap hinges: from the edge toward the middle, pointed
    xa, xb, h = RD - BAND + 0.05, 0.19 * RD + 1.7, 1.05
    poly = [(xb - 1.7, z), (xb, z - h), (xa, z - h), (xa, z + h), (xb, z + h)]
    for sx in (-1, 1):
        iron.append(prism(poly if sx > 0 else [(-px, pz) for px, pz in reversed(poly)], YD - PS_, YD + 0.05)[:2])
        for t in (0.2, 0.5, 0.8):
            studs.append(dome(sx * (xb + (xa - xb) * t), z, YD - PS_, SR * 0.9, SH * 0.9))
for sx in (-1, 1):                                                   # the pull handles: a square bar between two chamfered blocks
    x_ = sx * HX
    grips.append(box(x_ - 0.55, x_ + 0.55, YD - 1.7, YD - 0.8, HANDLE[0] + 0.6, HANDLE[1] - 0.6))
    for z in HANDLE:
        grips.append(box(x_ - 1.25, x_ + 1.25, YD - 1.9, YD + 0.05, z - 0.85, z + 0.85))
V, F = join(iron)
place("Temple Door Iron", V, F, [m_iron, m_edge], bevel_w=0.14, segments=3, edge=True)
V, F = join(grips)
place("Temple Door Handles", V, F, [m_iron, m_edge], bevel_w=0.24, segments=2, edge=True)
V, F = join(studs)
place("Temple Door Studs", V, F, [m_iron], smooth=True)

DOOR = [bpy.data.objects[nm] for nm in ("Temple Door Wall", "Temple Door Planks", "Temple Door Backing", "Temple Door Iron", "Temple Door Handles", "Temple Door Studs")]
# The two cool side lights stand behind the wall's line and reach the pillars, the floor and the chest from there.
# The wall and the door throw no shadow for them, so everything in front is lit as it was.
SKIP = coll("Temple Door Shadow Skip", TC)
for o in DOOR + [tunnel]:
    if o.name not in SKIP.objects:
        SKIP.objects.link(o)
for co in SKIP.collection_objects:
    co.light_linking.link_state = "EXCLUDE"
for nm in ("Temple Cool L", "Temple Cool R"):
    bpy.data.objects[nm].light_linking.blocker_collection = SKIP

# ------------------------------------------------------------------ the fire bowls
# Fourth round: "the rocks ... look like they're sitting on top of a plate ... There should be like rocks under those
# rocks ... the overall shape needs work ... The shape of the bowl is different and it's also much lower to the
# ground." (The position is fine, and so is the flame.)
# The picture looks down on its bowls, so much of what I had read as the block's height is the block's top seen from
# above. Taking that out: the block is low, about a quarter of the bowl's width high, and the bowl is wide and low,
# about 0.38 of its width high, sitting straight on the block on a wide foot (no stem), its sides flaring a little
# to a thick rim. The bowl is full of charcoal to its rim, heaped up in the middle: lumps on lumps, three layers.
# As shares of the bowl's width: its foot 0.63, its sides from 0.66 to 0.96, the rim band 0.07 high; the block's
# foot 0.88, its body 0.85 narrowing to 0.77, its cap 0.81 (a tenth narrower than the picture's, because the block
# stands nearer this camera than the bowl's middle and looks that much wider).
BX, BY = G("BOWL_X", 15.0), G("BOWL_Y", 50.0)                         # in front of each front pillar (they stand at 17.2, 58)
BS = G("BOWL_SIZE", 1.0)
FL = 1.0 / math.cos(math.pi / 8)                                     # corners of an eight sided bowl stand this much further out than its sides
PED = FLOOR + 1.55 * BS                                              # top of the block the bowl stands on
# half widths across the flat sides, and heights: the bowl is 6 wide and 2.25 high
BOWL = [(r * BS * FL, z * BS) for r, z in ((1.9, 0.0), (1.9, 0.2), (1.82, 0.27), (2.0, 0.36), (2.86, 1.74), (3.0, 1.79), (3.0, 2.25),
                                           (2.62, 2.25), (2.48, 2.08), (2.4, 1.85), (0.5, 1.55))]
COAL = PED + 1.6 * BS                                                # the glowing bed, deep inside, under the charcoal
blocks, cups, lumps = [], [], []
for sx in (-1, 1):
    cx = sx * BX
    blocks.append(frustum(cx, BY, 2.65 * BS, 2.65 * BS, FLOOR - 0.02, FLOOR + 0.45 * BS))
    blocks.append(frustum(cx, BY, 2.54 * BS, 2.3 * BS, FLOOR + 0.45 * BS, FLOOR + 1.25 * BS))
    blocks.append(frustum(cx, BY, 2.42 * BS, 2.42 * BS, FLOOR + 1.25 * BS, PED))
    cups.append(lathe(BOWL, 8, cx, BY, PED, turn=math.pi / 8))
    # charcoal: a layer filling the bowl to its rim, a second on top of it, a third heaped in the middle
    for h, R, cnt in ((0.28, 2.1, 11), (0.28, 0.95, 5), (0.78, 1.45, 8), (0.82, 0.3, 1), (1.25, 0.7, 4)):
        for k in range(cnt):
            a = 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / cnt
            rr = R * (rng.uniform(0.82, 1.0) if cnt > 1 else 0.0) * BS
            lumps.append(lump(cx + rr * math.cos(a), BY + rr * math.sin(a), COAL + (h + rng.uniform(-0.07, 0.07)) * BS, rng.uniform(0.5, 0.68) * BS))
V, F = join(blocks)
bowl_blocks = place("Temple Fire Bowl Blocks", V, F, [m_block], bevel_w=0.07)
V, F = join(cups)
bowls = place("Temple Fire Bowls", V, F, [m_bowl], bevel_w=0.07)
# each of the bowl's eight sides carries a sunk panel, as the picture's bowl is carved
import bmesh
bm = bmesh.new()
bm.from_mesh(bowls.data)
bm.normal_update()
sides = [f for f in bm.faces if len(f.verts) == 4 and PED + 0.7 * BS < f.calc_center_median().z < PED + 1.4 * BS
         and abs(f.normal.z) < 0.8 and f.calc_area() > 2.5 * BS * BS]
bmesh.ops.inset_individual(bm, faces=sides, thickness=0.24 * BS, depth=-0.08 * BS, use_even_offset=True)
bm.to_mesh(bowls.data)
bm.free()
V, F = join(lumps)
coal_lumps = place("Temple Coal Lumps", V, F, [m_lump], bevel_w=0.04, shadow=False)

# Loose stones from the fallen roof lay exactly where the blocks stand: the ones under and against the blocks are
# hidden (a mask on the heap; nothing is removed from it).
fb = bpy.data.objects["Temple Fallen Blocks"]
vg = fb.vertex_groups.get("v14 under bowls") or fb.vertex_groups.new(name="v14 under bowls")
vg.remove(list(range(len(fb.data.vertices))))
seen, hidden_stones = set(), 0
nbr = {}
for e in fb.data.edges:
    a, b = e.vertices
    nbr.setdefault(a, []).append(b)
    nbr.setdefault(b, []).append(a)
M = root.matrix_world.inverted() @ fb.matrix_world
for v0 in range(len(fb.data.vertices)):
    if v0 in seen:
        continue
    isl, stack = [], [v0]
    seen.add(v0)
    while stack:
        a = stack.pop()
        isl.append(a)
        for b in nbr.get(a, ()):
            if b not in seen:
                seen.add(b)
                stack.append(b)
    P = [M @ fb.data.vertices[i].co for i in isl]
    x0, x1, y0, y1 = min(q.x for q in P), max(q.x for q in P), min(q.y for q in P), max(q.y for q in P)
    half = 2.65 * BS + 0.35
    for sx in (-1, 1):
        if x1 > sx * BX - half and x0 < sx * BX + half and y1 > BY - half and y0 < BY + half:
            vg.add(isl, 1.0, "REPLACE")
            hidden_stones += 1
            break
mk = fb.modifiers.get("v14 under bowls") or fb.modifiers.new("v14 under bowls", "MASK")
mk.vertex_group = vg.name
mk.invert_vertex_group = True
while fb.modifiers[0] != mk:                                         # before the heap's own edge rounding
    fb.modifiers.move(list(fb.modifiers).index(mk), 0)

# the flame: the torches' own fire, wider and fuller for a bowl (the same code draws it, with a brazier's shape)
SRC = open(bpy.path.abspath("//tools/v11_torches.py")).read()
A = SRC.index("def time_node(n, name):")
B = SRC.index("# ------------------------------------------------------------------ coals in the cup")
C = SRC.index("# ------------------------------------------------------------------ the flame")
D = SRC.index("# a soft glow in the air round each fire")
ns = {"bpy": bpy, "math": math, "NT": NT, "mat": lambda name: mat("Temple Bowl Flame"), "G": lambda k, d=None: d,
      "SHAPE": G("BOWL_FLAME", dict(card=(5.2, 5.6), width=0.6, round=1.5, tongues=1.6, split=3.0, sway=0.9, few=0.6))}
exec(SRC[A:B] + SRC[C:D], ns)
fm, FW, FH = ns["fm"], ns["FW"], ns["FH"]
gm, emb, cm = bpy.data.materials["Temple Fire Glow"], bpy.data.materials["Temple Embers"], bpy.data.materials["Temple Coals"]


def card(name, w, h, base, yaw, material, tint=None, grow=False):
    me = mesh_from(name, [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)], [(0, 1, 2, 3)],
                   uvs={"UVMap": [(0, 0), (1, 0), (1, 1), (0, 1)]})
    o = put(name, me, TORCH, [material], root)                       # the object keeps its drivers (size and brightness follow lit_0)
    o.matrix_basis = Matrix.Translation(base) @ Matrix.Rotation(yaw, 4, "Z")
    o.visible_shadow = False
    o.hide_render = o.hide_viewport = False
    if tint:
        o.color = (tint[0], tint[1], tint[2], o.color[3])
    if grow:                                                         # the fire grows as it catches
        drive(o, "scale", "lit", index=2)
        drive(o, "scale", "0.35 + 0.65 * lit", index=0)
    drive(o, "color", "lit", index=3)
    return o


FIRES = []
for i, sx in ((0, -1), (6, 1)):
    top = Vector((sx * BX, BY, COAL + 1.3 * BS))                     # the fire rises from the top of the heap
    to = CAM - top
    yaw = math.atan2(to.x, -to.y)
    fwd = Vector((to.x, to.y, 0)).normalized()
    right = Vector((math.cos(yaw), math.sin(yaw), 0.0))
    card(f"Temple Flame Back {i:02d}", FW * 1.18, FH * 1.12, top - fwd * 0.12, yaw, fm, tint=(0.55, 0.47, 0.38), grow=True)
    card(f"Temple Flame {i:02d}", FW, FH, top, yaw, fm, grow=True)
    card(f"Temple Flame Core {i:02d}", FW * 0.66, FH * 0.72, top + fwd * 0.06, yaw, fm, tint=(1.0, 0.95, 0.8), grow=True)
    # a bowl of coals burns across its whole bed: a lower flame each side of the tall one, each its own shape
    for tag, off, kw, kh in (("A", right * 0.8 * BS - fwd * 0.3, 0.62, 0.55), ("B", right * -0.75 * BS + fwd * 0.3, 0.58, 0.48)):
        card(f"Temple Bowl Flame {tag} {i:02d}", FW * kw, FH * kh, top + off, yaw, fm, grow=True)
        card(f"Temple Bowl Flame {tag} Core {i:02d}", FW * kw * 0.62, FH * kh * 0.7, top + off + fwd * 0.05, yaw, fm, tint=(1.0, 0.95, 0.8), grow=True)
    card(f"Temple Fire Glow {i:02d}", 10.0, 10.0, top - Vector((0, 0, 5.0 - 0.45 * FH)) - fwd * 0.2, yaw, gm)
    card(f"Temple Embers {i:02d}", 3.6, 9.5, top + fwd * 0.1, yaw, emb)
    # the coals: a low glowing heap inside the rim, under the lumps
    R, rings, seg = 2.3 * BS, 5, 18
    Vc, Fc = [(0.0, 0.0, 0.3)], []
    for r_ in range(1, rings + 1):
        for k in range(seg):
            a = 2 * math.pi * k / seg
            rr = R * r_ / rings
            Vc.append((rr * math.cos(a), rr * math.sin(a), 0.3 * (1 - (r_ / rings) ** 2) + (rng.uniform(-0.05, 0.07) if r_ < rings else 0.0)))
    for k in range(seg):
        Fc.append((0, 1 + k, 1 + (k + 1) % seg))
    for r_ in range(1, rings):
        for k in range(seg):
            a, b = 1 + (r_ - 1) * seg + k, 1 + (r_ - 1) * seg + (k + 1) % seg
            Fc.append((a, a + seg, b + seg, b))
    co = put(f"Temple Coals {i:02d}", mesh_from(f"Temple Coals {i:02d}", Vc, Fc), TORCH, [cm], root)
    co.matrix_basis = Matrix.Translation((sx * BX, BY, COAL))
    co.hide_render = co.hide_viewport = False
    co.visible_shadow = False
    # the fire's light: just above the flame's heart, a little toward the camera
    lo = bpy.data.objects[f"Temple Torch Light {i:02d}"]
    lo.location = top + Vector((0, 0, 1.9)) + fwd * 0.4
    lo.data.shadow_soft_size = 1.0
    lo.data.use_shadow = True
    lo.data.volume_factor = G("BOWL_AIR", 1.2)                       # its halo in the hall's thin air (the torches had 2: it veiled the door)
    lo.hide_render = lo.hide_viewport = False
    ph = (sum(ord(ch) * (k_ + 1) for k_, ch in enumerate(lo.name)) % 628) / 100.0
    drive(lo.data, "energy", "%.1f * lit * (0.88 + 0.07 * sin(frame * 0.83 + %.2f) + 0.05 * sin(frame * 1.91 + %.2f))"
          % (G("BOWL_E", 7000.0), ph, ph * 2))
    FIRES.append((lo, top, fwd))


# ------------------------------------------------------------------ who is lit by what
def group(name, include=(), exclude=(), base=None):
    """A list of things for a light: the temple's usual list (base) and more, without some."""
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if base is not None and base.name not in c.children:
        c.children.link(base)
    for o in list(include) + list(exclude):
        if o.name not in c.objects:
            c.objects.link(o)
    for cc in c.collection_children:
        cc.light_linking.link_state = "INCLUDE"
    ex = {o.name for o in exclude}
    for co, o in zip(c.collection_objects, c.objects):
        co.light_linking.link_state = "EXCLUDE" if o.name in ex else "INCLUDE"
    return c


def lamp(name, kind, loc, aim, expr, color, recv, **kw):
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, bpy.data.lights.new(name, kind))
        DC.objects.link(o)
    if o.data.type != kind:
        o.data.type = kind
    o.parent = root
    o.matrix_parent_inverse.identity()
    o.location = loc
    if aim is not None:
        o.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    o.data.color = color
    for k_, val in kw.items():
        setattr(o.data, k_, val)
    o.light_linking.receiver_collection = recv
    drive(o.data, "energy", expr)
    return o


# The two warm lights that stood for the torches' glow on the big arch and on the wall above it shine past the door
# without touching it, and are nearly off: they glowed for six pairs of torches at half the pillars' height. Two fires
# on the floor leave the arch and the wall above the pillars dark.
no_door = group("Temple Receivers No Door", exclude=DOOR, base=RECV)
for nm, g in (("Temple Arch Warm", 0), ("Temple Arch Face", 1)):
    lo = bpy.data.objects[nm]
    lo.light_linking.receiver_collection = no_door
    drive(lo.data, "energy", "%.1f * lit" % (lo.data["v11_base"] * G("ARCH_DIM", 0.06)), g=g)
# The hall's cool light from above and its pale warm top light skip the door as well: they greyed its wood (measured
# against the picture, the planks came out a third too grey). The door is lit by the fires, its own glow and the moon.
for nm in ("Temple Cool Top", "Temple High Light"):
    bpy.data.objects[nm].light_linking.receiver_collection = no_door
# The fires light everything the torches lit, but not the moss at the pillars' feet: right beside a fire its tufts
# turned into bright yellow blobs.
# Nor the door's own wood and iron (fourth round): the fires lit the foot of the door brightest, and in the picture the
# door is brightest about its middle. The door has its own light for that, below.
LEAVES = [bpy.data.objects[nm] for nm in ("Temple Door Planks", "Temple Door Backing", "Temple Door Iron", "Temple Door Handles", "Temple Door Studs")]
fire_recv = group("Temple Bowl Fire Receivers", exclude=[bpy.data.objects["Temple Moss Tufts"]] + LEAVES, base=RECV)
door_parts = group("Temple Door Parts", include=LEAVES)
door_only = group("Temple Door Only", include=DOOR)
bowl_only = group("Temple Bowls Only", include=[bowls, coal_lumps])
block_only = group("Temple Bowl Blocks Only", include=[bowl_blocks])
iron_only = group("Temple Door Iron Only", include=[bpy.data.objects[nm] for nm in ("Temple Door Iron", "Temple Door Handles", "Temple Door Studs")])
for lo, top, fwd in FIRES:
    lo.light_linking.receiver_collection = fire_recv
    # what the floor throws back up onto the bowl and its block (the fire itself sits inside the rim and cannot reach them)
    # The bowl's flaring sides face a little downward, so nothing from above reaches them: their light comes up from
    # the firelit floor in front and from the middle of the hall, where the other fire is (so its eight sides each
    # take the light differently and read as sides). The block under it gets a quarter of that.
    mid = Vector((-1.0 if top.x > 0 else 1.0, 0.0, 0.0))
    at = Vector((top.x, top.y, FLOOR + 0.9)) + fwd * 5.0 + mid * 3.5
    lamp(lo.name.replace("Torch Light", "Bowl Fill"), "POINT", at, None,
         "%.1f * lit" % G("BOWL_FILL", 1600.0), (1.0, 0.62, 0.36), bowl_only, shadow_soft_size=1.5, use_shadow=False, volume_factor=0.0)
    lamp(lo.name.replace("Torch Light", "Bowl Block Fill"), "POINT", at + Vector((0, 0, 1.2)), None,
         "%.1f * lit" % G("BLOCK_FILL", 1250.0), (1.0, 0.62, 0.36), block_only, shadow_soft_size=1.5, use_shadow=False, volume_factor=0.0)
# The door's own firelight, fourth round. In the picture the door is lit from the upper left, in a pool that is
# brightest about its middle and falls to half a third of the way up or down from there (measured: planks 59, 28, 10
# of 255 beside the handles, 43, 22, 8 above the top straps, 46, 23, 9 above the bottom ones), and the light rakes across it: every grain
# line, hammer mark, stud and edge has a lit side and a shaded side. So: one warm light from the upper left front,
# aimed at the door's middle, soft at its edge. Only the door's own parts throw shadows in it (it shines down a long
# hall from the side, which a real lamp could not; the walls would be in the way).
mid_z = (ZB + ZS + RD) / 2.0
key_at = Vector((0.0, YD, mid_z)) + Vector((-0.34, -0.87, 0.36)).normalized() * 46.0
kl = lamp("Temple Door Glow", "SPOT", key_at, (0.0, YD, mid_z),
          "%.1f * lit * (0.93 + 0.04 * sin(frame * 0.61) + 0.03 * sin(frame * 1.37))" % G("DOOR_GLOW", 70000.0), (1.0, 0.56, 0.24), door_only,
          spot_size=math.radians(G("DOOR_POOL", 52.0)), spot_blend=1.0, shadow_soft_size=0.7, use_shadow=True, volume_factor=0.0, specular_factor=0.5)
kl.light_linking.blocker_collection = door_parts
# a little light straight on, without shadows, so the shaded sides are not black
lamp("Temple Door Fill", "AREA", (0.0, YD - 40.0, mid_z), (0.0, YD, mid_z), "%.1f * lit" % G("DOOR_FILL", 1500.0), (1.0, 0.56, 0.26), door_only,
     shape="RECTANGLE", size=30.0, size_y=40.0, use_shadow=False, volume_factor=0.0, specular_factor=0.0)
# and glints for edges, studs and hammer marks only (nothing on the flat faces): two far lights from high on either
# side, seen only as reflections and only in the iron (on the whole door, at four times this, they washed wood and
# stone pale), as the picture's iron has a warm line of light on its upper edges
for tag, sx in (("L", -1.0), ("R", 1.0)):
    lamp("Temple Door Glint " + tag, "SUN", (sx * 30.0, 30.0, 60.0), (0.0, YD, 20.0), "%.2f * lit" % G("DOOR_GLINT", 0.6), (1.0, 0.62, 0.32), iron_only,
         angle=math.radians(6.0), use_shadow=False, volume_factor=0.0, diffuse_factor=0.0, specular_factor=1.0)
old = bpy.data.objects.get("Temple Door Glint")                      # the first, one sided glint (it sheened the left half only)
if old:
    old.hide_render = old.hide_viewport = True
# In the dark the moonlight that falls on the wall above the arch reaches the door too.
BACK = bpy.data.collections["Temple Back Receivers"]
for o in DOOR + [tunnel]:
    if o.name not in BACK.objects:
        BACK.objects.link(o)

# ------------------------------------------------------------------ what is switched off (kept in the file)
OFF_START = ("Temple Apse", "Temple Corridor", "Temple Far Light", "Temple Fog Back", "Temple Torch Iron", "Temple Torch Sheen",
             "Temple Bay Glow", "Temple Back Glow", "Temple Back Floor", "Temple Moon Shaft", "Temple Rim L", "Temple Rim R",
             "Temple Floor Sheen", "Temple Arch Crown Light")
FIRE_PARTS = ("Temple Flame", "Temple Fire Glow", "Temple Embers", "Temple Coals", "Temple Torch Light")
off = []
for o in bpy.data.objects:
    nm = o.name
    hide = nm.startswith(OFF_START)
    if nm.startswith(FIRE_PARTS) and nm[-2:].isdigit() and nm[-2:] not in ("00", "06"):
        hide = True
    if hide:
        o.hide_render = True
        o.hide_viewport = True
        off.append(nm)
bpy.context.view_layer.update()
result = {"door": "ok", "switched_off": len(off), "planks": len(parts), "studs": len(studs), "stones_hidden": hidden_stones}
