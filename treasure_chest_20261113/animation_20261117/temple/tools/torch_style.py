"""Diagnostic only, never saved: show the torches in another shape for one render.
TORCH_STYLE=goblet|slim|bowl, TORCH_LEAN=degrees (slim only, 0 stands it straight up)  Chain before tools/v8_render.py."""
import bpy, os
st = os.environ.get("TORCH_STYLE")
if st:
    g = {"__name__": "torches", "TORCH_STYLE": st}
    if os.environ.get("TORCH_LEAN"):
        g["TORCH_LEAN"] = float(os.environ["TORCH_LEAN"])
    exec(open(bpy.path.abspath("//tools/v11_torches.py")).read(), g)
    print("TORCH STYLE", st)
