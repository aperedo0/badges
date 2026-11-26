"""Version 21: the two shafts of night light 50 percent weaker and equally strong, and the sand on the right starts
0.2 s after the sand on the left (owner, 2026-11-25).

Run inside Claude_Temple_Ceiling.blend; safe to run again (every run starts over from what was there before the
first run); nothing is deleted. V21_UNDO=1 puts everything back as it was.

The owner, after the whole video with the new left opening: "I want the lights to be 40% less strong. and I want
the left sand to come down 0.2 seconds before the right one. and also when the light from inside comes on, it
should affect the light coming from the top how real physics would, idk how that is, I just know it will be
affected. and if it's not then that's fine". Shown that with the lights at 40 percent less: "make them both
actually 60% less bright instead of 40 and also make the left light the same brightness as the right. and show me
what that looks like by itself". Shown that: "ok actually show me 50% and 40% instead of 60%, both on separate
images", and with the two pictures in front of them: "50".

1. The lights. "The lights" are the two shafts of night light from the roof (Temple Shaft L and R), the ones the
   talk had been about. Each light's strength is a driver: a number times (1.5 - 0.5 * gold), so it is half again
   as strong in the dark and eases to the plain number as the hall lights up. Only that number changes. The right
   light's number is taken times V21_LIGHT (0.5: half the light; the tries before were 0.6 and 0.4), and the left
   light, which had always been 1.65 times the right, takes the right light's new number (V21_LEFT=right; "own"
   keeps the left on its own number times V21_LIGHT). The beam in the air, its patch on the stone and the sand it
   lights follow, at every moment of the video. Colour, the turn to warm as the fires light, cone, softness, the
   steady shadow level of version 17 and the openings are not touched.

2. The sand. Both curtains of sand (Temple Dust Cloud L and R) share one material and one clock, `dustfall` on
   Temple Story: seconds since the chest first hits the platform (scene frame 17). The sand lets go 0.1 s after
   that. The clock cannot run before the hit (it is held at 0 until then), and the sand's sound is laid to it, so
   the left keeps its moment and the right waits: each curtain now has a number, `sand_delay` (seconds), that the
   material takes off the clock for that curtain only. Left 0, right V21_LAG (0.2). The right curtain does
   everything it did, 0.2 s (6 pictures) later; its look is not touched.

3. The light from inside the chest. Nothing is changed for it, because the video already does what real light
   does. Two lights never change each other: the roof beams keep their strength and shape when the lid opens.
   What changes is what is around them: the chest's light brightens the stone behind the beams (Temple Chest
   Burst) and the dusty air of the hall (Temple Burst Rays), so the beams stand out less while it is bright.
   Measured in the video of 2026-11-25: left beam 41 of 255 before the lid opens and 42 at the brightest moment,
   the stone beside it 2 and then 20.

    V21 test, saves nothing:  blender -b <file> --python tools/v21_roof_light_and_sand.py --python tools/v12_render.py
V21_LIGHT (0.5) is how much of the right light's strength stays, V21_LEFT (right) gives the left light the same
strength, V21_LAG (0.2) is the right sand's wait, V21_UNDO=1 undoes."""
import bpy, os, re

E = os.environ.get
OB = bpy.data.objects
KEEP = float(E("V21_LIGHT", "0.5"))
LEFT = E("V21_LEFT", "right")                       # "right": the left light as strong as the right; "own": its own number
LAG = float(E("V21_LAG", "0.2"))
UNDO = E("V21_UNDO") == "1"
TAG = "v21 before"                                   # on each shaft light: its strength driver as it was
PROP = "sand_delay"                                  # on each sand curtain: seconds it waits after the clock
N_READ, N_SUB = "sand delay of this curtain", "clock less its delay"
SHAFTS = ("Temple Shaft L", "Temple Shaft R")
SANDS = {"Temple Dust Cloud L": 0.0, "Temple Dust Cloud R": LAG}
mat = bpy.data.materials["Temple Dust Cloud"]
nt = mat.node_tree
clock, first = nt.nodes["fall time"], nt.nodes["Math"]
assert first.operation == "SUBTRACT" and abs(first.inputs[1].default_value - 0.1) < 1e-6, "the sand's clock is not wired the way v13 left it"
assert 0.0 < KEEP <= 1.5 and 0.0 <= LAG <= 1.0 and LEFT in ("right", "own")


def P(*a):
    print("V21", *a, flush=True)


def strength(o):
    """the driver that sets this light's strength"""
    ad = o.data.animation_data
    ds = [d for d in (ad.drivers if ad else []) if d.data_path == "energy"]
    assert len(ds) == 1, o.name + " has no strength driver"
    return ds[0]


def put_back():
    did = False
    for n in SHAFTS:
        o = OB[n]
        if TAG in o:
            strength(o).driver.expression = o[TAG]
            did = True
    for name in (N_SUB, N_READ):
        nd = nt.nodes.get(name)
        if nd is not None:
            nt.nodes.remove(nd)
            did = True
    if not first.inputs[0].is_linked:
        nt.links.new(clock.outputs[0], first.inputs[0])
    return did


had = put_back()
assert [l.to_node for l in clock.outputs[0].links] == [first], "something else reads the sand's clock in this material"
if UNDO:
    for n in SHAFTS:
        if TAG in OB[n]:
            del OB[n][TAG]
    for n in SANDS:
        if PROP in OB[n]:
            del OB[n][PROP]
else:
    was = {}
    for n in SHAFTS:
        o = OB[n]
        if TAG not in o:
            o[TAG] = strength(o).driver.expression
        m = re.match(r"^\s*([0-9.]+)\s*\*\s*(\(.*\))\s*$", o[TAG])
        assert m, n + ": strength driver is not a number times a bracket: " + o[TAG]
        was[n] = (float(m.group(1)), m.group(2))
    assert was[SHAFTS[0]][1] == was[SHAFTS[1]][1], "the two lights do not follow the same curve"
    for n in SHAFTS:
        o = OB[n]
        num = was[SHAFTS[1] if LEFT == "right" else n][0] * KEEP
        strength(o).driver.expression = "%.1f * %s" % (num, was[n][1])
        P(n, "strength:", o[TAG], "->", strength(o).driver.expression)
    for n, wait in SANDS.items():
        o = OB[n]
        assert [s.material for s in o.material_slots] == [mat], n + " does not wear the shared sand material"
        o[PROP] = float(wait)
        o.id_properties_ui(PROP).update(min=0.0, max=2.0, description="Seconds this curtain of sand waits after the chest's first hit before it does what the sand clock says")
    read = nt.nodes.new("ShaderNodeAttribute")
    read.name = read.label = N_READ
    read.attribute_type = "OBJECT"
    read.attribute_name = PROP
    sub = nt.nodes.new("ShaderNodeMath")
    sub.name = sub.label = N_SUB
    sub.operation = "SUBTRACT"
    read.location = (clock.location.x, clock.location.y - 140)
    sub.location = (clock.location.x + 170, clock.location.y - 60)
    for l in list(first.inputs[0].links):
        nt.links.remove(l)
    nt.links.new(clock.outputs[0], sub.inputs[0])
    nt.links.new(read.outputs["Fac"], sub.inputs[1])
    nt.links.new(sub.outputs[0], first.inputs[0])
    P("sand: left waits", SANDS["Temple Dust Cloud L"], "s, right waits", SANDS["Temple Dust Cloud R"], "s after the clock")
for o in [OB[n] for n in SHAFTS] + [OB[n] for n in SANDS] + [OB["Temple Story"]]:
    o.update_tag()
bpy.context.view_layer.update()
if UNDO:
    P("undone:" if had else "nothing to undo:", "roof lights and sand clock are as before version 21;",
      [strength(OB[n]).driver.expression for n in SHAFTS])
