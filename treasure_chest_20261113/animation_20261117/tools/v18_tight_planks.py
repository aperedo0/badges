"""Version 18: the three wood planks on the chest's front sit tight together (owner, 2026-11-24).

Run inside Claude_Temple_Ceiling.blend; safe to run again. Nothing is deleted and no mesh, picture, light or timing
is touched: only the materials the three front planks wear in this scene (Chest tone | Simple wood plank01, 02
and 03, set on the objects; the untoned materials of the same name on the meshes are not rendered and are left
alone). Every node this adds is
named "v18 ..."; the numbers it changes are kept on the material (custom property "v18 before"), and
V18_UNDO=1 puts everything back as it was.

The owner, on the reveal: "I notice that the wood planks have some tiny gaps between them, bring the wood planks
closer so that no gaps exist, adjust anything else you need to adjust".

What the gaps were. The front of the chest is three flat sheets, one per plank, shaped by their material (a height
picture pushes the surface in). Along every long edge of every plank the material did three things:
  * rounded the edge off over 0.04 and pulled it 70 percent of the way in, on top of a notch that the lower
    planks' height pictures already have along their upper edge, which made a groove about 0.08 wide and 0.05 deep
    between two planks, and the same groove where the wood meets the iron rims above and below;
  * painted the bottom of that groove nearly black (0.15 of the wood's colour, 0.03 wide);
  * shaded the wood toward the groove (0.72 at the edge).
In the video the groove is one to two pixels wide: a black line, and on its lower lip (the notched upper edge of
the lower plank) a hair thin blue white glint of the room's lights that breaks up into dots at video size (the
"tiny gaps"). It is not light from inside the chest: a black strip put behind the seam, and the lights inside the
chest switched off, each left it exactly as it was; hiding the lower plank removed it.

What this does. At each long edge the surface now runs straight to a level that both neighbours share, so two
planks meet exactly, with no groove and no lip to catch light:
  * the upper edge of the lower plank keeps its own level (the notch in its picture is filled in);
  * the lower edge of the plank above comes down to that same level over 0.02, a small rounded step, because the
    planks overlap like boards on a wall (each is thicker at the bottom than at the top; that shape is in the
    pictures and is kept);
  * where the wood meets the iron rims it keeps its own level, with no groove either;
  * the nearly black painted line becomes a hairline (half the wood's colour, 0.006 wide) so the boards still read
    as three boards, and the shading toward the edge is lighter (0.86 at the edge, over 0.04).
The lid, the sides and the back are single sheets whose joints are painted into their pictures; they are not touched.

    V18 test, saves nothing:  blender -b <file> --python tools/v18_tight_planks.py --python tools/v12_render.py
V18_STEP (0.02), V18_LINE (0.5), V18_LINE_W (0.003), V18_TONE (0.86), V18_TONE_W (0.04), V18_SEAM (0.62) set the
amounts; V18_UNDO=1 takes it all out."""
import bpy, os, json
import numpy as np

E = os.environ.get
TAG = "v18 "
STEP = float(E("V18_STEP", "0.02"))        # how far from the edge the surface is back on the plank's own shape
LINE = float(E("V18_LINE", "0.5"))         # the joint line: the wood's colour times this (it was 0.15)
LINE_W = float(E("V18_LINE_W", "0.003"))   # half the width of the joint line (it was 0.016)
TONE = float(E("V18_TONE", "0.86"))        # the shading toward the edge (it was 0.72)
TONE_W = float(E("V18_TONE_W", "0.04"))    # how far that shading reaches (it was 0.07)
SEAM = float(E("V18_SEAM", "0.62"))        # the level two planks meet at (height picture units; the lower plank's own)
UNDO = E("V18_UNDO") == "1"
# the level each plank keeps at its lower and upper edge: (lower, upper). Against the iron rims: its own level there.
LEVEL = {"R Simple Front Plank01": (0.96, SEAM), "R Simple Front Plank02": (SEAM, SEAM), "R Simple Front Plank03": (SEAM, 0.615)}
# the numbers this changes: (node, input number) -> what it is
NUMS = (("Seam gap", "From Min"), ("Seam gap", "From Max"), ("Seam shade", 0), ("Seam shade k", 1),
        ("Seam contact", "From Max"), ("Seam contact tone", 0), ("Seam contact k", 1))


def add(nt, kind, name):
    n = nt.nodes.new(kind)
    n.name = n.label = TAG + name
    return n


def undo(m):
    nt = m.node_tree
    N = nt.nodes
    if "v18 before" in m:
        for (node, inp), val in zip(NUMS, json.loads(m["v18 before"])):
            N[node].inputs[inp].default_value = val
        del m["v18 before"]
    if any(n.name.startswith(TAG) for n in N):
        nt.links.new(N["Seam height"].outputs[0], N["Displacement"].inputs["Height"])
    for n in [n for n in N if n.name.startswith(TAG)]:
        N.remove(n)


def v_runs_up(o):
    """True when the plank's picture runs bottom to top the way the plank does."""
    me = o.data
    uv = np.empty(len(me.loops) * 2, dtype=np.float32)
    me.uv_layers["SimplePlankUV"].data.foreach_get("uv", uv)
    vi = np.empty(len(me.loops), dtype=np.int32)
    me.loops.foreach_get("vertex_index", vi)
    co = np.empty(len(me.vertices) * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    z = co.reshape(-1, 3)[vi, 2]
    v = uv.reshape(-1, 2)[:, 1]
    return float(z[v > 0.9].mean()) > float(z[v < 0.1].mean())


def worn(o):
    """The material the plank is rendered with: the one on the object when there is one, else the mesh's."""
    return o.material_slots[0].material


def tight(o):
    m = worn(o)
    undo(m)                                             # start from the material as it was
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    m["v18 before"] = json.dumps([N[node].inputs[inp].default_value for node, inp in NUMS])
    lower, upper = LEVEL[o.name]
    if not v_runs_up(o):
        lower, upper = upper, lower
    # 1. the surface: at the edge the shared level, back on the plank's own shape STEP away
    which = add(nt, "ShaderNodeMath", "upper edge")
    which.operation = "GREATER_THAN"
    L.new(N["Seam uv"].outputs["Y"], which.inputs[0])
    which.inputs[1].default_value = 0.5
    level = add(nt, "ShaderNodeMix", "edge level")
    level.data_type = "FLOAT"
    L.new(which.outputs[0], level.inputs["Factor"])
    level.inputs["A"].default_value, level.inputs["B"].default_value = lower, upper
    ramp = add(nt, "ShaderNodeMapRange", "back to the plank")
    ramp.interpolation_type = "SMOOTHSTEP"
    L.new(N["Seam dist"].outputs[0], ramp.inputs["Value"])
    ramp.inputs["From Min"].default_value, ramp.inputs["From Max"].default_value = 0.0, STEP
    ramp.inputs["To Min"].default_value, ramp.inputs["To Max"].default_value = 0.0, 1.0
    h = add(nt, "ShaderNodeMix", "height")
    h.data_type = "FLOAT"
    L.new(ramp.outputs["Result"], h.inputs["Factor"])
    L.new(level.outputs["Result"], h.inputs["A"])
    L.new(N["Seam height bw"].outputs[0], h.inputs["B"])
    L.new(h.outputs["Result"], N["Displacement"].inputs["Height"])
    # 2. the colour: a hairline for the joint, lighter shading toward it
    N["Seam gap"].inputs["From Min"].default_value, N["Seam gap"].inputs["From Max"].default_value = 0.0, LINE_W
    N["Seam shade"].inputs[0].default_value, N["Seam shade k"].inputs[1].default_value = LINE, 1.0 - LINE
    N["Seam contact"].inputs["From Max"].default_value = TONE_W
    N["Seam contact tone"].inputs[0].default_value, N["Seam contact k"].inputs[1].default_value = TONE, 1.0 - TONE
    return (o.name, m.name, "picture runs up" if v_runs_up(o) else "picture runs down", (lower, upper))


done = []
for name in LEVEL:
    o = bpy.data.objects[name]
    if UNDO:
        undo(worn(o))
        done.append((name, worn(o).name, "put back"))
    else:
        done.append(tight(o))
bpy.context.view_layer.update()
print("V18 tight planks:", done, flush=True)
