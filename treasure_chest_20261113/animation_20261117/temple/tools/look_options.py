"""Examples of the falling sand for the owner to choose from. NOTHING IS SAVED and the scene is not changed: this
runs before tools/v12_render.py in the same background Blender and only affects that one render.
    OPT_SAND=S1 ... blender -b chest_reveal_v12_full.blend --python temple/tools/look_options.py --python tools/v12_render.py
NOW is the sand of the approved render (separate grains). S1 to S5 are the soft curtain after the owner's
reference picture of 2026-11-21; A to D are the grain options of the first sheet."""
import bpy, os
SOFT = dict(DUST_VEIL=1, SAND_GRAINS=0)
OPTS = {
    "NOW": dict(),
    "A": dict(SAND_OPACITY=0.6),
    "B": dict(SAND_OPACITY=0.6, SAND_SIZES=(0.012, 0.013), SAND_WIDE=1.5),
    "C": dict(SAND_OPACITY=0.6, SAND_SIZES=(0.009, 0.010), DUST_TRICKLES=5, DUST_GRAINS=260, SAND_WIDE=1.8),
    "D": dict(SAND_OPACITY=0.6, SAND_SIZES=(0.007, 0.008), DUST_TRICKLES=1, DUST_GRAINS=1900, SAND_WIDE=2.4, SAND_DUR=(0.10, 0.12)),
    "S1": dict(SOFT, DUST_CLOUD=0.012),                                             # soft curtain
    "S2": dict(SOFT, DUST_CLOUD=0.007),                                             # fainter
    "S3": dict(SOFT, DUST_CLOUD=0.02),                                              # stronger
    "S4": dict(SOFT, DUST_CLOUD=0.014, VEIL_LENGTH=4.5, VEIL_WIDTH=0.8),             # shorter and narrower
    "S5": dict(DUST_VEIL=1, SAND_GRAINS=1, DUST_CLOUD=0.01, SAND_OPACITY=0.6, DUST_GRAINS=90),   # soft curtain with a few grains in it
}
key = os.environ.get("OPT_SAND", "NOW")
ns = {"__name__": "look_options", **OPTS[key]}
exec(open(bpy.path.abspath("//tools/v12_dust.py")).read(), ns)
print("LOOK OPTIONS sand", key, ns.get("result"), flush=True)
