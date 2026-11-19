"""Build the whole Chest Reveal animation in one pass (run inside Blender):
    exec(open(".../tools/anim_all.py").read())
Order: landing -> (build, so the rings can sample the real motion) -> rings -> mystery, unlock,
opening, badge -> FX particles -> rest layer -> final build of every section's NLA strips."""
import bpy, sys, importlib
TOOLS = "/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/animation_20261117/tools"
sys.path.insert(0, TOOLS)
import anim_lib
importlib.reload(anim_lib)
from anim_lib import Keys, build, add_rest

ANIM_K = Keys()
ANIM_DEFER = True
bpy.context.window.scene = bpy.data.scenes["Chest Reveal"]
exec(open(TOOLS + "/anim_landing.py").read())
add_rest(ANIM_K)
build(ANIM_K)                       # landing + rest exist now, so the ring simulation can sample them
exec(open(TOOLS + "/anim_rings.py").read())
exec(open(TOOLS + "/" + globals().get("REVEAL", "anim_reveal.py")).read())   # v6: REVEAL = "anim_reveal_v6.py"
import os
if os.path.exists(TOOLS + "/anim_fx.py") and globals().get("FX_PARTICLES", True):   # v6: False, no dust or sparkles
    exec(open(TOOLS + "/anim_fx.py").read())
ANIM_K.k = {k: v for k, v in ANIM_K.k.items() if k[0] != "00 Rest"}
add_rest(ANIM_K)
made = build(ANIM_K)
print("anim_all: actions", len(made))
