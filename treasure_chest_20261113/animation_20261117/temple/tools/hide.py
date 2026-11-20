"""Diagnostic only, never saved: switch off the objects named in HIDE (comma separated) for this render."""
import bpy, os
for nm in [x for x in os.environ.get("HIDE", "").split(",") if x]:
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = True
