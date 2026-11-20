"""Diagnostic only, never saved: show the platform under the chest in another stone for one render.
DAIS_STYLE=pitted|dressed|carved  Chain before tools/v8_render.py."""
import bpy, os
st = os.environ.get("DAIS_STYLE")
if st:
    exec(open(bpy.path.abspath("//tools/v11_dais.py")).read(), {"__name__": "dais", "DAIS_STYLE": st})
    print("DAIS STYLE", st)
