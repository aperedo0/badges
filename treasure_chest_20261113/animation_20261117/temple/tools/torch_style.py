"""Diagnostic only, never saved: show the torches in another shape for one render.
TORCH_STYLE=goblet|slim|bowl  Chain before tools/v8_render.py."""
import bpy, os
st = os.environ.get("TORCH_STYLE")
if st:
    exec(open(bpy.path.abspath("//tools/v11_torches.py")).read(), {"__name__": "torches", "TORCH_STYLE": st})
    print("TORCH STYLE", st)
