"""Version 12: the mist behaves like real warm smoke (owner's third review, 2026-11-20: "something about it. It
seems to be doing some not very physics-like things ... Just make sure it's in line with actual physics. Like,
it should be interacting with the box correctly"). Run inside chest_reveal_v12_full.blend, then bake once:
    blender -b chest_reveal_v12_full.blend --python tools/v12_bake_mist.py

What was wrong, seen frame by frame against the chest: the smoke rose a little, then stalled, lay flat at the
rim like a liquid and faded where it lay. Real warm smoke keeps rising and leaves. Two causes:
- Too little lift. The simulation works in the scene's units, where the chest is 5.5 units wide; read as metres
  that is a chest the size of a room, so smoke with a normal lift crawled. With three times the lift (`beta` 3)
  it leaves the chest at about 3 units a second, which for a real chest 0.7 m wide is about 0.4 m a second: the
  speed of smoke off a candle.
- Coarse cells. At 64 cells across, the lid's side walls were barely one cell thick. At 96 every wall is two to
  three cells thick, so the smoke follows the walls, the lid and the rising badge.
Nothing else is changed: one fill of smoke made while the lid is shut, nothing pushing it, the swinging lid and
the badge moving it, and it thins as it rises. The late fade in v12_slow.py only clears the last traces."""
import bpy

G = globals().get
dom = bpy.data.objects["Reveal Opening Domain"]
ds = next(m for m in dom.modifiers if m.type == "FLUID").domain_settings
# Only when a value differs: writing a simulation setting in the open Blender, even with the value it already
# has, makes Blender clear the baked files (it wiped a bake that was still running, 2026-11-20).
changed = []
# Second pass, same day: with three times the lift the main puff left, but what spilled over the rim had cooled
# and hung beside the chest as a flat sheet at rim height for over a second. More lift (5), so that even the
# thinned smoke keeps rising, and it thins away sooner (50 frames against 68).
for key, want in (("beta", G("MIST_LIFT", 5.0)), ("resolution_max", G("MIST_RES", 96)), ("dissolve_speed", G("MIST_THIN", 50))):
    if abs(getattr(ds, key) - want) > 1e-6:
        setattr(ds, key, want)
        changed.append(key)
result = {"mist": "ok", "lift": ds.beta, "cells": ds.resolution_max, "changed (bake again if not empty)": changed}
